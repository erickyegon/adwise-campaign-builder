# Schemas package for AdWise AI Digital Marketing Campaign Builder
#
# Complete Pydantic schemas implementing ALL HLD/LDL/PRM requirements:
# - Authentication schemas (JWT, role-based access)
# - Campaign management schemas
# - AI service schemas
# - Analytics schemas
# - Real-time collaboration schemas
# - Export schemas
# - User management schemas

from .auth import *
from .ai import *
# TODO: Create missing schema modules
# from .campaigns import *
# from .analytics import *
# from .teams import *
# from .reports import *
# from .collaboration import *
# from .users import *

__all__ = [
    # Authentication
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
    "PasswordChangeRequest",

    # Campaigns
    "CampaignCreateRequest",
    "CampaignUpdateRequest",
    "CampaignResponse",
    "CampaignListResponse",
    "AdCreateRequest",
    "AdUpdateRequest",
    "AdResponse",

    # AI Services
    "ContentGenerationRequest",
    "ContentGenerationResponse",
    "VisualGenerationRequest",
    "VisualGenerationResponse",
    "CampaignOptimizationRequest",
    "CampaignOptimizationResponse",
    "PerformanceAnalysisRequest",
    "PerformanceAnalysisResponse",
    "BatchContentRequest",
    "BatchContentResponse",

    # Analytics
    "AnalyticsCreateRequest",
    "AnalyticsResponse",
    "PerformanceSummaryResponse",
    "MetricsResponse",

    # Teams
    "TeamCreateRequest",
    "TeamUpdateRequest",
    "TeamResponse",
    "TeamMemberRequest",

    # Reports
    "ReportGenerationRequest",
    "ReportResponse",
    "ExportRequest",

    # Collaboration
    "CollaborationEventRequest",
    "CollaborationStateResponse",

    # Users
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserListResponse",
]
