"""
Database Session Management Module

This module provides session management for:
- Async database sessions with proper lifecycle
- Dependency injection for FastAPI
- Transaction management
- Error handling and rollback
- Session monitoring and logging

Features:
- Context manager support
- Automatic commit/rollback
- Session pooling
- Performance monitoring
- Testing support
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .connection import get_database_manager

logger = logging.getLogger(__name__)


class SessionManager:
    """Session manager for database operations"""
    
    def __init__(self):
        self._db_manager: Optional = None
    
    async def _get_db_manager(self):
        """Get database manager instance"""
        if self._db_manager is None:
            self._db_manager = await get_database_manager()
        return self._db_manager
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session with proper lifecycle management
        
        Usage:
            async with session_manager.get_async_session() as session:
                # Use session for database operations
                result = await session.execute(query)
                # Session is automatically committed and closed
        """
        db_manager = await self._get_db_manager()
        
        async with db_manager.postgresql.get_session() as session:
            try:
                logger.debug("Async database session created")
                yield session
                logger.debug("Async database session committed")
            except Exception as e:
                logger.error(f"Database session error: {e}")
                raise
            finally:
                logger.debug("Async database session closed")
    
    async def get_sync_session(self) -> Session:
        """
        Get sync database session for migrations and admin tasks
        
        Note: Remember to close the session manually when using sync sessions
        """
        db_manager = await self._get_db_manager()
        session = db_manager.postgresql.get_sync_session()
        logger.debug("Sync database session created")
        return session


# Global session manager instance
session_manager = SessionManager()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting async database session
    
    Usage in FastAPI endpoints:
        @app.get("/users/")
        async def get_users(session: AsyncSession = Depends(get_async_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    async with session_manager.get_async_session() as session:
        yield session


async def get_sync_session() -> Session:
    """
    FastAPI dependency for getting sync database session
    
    Usage in FastAPI endpoints (for special cases):
        @app.get("/admin/migrate/")
        async def run_migration(session: Session = Depends(get_sync_session)):
            # Use session for migration operations
            # Remember to close session manually
            try:
                # Migration operations
                pass
            finally:
                session.close()
    """
    return await session_manager.get_sync_session()


class TransactionManager:
    """Advanced transaction management for complex operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._savepoints = []
    
    async def create_savepoint(self, name: str) -> None:
        """Create a savepoint for nested transactions"""
        savepoint = await self.session.begin_nested()
        self._savepoints.append((name, savepoint))
        logger.debug(f"Created savepoint: {name}")
    
    async def rollback_to_savepoint(self, name: str) -> None:
        """Rollback to a specific savepoint"""
        for i, (sp_name, savepoint) in enumerate(self._savepoints):
            if sp_name == name:
                await savepoint.rollback()
                # Remove this and all subsequent savepoints
                self._savepoints = self._savepoints[:i]
                logger.debug(f"Rolled back to savepoint: {name}")
                return
        raise ValueError(f"Savepoint '{name}' not found")
    
    async def commit_savepoint(self, name: str) -> None:
        """Commit a specific savepoint"""
        for i, (sp_name, savepoint) in enumerate(self._savepoints):
            if sp_name == name:
                await savepoint.commit()
                # Remove this savepoint
                self._savepoints.pop(i)
                logger.debug(f"Committed savepoint: {name}")
                return
        raise ValueError(f"Savepoint '{name}' not found")
    
    async def commit_all(self) -> None:
        """Commit all savepoints and the main transaction"""
        for name, savepoint in self._savepoints:
            await savepoint.commit()
            logger.debug(f"Committed savepoint: {name}")
        
        await self.session.commit()
        self._savepoints.clear()
        logger.debug("Committed main transaction")
    
    async def rollback_all(self) -> None:
        """Rollback all savepoints and the main transaction"""
        for name, savepoint in reversed(self._savepoints):
            await savepoint.rollback()
            logger.debug(f"Rolled back savepoint: {name}")
        
        await self.session.rollback()
        self._savepoints.clear()
        logger.debug("Rolled back main transaction")


@asynccontextmanager
async def transaction_context(session: AsyncSession) -> AsyncGenerator[TransactionManager, None]:
    """
    Context manager for advanced transaction management
    
    Usage:
        async with get_async_session() as session:
            async with transaction_context(session) as tx:
                # Create savepoints for complex operations
                await tx.create_savepoint("user_creation")
                
                # Create user
                user = User(name="John")
                session.add(user)
                
                try:
                    # Create related data
                    await tx.create_savepoint("profile_creation")
                    profile = Profile(user_id=user.id)
                    session.add(profile)
                    
                    # Commit everything if successful
                    await tx.commit_all()
                    
                except Exception:
                    # Rollback to user creation if profile fails
                    await tx.rollback_to_savepoint("user_creation")
                    # Or rollback everything
                    # await tx.rollback_all()
    """
    tx_manager = TransactionManager(session)
    try:
        yield tx_manager
    except Exception as e:
        logger.error(f"Transaction error: {e}")
        await tx_manager.rollback_all()
        raise


class SessionMonitor:
    """Monitor database session performance and usage"""
    
    def __init__(self):
        self.active_sessions = 0
        self.total_sessions = 0
        self.failed_sessions = 0
    
    def session_created(self) -> None:
        """Track session creation"""
        self.active_sessions += 1
        self.total_sessions += 1
        logger.debug(f"Session created. Active: {self.active_sessions}, Total: {self.total_sessions}")
    
    def session_closed(self, success: bool = True) -> None:
        """Track session closure"""
        self.active_sessions -= 1
        if not success:
            self.failed_sessions += 1
        logger.debug(f"Session closed. Active: {self.active_sessions}, Failed: {self.failed_sessions}")
    
    def get_stats(self) -> dict:
        """Get session statistics"""
        return {
            "active_sessions": self.active_sessions,
            "total_sessions": self.total_sessions,
            "failed_sessions": self.failed_sessions,
            "success_rate": (
                (self.total_sessions - self.failed_sessions) / self.total_sessions
                if self.total_sessions > 0 else 0
            )
        }


# Global session monitor
session_monitor = SessionMonitor()


@asynccontextmanager
async def monitored_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Session with monitoring capabilities
    
    Usage:
        async with monitored_session() as session:
            # Session usage is automatically monitored
            pass
    """
    session_monitor.session_created()
    success = False
    
    try:
        async with session_manager.get_async_session() as session:
            yield session
            success = True
    except Exception as e:
        logger.error(f"Monitored session error: {e}")
        raise
    finally:
        session_monitor.session_closed(success)
