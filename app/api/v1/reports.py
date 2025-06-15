"""
Reports & Export API Endpoints for AdWise AI Digital Marketing Campaign Builder

This module provides comprehensive reporting and export functionality as per HLD/LDL/PRM requirements:
- Custom report generation
- Scheduled reports
- Multiple export formats (PDF, Excel, CSV)
- Report templates
- Automated report delivery

Design Principles:
- Flexible report configuration
- Multiple export formats
- Scheduled and on-demand reports
- Template-based report generation
- Email delivery capabilities
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import io
import json

router = APIRouter()


# Enums
class ReportType(str, Enum):
    """Report type options"""
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    AD_PERFORMANCE = "ad_performance"
    AUDIENCE_INSIGHTS = "audience_insights"
    ROI_ANALYSIS = "roi_analysis"
    CUSTOM = "custom"


class ExportFormat(str, Enum):
    """Export format options"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ScheduleFrequency(str, Enum):
    """Schedule frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# Pydantic Models
class ReportConfig(BaseModel):
    """Report configuration"""
    report_type: ReportType = Field(..., description="Type of report")
    name: str = Field(..., min_length=1, max_length=200, description="Report name")
    description: Optional[str] = Field(None, max_length=500, description="Report description")
    date_range: Dict[str, str] = Field(..., description="Date range for the report")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Report filters")
    metrics: List[str] = Field(..., description="Metrics to include")
    export_format: ExportFormat = Field(default=ExportFormat.PDF, description="Export format")


class ReportSchedule(BaseModel):
    """Report schedule configuration"""
    frequency: ScheduleFrequency = Field(..., description="Schedule frequency")
    time: str = Field(..., description="Time to send (HH:MM)")
    recipients: List[str] = Field(..., description="Email recipients")
    is_active: bool = Field(default=True, description="Schedule active status")


class ReportResponse(BaseModel):
    """Report response model"""
    id: str = Field(..., description="Report ID")
    name: str = Field(..., description="Report name")
    report_type: ReportType = Field(..., description="Report type")
    status: ReportStatus = Field(..., description="Generation status")
    export_format: ExportFormat = Field(..., description="Export format")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    download_url: Optional[str] = Field(None, description="Download URL")
    created_at: str = Field(..., description="Creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    
    class Config:
        from_attributes = True


class ScheduledReportResponse(ReportResponse):
    """Scheduled report response"""
    schedule: ReportSchedule = Field(..., description="Schedule configuration")
    next_run: str = Field(..., description="Next scheduled run")


class ReportTemplate(BaseModel):
    """Report template model"""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: ReportType = Field(..., description="Report type")
    default_config: ReportConfig = Field(..., description="Default configuration")
    is_public: bool = Field(default=False, description="Public template")


# API Endpoints
@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0, description="Number of reports to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of reports to return"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in report name")
):
    """
    Get all reports with optional filtering and pagination
    
    - **skip**: Number of reports to skip (for pagination)
    - **limit**: Maximum number of reports to return
    - **report_type**: Filter by report type
    - **status**: Filter by status
    - **search**: Search in report name
    """
    # Mock reports data
    mock_reports = [
        {
            "id": "report_001",
            "name": "Monthly Campaign Performance",
            "report_type": "campaign_performance",
            "status": "completed",
            "export_format": "pdf",
            "file_size": 2048576,
            "download_url": "/api/v1/reports/report_001/download",
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z"
        },
        {
            "id": "report_002",
            "name": "Ad Performance Analysis",
            "report_type": "ad_performance",
            "status": "completed",
            "export_format": "excel",
            "file_size": 1536000,
            "download_url": "/api/v1/reports/report_002/download",
            "created_at": "2024-01-02T00:00:00Z",
            "completed_at": "2024-01-02T00:03:00Z"
        },
        {
            "id": "report_003",
            "name": "ROI Analysis Q1",
            "report_type": "roi_analysis",
            "status": "generating",
            "export_format": "pdf",
            "file_size": None,
            "download_url": None,
            "created_at": "2024-01-03T00:00:00Z",
            "completed_at": None
        }
    ]
    
    # Apply filters
    filtered_reports = mock_reports
    if report_type:
        filtered_reports = [r for r in filtered_reports if r["report_type"] == report_type]
    if status:
        filtered_reports = [r for r in filtered_reports if r["status"] == status]
    if search:
        search_lower = search.lower()
        filtered_reports = [
            r for r in filtered_reports 
            if search_lower in r["name"].lower()
        ]
    
    # Apply pagination
    return filtered_reports[skip:skip + limit]


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(config: ReportConfig):
    """
    Create a new report
    
    - **report_type**: Type of report to generate
    - **name**: Report name
    - **description**: Optional description
    - **date_range**: Date range for the report
    - **filters**: Report filters
    - **metrics**: Metrics to include
    - **export_format**: Export format (PDF, Excel, CSV, JSON)
    """
    # Mock report creation
    new_report = {
        "id": f"report_{len(await get_reports()) + 1:03d}",
        "name": config.name,
        "report_type": config.report_type,
        "status": "pending",
        "export_format": config.export_format,
        "file_size": None,
        "download_url": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    return new_report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """
    Get a specific report by ID
    
    - **report_id**: The ID of the report to retrieve
    """
    # Mock report retrieval
    if report_id == "report_001":
        return {
            "id": "report_001",
            "name": "Monthly Campaign Performance",
            "report_type": "campaign_performance",
            "status": "completed",
            "export_format": "pdf",
            "file_size": 2048576,
            "download_url": "/api/v1/reports/report_001/download",
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z"
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Report not found"
    )


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """
    Download a completed report
    
    - **report_id**: The ID of the report to download
    """
    # Mock report download
    if report_id != "report_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Generate mock report content
    report_content = {
        "report_id": report_id,
        "name": "Monthly Campaign Performance",
        "generated_at": datetime.now().isoformat(),
        "data": {
            "campaigns": [
                {
                    "name": "Summer Sale Campaign",
                    "impressions": 45000,
                    "clicks": 1350,
                    "conversions": 67,
                    "spend": 900.0,
                    "roas": 4.8
                }
            ],
            "summary": {
                "total_impressions": 125000,
                "total_clicks": 3750,
                "total_conversions": 187,
                "total_spend": 2500.0,
                "average_roas": 4.2
            }
        }
    }
    
    # Convert to JSON string
    json_content = json.dumps(report_content, indent=2)
    
    # Create streaming response
    def generate():
        yield json_content.encode()
    
    return StreamingResponse(
        io.BytesIO(json_content.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.json"}
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: str):
    """
    Delete a report
    
    - **report_id**: The ID of the report to delete
    """
    if report_id != "report_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Mock report deletion
    return None


@router.get("/templates/", response_model=List[ReportTemplate])
async def get_report_templates():
    """
    Get available report templates
    """
    # Mock templates
    return [
        {
            "id": "template_001",
            "name": "Campaign Performance Template",
            "description": "Standard campaign performance report with key metrics",
            "report_type": "campaign_performance",
            "default_config": {
                "report_type": "campaign_performance",
                "name": "Campaign Performance Report",
                "description": "Automated campaign performance report",
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                "filters": {},
                "metrics": ["impressions", "clicks", "conversions", "spend", "roas"],
                "export_format": "pdf"
            },
            "is_public": True
        },
        {
            "id": "template_002",
            "name": "ROI Analysis Template",
            "description": "Comprehensive ROI analysis with detailed breakdowns",
            "report_type": "roi_analysis",
            "default_config": {
                "report_type": "roi_analysis",
                "name": "ROI Analysis Report",
                "description": "Detailed ROI analysis report",
                "date_range": {"start": "2024-01-01", "end": "2024-03-31"},
                "filters": {},
                "metrics": ["spend", "revenue", "roas", "cpa", "ltv"],
                "export_format": "excel"
            },
            "is_public": True
        }
    ]


@router.post("/templates/{template_id}/generate", response_model=ReportResponse)
async def generate_from_template(
    template_id: str,
    overrides: Optional[Dict[str, Any]] = None
):
    """
    Generate a report from a template
    
    - **template_id**: Template ID to use
    - **overrides**: Optional configuration overrides
    """
    if template_id not in ["template_001", "template_002"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Mock report generation from template
    new_report = {
        "id": f"report_tmpl_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "name": f"Report from {template_id}",
        "report_type": "campaign_performance",
        "status": "pending",
        "export_format": "pdf",
        "file_size": None,
        "download_url": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    return new_report


@router.get("/scheduled/", response_model=List[ScheduledReportResponse])
async def get_scheduled_reports():
    """
    Get all scheduled reports
    """
    # Mock scheduled reports
    return [
        {
            "id": "scheduled_001",
            "name": "Weekly Performance Report",
            "report_type": "campaign_performance",
            "status": "completed",
            "export_format": "pdf",
            "file_size": 1024000,
            "download_url": "/api/v1/reports/scheduled_001/download",
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z",
            "schedule": {
                "frequency": "weekly",
                "time": "09:00",
                "recipients": ["manager@adwise.ai", "admin@adwise.ai"],
                "is_active": True
            },
            "next_run": "2024-01-08T09:00:00Z"
        }
    ]


@router.post("/scheduled/", response_model=ScheduledReportResponse)
async def create_scheduled_report(
    config: ReportConfig,
    schedule: ReportSchedule
):
    """
    Create a scheduled report
    
    - **config**: Report configuration
    - **schedule**: Schedule configuration
    """
    # Mock scheduled report creation
    new_scheduled_report = {
        "id": f"scheduled_{len(await get_scheduled_reports()) + 1:03d}",
        "name": config.name,
        "report_type": config.report_type,
        "status": "pending",
        "export_format": config.export_format,
        "file_size": None,
        "download_url": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "schedule": schedule.dict(),
        "next_run": "2024-01-08T09:00:00Z"
    }
    
    return new_scheduled_report
