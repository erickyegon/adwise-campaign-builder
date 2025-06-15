"""
Analytics API Endpoints for AdWise AI Digital Marketing Campaign Builder

This module provides comprehensive analytics functionality as per HLD/LDL/PRM requirements:
- Campaign performance analytics
- Ad performance metrics
- ROI and conversion tracking
- Real-time dashboard data
- Custom analytics reports

Design Principles:
- Real-time data processing
- Comprehensive metrics collection
- Customizable date ranges
- Multi-dimensional analysis
- Export capabilities
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter()


# Enums
class MetricType(str, Enum):
    """Available metric types"""
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    SPEND = "spend"
    CTR = "ctr"
    CPC = "cpc"
    CPA = "cpa"
    ROAS = "roas"


class TimeRange(str, Enum):
    """Time range options"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    CUSTOM = "custom"


# Pydantic Models
class MetricValue(BaseModel):
    """Single metric value"""
    metric: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    change: float = Field(default=0.0, description="Change from previous period")
    change_percentage: float = Field(default=0.0, description="Percentage change")


class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    timestamp: str = Field(..., description="Timestamp")
    value: float = Field(..., description="Value at this timestamp")


class TimeSeriesData(BaseModel):
    """Time series data"""
    metric: str = Field(..., description="Metric name")
    data_points: List[TimeSeriesPoint] = Field(..., description="Time series data points")


class CampaignAnalytics(BaseModel):
    """Campaign analytics summary"""
    campaign_id: str = Field(..., description="Campaign ID")
    campaign_name: str = Field(..., description="Campaign name")
    metrics: List[MetricValue] = Field(..., description="Campaign metrics")
    time_series: List[TimeSeriesData] = Field(default_factory=list, description="Time series data")


class OverallAnalytics(BaseModel):
    """Overall analytics summary"""
    total_campaigns: int = Field(..., description="Total number of campaigns")
    total_ads: int = Field(..., description="Total number of ads")
    overall_metrics: List[MetricValue] = Field(..., description="Overall metrics")
    top_campaigns: List[CampaignAnalytics] = Field(..., description="Top performing campaigns")


class ComparisonAnalytics(BaseModel):
    """Comparison analytics between periods"""
    current_period: Dict[str, float] = Field(..., description="Current period metrics")
    previous_period: Dict[str, float] = Field(..., description="Previous period metrics")
    changes: Dict[str, float] = Field(..., description="Changes between periods")
    percentage_changes: Dict[str, float] = Field(..., description="Percentage changes")


# API Endpoints
@router.get("/overview", response_model=OverallAnalytics)
async def get_analytics_overview(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Time range for analytics"),
    start_date: Optional[str] = Query(None, description="Start date for custom range (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for custom range (YYYY-MM-DD)")
):
    """
    Get overall analytics overview
    
    - **time_range**: Predefined time range or custom
    - **start_date**: Start date for custom range
    - **end_date**: End date for custom range
    """
    # Mock analytics data
    return {
        "total_campaigns": 15,
        "total_ads": 45,
        "overall_metrics": [
            {"metric": "impressions", "value": 125000, "change": 15000, "change_percentage": 13.6},
            {"metric": "clicks", "value": 3750, "change": 450, "change_percentage": 13.6},
            {"metric": "conversions", "value": 187, "change": 23, "change_percentage": 14.0},
            {"metric": "spend", "value": 2500.0, "change": 300.0, "change_percentage": 13.6},
            {"metric": "ctr", "value": 3.0, "change": 0.2, "change_percentage": 7.1},
            {"metric": "cpc", "value": 0.67, "change": -0.05, "change_percentage": -6.9},
            {"metric": "cpa", "value": 13.37, "change": -1.2, "change_percentage": -8.2},
            {"metric": "roas", "value": 4.2, "change": 0.3, "change_percentage": 7.7}
        ],
        "top_campaigns": [
            {
                "campaign_id": "campaign_001",
                "campaign_name": "Summer Sale Campaign",
                "metrics": [
                    {"metric": "impressions", "value": 45000, "change": 5000, "change_percentage": 12.5},
                    {"metric": "clicks", "value": 1350, "change": 150, "change_percentage": 12.5},
                    {"metric": "conversions", "value": 67, "change": 8, "change_percentage": 13.6},
                    {"metric": "roas", "value": 4.8, "change": 0.4, "change_percentage": 9.1}
                ]
            },
            {
                "campaign_id": "campaign_002",
                "campaign_name": "Brand Awareness Campaign",
                "metrics": [
                    {"metric": "impressions", "value": 35000, "change": 3000, "change_percentage": 9.4},
                    {"metric": "clicks", "value": 1050, "change": 100, "change_percentage": 10.5},
                    {"metric": "conversions", "value": 52, "change": 6, "change_percentage": 13.0},
                    {"metric": "roas", "value": 3.9, "change": 0.2, "change_percentage": 5.4}
                ]
            }
        ]
    }


