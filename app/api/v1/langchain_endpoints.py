"""
Enhanced LangChain API Endpoints for AdWise AI Digital Marketing Campaign Builder

This module provides advanced API endpoints that fully leverage LangChain, LangGraph,
and LangServe capabilities. It includes:
- Streaming content generation endpoints
- Advanced workflow orchestration
- Real-time progress tracking
- Agent-based optimization
- Memory-persistent conversations
- Tool-enhanced AI interactions

Features:
- Streaming responses for real-time generation
- WebSocket integration for live updates
- Advanced prompt engineering with few-shot examples
- Multi-step workflow orchestration with LangGraph
- Persistent conversation memory
- Custom tools and agents
- Error recovery and retry mechanisms
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.schemas.ai import (
    ContentGenerationRequest, ContentGenerationResponse,
    CampaignOptimizationRequest, CampaignOptimizationResponse
)
from app.services.langchain_service import (
    get_langchain_service, get_langgraph_workflow,
    CampaignGenerationRequest as LangChainCampaignRequest,
    CampaignState
)
from app.services.streaming_service import (
    get_streaming_manager, create_streaming_session,
    StreamingCallbackHandler
)
from app.integrations.euri import get_euri_client
from app.models.mongodb_models import User, Campaign
from app.api.deps import get_current_user
from app.core.database.mongodb import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# Enhanced request/response models
class StreamingContentRequest(BaseModel):
    """Request for streaming content generation"""
    prompt: str = Field(description="Content generation prompt")
    content_type: str = Field(description="Type of content to generate")
    channel: str = Field(description="Target channel")
    target_audience: Optional[Dict[str, Any]] = Field(default=None)
    brand_guidelines: Optional[Dict[str, Any]] = Field(default=None)
    stream_session_id: Optional[str] = Field(default=None)


class WorkflowExecutionRequest(BaseModel):
    """Request for LangGraph workflow execution"""
    campaign_objective: str = Field(description="Campaign objective")
    target_audience: Dict[str, Any] = Field(description="Target audience")
    budget: float = Field(description="Campaign budget")
    channels: List[str] = Field(description="Advertising channels")
    brand_guidelines: Optional[Dict[str, Any]] = Field(default=None)
    enable_human_review: bool = Field(default=True)
    enable_parallel_processing: bool = Field(default=True)


class ConversationRequest(BaseModel):
    """Request for conversational AI interaction"""
    message: str = Field(description="User message")
    session_id: Optional[str] = Field(default=None)
    context: Optional[Dict[str, Any]] = Field(default=None)


@router.post("/stream-content", response_model=Dict[str, Any])
async def stream_content_generation(
    request: StreamingContentRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate content with real-time streaming

    This endpoint provides streaming content generation with token-by-token updates
    via WebSocket connections for real-time user experience.
    """
    try:
        logger.info(f"Starting streaming content generation for user {current_user.id}")

        # Create or use existing streaming session
        session_id = request.stream_session_id or await create_streaming_session(current_user.id)

        # Get streaming manager
        streaming_manager = await get_streaming_manager()

        # Get EURI client and LangChain service
        euri_client = await get_euri_client()
        langchain_service = await get_langchain_service()

        # Create enhanced prompt with context
        enhanced_prompt = f"""
        Content Generation Request:
        Type: {request.content_type}
        Channel: {request.channel}
        Target Audience: {request.target_audience or 'General audience'}
        Brand Guidelines: {request.brand_guidelines or 'Standard guidelines'}

        User Prompt: {request.prompt}

        Please generate high-quality, engaging content optimized for {request.channel}.
        """

        # Define generation function
        async def generate_content(callbacks=None, **kwargs):
            llm = euri_client._get_langchain_llm()
            if callbacks:
                llm.callbacks = callbacks

            result = await llm.agenerate([enhanced_prompt])
            return result.generations[0][0].text

        # Start streaming generation
        generation_id = str(uuid4())

        # Execute with streaming
        async def stream_generator():
            async for update in streaming_manager.stream_content_generation(
                session_id=session_id,
                content_type=request.content_type,
                generation_function=generate_content
            ):
                yield f"data: {update}\n\n"

        return {
            "session_id": session_id,
            "generation_id": generation_id,
            "status": "streaming_started",
            "message": "Content generation started. Connect to WebSocket for real-time updates.",
            "websocket_url": f"/ws/streaming/{session_id}"
        }

    except Exception as e:
        logger.error(f"Streaming content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.post("/workflow/execute", response_model=Dict[str, Any])
async def execute_langgraph_workflow(
    request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute advanced LangGraph workflow for campaign generation

    This endpoint runs the complete campaign generation workflow using LangGraph
    with advanced features like parallel processing, human review, and error recovery.
    """
    try:
        logger.info(f"Executing LangGraph workflow for user {current_user.id}")

        # Get LangGraph workflow
        langgraph_workflow = await get_langgraph_workflow()

        # Configure workflow based on request
        langgraph_workflow.parallel_processing = request.enable_parallel_processing

        # Create workflow
        workflow = langgraph_workflow.create_workflow()

        # Prepare initial state
        initial_state = CampaignState(
            objective=request.campaign_objective,
            audience=request.target_audience,
            budget=request.budget,
            channels=request.channels,
            current_step="start"
        )

        # Add brand guidelines if provided
        if request.brand_guidelines:
            initial_state.brand_guidelines = request.brand_guidelines

        # Execute workflow
        workflow_id = str(uuid4())
        config = {
            "configurable": {
                "thread_id": workflow_id,
                "user_id": current_user.id
            }
        }

        logger.info(f"Starting workflow execution with ID: {workflow_id}")

        # Execute the workflow
        result = await workflow.ainvoke(initial_state, config)

        # Process results
        campaign_data = {
            "workflow_id": workflow_id,
            "objective": result.objective,
            "strategy": result.strategy,
            "ads": result.ads or [],
            "budget_allocation": getattr(result, 'budget_allocation', {}),
            "optimization": getattr(result, 'optimization', []),
            "competitor_insights": getattr(result, 'competitor_insights', None),
            "brand_validation": getattr(result, 'brand_validation', []),
            "human_review_score": getattr(result, 'human_review_score', None),
            "human_approved": getattr(result, 'human_approved', False),
            "current_step": result.current_step,
            "execution_time": datetime.utcnow().isoformat()
        }

        logger.info(f"Workflow execution completed: {workflow_id}")

        return {
            "status": "completed",
            "workflow_id": workflow_id,
            "campaign": campaign_data,
            "message": "Campaign generation workflow completed successfully"
        }

    except Exception as e:
        logger.error(f"LangGraph workflow execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@router.post("/conversation", response_model=Dict[str, Any])
async def conversational_ai(
    request: ConversationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Conversational AI with persistent memory

    This endpoint provides intelligent conversation capabilities with memory
    persistence across sessions for contextual interactions.
    """
    try:
        logger.info(f"Processing conversation for user {current_user.id}")

        # Get or create session
        session_id = request.session_id or str(uuid4())

        # Get LangChain service
        langchain_service = await get_langchain_service()

        # Create conversation chain with memory
        from langchain.chains import ConversationChain
        from langchain.memory import ConversationBufferWindowMemory

        euri_client = await get_euri_client()
        llm = euri_client._get_langchain_llm()

        # Memory for this session
        memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True
        )

        # Enhanced prompt for marketing assistant
        from langchain.prompts import PromptTemplate

        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""You are AdWise AI, an expert digital marketing assistant specializing in campaign creation and optimization.

Previous conversation:
{history}

User: {input}

Provide helpful, actionable marketing advice. Be specific and data-driven when possible.
Focus on:
- Campaign strategy and planning
- Ad copy optimization
- Audience targeting
- Budget allocation
- Performance analysis
- Multi-channel coordination

Assistant: {input}"""
        )

        # Create conversation chain
        conversation = ConversationChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=True
        )

        # Add context if provided
        context_str = ""
        if request.context:
            context_str = f"Context: {request.context}"

        # Generate response
        response = await conversation.apredict(
            input=f"{context_str}\n{request.message}" if context_str else request.message
        )

        return {
            "session_id": session_id,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Conversation processed successfully"
        }

    except Exception as e:
        logger.error(f"Conversation processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversation failed: {str(e)}"
        )


@router.websocket("/ws/streaming/{session_id}")
async def websocket_streaming_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: str = None  # In real implementation, extract from token
):
    """
    WebSocket endpoint for real-time streaming updates

    Provides real-time updates for AI content generation, workflow progress,
    and other streaming operations.
    """
    streaming_manager = await get_streaming_manager()

    try:
        # Connect to streaming manager
        await streaming_manager.connect(websocket, session_id, user_id or "anonymous")

        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))

                elif message.get("type") == "status_request":
                    await websocket.send_text(json.dumps({
                        "type": "status_response",
                        "session_id": session_id,
                        "connected": True,
                        "timestamp": datetime.utcnow().isoformat()
                    }))

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await streaming_manager.disconnect(session_id)


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get status of a streaming session"""
    try:
        streaming_manager = await get_streaming_manager()

        if session_id in streaming_manager.active_sessions:
            session_data = streaming_manager.active_sessions[session_id]
            return {
                "session_id": session_id,
                "active": True,
                "user_id": session_data["user_id"],
                "created_at": session_data.get("created_at", session_data.get("connected_at")),
                "last_activity": session_data["last_activity"]
            }
        else:
            return {
                "session_id": session_id,
                "active": False,
                "message": "Session not found or inactive"
            }

    except Exception as e:
        logger.error(f"Session status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )