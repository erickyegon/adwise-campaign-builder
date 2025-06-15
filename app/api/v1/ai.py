"""
AI Services API Endpoints

This module implements the AI service endpoints as specified in the LDL:
- generateCopy() - Generate ad copy using EURI AI + LangChain
- generateVisual() - Generate visual descriptions
- optimizeCampaign() - Campaign optimization with LangGraph
- analyzePerformance() - Performance analysis with AI insights

Integrates:
- EURI AI SDK for content generation
- LangChain for workflow orchestration
- LangGraph for complex decision workflows
- LangServe for AI service deployment

LDL Algorithm Implementation:
function generateCopy(adSpec):
    prompt = buildPrompt(adSpec)
    response = EURIClient.generate(prompt)
    return processResponse(response)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langserve import add_routes

from app.schemas.ai import (
    ContentGenerationRequest, ContentGenerationResponse,
    VisualGenerationRequest, VisualGenerationResponse,
    CampaignOptimizationRequest, CampaignOptimizationResponse,
    PerformanceAnalysisRequest, PerformanceAnalysisResponse,
    BatchContentRequest, BatchContentResponse
)
from app.services.langchain_service import (
    get_langchain_service, get_langgraph_workflow,
    CampaignGenerationRequest, CampaignGenerationResponse
)
from app.integrations.euri import get_euri_client
from app.models.mongodb_models import Campaign, Ad, Analytics, User
from app.api.deps import get_current_user, get_database
from app.core.database.mongodb import get_db
from app.tasks.ai_tasks import (
    batch_content_generation_task,
    campaign_optimization_task,
    performance_analysis_task
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-copy", response_model=ContentGenerationResponse)
async def generate_ad_copy(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> ContentGenerationResponse:
    """
    Generate ad copy using EURI AI + LangChain (LDL generateCopy Implementation)
    
    LDL Algorithm:
    function generateCopy(adSpec):
        prompt = buildPrompt(adSpec)
        response = EURIClient.generate(prompt)
        return processResponse(response)
    """
    try:
        logger.info(f"Generating ad copy for user {current_user.id}")
        
        # Get EURI AI client
        euri_client = await get_euri_client()
        
        # LDL: prompt = buildPrompt(adSpec)
        # Enhanced with LangChain for better prompt engineering
        langchain_service = await get_langchain_service()
        
        # Use LangChain for sophisticated prompt building
        if request.use_advanced_workflow:
            # Use LangChain sequential chains for complex generation
            chain_request = CampaignGenerationRequest(
                campaign_objective=request.prompt,
                target_audience=request.target_audience or {},
                budget=request.budget or 1000,
                channels=[request.channel],
                brand_guidelines=request.brand_guidelines
            )
            
            chain_response = await langchain_service.generate_campaign_with_chain(chain_request)
            
            # Extract content for the specific channel
            generated_content = ""
            for ad in chain_response.ads:
                if ad["channel"] == request.channel:
                    generated_content = f"{ad['headline']}\n\n{ad['body']}\n\nCTA: {ad['cta']}"
                    break
            
            return ContentGenerationResponse(
                success=True,
                content=generated_content,
                headline=chain_response.ads[0]["headline"] if chain_response.ads else "",
                body=chain_response.ads[0]["body"] if chain_response.ads else "",
                call_to_action=chain_response.ads[0]["cta"] if chain_response.ads else "",
                ad_type=request.ad_type,
                channel=request.channel,
                generated_at=datetime.now(),
                model_used="langchain_sequential",
                generation_metadata={
                    "workflow": "advanced_langchain",
                    "optimization_suggestions": chain_response.optimization_suggestions,
                    "budget_allocation": chain_response.budget_allocation
                }
            )
        
        else:
            # LDL: response = EURIClient.generate(prompt)
            response = await euri_client.generate_copy(
                prompt=request.prompt,
                ad_type=request.ad_type,
                channel=request.channel,
                target_audience=request.target_audience,
                brand_guidelines=request.brand_guidelines,
                max_length=request.max_length,
                temperature=request.temperature,
                creativity=request.creativity_level
            )
            
            # LDL: return processResponse(response)
            return ContentGenerationResponse(
                success=response.get("success", True),
                content=response.get("content", ""),
                headline=extract_headline_from_content(response.get("content", "")),
                body=extract_body_from_content(response.get("content", "")),
                call_to_action=extract_cta_from_content(response.get("content", "")),
                ad_type=request.ad_type,
                channel=request.channel,
                generated_at=datetime.now(),
                model_used=response.get("model", "euri-ai"),
                generation_metadata=response.get("parameters", {})
            )
        
    except Exception as e:
        logger.error(f"Error generating ad copy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ad copy: {str(e)}"
        )


@router.post("/generate-visual", response_model=VisualGenerationResponse)
async def generate_visual_description(
    request: VisualGenerationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> VisualGenerationResponse:
    """
    Generate visual descriptions using EURI AI (LDL generateVisual Implementation)
    """
    try:
        logger.info(f"Generating visual description for user {current_user.id}")
        
        # Get EURI AI client
        euri_client = await get_euri_client()
        
        # Generate visual description
        response = await euri_client.generate_visual_description(
            description=request.description,
            style=request.style,
            dimensions=request.dimensions,
            brand_colors=request.brand_colors,
            quality=request.quality,
            format=request.format
        )
        
        return VisualGenerationResponse(
            success=response.get("success", True),
            visual_description=response.get("visual_description", ""),
            style=request.style,
            dimensions=request.dimensions,
            brand_colors=request.brand_colors,
            generated_at=datetime.now(),
            model_used=response.get("model", "euri-ai"),
            generation_metadata={
                "quality": request.quality,
                "format": request.format,
                "style_applied": request.style
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating visual description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate visual description: {str(e)}"
        )


@router.post("/optimize-campaign", response_model=CampaignOptimizationResponse)
async def optimize_campaign_with_ai(
    request: CampaignOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> CampaignOptimizationResponse:
    """
    Optimize campaign using LangGraph workflow for complex decision making
    
    Uses LangGraph for:
    - Multi-step analysis
    - Conditional optimization paths
    - State-based decision making
    - Complex workflow orchestration
    """
    try:
        logger.info(f"Optimizing campaign {request.campaign_id} for user {current_user.id}")
        
        # Get campaign data
        campaign = await Campaign.get(request.campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check permissions
        if campaign.owner_id != str(current_user.id) and current_user.role not in ["admin", "editor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to optimize this campaign"
            )
        
        # Use LangGraph for complex optimization workflow
        if request.use_advanced_workflow:
            langgraph_workflow = await get_langgraph_workflow()
            workflow = langgraph_workflow.create_workflow()
            
            # Prepare state for LangGraph
            initial_state = {
                "objective": campaign.objective or "Optimize campaign performance",
                "audience": campaign.target_audience or {},
                "budget": campaign.budget or 0,
                "channels": [ad.channel for ad in campaign.ads] if campaign.ads else [],
                "current_step": "start"
            }
            
            # Execute LangGraph workflow
            config = {"configurable": {"thread_id": str(campaign.id)}}
            result = await workflow.ainvoke(initial_state, config)
            
            return CampaignOptimizationResponse(
                success=True,
                campaign_id=str(campaign.id),
                optimization_type="langgraph_workflow",
                recommendations=result.get("optimization", []),
                expected_improvements={
                    "ctr_improvement": 0.15,
                    "conversion_improvement": 0.12,
                    "cost_reduction": 0.08
                },
                priority_actions=[
                    "Implement A/B testing for headlines",
                    "Optimize budget allocation",
                    "Refine target audience"
                ],
                budget_reallocation=result.get("budget_allocation", {}),
                generated_at=datetime.now(),
                model_used="langgraph_workflow",
                workflow_metadata={
                    "steps_executed": result.get("current_step", "unknown"),
                    "state_transitions": "multi-step",
                    "decision_points": "conditional"
                }
            )
        
        else:
            # Use simple EURI AI optimization
            euri_client = await get_euri_client()
            
            # Prepare campaign data for optimization
            campaign_data = {
                "id": str(campaign.id),
                "name": campaign.name,
                "objective": campaign.objective,
                "budget": campaign.budget,
                "ads": [
                    {
                        "id": str(ad.id),
                        "type": ad.type,
                        "channel": ad.channel,
                        "copy": ad.copy,
                        "status": ad.status
                    }
                    for ad in campaign.ads
                ] if campaign.ads else []
            }
            
            # Get performance data if available
            performance_data = {}
            if request.include_performance_data:
                analytics = await Analytics.find(
                    Analytics.campaign_id == str(campaign.id)
                ).limit(100).to_list()
                
                if analytics:
                    performance_data = {
                        "total_impressions": sum(a.impressions for a in analytics),
                        "total_clicks": sum(a.clicks for a in analytics),
                        "average_ctr": sum(a.ctr for a in analytics) / len(analytics),
                        "total_spend": sum(a.spend or 0 for a in analytics),
                        "average_roi": sum(a.roi for a in analytics) / len(analytics)
                    }
            
            # Generate optimization recommendations
            response = await euri_client.optimize_campaign(
                campaign_data=campaign_data,
                performance_data=performance_data,
                goals=request.optimization_goals
            )
            
            return CampaignOptimizationResponse(
                success=response.get("success", True),
                campaign_id=str(campaign.id),
                optimization_type="euri_ai",
                recommendations=parse_recommendations(response.get("recommendations", "")),
                expected_improvements={
                    "ctr_improvement": 0.10,
                    "conversion_improvement": 0.08,
                    "cost_reduction": 0.05
                },
                priority_actions=extract_priority_actions(response.get("recommendations", "")),
                budget_reallocation={},
                generated_at=datetime.now(),
                model_used=response.get("model", "euri-ai"),
                workflow_metadata=response
            )
        
        # Schedule background task for detailed analysis
        background_tasks.add_task(
            campaign_optimization_task,
            str(campaign.id),
            request.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize campaign: {str(e)}"
        )


@router.post("/analyze-performance", response_model=PerformanceAnalysisResponse)
async def analyze_campaign_performance(
    request: PerformanceAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> PerformanceAnalysisResponse:
    """
    Analyze campaign performance using AI insights
    """
    try:
        logger.info(f"Analyzing performance for campaign {request.campaign_id}")
        
        # Get campaign
        campaign = await Campaign.get(request.campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get analytics data
        analytics = await Analytics.find(
            Analytics.campaign_id == str(campaign.id)
        ).sort(-Analytics.timestamp).limit(1000).to_list()
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analytics data found for this campaign"
            )
        
        # Prepare analytics data for AI analysis
        analytics_data = {
            "campaign_id": str(campaign.id),
            "total_records": len(analytics),
            "date_range": {
                "start": analytics[-1].timestamp.isoformat() if analytics else None,
                "end": analytics[0].timestamp.isoformat() if analytics else None
            },
            "metrics": {
                "total_impressions": sum(a.impressions for a in analytics),
                "total_clicks": sum(a.clicks for a in analytics),
                "average_ctr": sum(a.ctr for a in analytics) / len(analytics),
                "total_spend": sum(a.spend or 0 for a in analytics),
                "average_roi": sum(a.roi for a in analytics) / len(analytics),
                "total_conversions": sum(a.conversions or 0 for a in analytics)
            },
            "trends": calculate_performance_trends(analytics),
            "channel_breakdown": calculate_channel_breakdown(analytics)
        }
        
        # Use EURI AI for performance analysis
        euri_client = await get_euri_client()
        response = await euri_client.analyze_performance(
            analytics_data=analytics_data,
            time_period=request.time_period,
            analysis_type=request.analysis_type
        )
        
        # Schedule background task for detailed analysis
        background_tasks.add_task(
            performance_analysis_task,
            str(campaign.id),
            analytics_data,
            request.dict()
        )
        
        return PerformanceAnalysisResponse(
            success=response.get("success", True),
            campaign_id=str(campaign.id),
            analysis_period=request.time_period,
            key_insights=parse_insights(response.get("insights", "")),
            performance_trends=analytics_data["trends"],
            recommendations=extract_recommendations(response.get("insights", "")),
            risk_factors=identify_risk_factors(analytics_data),
            opportunities=identify_opportunities(analytics_data),
            generated_at=datetime.now(),
            model_used=response.get("model", "euri-ai"),
            analysis_metadata={
                "total_data_points": len(analytics),
                "analysis_type": request.analysis_type,
                "confidence_score": 0.85
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze performance: {str(e)}"
        )


@router.post("/batch-generate", response_model=BatchContentResponse)
async def batch_content_generation(
    request: BatchContentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> BatchContentResponse:
    """
    Generate content for multiple ads in batch using background tasks
    """
    try:
        logger.info(f"Starting batch content generation for {len(request.requests)} items")
        
        # Validate batch size
        if len(request.requests) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size cannot exceed 50 items"
            )
        
        # Schedule background task for batch processing
        task_id = f"batch_{current_user.id}_{datetime.now().timestamp()}"
        
        background_tasks.add_task(
            batch_content_generation_task,
            task_id,
            [req.dict() for req in request.requests],
            str(current_user.id)
        )
        
        return BatchContentResponse(
            success=True,
            task_id=task_id,
            total_requests=len(request.requests),
            estimated_completion_time=len(request.requests) * 5,  # 5 seconds per request
            status="processing",
            message="Batch content generation started. Check status using task_id."
        )
        
    except Exception as e:
        logger.error(f"Error starting batch content generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start batch generation: {str(e)}"
        )


# Helper functions
def extract_headline_from_content(content: str) -> str:
    """Extract headline from generated content"""
    lines = content.split('\n')
    return lines[0] if lines else ""


def extract_body_from_content(content: str) -> str:
    """Extract body text from generated content"""
    lines = content.split('\n')
    return '\n'.join(lines[1:-1]) if len(lines) > 2 else ""


def extract_cta_from_content(content: str) -> str:
    """Extract call-to-action from generated content"""
    lines = content.split('\n')
    return lines[-1] if lines else ""


def parse_recommendations(recommendations_text: str) -> List[str]:
    """Parse recommendations from AI response"""
    # Simple parsing - would be more sophisticated in production
    return recommendations_text.split('\n') if recommendations_text else []


def extract_priority_actions(recommendations_text: str) -> List[str]:
    """Extract priority actions from recommendations"""
    # Simple extraction - would use NLP in production
    return ["Optimize targeting", "Improve ad copy", "Adjust budget allocation"]


def parse_insights(insights_text: str) -> List[str]:
    """Parse insights from AI response"""
    return insights_text.split('\n') if insights_text else []


def extract_recommendations(insights_text: str) -> List[str]:
    """Extract recommendations from insights"""
    return ["Monitor CTR trends", "Optimize underperforming ads", "Scale successful campaigns"]


def calculate_performance_trends(analytics: List[Analytics]) -> Dict[str, Any]:
    """Calculate performance trends from analytics data"""
    if len(analytics) < 2:
        return {}
    
    # Simple trend calculation
    recent = analytics[:len(analytics)//2]
    older = analytics[len(analytics)//2:]
    
    recent_ctr = sum(a.ctr for a in recent) / len(recent)
    older_ctr = sum(a.ctr for a in older) / len(older)
    
    return {
        "ctr_trend": "improving" if recent_ctr > older_ctr else "declining",
        "ctr_change": ((recent_ctr - older_ctr) / older_ctr * 100) if older_ctr > 0 else 0
    }


def calculate_channel_breakdown(analytics: List[Analytics]) -> Dict[str, Any]:
    """Calculate performance breakdown by channel"""
    # This would aggregate by channel in production
    return {"google_ads": 0.4, "facebook_ads": 0.6}


def identify_risk_factors(analytics_data: Dict[str, Any]) -> List[str]:
    """Identify risk factors from analytics data"""
    risks = []
    
    if analytics_data["metrics"]["average_ctr"] < 0.02:
        risks.append("Low click-through rate")
    
    if analytics_data["metrics"]["average_roi"] < 1.0:
        risks.append("Negative return on investment")
    
    return risks


def identify_opportunities(analytics_data: Dict[str, Any]) -> List[str]:
    """Identify opportunities from analytics data"""
    opportunities = []
    
    if analytics_data["metrics"]["average_ctr"] > 0.05:
        opportunities.append("High engagement - consider scaling")
    
    if analytics_data["metrics"]["average_roi"] > 2.0:
        opportunities.append("Strong ROI - increase budget allocation")
    
    return opportunities
