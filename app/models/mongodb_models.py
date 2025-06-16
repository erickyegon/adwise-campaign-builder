"""
MongoDB Models for AdWise AI Digital Marketing Campaign Builder

Complete Beanie ODM models implementing HLD/LDL/PRM requirements:
- User management with role-based access
- Campaign management with collaboration
- Ad content and performance tracking
- Analytics and reporting data
- Real-time collaboration support

Design Principles:
- Follows LDL schema specifications exactly
- Optimized for MongoDB document structure
- Supports real-time collaboration
- Analytics-ready with aggregation support
- Professional error handling
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from decimal import Decimal

from beanie import Document, Indexed, Link, before_event, after_event
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class UserRole(str, Enum):
    """User roles as per PRM specifications"""
    ADMIN = "admin"      # Full system access
    MANAGER = "manager"  # Team management
    EDITOR = "editor"    # Create/edit campaigns
    VIEWER = "viewer"    # Read-only access


class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class CampaignStatus(str, Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    REVIEW = "review"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AdType(str, Enum):
    """Ad type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    TEXT = "text"
    COLLECTION = "collection"
    STORY = "story"


class AdChannel(str, Enum):
    """Advertising channel enumeration"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    GOOGLE_ADS = "google_ads"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    SNAPCHAT = "snapchat"
    YOUTUBE = "youtube"


class AdStatus(str, Enum):
    """Ad status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


# =============================================================================
# EMBEDDED DOCUMENTS AND SUBDOCUMENTS
# =============================================================================

