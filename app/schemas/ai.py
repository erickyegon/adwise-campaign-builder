"""
AI Service Schemas for AdWise AI Digital Marketing Campaign Builder

Pydantic schemas for AI-powered content generation and optimization services.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ContentGenerationRequest(BaseModel):
    """Request schema for AI content generation"""
    
    prompt: str = Field(..., description="Content generation prompt")
    content_type: str = Field(..., description="Type of content to generate")
    target_audience: Optional[Dict[str, Any]] = Field(
        default=None, description="Target audience specifications"
    )
    brand_guidelines: Optional[Dict[str, Any]] = Field(
        default=None, description="Brand guidelines and constraints"
    )
    channel: Optional[str] = Field(
        default=None, description="Marketing channel (social, email, etc.)"
    )
    max_length: Optional[int] = Field(
        default=None, description="Maximum content length"
    )
    tone: Optional[str] = Field(
        default="professional", description="Content tone"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a compelling ad copy for luxury watches",
                "content_type": "ad_copy",
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["luxury", "fashion", "watches"]
                },
                "channel": "social_media",
                "tone": "elegant"
            }
        }


class ContentGenerationResponse(BaseModel):
    """Response schema for AI content generation"""
    
    content: str = Field(..., description="Generated content")
    content_type: str = Field(..., description="Type of generated content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Generation metadata"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Optimization suggestions"
    )
    confidence_score: Optional[float] = Field(
        default=None, description="Generation confidence score"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Discover timeless elegance with our luxury watch collection...",
                "content_type": "ad_copy",
                "metadata": {
                    "word_count": 45,
                    "reading_level": "professional"
                },
                "suggestions": ["Consider adding a call-to-action"],
                "confidence_score": 0.92
            }
        }


class CampaignOptimizationRequest(BaseModel):
    """Request schema for campaign optimization"""
    
    campaign_id: str = Field(..., description="Campaign identifier")
    performance_data: Dict[str, Any] = Field(
        ..., description="Current campaign performance metrics"
    )
    optimization_goals: List[str] = Field(
        ..., description="Optimization objectives"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default=None, description="Optimization constraints"
    )
    budget_limit: Optional[float] = Field(
        default=None, description="Budget constraints"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "performance_data": {
                    "ctr": 0.025,
                    "conversion_rate": 0.03,
                    "cost_per_click": 1.50
                },
                "optimization_goals": ["increase_ctr", "reduce_cost"],
                "budget_limit": 5000.0
            }
        }


class CampaignOptimizationResponse(BaseModel):
    """Response schema for campaign optimization"""
    
    campaign_id: str = Field(..., description="Campaign identifier")
    optimizations: List[Dict[str, Any]] = Field(
        ..., description="Recommended optimizations"
    )
    expected_improvements: Dict[str, float] = Field(
        ..., description="Expected performance improvements"
    )
    priority_score: float = Field(
        ..., description="Optimization priority score"
    )
    implementation_steps: List[str] = Field(
        ..., description="Step-by-step implementation guide"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "optimizations": [
                    {
                        "type": "ad_copy_update",
                        "description": "Update headline for better engagement"
                    }
                ],
                "expected_improvements": {
                    "ctr_increase": 0.15,
                    "cost_reduction": 0.10
                },
                "priority_score": 0.85,
                "implementation_steps": [
                    "Update ad headlines",
                    "Adjust targeting parameters"
                ]
            }
        }


# Additional AI service schemas
class VisualGenerationRequest(BaseModel):
    """Request schema for AI visual content generation"""
    
    description: str = Field(..., description="Visual content description")
    style: Optional[str] = Field(default="modern", description="Visual style")
    dimensions: Optional[Dict[str, int]] = Field(
        default=None, description="Image dimensions"
    )
    brand_colors: Optional[List[str]] = Field(
        default=None, description="Brand color palette"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Luxury watch product showcase",
                "style": "elegant",
                "dimensions": {"width": 1200, "height": 800},
                "brand_colors": ["#000000", "#FFD700"]
            }
        }


class VisualGenerationResponse(BaseModel):
    """Response schema for AI visual content generation"""
    
    image_url: str = Field(..., description="Generated image URL")
    description: str = Field(..., description="Image description")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Generation metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/generated-image.jpg",
                "description": "Luxury watch product showcase",
                "metadata": {
                    "style": "elegant",
                    "generation_time": 3.2
                }
            }
        }


class PerformanceAnalysisRequest(BaseModel):
    """Request schema for AI performance analysis"""
    
    campaign_ids: List[str] = Field(..., description="Campaign identifiers")
    date_range: Dict[str, str] = Field(..., description="Analysis date range")
    metrics: List[str] = Field(..., description="Metrics to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_ids": ["camp_123", "camp_456"],
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                },
                "metrics": ["ctr", "conversion_rate", "roas"]
            }
        }


class PerformanceAnalysisResponse(BaseModel):
    """Response schema for AI performance analysis"""
    
    analysis_results: Dict[str, Any] = Field(..., description="Analysis results")
    insights: List[str] = Field(..., description="Key insights")
    recommendations: List[str] = Field(..., description="Recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_results": {
                    "overall_performance": "above_average",
                    "top_performing_campaign": "camp_123"
                },
                "insights": ["Campaign 123 shows strong engagement"],
                "recommendations": ["Increase budget for top performers"]
            }
        }


class BatchContentRequest(BaseModel):
    """Request schema for batch content generation"""
    
    requests: List[ContentGenerationRequest] = Field(
        ..., description="Batch of content generation requests"
    )
    batch_settings: Optional[Dict[str, Any]] = Field(
        default=None, description="Batch processing settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "prompt": "Create ad copy for watches",
                        "content_type": "ad_copy"
                    }
                ],
                "batch_settings": {
                    "parallel_processing": True
                }
            }
        }


class BatchContentResponse(BaseModel):
    """Response schema for batch content generation"""
    
    results: List[ContentGenerationResponse] = Field(
        ..., description="Batch generation results"
    )
    batch_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Batch processing metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "content": "Generated ad copy...",
                        "content_type": "ad_copy",
                        "metadata": {},
                        "suggestions": []
                    }
                ],
                "batch_metadata": {
                    "total_requests": 1,
                    "processing_time": 5.2
                }
            }
        }
