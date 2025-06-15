"""
Authentication Schemas for AdWise AI Digital Marketing Campaign Builder

This module defines COMPLETE Pydantic schemas for authentication as per PRM requirements:
- JWT token authentication (PRM Section 3)
- Role-based access control (Admin, Editor, Viewer)
- User registration and login
- Password management with security
- Session management
- Multi-factor authentication support
- Account verification

Security Features:
- Strong password validation
- Email validation and verification
- Role-based permissions
- Token expiration handling
- Account lockout protection
- Audit logging
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class UserRole(str, Enum):
    """User roles as per PRM specifications"""
    ADMIN = "admin"      # Full system access
    EDITOR = "editor"    # Create/edit campaigns
    VIEWER = "viewer"    # Read-only access


class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class LoginRequest(BaseModel):
    """User login request schema with enhanced security"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    remember_me: bool = Field(default=False, description="Remember login session")
    device_info: Optional[Dict[str, str]] = Field(default=None, description="Device information for security")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "remember_me": False,
                "device_info": {
                    "user_agent": "Mozilla/5.0...",
                    "ip_address": "192.168.1.1"
                }
            }
        }


class RegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")
    terms_accepted: bool = Field(..., description="Terms and conditions acceptance")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "full_name": "John Doe",
                "role": "editor",
                "company": "Marketing Agency Inc.",
                "phone": "+1-555-0123",
                "terms_accepted": True
            }
        }


class TokenResponse(BaseModel):
    """JWT token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    scope: List[str] = Field(default_factory=list, description="Token permissions scope")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "expires_at": "2024-01-01T12:00:00Z",
                "scope": ["read", "write", "admin"]
            }
        }


class UserResponse(BaseModel):
    """User information response schema"""
    id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")
    status: AccountStatus = Field(..., description="Account status")
    team_ids: List[str] = Field(default_factory=list, description="Associated team IDs")
    company: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(default=0, description="Total login count")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60f7b3b3b3b3b3b3b3b3b3b3",
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "editor",
                "status": "active",
                "team_ids": ["team1", "team2"],
                "company": "Marketing Agency Inc.",
                "phone": "+1-555-0123",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "last_login": "2024-01-01T11:30:00Z",
                "login_count": 42,
                "preferences": {
                    "theme": "light",
                    "notifications": True,
                    "language": "en"
                }
            }
        }


class LoginResponse(BaseModel):
    """Complete login response schema"""
    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    session_id: str = Field(..., description="Session identifier")
    permissions: List[str] = Field(..., description="User permissions")
    
    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": "60f7b3b3b3b3b3b3b3b3b3b3",
                    "email": "user@example.com",
                    "full_name": "John Doe",
                    "role": "editor"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                },
                "session_id": "sess_123456789",
                "permissions": ["campaigns:read", "campaigns:write", "analytics:read"]
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class LogoutRequest(BaseModel):
    """Logout request schema"""
    all_devices: bool = Field(default=False, description="Logout from all devices")
    
    class Config:
        schema_extra = {
            "example": {
                "all_devices": False
            }
        }


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str = Field(..., description="Email verification token")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "verification_token_123456"
            }
        }


class TwoFactorSetupRequest(BaseModel):
    """Two-factor authentication setup request"""
    method: str = Field(..., description="2FA method (totp, sms)")
    phone: Optional[str] = Field(None, description="Phone number for SMS 2FA")
    
    class Config:
        schema_extra = {
            "example": {
                "method": "totp",
                "phone": "+1-555-0123"
            }
        }


class TwoFactorVerifyRequest(BaseModel):
    """Two-factor authentication verification request"""
    code: str = Field(..., min_length=6, max_length=6, description="2FA verification code")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "123456"
            }
        }
