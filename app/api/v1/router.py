"""
Main API Router for AdWise AI Digital Marketing Campaign Builder

This module provides the main API router that includes all endpoint modules
as specified in the HLD/LDL/PRM requirements:
- Campaign management endpoints
- User authentication and management
- AI content generation endpoints
- Analytics and reporting endpoints
- Real-time collaboration endpoints
- Export functionality endpoints

Design Principles:
- RESTful API design
- Comprehensive error handling
- Authentication and authorization
- Rate limiting and security
- OpenAPI documentation
"""

from fastapi import APIRouter

# Import all routers with error handling
try:
    from .auth import router as auth_router
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

try:
    from .users import router as users_router
    USERS_AVAILABLE = True
except ImportError:
    USERS_AVAILABLE = False

try:
    from .teams import router as teams_router
    TEAMS_AVAILABLE = True
except ImportError:
    TEAMS_AVAILABLE = False

try:
    from .campaigns import router as campaigns_router
    CAMPAIGNS_AVAILABLE = True
except ImportError:
    CAMPAIGNS_AVAILABLE = False

try:
    from .ads import router as ads_router
    ADS_AVAILABLE = True
except ImportError:
    ADS_AVAILABLE = False

try:
    from .ai import router as ai_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from .analytics import router as analytics_router
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

try:
    from .reports import router as reports_router
    REPORTS_AVAILABLE = True
except ImportError:
    REPORTS_AVAILABLE = False

try:
    from .collaboration import router as collaboration_router
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False

try:
    from .health import router as health_router
    HEALTH_AVAILABLE = True
except ImportError:
    HEALTH_AVAILABLE = False

# Main API router
api_router = APIRouter()

# Include all available sub-routers
if AUTH_AVAILABLE:
    api_router.include_router(
        auth_router,
        prefix="/auth",
        tags=["Authentication"]
    )

if USERS_AVAILABLE:
    api_router.include_router(
        users_router,
        prefix="/users",
        tags=["User Management"]
    )

if TEAMS_AVAILABLE:
    api_router.include_router(
        teams_router,
        prefix="/teams",
        tags=["Team Management"]
    )

if CAMPAIGNS_AVAILABLE:
    api_router.include_router(
        campaigns_router,
        prefix="/campaigns",
        tags=["Campaign Management"]
    )

if ADS_AVAILABLE:
    api_router.include_router(
        ads_router,
        prefix="/ads",
        tags=["Ad Management"]
    )

if AI_AVAILABLE:
    api_router.include_router(
        ai_router,
        prefix="/ai",
        tags=["AI Services"]
    )

if ANALYTICS_AVAILABLE:
    api_router.include_router(
        analytics_router,
        prefix="/analytics",
        tags=["Analytics"]
    )

if REPORTS_AVAILABLE:
    api_router.include_router(
        reports_router,
        prefix="/reports",
        tags=["Reports & Export"]
    )

if COLLABORATION_AVAILABLE:
    api_router.include_router(
        collaboration_router,
        prefix="/collaboration",
        tags=["Real-time Collaboration"]
    )

if HEALTH_AVAILABLE:
    api_router.include_router(
        health_router,
        prefix="/health",
        tags=["Health & Monitoring"]
    )

# Add a root endpoint for the API
@api_router.get("/")
async def api_root():
    """
    API root endpoint
    
    Returns information about available API endpoints
    """
    available_endpoints = []
    
    if AUTH_AVAILABLE:
        available_endpoints.append({
            "prefix": "/auth",
            "description": "Authentication and authorization endpoints",
            "endpoints": [
                "POST /auth/login",
                "POST /auth/logout",
                "POST /auth/register",
                "GET /auth/me"
            ]
        })
    
    if USERS_AVAILABLE:
        available_endpoints.append({
            "prefix": "/users",
            "description": "User management endpoints",
            "endpoints": [
                "GET /users/",
                "POST /users/",
                "GET /users/{user_id}",
                "PUT /users/{user_id}",
                "DELETE /users/{user_id}"
            ]
        })
    
    if TEAMS_AVAILABLE:
        available_endpoints.append({
            "prefix": "/teams",
            "description": "Team management endpoints",
            "endpoints": [
                "GET /teams/",
                "POST /teams/",
                "GET /teams/{team_id}",
                "PUT /teams/{team_id}",
                "DELETE /teams/{team_id}"
            ]
        })
    
    if CAMPAIGNS_AVAILABLE:
        available_endpoints.append({
            "prefix": "/campaigns",
            "description": "Campaign management endpoints",
            "endpoints": [
                "GET /campaigns/",
                "POST /campaigns/",
                "GET /campaigns/{campaign_id}",
                "PUT /campaigns/{campaign_id}",
                "DELETE /campaigns/{campaign_id}"
            ]
        })
    
    if ADS_AVAILABLE:
        available_endpoints.append({
            "prefix": "/ads",
            "description": "Ad management endpoints",
            "endpoints": [
                "GET /ads/",
                "POST /ads/",
                "GET /ads/{ad_id}",
                "PUT /ads/{ad_id}",
                "DELETE /ads/{ad_id}",
                "POST /ads/generate"
            ]
        })
    
    if AI_AVAILABLE:
        available_endpoints.append({
            "prefix": "/ai",
            "description": "AI services endpoints",
            "endpoints": [
                "POST /ai/generate/content",
                "POST /ai/generate/campaign",
                "POST /ai/analyze/audience",
                "POST /ai/optimize/ad"
            ]
        })
    
    if ANALYTICS_AVAILABLE:
        available_endpoints.append({
            "prefix": "/analytics",
            "description": "Analytics and metrics endpoints",
            "endpoints": [
                "GET /analytics/overview",
                "GET /analytics/campaigns/{campaign_id}",
                "GET /analytics/comparison",
                "GET /analytics/metrics"
            ]
        })
    
    if REPORTS_AVAILABLE:
        available_endpoints.append({
            "prefix": "/reports",
            "description": "Reports and export endpoints",
            "endpoints": [
                "GET /reports/",
                "POST /reports/",
                "GET /reports/{report_id}",
                "GET /reports/{report_id}/download",
                "GET /reports/templates/"
            ]
        })
    
    if COLLABORATION_AVAILABLE:
        available_endpoints.append({
            "prefix": "/collaboration",
            "description": "Real-time collaboration endpoints",
            "endpoints": [
                "GET /collaboration/activities",
                "GET /collaboration/comments",
                "POST /collaboration/comments",
                "GET /collaboration/sessions"
            ]
        })
    
    if HEALTH_AVAILABLE:
        available_endpoints.append({
            "prefix": "/health",
            "description": "Health monitoring endpoints",
            "endpoints": [
                "GET /health/",
                "GET /health/detailed",
                "GET /health/dependencies",
                "GET /health/metrics"
            ]
        })
    
    return {
        "message": "AdWise AI Digital Marketing Campaign Builder API",
        "version": "1.0.0",
        "description": "Comprehensive API for AI-powered digital marketing campaign management",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "available_endpoints": available_endpoints,
        "total_endpoint_groups": len(available_endpoints)
    }

__all__ = ["api_router"]
