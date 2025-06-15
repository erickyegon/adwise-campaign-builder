"""
Real-time Collaboration API Endpoints for AdWise AI Digital Marketing Campaign Builder

This module provides comprehensive real-time collaboration functionality as per HLD/LDL/PRM requirements:
- Real-time document editing
- Comment and feedback system
- Version control and history
- Live collaboration sessions
- Notification system

Design Principles:
- WebSocket-based real-time communication
- Conflict resolution for concurrent edits
- Comprehensive activity tracking
- Role-based collaboration permissions
- Real-time presence indicators
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

router = APIRouter()


# Enums
class ActivityType(str, Enum):
    """Activity type options"""
    EDIT = "edit"
    COMMENT = "comment"
    APPROVE = "approve"
    REJECT = "reject"
    SHARE = "share"
    VIEW = "view"


class CommentStatus(str, Enum):
    """Comment status options"""
    OPEN = "open"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class SessionStatus(str, Enum):
    """Collaboration session status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ENDED = "ended"


# Pydantic Models
class CollaborationActivity(BaseModel):
    """Collaboration activity model"""
    id: str = Field(..., description="Activity ID")
    user_id: str = Field(..., description="User who performed the activity")
    username: str = Field(..., description="Username")
    activity_type: ActivityType = Field(..., description="Type of activity")
    resource_type: str = Field(..., description="Type of resource (campaign, ad, etc.)")
    resource_id: str = Field(..., description="ID of the resource")
    description: str = Field(..., description="Activity description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: str = Field(..., description="Activity timestamp")


class Comment(BaseModel):
    """Comment model"""
    id: str = Field(..., description="Comment ID")
    user_id: str = Field(..., description="User who made the comment")
    username: str = Field(..., description="Username")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="ID of the resource")
    content: str = Field(..., description="Comment content")
    status: CommentStatus = Field(default=CommentStatus.OPEN, description="Comment status")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for replies")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class CommentCreate(BaseModel):
    """Comment creation model"""
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="ID of the resource")
    content: str = Field(..., min_length=1, max_length=1000, description="Comment content")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for replies")


class CommentUpdate(BaseModel):
    """Comment update model"""
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[CommentStatus] = None


class CollaborationSession(BaseModel):
    """Collaboration session model"""
    id: str = Field(..., description="Session ID")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="ID of the resource")
    participants: List[Dict[str, Any]] = Field(..., description="Session participants")
    status: SessionStatus = Field(..., description="Session status")
    started_at: str = Field(..., description="Session start time")
    ended_at: Optional[str] = Field(None, description="Session end time")


