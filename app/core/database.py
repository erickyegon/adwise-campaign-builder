"""
Advanced Database Configuration for AdWise AI Digital Marketing Campaign Builder

This module provides a comprehensive database setup with:
- PostgreSQL as primary database with JSONB support
- Redis for caching and real-time features
- Vector database integration for AI embeddings
- Connection pooling and async support
- Database health monitoring
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Base class for all database models
Base = declarative_base()

class DatabaseManager:
    """
    Comprehensive database manager handling PostgreSQL and Redis connections
    with advanced features like connection pooling, health checks, and monitoring
    """
    
    def __init__(self):
        self.async_engine: Optional[AsyncEngine] = None
        self.sync_engine = None
        self.async_session_factory: Optional[async_sessionmaker] = None
        self.sync_session_factory = None
        self.redis_client: Optional[redis.Redis] = None
        self.redis_cache_client: Optional[redis.Redis] = None
        self._connection_pools: Dict[str, Any] = {}
        
    async def initialize_databases(self) -> None:
        """Initialize all database connections with comprehensive configuration"""
        try:
            await self._setup_postgresql()
            await self._setup_redis()
            await self._setup_vector_database()
            await self._verify_connections()
            logger.info("All database connections initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _setup_postgresql(self) -> None:
        """Setup PostgreSQL with advanced configuration"""
        # Async Engine Configuration
        async_database_url = (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
            f"{quote_plus(settings.POSTGRES_PASSWORD)}@"
            f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
            f"{settings.POSTGRES_DB}"
        )
        
        # Advanced engine configuration for production
        self.async_engine = create_async_engine(
            async_database_url,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before use
            connect_args={
                "server_settings": {
                    "application_name": "adwise_ai_campaign_builder",
                    "jit": "off",  # Disable JIT for better performance on small queries
                },
                "command_timeout": 60,
                "statement_cache_size": 0,  # Disable prepared statement cache
            }
        )
        
        # Sync Engine for migrations and admin tasks
        sync_database_url = (
            f"postgresql+psycopg2://{settings.POSTGRES_USER}:"
            f"{quote_plus(settings.POSTGRES_PASSWORD)}@"
            f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
            f"{settings.POSTGRES_DB}"
        )
        
        self.sync_engine = create_engine(
            sync_database_url,
            echo=settings.DATABASE_ECHO,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        
        # Session factories
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
        
        # Setup database event listeners for monitoring
        self._setup_database_events()
        
        logger.info("PostgreSQL connection configured successfully")
    
    async def _setup_redis(self) -> None:
        """Setup Redis with clustering and caching configuration"""
        # Main Redis connection for sessions and real-time features
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            retry_on_timeout=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,
        )
        
        # Separate Redis connection for caching with different configuration
        self.redis_cache_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_CACHE_DB,
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
            socket_timeout=10,
            socket_connect_timeout=5,
        )
        
        logger.info("Redis connections configured successfully")
    
    async def _setup_vector_database(self) -> None:
        """Setup vector database for AI embeddings and similarity search"""
        try:
            # Install pgvector extension if not exists
            async with self.async_engine.begin() as conn:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))
            
            logger.info("Vector database extensions installed successfully")
        except Exception as e:
            logger.warning(f"Vector database setup warning: {e}")
    
    def _setup_database_events(self) -> None:
        """Setup SQLAlchemy event listeners for monitoring and optimization"""
        
        @event.listens_for(self.async_engine.sync_engine, "connect")
        def set_postgresql_search_path(dbapi_connection, connection_record):
            """Set search path and optimize PostgreSQL connection"""
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                cursor.execute("SET timezone TO 'UTC'")
                cursor.execute("SET statement_timeout TO '300s'")
                cursor.execute("SET lock_timeout TO '30s'")
        
        @event.listens_for(self.async_engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring"""
            logger.debug("Database connection checked out from pool")
        
        @event.listens_for(self.async_engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin for monitoring"""
            logger.debug("Database connection returned to pool")
    
    async def _verify_connections(self) -> None:
        """Verify all database connections are working"""
        # Test PostgreSQL
        async with self.async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        # Test Redis
        await self.redis_client.ping()
        await self.redis_cache_client.ping()
        
        logger.info("All database connections verified successfully")
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with proper error handling"""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
        
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
        """Get synchronous database session for migrations"""
        if not self.sync_session_factory:
            raise RuntimeError("Database not initialized")
        return self.sync_session_factory()
    
    async def get_redis_client(self) -> redis.Redis:
        """Get Redis client for general use"""
        if not self.redis_client:
            raise RuntimeError("Redis not initialized")
        return self.redis_client
    
    async def get_cache_client(self) -> redis.Redis:
        """Get Redis client specifically for caching"""
        if not self.redis_cache_client:
            raise RuntimeError("Redis cache not initialized")
        return self.redis_cache_client
    
    async def health_check(self) -> Dict[str, bool]:
        """Comprehensive health check for all database connections"""
        health_status = {
            "postgresql": False,
            "redis": False,
            "redis_cache": False,
        }
        
        try:
            # PostgreSQL health check
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["postgresql"] = True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
        
        try:
            # Redis health check
            await self.redis_client.ping()
            health_status["redis"] = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
        
        try:
            # Redis cache health check
            await self.redis_cache_client.ping()
            health_status["redis_cache"] = True
        except Exception as e:
            logger.error(f"Redis cache health check failed: {e}")
        
        return health_status
    
    async def close_connections(self) -> None:
        """Gracefully close all database connections"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.sync_engine:
                self.sync_engine.dispose()
            if self.redis_client:
                await self.redis_client.close()
            if self.redis_cache_client:
                await self.redis_cache_client.close()
            logger.info("All database connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for dependency injection
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session"""
    async with db_manager.get_async_session() as session:
        yield session

async def get_redis() -> redis.Redis:
    """Dependency for getting Redis client"""
    return await db_manager.get_redis_client()

async def get_cache() -> redis.Redis:
    """Dependency for getting Redis cache client"""
    return await db_manager.get_cache_client()