class UserProfile(BaseModel):
    """User profile information"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    timezone: str = Field(default="UTC")
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class UserSettings(BaseModel):
    """User preferences and settings"""
    notifications: Dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "push": True,
        "sms": False
    })
    theme: str = Field(default="light")
    language: str = Field(default="en")
    dashboard_layout: Dict[str, Any] = Field(default_factory=dict)


class BudgetInfo(BaseModel):
    """Campaign budget information"""
    total: float = Field(..., ge=0)
    daily: Optional[float] = Field(None, ge=0)
    spent: float = Field(default=0.0, ge=0)
    currency: str = Field(default="USD")
    
    @validator('daily')
    def validate_daily_budget(cls, v, values):
        if v is not None and 'total' in values and v > values['total']:
            raise ValueError('Daily budget cannot exceed total budget')
        return v


class TargetingInfo(BaseModel):
    """Campaign targeting information"""
    demographics: Dict[str, Any] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    behaviors: List[str] = Field(default_factory=list)
    custom_audiences: List[str] = Field(default_factory=list)
    lookalike_audiences: List[str] = Field(default_factory=list)


class PerformanceMetrics(BaseModel):
    """Performance metrics for campaigns and ads"""
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spend: float = Field(default=0.0, ge=0)
    revenue: float = Field(default=0.0, ge=0)
    ctr: float = Field(default=0.0, ge=0)  # Click-through rate
    cpc: float = Field(default=0.0, ge=0)  # Cost per click
    cpm: float = Field(default=0.0, ge=0)  # Cost per mille
    roas: float = Field(default=0.0, ge=0)  # Return on ad spend
    conversion_rate: float = Field(default=0.0, ge=0)


class Collaborator(BaseModel):
    """Campaign collaborator information"""
    user_id: str = Field(...)
    role: str = Field(...)  # editor, viewer, approver
    permissions: List[str] = Field(default_factory=list)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    added_by: str = Field(...)


class ChangeEntry(BaseModel):
    """Change history entry"""
    user_id: str = Field(...)
    action: str = Field(...)  # created, updated, deleted, etc.
    field: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None


class AdContent(BaseModel):
    """Ad content information"""
    headline: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    call_to_action: str = Field(..., max_length=50)
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    landing_page_url: Optional[str] = None
    additional_images: List[str] = Field(default_factory=list)


# =============================================================================
# MAIN DOCUMENT MODELS
# =============================================================================

class User(Document):
    """
    User model implementing LDL specifications
    
    LDL Fields: _id, email, passwordHash, role, teamIds[]
    Enhanced with profile, settings, and collaboration features
    """
    
    # Core LDL fields
    email: Indexed(EmailStr, unique=True) = Field(...)
    password_hash: str = Field(..., alias="passwordHash")
    role: UserRole = Field(default=UserRole.EDITOR)
    team_ids: List[str] = Field(default_factory=list, alias="teamIds")
    
    # Enhanced fields for functionality
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    profile: UserProfile = Field(...)
    settings: UserSettings = Field(default_factory=UserSettings)
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("username", ASCENDING)], unique=True, sparse=True),
            IndexModel([("role", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("team_ids", ASCENDING)]),
        ]
    
    @before_event("update")
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.profile.first_name} {self.profile.last_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "status": self.status,
            "profile": self.profile.dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class Team(Document):
    """Team model for collaboration"""
    
    name: str = Field(..., min_length=1, max_length=100)
    slug: Indexed(str, unique=True) = Field(...)
    description: Optional[str] = Field(None, max_length=500)
    owner_id: str = Field(...)
    member_ids: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "teams"
        indexes = [
            IndexModel([("slug", ASCENDING)], unique=True),
            IndexModel([("owner_id", ASCENDING)]),
            IndexModel([("member_ids", ASCENDING)]),
        ]


class Campaign(Document):
    """
    Campaign model implementing LDL specifications

    LDL Fields: _id, name, ownerId, teamId, ads[], status, createdAt
    Enhanced with targeting, budget, performance, and collaboration
    """

    # Core LDL fields
    name: str = Field(..., min_length=1, max_length=200)
    owner_id: str = Field(..., alias="ownerId")
    team_id: Optional[str] = Field(None, alias="teamId")
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")

    # Enhanced fields for functionality
    description: Optional[str] = Field(None, max_length=1000)
    objective: str = Field(..., max_length=100)
    budget: BudgetInfo = Field(...)
    targeting: TargetingInfo = Field(default_factory=TargetingInfo)
    platforms: List[AdChannel] = Field(default_factory=list)
    performance: PerformanceMetrics = Field(default_factory=PerformanceMetrics)

    # Collaboration features
    collaborators: List[Collaborator] = Field(default_factory=list)
    change_history: List[ChangeEntry] = Field(default_factory=list)

    # Schedule information
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: str = Field(default="UTC")

    # Content and creative
    brand_guidelines: Dict[str, Any] = Field(default_factory=dict)
    content_themes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # AI-generated content
    ai_generated: bool = Field(default=False)
    ai_model_used: Optional[str] = None
    ai_generation_params: Dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "campaigns"
        indexes = [
            IndexModel([("owner_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("team_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("status", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("platforms", ASCENDING)]),
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("performance.roas", DESCENDING)]),
            IndexModel([("start_date", ASCENDING), ("end_date", ASCENDING)]),
            IndexModel([("name", TEXT)]),
        ]

    @before_event("update")
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)

    def add_collaborator(self, user_id: str, role: str, added_by: str, permissions: List[str] = None):
        """Add a collaborator to the campaign"""
        collaborator = Collaborator(
            user_id=user_id,
            role=role,
            permissions=permissions or [],
            added_by=added_by
        )
        self.collaborators.append(collaborator)

        # Add change history entry
        change = ChangeEntry(
            user_id=added_by,
            action="collaborator_added",
            description=f"Added {role} collaborator"
        )
        self.change_history.append(change)

    def log_change(self, user_id: str, action: str, field: str = None,
                   old_value: Any = None, new_value: Any = None, description: str = None):
        """Log a change to the campaign"""
        change = ChangeEntry(
            user_id=user_id,
            action=action,
            field=field,
            old_value=old_value,
            new_value=new_value,
            description=description
        )
        self.change_history.append(change)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "objective": self.objective,
            "budget": self.budget.dict(),
            "targeting": self.targeting.dict(),
            "platforms": self.platforms,
            "performance": self.performance.dict(),
            "collaborators_count": len(self.collaborators),
            "tags": self.tags,
            "ai_generated": self.ai_generated,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }


class Ad(Document):
    """
    Ad model for individual advertisements

    Enhanced with content, targeting, and performance tracking
    """

    # Core fields
    campaign_id: str = Field(...)
    name: str = Field(..., min_length=1, max_length=200)
    type: AdType = Field(...)
    channel: AdChannel = Field(...)
    status: AdStatus = Field(default=AdStatus.DRAFT)

    # Content
    content: AdContent = Field(...)

    # Targeting (can override campaign targeting)
    targeting: Optional[TargetingInfo] = None

    # Budget (can have ad-level budget)
    budget: Optional[BudgetInfo] = None

    # Performance
    performance: PerformanceMetrics = Field(default_factory=PerformanceMetrics)

    # AI generation
    ai_generated: bool = Field(default=False)
    ai_model_used: Optional[str] = None
    ai_generation_params: Dict[str, Any] = Field(default_factory=dict)
    ai_optimization_history: List[Dict[str, Any]] = Field(default_factory=list)

    # A/B Testing
    ab_test_group: Optional[str] = None
    ab_test_variant: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "ads"
        indexes = [
            IndexModel([("campaign_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("channel", ASCENDING), ("type", ASCENDING)]),
            IndexModel([("status", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("performance.ctr", DESCENDING)]),
            IndexModel([("performance.roas", DESCENDING)]),
            IndexModel([("ai_generated", ASCENDING)]),
            IndexModel([("ab_test_group", ASCENDING)]),
        ]

    @before_event("update")
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "campaign_id": self.campaign_id,
            "name": self.name,
            "type": self.type,
            "channel": self.channel,
            "status": self.status,
            "content": self.content.dict(),
            "performance": self.performance.dict(),
            "ai_generated": self.ai_generated,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# List of all document models for Beanie initialization
DOCUMENT_MODELS = [User, Team, Campaign, Ad]
