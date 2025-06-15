"""
Team Management API Endpoints for AdWise AI Digital Marketing Campaign Builder

This module provides comprehensive team management functionality as per HLD/LDL/PRM requirements:
- Team creation and management
- Team member management
- Role assignments within teams
- Team permissions and access control
- Team collaboration features

Design Principles:
- RESTful API design with proper HTTP methods
- Hierarchical team structure support
- Role-based access control within teams
- Comprehensive member management
- Team activity tracking
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic Models
class TeamBase(BaseModel):
    """Base team model"""
    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, max_length=500, description="Team description")
    is_active: bool = Field(default=True, description="Team active status")


class TeamCreate(TeamBase):
    """Team creation model"""
    pass


class TeamUpdate(BaseModel):
    """Team update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class TeamMember(BaseModel):
    """Team member model"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="Role in team")
    joined_at: str = Field(..., description="Join timestamp")


class TeamResponse(TeamBase):
    """Team response model"""
    id: str = Field(..., description="Team ID")
    owner_id: str = Field(..., description="Team owner ID")
    member_count: int = Field(..., description="Number of team members")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TeamWithMembers(TeamResponse):
    """Team response with members"""
    members: List[TeamMember] = Field(default_factory=list, description="Team members")


class AddMemberRequest(BaseModel):
    """Add member request model"""
    user_id: str = Field(..., description="User ID to add")
    role: str = Field(default="member", description="Role in team")


class UpdateMemberRequest(BaseModel):
    """Update member request model"""
    role: str = Field(..., description="New role for member")


# API Endpoints
@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    skip: int = Query(0, ge=0, description="Number of teams to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of teams to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in team name or description")
):
    """
    Get all teams with optional filtering and pagination
    
    - **skip**: Number of teams to skip (for pagination)
    - **limit**: Maximum number of teams to return
    - **is_active**: Filter by active status
    - **search**: Search in team name or description
    """
    # Mock data for demonstration
    mock_teams = [
        {
            "id": "team_001",
            "name": "Marketing Team",
            "description": "Main marketing team for digital campaigns",
            "is_active": True,
            "owner_id": "user_001",
            "member_count": 5,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "team_002",
            "name": "Creative Team",
            "description": "Content creation and design team",
            "is_active": True,
            "owner_id": "user_002",
            "member_count": 3,
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        },
        {
            "id": "team_003",
            "name": "Analytics Team",
            "description": "Data analysis and reporting team",
            "is_active": True,
            "owner_id": "user_001",
            "member_count": 2,
            "created_at": "2024-01-03T00:00:00Z",
            "updated_at": "2024-01-03T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_teams = mock_teams
    if is_active is not None:
        filtered_teams = [t for t in filtered_teams if t["is_active"] == is_active]
    if search:
        search_lower = search.lower()
        filtered_teams = [
            t for t in filtered_teams 
            if search_lower in t["name"].lower() 
            or (t["description"] and search_lower in t["description"].lower())
        ]
    
    # Apply pagination
    return filtered_teams[skip:skip + limit]


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team: TeamCreate):
    """
    Create a new team
    
    - **name**: Team name (1-100 characters)
    - **description**: Optional team description
    - **is_active**: Team active status (default: True)
    """
    # Mock team creation
    new_team = {
        "id": f"team_{len(await get_teams()) + 1:03d}",
        "name": team.name,
        "description": team.description,
        "is_active": team.is_active,
        "owner_id": "user_001",  # Mock current user
        "member_count": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    return new_team


@router.get("/{team_id}", response_model=TeamWithMembers)
async def get_team(team_id: str):
    """
    Get a specific team by ID with members
    
    - **team_id**: The ID of the team to retrieve
    """
    # Mock team retrieval
    if team_id == "team_001":
        return {
            "id": "team_001",
            "name": "Marketing Team",
            "description": "Main marketing team for digital campaigns",
            "is_active": True,
            "owner_id": "user_001",
            "member_count": 3,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "members": [
                {
                    "user_id": "user_001",
                    "username": "admin",
                    "email": "admin@adwise.ai",
                    "role": "owner",
                    "joined_at": "2024-01-01T00:00:00Z"
                },
                {
                    "user_id": "user_002",
                    "username": "manager",
                    "email": "manager@adwise.ai",
                    "role": "manager",
                    "joined_at": "2024-01-02T00:00:00Z"
                },
                {
                    "user_id": "user_003",
                    "username": "creator",
                    "email": "creator@adwise.ai",
                    "role": "member",
                    "joined_at": "2024-01-03T00:00:00Z"
                }
            ]
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Team not found"
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(team_id: str, team_update: TeamUpdate):
    """
    Update a team's information
    
    - **team_id**: The ID of the team to update
    - **team_update**: Fields to update (only provided fields will be updated)
    """
    # Mock team update
    if team_id != "team_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    updated_team = {
        "id": "team_001",
        "name": team_update.name or "Marketing Team",
        "description": team_update.description or "Main marketing team for digital campaigns",
        "is_active": team_update.is_active if team_update.is_active is not None else True,
        "owner_id": "user_001",
        "member_count": 3,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    return updated_team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: str):
    """
    Delete a team (soft delete - sets is_active to False)
    
    - **team_id**: The ID of the team to delete
    """
    if team_id != "team_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Mock team deletion (soft delete)
    return None


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
async def add_team_member(team_id: str, member_request: AddMemberRequest):
    """
    Add a member to a team
    
    - **team_id**: The ID of the team
    - **user_id**: The ID of the user to add
    - **role**: The role to assign (owner, manager, member)
    """
    if team_id != "team_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return {"message": f"User {member_request.user_id} added to team with role {member_request.role}"}


@router.put("/{team_id}/members/{user_id}")
async def update_team_member(team_id: str, user_id: str, member_update: UpdateMemberRequest):
    """
    Update a team member's role
    
    - **team_id**: The ID of the team
    - **user_id**: The ID of the user to update
    - **role**: The new role to assign
    """
    if team_id != "team_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return {"message": f"User {user_id} role updated to {member_update.role}"}


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(team_id: str, user_id: str):
    """
    Remove a member from a team
    
    - **team_id**: The ID of the team
    - **user_id**: The ID of the user to remove
    """
    if team_id != "team_001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Mock member removal
    return None
