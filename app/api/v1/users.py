"""
User Management API Endpoints for AdWise AI Digital Marketing Campaign Builder

This module provides comprehensive user management functionality as per HLD/LDL/PRM requirements:
- User registration and profile management
- User authentication and authorization
- Role-based access control
- User preferences and settings
- Team membership management

Design Principles:
- RESTful API design with proper HTTP methods
- Comprehensive input validation
- Secure password handling
- Role-based permissions
- Detailed error responses
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from app.core.config import get_settings

router = APIRouter()
security = HTTPBearer()
settings = get_settings()


# Pydantic Models
class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    role: str = Field(default="user", description="User role")
    is_active: bool = Field(default=True, description="User active status")


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """User update model"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response model"""
    id: str = Field(..., description="User ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    """User preferences model"""
    theme: str = Field(default="light", description="UI theme preference")
    language: str = Field(default="en", description="Language preference")
    timezone: str = Field(default="UTC", description="Timezone preference")
    notifications_email: bool = Field(default=True, description="Email notifications")
    notifications_push: bool = Field(default=True, description="Push notifications")


# API Endpoints
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in username, email, or name")
):
    """
    Get all users with optional filtering and pagination
    
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    - **role**: Filter users by role
    - **is_active**: Filter by active status
    - **search**: Search in username, email, first_name, or last_name
    """
    # Mock data for demonstration
    mock_users = [
        {
            "id": "user_001",
            "email": "admin@adwise.ai",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "user_002",
            "email": "manager@adwise.ai",
            "username": "manager",
            "first_name": "Campaign",
            "last_name": "Manager",
            "role": "manager",
            "is_active": True,
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        },
        {
            "id": "user_003",
            "email": "creator@adwise.ai",
            "username": "creator",
            "first_name": "Content",
            "last_name": "Creator",
            "role": "user",
            "is_active": True,
            "created_at": "2024-01-03T00:00:00Z",
            "updated_at": "2024-01-03T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_users = mock_users
    if role:
        filtered_users = [u for u in filtered_users if u["role"] == role]
    if is_active is not None:
        filtered_users = [u for u in filtered_users if u["is_active"] == is_active]
    if search:
        search_lower = search.lower()
        filtered_users = [
            u for u in filtered_users 
            if search_lower in u["username"].lower() 
            or search_lower in u["email"].lower()
            or search_lower in u["first_name"].lower()
            or search_lower in u["last_name"].lower()
        ]
    
    # Apply pagination
    return filtered_users[skip:skip + limit]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user
    
    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique, 3-50 characters)
    - **password**: Password (minimum 8 characters)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **role**: User role (admin, manager, user)
    """
    # Mock user creation
    new_user = {
        "id": f"user_{len(await get_users()) + 1:03d}",
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    return new_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get a specific user by ID
    
    - **user_id**: The ID of the user to retrieve
    """
    # Mock user retrieval
    if user_id == "user_001":
        return {
            "id": "user_001",
            "email": "admin@adwise.ai",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Update a user's information
    
    - **user_id**: The ID of the user to update
    - **user_update**: Fields to update (only provided fields will be updated)
    """
    # Mock user update
    if user_id != "user_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = {
        "id": "user_001",
        "email": "admin@adwise.ai",
        "username": "admin",
        "first_name": user_update.first_name or "Admin",
        "last_name": user_update.last_name or "User",
        "role": user_update.role or "admin",
        "is_active": user_update.is_active if user_update.is_active is not None else True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """
    Delete a user (soft delete - sets is_active to False)
    
    - **user_id**: The ID of the user to delete
    """
    if user_id != "user_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Mock user deletion (soft delete)
    return None


@router.get("/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """
    Get user preferences
    
    - **user_id**: The ID of the user
    """
    if user_id != "user_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "theme": "dark",
        "language": "en",
        "timezone": "UTC",
        "notifications_email": True,
        "notifications_push": False
    }


@router.put("/{user_id}/preferences", response_model=UserPreferences)
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """
    Update user preferences
    
    - **user_id**: The ID of the user
    - **preferences**: New preference settings
    """
    if user_id != "user_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return preferences
