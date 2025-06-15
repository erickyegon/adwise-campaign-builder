"""
Core Configuration Module for AdWise AI Digital Marketing Campaign Builder

This module provides comprehensive configuration management with:
- Environment-based settings
- Database configuration
- Redis configuration  
- AI service configuration
- Security settings
- Logging configuration
- Feature flags

Design Principles:
- Type-safe configuration with Pydantic
- Environment-specific overrides
- Validation of critical settings
- Secure secret management
"""

import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from pydantic import (
    Field,
    validator,
    PostgresDsn,
    RedisDsn,
    HttpUrl,
    EmailStr
)
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""

    # PostgreSQL Configuration
    POSTGRES_HOST: str = Field(
        default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_USER: str = Field(
        default="adwise_user", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(
        default="password", description="PostgreSQL password")
    POSTGRES_DB: str = Field(default="adwise_campaigns",
                             description="PostgreSQL database name")

    # Connection Pool Settings
    DATABASE_POOL_SIZE: int = Field(
        default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(
        default=30, description="Database max overflow connections")
    DATABASE_POOL_TIMEOUT: int = Field(
        default=30, description="Database pool timeout in seconds")
    DATABASE_POOL_RECYCLE: int = Field(
        default=3600, description="Database pool recycle time")
    DATABASE_ECHO: bool = Field(
        default=False, description="Enable SQLAlchemy query logging")

    # Migration Settings
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        # Use string formatting instead of PostgresDsn.build()
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST")
        port = values.get("POSTGRES_PORT")
        db = values.get("POSTGRES_DB")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    class Config:
        env_prefix = "DB_"
        case_sensitive = True
        extra = "allow"


class RedisSettings(BaseSettings):
    """Redis configuration settings"""

    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(
        default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_CACHE_DB: int = Field(
        default=1, description="Redis cache database number")
    REDIS_SESSION_DB: int = Field(
        default=2, description="Redis session database number")

    # Connection Settings
    REDIS_MAX_CONNECTIONS: int = Field(
        default=50, description="Redis max connections")
    REDIS_SOCKET_TIMEOUT: int = Field(
        default=5, description="Redis socket timeout")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(
        default=5, description="Redis connect timeout")
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(
        default=30, description="Redis health check interval")

    # Cache Settings
    CACHE_TTL_DEFAULT: int = Field(
        default=3600, description="Default cache TTL in seconds")
    CACHE_TTL_SHORT: int = Field(
        default=300, description="Short cache TTL in seconds")
    CACHE_TTL_LONG: int = Field(
        default=86400, description="Long cache TTL in seconds")

    # Redis URL
    REDIS_URL: Optional[RedisDsn] = None

    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        # Use string formatting instead of RedisDsn.build()
        password = values.get("REDIS_PASSWORD")
        host = values.get("REDIS_HOST")
        port = values.get("REDIS_PORT")
        db = values.get("REDIS_DB") or 0
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    class Config:
        env_prefix = "REDIS_"
        case_sensitive = True
        extra = "allow"


class SecuritySettings(BaseSettings):
    """Security and authentication settings"""

    # JWT Configuration
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiry")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiry")

    # Password Security
    PASSWORD_MIN_LENGTH: int = Field(
        default=8, description="Minimum password length")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(
        default=True, description="Require uppercase")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(
        default=True, description="Require lowercase")
    PASSWORD_REQUIRE_NUMBERS: bool = Field(
        default=True, description="Require numbers")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(
        default=True, description="Require special chars")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60, description="API rate limit per minute")
    RATE_LIMIT_BURST: int = Field(
        default=10, description="Rate limit burst allowance")

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    ALLOWED_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH"],
        description="Allowed HTTP methods"
    )
    ALLOWED_HEADERS: List[str] = Field(
        default=["*"],
        description="Allowed headers"
    )

    # Session Security
    SESSION_COOKIE_SECURE: bool = Field(
        default=True, description="Secure session cookies")
    SESSION_COOKIE_HTTPONLY: bool = Field(
        default=True, description="HTTP-only session cookies")
    SESSION_COOKIE_SAMESITE: str = Field(
        default="lax", description="SameSite cookie policy")

    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = True
        extra = "allow"


class AISettings(BaseSettings):
    """AI and machine learning configuration"""

    # EURI API Configuration
    EURI_API_KEY: str = Field(
        default="test-key", description="EURI API key for AI services")
    EURI_BASE_URL: HttpUrl = Field(
        default="https://api.euri.ai/v1",
        description="EURI API base URL"
    )
    EURI_TIMEOUT: int = Field(
        default=30, description="EURI API timeout in seconds")
    EURI_MAX_RETRIES: int = Field(
        default=3, description="EURI API max retries")

    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = Field(
        default=False, description="Enable LangChain tracing")
    LANGCHAIN_API_KEY: Optional[str] = Field(
        default=None, description="LangChain API key")
    LANGCHAIN_PROJECT: str = Field(
        default="adwise-campaigns", description="LangChain project")

    # AI Model Settings
    DEFAULT_AI_MODEL: str = Field(
        default="gpt-4", description="Default AI model")
    CONTENT_GENERATION_MODEL: str = Field(
        default="gpt-4", description="Content generation model")
    ANALYTICS_MODEL: str = Field(
        default="gpt-3.5-turbo", description="Analytics model")
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002", description="Embedding model")

    # AI Processing Limits
    MAX_CONTENT_LENGTH: int = Field(
        default=4000, description="Max content length for AI")
    MAX_CAMPAIGNS_PER_BATCH: int = Field(
        default=10, description="Max campaigns per AI batch")
    AI_PROCESSING_TIMEOUT: int = Field(
        default=120, description="AI processing timeout")

    # Vector Database
    VECTOR_DIMENSION: int = Field(
        default=1536, description="Vector embedding dimension")
    SIMILARITY_THRESHOLD: float = Field(
        default=0.8, description="Similarity search threshold")

    class Config:
        env_prefix = "AI_"
        case_sensitive = True
        extra = "allow"


class ApplicationSettings(BaseSettings):
    """Main application configuration"""

    # Application Info
    APP_NAME: str = Field(default="AdWise AI Campaign Builder",
                          description="Application name")
    APP_VERSION: str = Field(
        default="1.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(
        default="AI-powered digital marketing campaign builder",
        description="Application description"
    )

    # Environment
    ENVIRONMENT: str = Field(default="development",
                             description="Environment name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    TESTING: bool = Field(default=False, description="Testing mode")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    DOCS_URL: str = Field(default="/docs", description="API docs URL")
    REDOC_URL: str = Field(default="/redoc", description="ReDoc URL")
    OPENAPI_URL: str = Field(default="/openapi.json",
                             description="OpenAPI JSON URL")

    @property
    def is_production(self) -> bool:
        """Check if environment is production"""
        return self.ENVIRONMENT.lower() == "production"

    # File Upload Settings
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024, description="Max file size (10MB)")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "application/pdf"],
        description="Allowed file types"
    )
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")

    # Email Configuration
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(
        default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(
        default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=True, description="SMTP TLS")
    FROM_EMAIL: Optional[EmailStr] = Field(
        default=None, description="From email address")

    # Feature Flags
    ENABLE_REAL_TIME_COLLABORATION: bool = Field(
        default=True, description="Enable real-time collaboration")
    ENABLE_AI_CONTENT_GENERATION: bool = Field(
        default=True, description="Enable AI content generation")
    ENABLE_ANALYTICS: bool = Field(
        default=True, description="Enable analytics")
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(
        default=True, description="Enable email notifications")
    ENABLE_SOCIAL_MEDIA_INTEGRATION: bool = Field(
        default=True, description="Enable social media integration")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="json", description="Log format (json/text)")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment


class Settings(BaseSettings):
    """Combined application settings"""

    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    ai: AISettings = AISettings()
    app: ApplicationSettings = ApplicationSettings()

    @property
    def is_development(self) -> bool:
        return self.app.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.app.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.app.ENVIRONMENT == "testing"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


# Global settings instance
settings = get_settings()
