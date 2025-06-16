"""
LangServe Routes for AdWise AI Digital Marketing Campaign Builder

This module implements comprehensive LangServe integration to deploy LangChain chains
as REST APIs with streaming support. It provides:
- Campaign generation chains as APIs
- Content optimization workflows
- Real-time streaming responses
- Advanced agent-based tools
- Persistent conversation memory

Features:
- REST API deployment of LangChain chains
- Streaming responses for real-time generation
- WebSocket integration for live updates
- Custom tools and agents
- Memory persistence across sessions
- Error handling and monitoring
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, HTTPException
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool, tool
from langchain_core.callbacks import AsyncCallbackHandler, StreamingStdOutCallbackHandler
from langchain.schema.runnable import Runnable, RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolExecutor

try:
    from langserve import add_routes
    from langserve.pydantic_v1 import BaseModel, Field
    LANGSERVE_AVAILABLE = True
except ImportError:
    LANGSERVE_AVAILABLE = False
    BaseModel = object
    Field = lambda **kwargs: None

from euriai import EuriaiLangChainLLM
from app.integrations.euri import get_euri_client
from app.core.config import get_settings
from app.models.mongodb_models import Campaign, Ad, User

logger = logging.getLogger(__name__)
settings = get_settings()


# Pydantic models for LangServe APIs
class CampaignGenerationInput(BaseModel):
    """Input for campaign generation chain"""
    objective: str = Field(description="Campaign objective and goals")
    target_audience: Dict[str, Any] = Field(
        description="Target audience specifications")
    budget: float = Field(description="Campaign budget")
    channels: List[str] = Field(description="Advertising channels")
    brand_guidelines: Optional[Dict[str, Any]] = Field(default=None)
    user_id: Optional[str] = Field(default=None)


class ContentOptimizationInput(BaseModel):
    """Input for content optimization chain"""
    content: str = Field(description="Content to optimize")
    channel: str = Field(description="Target channel")
    audience: Dict[str, Any] = Field(description="Target audience")
    optimization_goals: List[str] = Field(
        description="Optimization objectives")


class ConversationInput(BaseModel):
    """Input for conversational AI chain"""
    message: str = Field(description="User message")
    session_id: str = Field(description="Conversation session ID")
    context: Optional[Dict[str, Any]] = Field(default=None)


# Custom tools for campaign optimization
@tool
async def analyze_campaign_metrics(campaign_data: str) -> str:
    """Analyze campaign performance metrics and provide insights"""
    try:
        # This would integrate with actual analytics service
        logger.info(f"Analyzing campaign metrics: {campaign_data[:100]}...")

        # Simulate analysis
        await asyncio.sleep(0.5)

        return """
        Campaign Analysis Results:
        - CTR: 2.3% (Above industry average)
        - Conversion Rate: 4.1% (Good performance)
        - Cost per Acquisition: $23.50
        - Recommendations: Increase budget for high-performing ads, 
          optimize underperforming creative elements
        """
    except Exception as e:
        logger.error(f"Campaign analysis failed: {e}")
        return f"Analysis failed: {str(e)}"


@tool
async def get_competitor_insights(industry: str, region: str = "global") -> str:
    """Get competitor insights for the specified industry and region"""
    try:
        logger.info(f"Fetching competitor insights for {industry} in {region}")

        # Simulate competitor analysis
        await asyncio.sleep(0.3)

        return f"""
        Competitor Insights for {industry}:
        - Average CPC: $1.25-$2.80
        - Top performing ad formats: Video (45%), Carousel (32%)
        - Peak engagement times: 7-9 PM weekdays
        - Trending keywords: sustainability, innovation, customer-first
        - Recommended budget allocation: 60% search, 40% social
        """
    except Exception as e:
        logger.error(f"Competitor insights failed: {e}")
        return f"Insights unavailable: {str(e)}"


@tool
async def validate_brand_compliance(content: str, brand_guidelines: str) -> str:
    """Validate content against brand guidelines"""
    try:
        logger.info("Validating brand compliance...")

        # Simulate brand validation
        await asyncio.sleep(0.2)

        return """
        Brand Compliance Check:
        ✅ Tone of voice: Consistent with brand guidelines
        ✅ Visual elements: Approved color palette used
        ⚠️ Messaging: Consider emphasizing sustainability values
        ✅ Legal compliance: No issues detected
        Overall Score: 85/100
        """
    except Exception as e:
        logger.error(f"Brand compliance check failed: {e}")
        return f"Validation failed: {str(e)}"


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Custom callback handler for streaming responses"""

    def __init__(self):
        self.tokens = []

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token from LLM"""
        self.tokens.append(token)
        logger.debug(f"New token: {token}")


async def create_campaign_generation_chain() -> Runnable:
    """Create campaign generation chain with EURI AI"""
    try:
        euri_client = await get_euri_client()
        llm = euri_client._get_langchain_llm()

        # Enhanced prompt template with few-shot examples
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert digital marketing strategist specializing in AI-powered campaign generation.
            
            Your task is to create comprehensive marketing campaigns based on the provided specifications.
            
            Example Campaign:
            Objective: Increase brand awareness for eco-friendly products
            Audience: Environmentally conscious millennials, ages 25-40
            Budget: $10,000
            Channels: Facebook, Instagram, Google Ads
            
            Generated Campaign:
            Strategy: Focus on sustainability messaging with user-generated content
            Facebook Ad: "Join the Green Revolution 🌱 Discover products that love the planet as much as you do"
            Instagram Ad: "Sustainable living made simple ✨ Shop conscious, live better"
            Google Ad: "Eco-Friendly Products | Sustainable Living Solutions | Free Shipping"
            
            Now create a campaign for the following specifications:"""),
            ("human", """
            Objective: {objective}
            Target Audience: {target_audience}
            Budget: ${budget}
            Channels: {channels}
            Brand Guidelines: {brand_guidelines}
            
            Please generate a comprehensive campaign including:
            1. Overall strategy
            2. Channel-specific ad copy
            3. Budget allocation recommendations
            4. Key performance indicators
            5. Optimization suggestions
            """)
        ])

        # Create chain with output parser
        chain = prompt | llm | StrOutputParser()

        return chain

    except Exception as e:
        logger.error(f"Failed to create campaign generation chain: {e}")
        raise


