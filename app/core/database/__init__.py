"""
Database Module for AdWise AI Digital Marketing Campaign Builder

This module provides modular database functionality with:
- PostgreSQL connection management
- Redis connection management  
- Session management
- Health monitoring
- Migration support

Design Principles:
- Separation of concerns
- Dependency injection ready
- Easy testing and mocking
- Production-ready configuration
"""

from .connection import DatabaseManager, get_database_manager
from .session import get_async_session, get_sync_session
from .base import Base, BaseModel

__all__ = [
    "DatabaseManager",
    "get_database_manager", 
    "get_async_session",
    "get_sync_session",
    "Base",
    "BaseModel"
]
