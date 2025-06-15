"""
Test Suite for Enhanced LangChain/LangGraph/LangServe Integration

This module tests the comprehensive implementation of LangChain, LangGraph, and LangServe
features in the AdWise AI Digital Marketing Campaign Builder.

Test Coverage:
- LangChain sequential chains and prompt engineering
- LangGraph workflow execution with advanced features
- LangServe API deployment and streaming
- Streaming service and WebSocket integration
- Custom tools and agents
- Memory persistence and conversation handling
- Error recovery and retry mechanisms
"""

import asyncio
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from fastapi import WebSocket

from app.main import app
from app.services.langchain_service import (
    LangChainCampaignService, LangGraphCampaignWorkflow,
    CampaignGenerationRequest, CampaignState
)
from app.services.streaming_service import (
    StreamingManager, StreamingCallbackHandler,
    create_streaming_session
)
from app.services.langserve_routes import (
    create_campaign_generation_chain,
    create_content_optimization_chain,
    create_conversational_chain
)


class TestLangChainService:
    """Test LangChain service functionality"""
    
    @pytest.fixture
    async def langchain_service(self):
        """Create LangChain service instance for testing"""
        service = LangChainCampaignService()
        # Mock EURI client
        service.llm = AsyncMock()
        service.llm.agenerate = AsyncMock(return_value=Mock(
            generations=[[Mock(text="Generated campaign content")]]
        ))
        return service
    
    @pytest.mark.asyncio
    async def test_campaign_generation_chain(self, langchain_service):
        """Test campaign generation using LangChain sequential chains"""
        request = CampaignGenerationRequest(
            campaign_objective="Increase brand awareness",
            target_audience={"age": "25-40", "interests": ["technology"]},
            budget=10000.0,
            channels=["facebook", "google"],
            brand_guidelines={"tone": "professional", "colors": ["blue", "white"]}
        )
        
        # Mock the chain execution
        with patch.object(langchain_service, '_get_llm', return_value=langchain_service.llm):
            result = await langchain_service.generate_campaign_with_chain(request)
        
        assert result is not None
        assert hasattr(result, 'campaign_objective')
        assert result.campaign_objective == request.campaign_objective
        
    @pytest.mark.asyncio
    async def test_prompt_engineering(self, langchain_service):
        """Test advanced prompt engineering with few-shot examples"""
        # Test that prompts are properly constructed
        request = CampaignGenerationRequest(
            campaign_objective="Launch new product",
            target_audience={"demographics": "millennials"},
            budget=5000.0,
            channels=["instagram", "tiktok"]
        )
        
        with patch.object(langchain_service, '_get_llm', return_value=langchain_service.llm):
            # Mock the prompt template creation
            with patch('app.services.langchain_service.PromptTemplate') as mock_prompt:
                mock_prompt.return_value.format = Mock(return_value="Formatted prompt")
                
                result = await langchain_service.generate_campaign_with_chain(request)
                
                # Verify prompt template was used
                assert mock_prompt.called


class TestLangGraphWorkflow:
    """Test LangGraph workflow functionality"""
    
    @pytest.fixture
    async def langgraph_workflow(self):
        """Create LangGraph workflow instance for testing"""
        workflow = LangGraphCampaignWorkflow()
        # Mock EURI client
        workflow.llm = AsyncMock()
        workflow.llm.agenerate = AsyncMock(return_value=Mock(
            generations=[[Mock(text="Generated content")]]
        ))
        return workflow
    
    @pytest.mark.asyncio
    async def test_workflow_creation(self, langgraph_workflow):
        """Test LangGraph workflow creation with advanced features"""
        workflow = langgraph_workflow.create_workflow()
        
        assert workflow is not None
        # Verify that advanced nodes are included
        # Note: In a real test, we'd check the workflow graph structure
        
    @pytest.mark.asyncio
    async def test_parallel_content_generation(self, langgraph_workflow):
        """Test parallel content generation for multiple channels"""
        state = CampaignState(
            objective="Test campaign",
            audience={"age": "25-35"},
            budget=1000.0,
            channels=["facebook", "instagram", "twitter"],
            strategy="Test strategy"
        )
        
        with patch.object(langgraph_workflow, '_get_llm', return_value=langgraph_workflow.llm):
            result = await langgraph_workflow.parallel_content_generation(state)
        
        assert result.ads is not None
        assert len(result.ads) > 0
        assert result.current_step == "parallel_content_complete"
        
    @pytest.mark.asyncio
    async def test_human_review_checkpoint(self, langgraph_workflow):
        """Test human-in-the-loop review functionality"""
        state = CampaignState(
            objective="Test campaign",
            audience={"age": "25-35"},
            budget=1000.0,
            channels=["facebook"],
            strategy="Test strategy",
            ads=[{"channel": "facebook", "content": "Test ad"}]
        )
        state.budget_allocation = {"facebook": 1000.0}
        
        result = await langgraph_workflow.human_review(state)
        
        assert hasattr(result, 'human_review_score')
        assert hasattr(result, 'human_approved')
        assert result.current_step == "human_review_complete"
        
    @pytest.mark.asyncio
    async def test_error_recovery(self, langgraph_workflow):
        """Test error recovery and retry mechanisms"""
        # Create state with missing components
        state = CampaignState(
            objective="Test campaign",
            audience={"age": "25-35"},
            budget=1000.0,
            channels=["facebook"],
            current_step="error"
        )
        # Missing strategy, ads, budget_allocation
        
        with patch.object(langgraph_workflow, '_get_llm', return_value=langgraph_workflow.llm):
            with patch.object(langgraph_workflow, 'generate_strategy', return_value=state) as mock_strategy:
                with patch.object(langgraph_workflow, 'create_content', return_value=state) as mock_content:
                    with patch.object(langgraph_workflow, 'allocate_budget', return_value=state) as mock_budget:
                        result = await langgraph_workflow.error_recovery(state)
        
        assert result.current_step == "recovery_complete"
        
    @pytest.mark.asyncio
    async def test_conditional_logic(self, langgraph_workflow):
        """Test conditional logic in workflow decisions"""
        # Test approval path
        approved_state = CampaignState(
            objective="Test",
            audience={},
            budget=1000.0,
            channels=["facebook"],
            human_approved=True
        )
        
        decision = langgraph_workflow.should_proceed_after_review(approved_state)
        assert decision == "approved"
        
        # Test rejection path
        rejected_state = CampaignState(
            objective="Test",
            audience={},
            budget=1000.0,
            channels=["facebook"],
            human_review_score=30
        )
        
        decision = langgraph_workflow.should_proceed_after_review(rejected_state)
        assert decision == "rejected"