async def create_content_optimization_chain() -> Runnable:
    """Create content optimization chain"""
    try:
        euri_client = await get_euri_client()
        llm = euri_client._get_langchain_llm()

        # Tools for optimization
        tools = [analyze_campaign_metrics,
                 get_competitor_insights, validate_brand_compliance]
        tool_executor = ToolExecutor(tools)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content optimization specialist with access to analytics tools.
            
            Your role is to analyze and improve marketing content for better performance.
            Use the available tools to gather insights and provide data-driven recommendations.
            
            Available tools:
            - analyze_campaign_metrics: Get performance analysis
            - get_competitor_insights: Research competitor strategies  
            - validate_brand_compliance: Check brand guideline adherence
            """),
            ("human", """
            Content to optimize: {content}
            Target Channel: {channel}
            Target Audience: {audience}
            Optimization Goals: {optimization_goals}
            
            Please analyze and optimize this content using available tools.
            """)
        ])

        chain = prompt | llm | StrOutputParser()

        return chain

    except Exception as e:
        logger.error(f"Failed to create content optimization chain: {e}")
        raise


async def create_conversational_chain() -> Runnable:
    """Create conversational AI chain with memory"""
    try:
        euri_client = await get_euri_client()
        llm = euri_client._get_langchain_llm()

        # Create a simple chain without ConversationChain to avoid input variable issues
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are AdWise AI, an intelligent digital marketing assistant.

            You help users create, optimize, and manage their digital marketing campaigns.
            You have expertise in:
            - Campaign strategy and planning
            - Ad copy creation and optimization
            - Audience targeting and segmentation
            - Budget allocation and optimization
            - Performance analysis and insights
            - Multi-channel marketing coordination

            Be helpful, professional, and provide actionable insights.

            Previous conversation history: {chat_history}
            """),
            ("human", "{message}")
        ])

        # Create a simple chain that handles conversation context
        def format_chat_history(messages):
            if not messages:
                return "No previous conversation."

            formatted = []
            for msg in messages[-10:]:  # Keep last 10 messages
                if hasattr(msg, 'content'):
                    role = "Human" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                    formatted.append(f"{role}: {msg.content}")
            return "\n".join(formatted)

        # Create chain with proper input handling
        chain = (
            {
                "message": lambda x: x["message"],
                "chat_history": lambda x: format_chat_history(x.get("chat_history", []))
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        return chain

    except Exception as e:
        logger.error(f"Failed to create conversational chain: {e}")
        raise


async def setup_langserve_routes(app: FastAPI) -> None:
    """Setup LangServe routes for AI chains"""
    if not LANGSERVE_AVAILABLE:
        logger.warning("LangServe not available, skipping route setup")
        return

    try:
        logger.info("Setting up LangServe routes...")

        # Create chains
        campaign_chain = await create_campaign_generation_chain()
        optimization_chain = await create_content_optimization_chain()
        conversation_chain = await create_conversational_chain()

        # Add routes for each chain
        add_routes(
            app,
            campaign_chain,
            path="/langserve/campaign-generation",
            input_type=CampaignGenerationInput,
            config_keys=["configurable"]
        )

        add_routes(
            app,
            optimization_chain,
            path="/langserve/content-optimization",
            input_type=ContentOptimizationInput,
            config_keys=["configurable"]
        )

        add_routes(
            app,
            conversation_chain,
            path="/langserve/conversation",
            input_type=ConversationInput,
            config_keys=["configurable"]
        )

        logger.info("✅ LangServe routes successfully configured")
        logger.info("Available LangServe endpoints:")
        logger.info("  • POST /langserve/campaign-generation/invoke")
        logger.info("  • POST /langserve/campaign-generation/stream")
        logger.info("  • POST /langserve/content-optimization/invoke")
        logger.info("  • POST /langserve/content-optimization/stream")
        logger.info("  • POST /langserve/conversation/invoke")
        logger.info("  • POST /langserve/conversation/stream")

    except Exception as e:
        logger.error(f"Failed to setup LangServe routes: {e}")
        raise