@router.get("/campaigns/{campaign_id}", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: str,
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Time range for analytics"),
    start_date: Optional[str] = Query(None, description="Start date for custom range"),
    end_date: Optional[str] = Query(None, description="End date for custom range"),
    include_time_series: bool = Query(True, description="Include time series data")
):
    """
    Get analytics for a specific campaign
    
    - **campaign_id**: Campaign ID to analyze
    - **time_range**: Predefined time range or custom
    - **start_date**: Start date for custom range
    - **end_date**: End date for custom range
    - **include_time_series**: Whether to include time series data
    """
    # Mock campaign analytics
    analytics = {
        "campaign_id": campaign_id,
        "campaign_name": "Summer Sale Campaign",
        "metrics": [
            {"metric": "impressions", "value": 45000, "change": 5000, "change_percentage": 12.5},
            {"metric": "clicks", "value": 1350, "change": 150, "change_percentage": 12.5},
            {"metric": "conversions", "value": 67, "change": 8, "change_percentage": 13.6},
            {"metric": "spend", "value": 900.0, "change": 100.0, "change_percentage": 12.5},
            {"metric": "ctr", "value": 3.0, "change": 0.0, "change_percentage": 0.0},
            {"metric": "cpc", "value": 0.67, "change": -0.02, "change_percentage": -2.9},
            {"metric": "cpa", "value": 13.43, "change": -0.5, "change_percentage": -3.6},
            {"metric": "roas", "value": 4.8, "change": 0.4, "change_percentage": 9.1}
        ]
    }
    
    if include_time_series:
        # Generate mock time series data
        base_date = datetime.now() - timedelta(days=30)
        analytics["time_series"] = [
            {
                "metric": "impressions",
                "data_points": [
                    {
                        "timestamp": (base_date + timedelta(days=i)).isoformat(),
                        "value": 1500 + (i * 50) + (i % 7 * 200)
                    }
                    for i in range(30)
                ]
            },
            {
                "metric": "clicks",
                "data_points": [
                    {
                        "timestamp": (base_date + timedelta(days=i)).isoformat(),
                        "value": 45 + (i * 1.5) + (i % 7 * 6)
                    }
                    for i in range(30)
                ]
            }
        ]
    
    return analytics