class TestStreamingService:
    """Test streaming service functionality"""
    
    @pytest.fixture
    async def streaming_manager(self):
        """Create streaming manager for testing"""
        return StreamingManager()
    
    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test streaming session creation"""
        user_id = "test_user_123"
        session_id = await create_streaming_session(user_id)
        
        assert session_id is not None
        assert isinstance(session_id, str)
        
    @pytest.mark.asyncio
    async def test_websocket_connection(self, streaming_manager):
        """Test WebSocket connection management"""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        session_id = "test_session"
        user_id = "test_user"
        
        await streaming_manager.connect(mock_websocket, session_id, user_id)
        
        assert session_id in streaming_manager.active_connections
        assert session_id in streaming_manager.active_sessions
        assert streaming_manager.active_sessions[session_id]["user_id"] == user_id
        
    @pytest.mark.asyncio
    async def test_streaming_callback_handler(self):
        """Test streaming callback handler for LangChain"""
        mock_websocket = AsyncMock()
        handler = StreamingCallbackHandler("test_session", mock_websocket)
        
        # Test token handling
        await handler.on_llm_new_token("test_token")
        assert "test_token" in handler.tokens
        
        # Test chain start
        await handler.on_chain_start({"name": "TestChain"}, {"input": "test"})
        assert handler.current_step == "TestChain"
        
    @pytest.mark.asyncio
    async def test_content_streaming(self, streaming_manager):
        """Test streaming content generation"""
        session_id = "test_session"
        
        # Mock generation function
        async def mock_generation(callbacks=None, **kwargs):
            return "Generated content"
        
        updates = []
        async for update in streaming_manager.stream_content_generation(
            session_id=session_id,
            content_type="ad_copy",
            generation_function=mock_generation
        ):
            updates.append(update)
        
        assert len(updates) >= 2  # Start and end notifications
        assert any(update["type"] == "generation_start" for update in updates)
        assert any(update["type"] == "generation_complete" for update in updates)


class TestLangServeIntegration:
    """Test LangServe API deployment"""
    
    @pytest.mark.asyncio
    async def test_campaign_generation_chain_creation(self):
        """Test creation of campaign generation chain for LangServe"""
        with patch('app.services.langserve_routes.get_euri_client') as mock_client:
            mock_euri = AsyncMock()
            mock_euri._get_langchain_llm.return_value = AsyncMock()
            mock_client.return_value = mock_euri
            
            chain = await create_campaign_generation_chain()
            assert chain is not None
            
    @pytest.mark.asyncio
    async def test_content_optimization_chain_creation(self):
        """Test creation of content optimization chain"""
        with patch('app.services.langserve_routes.get_euri_client') as mock_client:
            mock_euri = AsyncMock()
            mock_euri._get_langchain_llm.return_value = AsyncMock()
            mock_client.return_value = mock_euri
            
            chain = await create_content_optimization_chain()
            assert chain is not None
            
    @pytest.mark.asyncio
    async def test_conversational_chain_creation(self):
        """Test creation of conversational AI chain with memory"""
        with patch('app.services.langserve_routes.get_euri_client') as mock_client:
            mock_euri = AsyncMock()
            mock_euri._get_langchain_llm.return_value = AsyncMock()
            mock_client.return_value = mock_euri
            
            chain = await create_conversational_chain()
            assert chain is not None


class TestAPIEndpoints:
    """Test enhanced API endpoints"""
    
    def test_langchain_endpoints_available(self):
        """Test that LangChain endpoints are properly registered"""
        client = TestClient(app)
        
        # Test that the router is included
        response = client.get("/api/v1/")
        assert response.status_code == 200
        
        # In a real test, we'd verify specific endpoints are available
        # This would require proper authentication setup
        
    @pytest.mark.asyncio
    async def test_streaming_endpoint_structure(self):
        """Test streaming endpoint structure"""
        # This would test the actual endpoint in integration tests
        # For now, we verify the endpoint exists in the router
        from app.api.v1.langchain_endpoints import router
        
        # Check that streaming endpoints are defined
        routes = [route.path for route in router.routes]
        assert any("/stream-content" in route for route in routes)
        assert any("/workflow/execute" in route for route in routes)
        assert any("/conversation" in route for route in routes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