class Participant(BaseModel):
    """Session participant model"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
    joined_at: str = Field(..., description="Join timestamp")
    is_active: bool = Field(..., description="Currently active")
    cursor_position: Optional[Dict[str, Any]] = Field(None, description="Cursor position")


class VersionHistory(BaseModel):
    """Version history model"""
    id: str = Field(..., description="Version ID")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="ID of the resource")
    version_number: int = Field(..., description="Version number")
    user_id: str = Field(..., description="User who created this version")
    username: str = Field(..., description="Username")
    changes: Dict[str, Any] = Field(..., description="Changes made in this version")
    created_at: str = Field(..., description="Creation timestamp")


# API Endpoints
@router.get("/activities", response_model=List[CollaborationActivity])
async def get_activities(
    skip: int = Query(0, ge=0, description="Number of activities to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of activities to return"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    activity_type: Optional[ActivityType] = Query(None, description="Filter by activity type")
):
    """
    Get collaboration activities with optional filtering
    
    - **skip**: Number of activities to skip (for pagination)
    - **limit**: Maximum number of activities to return
    - **resource_type**: Filter by resource type
    - **resource_id**: Filter by specific resource
    - **user_id**: Filter by user
    - **activity_type**: Filter by activity type
    """
    # Mock activities data
    mock_activities = [
        {
            "id": "activity_001",
            "user_id": "user_001",
            "username": "admin",
            "activity_type": "edit",
            "resource_type": "campaign",
            "resource_id": "campaign_001",
            "description": "Updated campaign budget",
            "metadata": {"field": "budget", "old_value": 1000, "new_value": 1200},
            "timestamp": "2024-01-01T10:30:00Z"
        },
        {
            "id": "activity_002",
            "user_id": "user_002",
            "username": "manager",
            "activity_type": "comment",
            "resource_type": "ad",
            "resource_id": "ad_001",
            "description": "Added comment on ad creative",
            "metadata": {"comment_id": "comment_001"},
            "timestamp": "2024-01-01T11:15:00Z"
        },
        {
            "id": "activity_003",
            "user_id": "user_003",
            "username": "creator",
            "activity_type": "approve",
            "resource_type": "ad",
            "resource_id": "ad_001",
            "description": "Approved ad for publication",
            "metadata": {"approval_status": "approved"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_activities = mock_activities
    if resource_type:
        filtered_activities = [a for a in filtered_activities if a["resource_type"] == resource_type]
    if resource_id:
        filtered_activities = [a for a in filtered_activities if a["resource_id"] == resource_id]
    if user_id:
        filtered_activities = [a for a in filtered_activities if a["user_id"] == user_id]
    if activity_type:
        filtered_activities = [a for a in filtered_activities if a["activity_type"] == activity_type]
    
    # Apply pagination
    return filtered_activities[skip:skip + limit]


@router.get("/comments", response_model=List[Comment])
async def get_comments(
    resource_type: str = Query(..., description="Type of resource"),
    resource_id: str = Query(..., description="ID of the resource"),
    status: Optional[CommentStatus] = Query(None, description="Filter by status"),
    parent_id: Optional[str] = Query(None, description="Filter by parent comment")
):
    """
    Get comments for a specific resource
    
    - **resource_type**: Type of resource (campaign, ad, etc.)
    - **resource_id**: ID of the resource
    - **status**: Filter by comment status
    - **parent_id**: Filter by parent comment (for replies)
    """
    # Mock comments data
    mock_comments = [
        {
            "id": "comment_001",
            "user_id": "user_002",
            "username": "manager",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "content": "The headline could be more compelling. Consider adding urgency.",
            "status": "open",
            "parent_id": None,
            "created_at": "2024-01-01T11:15:00Z",
            "updated_at": "2024-01-01T11:15:00Z"
        },
        {
            "id": "comment_002",
            "user_id": "user_003",
            "username": "creator",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "content": "Good point! I'll update it to include 'Limited Time Offer'",
            "status": "open",
            "parent_id": "comment_001",
            "created_at": "2024-01-01T11:30:00Z",
            "updated_at": "2024-01-01T11:30:00Z"
        },
        {
            "id": "comment_003",
            "user_id": "user_001",
            "username": "admin",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "content": "Looks great! Ready for approval.",
            "status": "resolved",
            "parent_id": None,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:05:00Z"
        }
    ]
    
    # Apply filters
    filtered_comments = mock_comments
    if status:
        filtered_comments = [c for c in filtered_comments if c["status"] == status]
    if parent_id is not None:
        filtered_comments = [c for c in filtered_comments if c["parent_id"] == parent_id]
    
    return filtered_comments


@router.post("/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate):
    """
    Create a new comment
    
    - **resource_type**: Type of resource
    - **resource_id**: ID of the resource
    - **content**: Comment content
    - **parent_id**: Optional parent comment ID for replies
    """
    # Mock comment creation
    new_comment = {
        "id": f"comment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_id": "user_001",  # Mock current user
        "username": "admin",
        "resource_type": comment.resource_type,
        "resource_id": comment.resource_id,
        "content": comment.content,
        "status": "open",
        "parent_id": comment.parent_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    return new_comment


@router.put("/comments/{comment_id}", response_model=Comment)
async def update_comment(comment_id: str, comment_update: CommentUpdate):
    """
    Update a comment
    
    - **comment_id**: ID of the comment to update
    - **comment_update**: Fields to update
    """
    # Mock comment update
    if comment_id != "comment_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    updated_comment = {
        "id": comment_id,
        "user_id": "user_002",
        "username": "manager",
        "resource_type": "ad",
        "resource_id": "ad_001",
        "content": comment_update.content or "The headline could be more compelling. Consider adding urgency.",
        "status": comment_update.status or "open",
        "parent_id": None,
        "created_at": "2024-01-01T11:15:00Z",
        "updated_at": datetime.now().isoformat()
    }
    
    return updated_comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: str):
    """
    Delete a comment
    
    - **comment_id**: ID of the comment to delete
    """
    if comment_id != "comment_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Mock comment deletion
    return None


@router.get("/sessions", response_model=List[CollaborationSession])
async def get_collaboration_sessions(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    status: Optional[SessionStatus] = Query(None, description="Filter by session status")
):
    """
    Get active collaboration sessions
    
    - **resource_type**: Filter by resource type
    - **resource_id**: Filter by specific resource
    - **status**: Filter by session status
    """
    # Mock sessions data
    mock_sessions = [
        {
            "id": "session_001",
            "resource_type": "campaign",
            "resource_id": "campaign_001",
            "participants": [
                {
                    "user_id": "user_001",
                    "username": "admin",
                    "role": "admin",
                    "joined_at": "2024-01-01T10:00:00Z",
                    "is_active": True,
                    "cursor_position": {"line": 5, "column": 10}
                },
                {
                    "user_id": "user_002",
                    "username": "manager",
                    "role": "manager",
                    "joined_at": "2024-01-01T10:05:00Z",
                    "is_active": True,
                    "cursor_position": {"line": 12, "column": 25}
                }
            ],
            "status": "active",
            "started_at": "2024-01-01T10:00:00Z",
            "ended_at": None
        }
    ]
    
    # Apply filters
    filtered_sessions = mock_sessions
    if resource_type:
        filtered_sessions = [s for s in filtered_sessions if s["resource_type"] == resource_type]
    if resource_id:
        filtered_sessions = [s for s in filtered_sessions if s["resource_id"] == resource_id]
    if status:
        filtered_sessions = [s for s in filtered_sessions if s["status"] == status]
    
    return filtered_sessions


@router.get("/versions/{resource_type}/{resource_id}", response_model=List[VersionHistory])
async def get_version_history(
    resource_type: str,
    resource_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of versions to return")
):
    """
    Get version history for a resource
    
    - **resource_type**: Type of resource
    - **resource_id**: ID of the resource
    - **limit**: Maximum number of versions to return
    """
    # Mock version history
    mock_versions = [
        {
            "id": "version_003",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "version_number": 3,
            "user_id": "user_001",
            "username": "admin",
            "changes": {
                "budget": {"old": 1000, "new": 1200},
                "description": {"old": "Summer sale", "new": "Summer sale - limited time"}
            },
            "created_at": "2024-01-01T12:00:00Z"
        },
        {
            "id": "version_002",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "version_number": 2,
            "user_id": "user_002",
            "username": "manager",
            "changes": {
                "headline": {"old": "Summer Sale", "new": "Summer Sale - Up to 50% Off!"}
            },
            "created_at": "2024-01-01T10:30:00Z"
        },
        {
            "id": "version_001",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "version_number": 1,
            "user_id": "user_003",
            "username": "creator",
            "changes": {
                "created": True
            },
            "created_at": "2024-01-01T09:00:00Z"
        }
    ]
    
    return mock_versions[:limit]
