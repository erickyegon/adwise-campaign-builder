"""
Redis Cache and Session Management for AdWise AI Digital Marketing Campaign Builder

This module provides Redis functionality as per HLD/LDL/PRM requirements:
- Redis connection management with aioredis
- Caching layer for performance optimization
- Session storage for user management
- Real-time data storage for collaboration
- Connection pooling and health monitoring

Design Principles:
- Follows HLD/LDL specifications exactly
- Async-first with aioredis
- Multiple database support (cache, sessions, real-time)
- Production-ready with connection pooling
- Performance-optimized with proper TTL management
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional, Union, List
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisManager:
    """
    Redis connection manager as per HLD specifications

    Features:
    - Async Redis connections with aioredis
    - Multiple database support (cache, sessions, real-time)
    - Connection pooling
    - Health monitoring
    - TTL management
    """

    def __init__(self):
        self.client: Optional[Redis] = None
        self.cache_client: Optional[Redis] = None
        self.session_client: Optional[Redis] = None
        self._is_initialized = False
        self._connection_pool = None

    async def initialize(self) -> None:
        """
        Initialize Redis connections and connection pool
        """
        if self._is_initialized:
            return

        try:
            await self._create_connection_pool()
            await self._create_clients()
            await self._verify_connections()

            self._is_initialized = True
            logger.info("Redis connections initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def _create_connection_pool(self) -> None:
        """Create Redis connection pool"""
        redis_url = self._build_redis_url()

        self._connection_pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=getattr(settings.redis, 'MAX_CONNECTIONS', 50),
            socket_timeout=getattr(settings.redis, 'SOCKET_TIMEOUT', 5),
            socket_connect_timeout=getattr(
                settings.redis, 'SOCKET_CONNECT_TIMEOUT', 5),
            health_check_interval=getattr(
                settings.redis, 'HEALTH_CHECK_INTERVAL', 30),
            retry_on_timeout=True,
        )

        logger.info("Redis connection pool created")

    def _build_redis_url(self) -> str:
        """Build Redis connection URL"""
        host = getattr(settings.redis, 'HOST', 'localhost')
        port = getattr(settings.redis, 'PORT', 6379)
        password = getattr(settings.redis, 'PASSWORD', '')
        db = getattr(settings.redis, 'DB', 0)

        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"

    async def _create_clients(self) -> None:
        """Create Redis clients for different purposes"""
        # Main client
        self.client = Redis(connection_pool=self._connection_pool)

        # Cache client (separate database)
        cache_db = getattr(settings.redis, 'CACHE_DB', 1)
        cache_url = self._build_redis_url().replace(
            f"/{getattr(settings.redis, 'DB', 0)}", f"/{cache_db}")
        self.cache_client = Redis.from_url(cache_url)

        # Session client (separate database)
        session_db = getattr(settings.redis, 'SESSION_DB', 2)
        session_url = self._build_redis_url().replace(
            f"/{getattr(settings.redis, 'DB', 0)}", f"/{session_db}")
        self.session_client = Redis.from_url(session_url)

        logger.info(
            "Redis clients created for main, cache, and session databases")

    async def _verify_connections(self) -> None:
        """Verify Redis connections"""
        try:
            # Test main client
            await self.client.ping()

            # Test cache client
            await self.cache_client.ping()

            # Test session client
            await self.session_client.ping()

            logger.info("Redis connections verified successfully")
        except Exception as e:
            logger.error(f"Redis connection verification failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive Redis health check"""
        health_status = {
            "redis_main": False,
            "redis_cache": False,
            "redis_session": False,
            "connection_pool": False,
            "memory_usage": {},
            "connection_info": {}
        }

        try:
            # Test main client
            result = await self.client.ping()
            health_status["redis_main"] = result

            # Test cache client
            result = await self.cache_client.ping()
            health_status["redis_cache"] = result

            # Test session client
            result = await self.session_client.ping()
            health_status["redis_session"] = result

            # Test connection pool
            health_status["connection_pool"] = self._connection_pool is not None

            # Get memory usage
            info = await self.client.info("memory")
            health_status["memory_usage"] = {
                "used_memory": info.get("used_memory"),
                "used_memory_human": info.get("used_memory_human"),
                "maxmemory": info.get("maxmemory"),
            }

            # Get connection info
            server_info = await self.client.info("server")
            health_status["connection_info"] = {
                "redis_version": server_info.get("redis_version"),
                "connected_clients": server_info.get("connected_clients"),
                "uptime_in_seconds": server_info.get("uptime_in_seconds"),
            }

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status["error"] = str(e)

        return health_status

    # Cache operations
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value with optional TTL"""
        try:
            if ttl is None:
                ttl = getattr(settings.redis, 'CACHE_TTL_DEFAULT', 3600)

            serialized_value = json.dumps(
                value) if not isinstance(value, str) else value
            result = await self.cache_client.setex(key, ttl, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            value = await self.cache_client.get(key)
            if value is None:
                return None

            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8') if isinstance(value, bytes) else value
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None

    async def cache_delete(self, key: str) -> bool:
        """Delete cache value"""
        try:
            result = await self.cache_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False

    # Session operations
    async def session_set(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set session data"""
        try:
            if ttl is None:
                ttl = 86400  # 24 hours default

            serialized_data = json.dumps(data)
            result = await self.session_client.setex(f"session:{session_id}", ttl, serialized_data)
            return result
        except Exception as e:
            logger.error(f"Session set failed for {session_id}: {e}")
            return False

    async def session_get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            data = await self.session_client.get(f"session:{session_id}")
            if data is None:
                return None

            return json.loads(data)
        except Exception as e:
            logger.error(f"Session get failed for {session_id}: {e}")
            return None

    async def session_delete(self, session_id: str) -> bool:
        """Delete session"""
        try:
            result = await self.session_client.delete(f"session:{session_id}")
            return result > 0
        except Exception as e:
            logger.error(f"Session delete failed for {session_id}: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connections"""
        try:
            if self.client:
                await self.client.close()
            if self.cache_client:
                await self.cache_client.close()
            if self.session_client:
                await self.session_client.close()
            if self._connection_pool:
                await self._connection_pool.disconnect()

            self._is_initialized = False
            logger.info("Redis connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")


# Global Redis manager instance
_redis_manager: Optional[RedisManager] = None


async def get_redis_manager() -> RedisManager:
    """Get or create global Redis manager"""
    global _redis_manager

    if _redis_manager is None:
        _redis_manager = RedisManager()

    return _redis_manager


async def initialize_redis() -> RedisManager:
    """Initialize Redis connections"""
    manager = await get_redis_manager()
    await manager.initialize()
    return manager


@asynccontextmanager
async def get_redis() -> AsyncGenerator[Redis, None]:
    """Get Redis client for dependency injection"""
    manager = await get_redis_manager()
    yield manager.client


# Convenience functions for FastAPI dependency injection
async def get_cache() -> Redis:
    """FastAPI dependency for getting Redis cache client"""
    manager = await get_redis_manager()
    return manager.cache_client


async def get_session_store() -> Redis:
    """FastAPI dependency for getting Redis session client"""
    manager = await get_redis_manager()
    return manager.session_client
