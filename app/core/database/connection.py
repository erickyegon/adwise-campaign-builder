"""
Database Connection Management Module

This module handles all database connections with:
- PostgreSQL async/sync connections
- Redis connections for caching and sessions
- Connection pooling and health monitoring
- Graceful connection lifecycle management

Features:
- Production-ready connection pooling
- Automatic reconnection handling
- Health check endpoints
- Performance monitoring
- Secure connection configuration
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional
from urllib.parse import quote_plus

import asyncpg
import redis.asyncio as redis
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker, 
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PostgreSQLManager:
    """PostgreSQL connection manager with async/sync support"""
    
    def __init__(self):
        self.async_engine: Optional[AsyncEngine] = None
        self.sync_engine = None
        self.async_session_factory: Optional[async_sessionmaker] = None
        self.sync_session_factory = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connections"""
        if self._is_initialized:
            return
            
        try:
            await self._create_async_engine()
            self._create_sync_engine()
            self._setup_session_factories()
            self._setup_event_listeners()
            await self._verify_connection()
            
            self._is_initialized = True
            logger.info("PostgreSQL connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise
    
    async def _create_async_engine(self) -> None:
        """Create async SQLAlchemy engine"""
        async_url = (
            f"postgresql+asyncpg://{settings.database.POSTGRES_USER}:"
            f"{quote_plus(settings.database.POSTGRES_PASSWORD)}@"
            f"{settings.database.POSTGRES_HOST}:{settings.database.POSTGRES_PORT}/"
            f"{settings.database.POSTGRES_DB}"
        )
        
        self.async_engine = create_async_engine(
            async_url,
            echo=settings.database.DATABASE_ECHO,
            pool_size=settings.database.DATABASE_POOL_SIZE,
            max_overflow=settings.database.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.database.DATABASE_POOL_TIMEOUT,
            pool_recycle=settings.database.DATABASE_POOL_RECYCLE,
            pool_pre_ping=True,
            connect_args={
                "server_settings": {
                    "application_name": "adwise_ai_campaign_builder",
                    "jit": "off",
                },
                "command_timeout": 60,
                "statement_cache_size": 0,
            }
        )
    
    def _create_sync_engine(self) -> None:
        """Create sync SQLAlchemy engine for migrations"""
        sync_url = (
            f"postgresql+psycopg2://{settings.database.POSTGRES_USER}:"
            f"{quote_plus(settings.database.POSTGRES_PASSWORD)}@"
            f"{settings.database.POSTGRES_HOST}:{settings.database.POSTGRES_PORT}/"
            f"{settings.database.POSTGRES_DB}"
        )
        
        self.sync_engine = create_engine(
            sync_url,
            echo=settings.database.DATABASE_ECHO,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
    
    def _setup_session_factories(self) -> None:
        """Setup session factories"""
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
        
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            autoflush=True,
            autocommit=False,
        )
    
    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners"""
        
        @event.listens_for(self.async_engine.sync_engine, "connect")
        def set_postgresql_settings(dbapi_connection, connection_record):
            """Optimize PostgreSQL connection settings"""
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                cursor.execute("SET timezone TO 'UTC'")
                cursor.execute("SET statement_timeout TO '300s'")
                cursor.execute("SET lock_timeout TO '30s'")
        
        @event.listens_for(self.async_engine.sync_engine, "checkout")
        def log_connection_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection pool checkout"""
            logger.debug("PostgreSQL connection checked out from pool")
        
        @event.listens_for(self.async_engine.sync_engine, "checkin")
        def log_connection_checkin(dbapi_connection, connection_record):
            """Log connection pool checkin"""
            logger.debug("PostgreSQL connection returned to pool")
    
    async def _verify_connection(self) -> None:
        """Verify PostgreSQL connection"""
        async with self.async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with proper error handling"""
        if not self._is_initialized:
            raise RuntimeError("PostgreSQL not initialized")
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get sync database session"""
        if not self._is_initialized:
            raise RuntimeError("PostgreSQL not initialized")
        return self.sync_session_factory()
    
    async def health_check(self) -> bool:
        """Check PostgreSQL health"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close PostgreSQL connections"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.sync_engine:
                self.sync_engine.dispose()
            self._is_initialized = False
            logger.info("PostgreSQL connections closed")
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connections: {e}")


class RedisManager:
    """Redis connection manager for caching and sessions"""
    
    def __init__(self):
        self.main_client: Optional[redis.Redis] = None
        self.cache_client: Optional[redis.Redis] = None
        self.session_client: Optional[redis.Redis] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize Redis connections"""
        if self._is_initialized:
            return
            
        try:
            self._create_clients()
            await self._verify_connections()
            
            self._is_initialized = True
            logger.info("Redis connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def _create_clients(self) -> None:
        """Create Redis clients for different purposes"""
        base_config = {
            "host": settings.redis.REDIS_HOST,
            "port": settings.redis.REDIS_PORT,
            "password": settings.redis.REDIS_PASSWORD,
            "decode_responses": True,
            "retry_on_timeout": True,
            "socket_timeout": settings.redis.REDIS_SOCKET_TIMEOUT,
            "socket_connect_timeout": settings.redis.REDIS_SOCKET_CONNECT_TIMEOUT,
            "health_check_interval": settings.redis.REDIS_HEALTH_CHECK_INTERVAL,
        }
        
        # Main Redis client for general use
        self.main_client = redis.Redis(
            **base_config,
            db=settings.redis.REDIS_DB,
            max_connections=settings.redis.REDIS_MAX_CONNECTIONS,
        )
        
        # Cache-specific client
        self.cache_client = redis.Redis(
            **base_config,
            db=settings.redis.REDIS_CACHE_DB,
            max_connections=20,
        )
        
        # Session-specific client
        self.session_client = redis.Redis(
            **base_config,
            db=settings.redis.REDIS_SESSION_DB,
            max_connections=15,
        )
    
    async def _verify_connections(self) -> None:
        """Verify all Redis connections"""
        await self.main_client.ping()
        await self.cache_client.ping()
        await self.session_client.ping()
    
    async def get_main_client(self) -> redis.Redis:
        """Get main Redis client"""
        if not self._is_initialized:
            raise RuntimeError("Redis not initialized")
        return self.main_client
    
    async def get_cache_client(self) -> redis.Redis:
        """Get cache Redis client"""
        if not self._is_initialized:
            raise RuntimeError("Redis not initialized")
        return self.cache_client
    
    async def get_session_client(self) -> redis.Redis:
        """Get session Redis client"""
        if not self._is_initialized:
            raise RuntimeError("Redis not initialized")
        return self.session_client
    
    async def health_check(self) -> Dict[str, bool]:
        """Check Redis health for all clients"""
        health = {"main": False, "cache": False, "session": False}
        
        try:
            await self.main_client.ping()
            health["main"] = True
        except Exception as e:
            logger.error(f"Redis main client health check failed: {e}")
        
        try:
            await self.cache_client.ping()
            health["cache"] = True
        except Exception as e:
            logger.error(f"Redis cache client health check failed: {e}")
        
        try:
            await self.session_client.ping()
            health["session"] = True
        except Exception as e:
            logger.error(f"Redis session client health check failed: {e}")
        
        return health
    
    async def close(self) -> None:
        """Close all Redis connections"""
        try:
            if self.main_client:
                await self.main_client.close()
            if self.cache_client:
                await self.cache_client.close()
            if self.session_client:
                await self.session_client.close()
            self._is_initialized = False
            logger.info("Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")


class DatabaseManager:
    """Main database manager coordinating PostgreSQL and Redis"""
    
    def __init__(self):
        self.postgresql = PostgreSQLManager()
        self.redis = RedisManager()
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize all database connections"""
        if self._is_initialized:
            return
            
        try:
            await self.postgresql.initialize()
            await self.redis.initialize()
            
            self._is_initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            await self.close()
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        return {
            "postgresql": await self.postgresql.health_check(),
            "redis": await self.redis.health_check(),
            "overall": self._is_initialized
        }
    
    async def close(self) -> None:
        """Close all database connections"""
        try:
            await self.postgresql.close()
            await self.redis.close()
            self._is_initialized = False
            logger.info("Database manager closed")
        except Exception as e:
            logger.error(f"Error closing database manager: {e}")


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get or create global database manager"""
    global _database_manager
    
    if _database_manager is None:
        _database_manager = DatabaseManager()
        await _database_manager.initialize()
    
    return _database_manager
