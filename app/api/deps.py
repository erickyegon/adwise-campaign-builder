"""
API Dependencies for AdWise AI Digital Marketing Campaign Builder

Common dependencies used across API endpoints including authentication,
database connections, and service dependencies.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Mock authentication for testing
security = HTTPBearer()


class CurrentUser(BaseModel):
    """Mock user model for testing"""
    id: str = "test_user_123"
    email: str = "test@example.com"
    username: str = "testuser"
    is_active: bool = True
    roles: list = ["user"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Mock dependency to get current authenticated user
    
    In production, this would validate JWT tokens and return actual user data.
    For testing, returns a mock user.
    """
    # Mock authentication - in production this would validate the JWT token
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For testing, return mock user
    return CurrentUser()


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> CurrentUser:
    """
    Dependency to ensure user has admin privileges
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# Database dependencies (mock for testing)
async def get_database():
    """
    Mock database dependency
    
    In production, this would return actual database connection.
    """
    return {"status": "mock_database"}


async def get_redis():
    """
    Mock Redis dependency
    
    In production, this would return actual Redis connection.
    """
    return {"status": "mock_redis"}


# Service dependencies
async def get_ai_service():
    """
    Mock AI service dependency
    
    In production, this would return configured AI service instance.
    """
    return {"status": "mock_ai_service"}


async def get_langchain_service():
    """
    Mock LangChain service dependency
    
    In production, this would return configured LangChain service instance.
    """
    return {"status": "mock_langchain_service"}


# Validation dependencies
def validate_campaign_access(campaign_id: str):
    """
    Dependency to validate user access to campaign
    """
    async def _validate(current_user: CurrentUser = Depends(get_current_active_user)):
        # Mock validation - in production would check database
        return {"campaign_id": campaign_id, "access": "granted"}
    return _validate


def validate_team_access(team_id: str):
    """
    Dependency to validate user access to team
    """
    async def _validate(current_user: CurrentUser = Depends(get_current_active_user)):
        # Mock validation - in production would check database
        return {"team_id": team_id, "access": "granted"}
    return _validate


# Pagination dependencies
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


async def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """
    Dependency for pagination parameters
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    if size < 1 or size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size must be between 1 and 100"
        )
    return PaginationParams(page=page, size=size)


# Rate limiting dependencies (mock)
async def rate_limit_check():
    """
    Mock rate limiting dependency
    
    In production, this would implement actual rate limiting.
    """
    return {"rate_limit": "ok"}


# Feature flag dependencies
async def check_feature_flag(feature: str):
    """
    Mock feature flag dependency
    
    In production, this would check actual feature flags.
    """
    # Mock - all features enabled for testing
    return {"feature": feature, "enabled": True}


# Request validation dependencies
def validate_json_content():
    """
    Dependency to validate JSON content type
    """
    async def _validate():
        # Mock validation
        return {"content_type": "application/json"}
    return _validate


# Logging dependencies
async def get_request_logger():
    """
    Mock request logger dependency
    
    In production, this would return configured logger.
    """
    import logging
    return logging.getLogger("adwise.api")


# Cache dependencies
async def get_cache_service():
    """
    Mock cache service dependency
    
    In production, this would return configured cache service.
    """
    return {"status": "mock_cache"}


# Export dependencies
async def get_export_service():
    """
    Mock export service dependency
    
    In production, this would return configured export service.
    """
    return {"status": "mock_export"}


# Analytics dependencies
async def get_analytics_service():
    """
    Mock analytics service dependency
    
    In production, this would return configured analytics service.
    """
    return {"status": "mock_analytics"}


# WebSocket dependencies
async def get_websocket_manager():
    """
    Mock WebSocket manager dependency
    
    In production, this would return configured WebSocket manager.
    """
    return {"status": "mock_websocket_manager"}