@router.get("/comparison", response_model=ComparisonAnalytics)
async def get_comparison_analytics(
    current_start: str = Query(..., description="Current period start date (YYYY-MM-DD)"),
    current_end: str = Query(..., description="Current period end date (YYYY-MM-DD)"),
    previous_start: str = Query(..., description="Previous period start date (YYYY-MM-DD)"),
    previous_end: str = Query(..., description="Previous period end date (YYYY-MM-DD)"),
    campaign_id: Optional[str] = Query(None, description="Specific campaign to compare")
):
    """
    Compare analytics between two time periods
    
    - **current_start**: Start date of current period
    - **current_end**: End date of current period
    - **previous_start**: Start date of previous period
    - **previous_end**: End date of previous period
    - **campaign_id**: Optional specific campaign to compare
    """
    # Mock comparison data
    current_metrics = {
        "impressions": 45000,
        "clicks": 1350,
        "conversions": 67,
        "spend": 900.0,
        "ctr": 3.0,
        "cpc": 0.67,
        "cpa": 13.43,
        "roas": 4.8
    }
    
    previous_metrics = {
        "impressions": 40000,
        "clicks": 1200,
        "conversions": 59,
        "spend": 800.0,
        "ctr": 3.0,
        "cpc": 0.67,
        "cpa": 13.56,
        "roas": 4.4
    }
    
    changes = {
        metric: current_metrics[metric] - previous_metrics[metric]
        for metric in current_metrics
    }
    
    percentage_changes = {
        metric: (changes[metric] / previous_metrics[metric] * 100) if previous_metrics[metric] != 0 else 0
        for metric in changes
    }
    
    return {
        "current_period": current_metrics,
        "previous_period": previous_metrics,
        "changes": changes,
        "percentage_changes": percentage_changes
    }


@router.get("/metrics", response_model=List[MetricValue])
async def get_metrics(
    metrics: List[MetricType] = Query(..., description="List of metrics to retrieve"),
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Time range for metrics"),
    campaign_id: Optional[str] = Query(None, description="Specific campaign ID"),
    ad_id: Optional[str] = Query(None, description="Specific ad ID")
):
    """
    Get specific metrics with optional filtering
    
    - **metrics**: List of metrics to retrieve
    - **time_range**: Time range for the metrics
    - **campaign_id**: Optional campaign filter
    - **ad_id**: Optional ad filter
    """
    # Mock metrics data
    mock_metrics = {
        "impressions": {"value": 45000, "change": 5000, "change_percentage": 12.5},
        "clicks": {"value": 1350, "change": 150, "change_percentage": 12.5},
        "conversions": {"value": 67, "change": 8, "change_percentage": 13.6},
        "spend": {"value": 900.0, "change": 100.0, "change_percentage": 12.5},
        "ctr": {"value": 3.0, "change": 0.0, "change_percentage": 0.0},
        "cpc": {"value": 0.67, "change": -0.02, "change_percentage": -2.9},
        "cpa": {"value": 13.43, "change": -0.5, "change_percentage": -3.6},
        "roas": {"value": 4.8, "change": 0.4, "change_percentage": 9.1}
    }
    
    return [
        {
            "metric": metric,
            "value": mock_metrics[metric]["value"],
            "change": mock_metrics[metric]["change"],
            "change_percentage": mock_metrics[metric]["change_percentage"]
        }
        for metric in metrics if metric in mock_metrics
    ]


@router.get("/time-series/{metric}", response_model=TimeSeriesData)
async def get_time_series(
    metric: MetricType,
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Time range for time series"),
    start_date: Optional[str] = Query(None, description="Start date for custom range"),
    end_date: Optional[str] = Query(None, description="End date for custom range"),
    granularity: str = Query("daily", description="Data granularity (hourly, daily, weekly)")
):
    """
    Get time series data for a specific metric
    
    - **metric**: The metric to get time series for
    - **time_range**: Time range for the data
    - **start_date**: Start date for custom range
    - **end_date**: End date for custom range
    - **granularity**: Data granularity (hourly, daily, weekly)
    """
    # Generate mock time series data
    base_date = datetime.now() - timedelta(days=30)
    
    # Different base values for different metrics
    base_values = {
        "impressions": 1500,
        "clicks": 45,
        "conversions": 2,
        "spend": 30.0,
        "ctr": 3.0,
        "cpc": 0.67,
        "cpa": 15.0,
        "roas": 4.0
    }
    
    base_value = base_values.get(metric, 100)
    
    data_points = [
        {
            "timestamp": (base_date + timedelta(days=i)).isoformat(),
            "value": base_value + (i * (base_value * 0.02)) + (i % 7 * (base_value * 0.1))
        }
        for i in range(30)
    ]
    
    return {
        "metric": metric,
        "data_points": data_points
    }
