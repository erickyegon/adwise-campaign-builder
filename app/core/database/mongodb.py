"""
MongoDB Database Configuration for AdWise AI Digital Marketing Campaign Builder

This module provides MongoDB database functionality as per HLD/LDL/PRM requirements:
- MongoDB connection management with Motor (async driver)
- Beanie ODM for document modeling
- Connection pooling and health monitoring
- Atlas cloud support for production
- Aggregation pipeline support for analytics

Design Principles:
- Follows HLD/LDL specifications exactly
- Async-first with Motor driver
- Document-based modeling with Beanie
- Production-ready with Atlas support
- Analytics-optimized with aggregation pipelines
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional, List
from urllib.parse import quote_plus

import motor.motor_asyncio
from beanie import init_beanie
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MongoDBManager:
    """
    MongoDB connection manager as per HLD specifications
    
    Features:
    - Async MongoDB connections with Motor
    - Beanie ODM integration
    - Connection pooling
    - Health monitoring
    - Atlas cloud support
    """
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.sync_client: Optional[MongoClient] = None
        self._is_initialized = False
        self._document_models: List = []
    
    async def initialize(self, document_models: List = None) -> None:
        """
        Initialize MongoDB connections and Beanie ODM
        
        Args:
            document_models: List of Beanie document models to initialize
        """
        if self._is_initialized:
            return
        
        try:
            await self._create_async_client()
            self._create_sync_client()
            
            if document_models:
                self._document_models = document_models
                await self._initialize_beanie()
            
            await self._verify_connection()
            await self._setup_indexes()
            
            self._is_initialized = True
            logger.info("MongoDB connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {e}")
            raise
    
    async def _create_async_client(self) -> None:
        """Create async MongoDB client with Motor"""
        # Determine connection URL
        if settings.app.is_production and hasattr(settings, 'MONGODB_ATLAS_URL'):
            connection_url = settings.MONGODB_ATLAS_URL
            database_name = getattr(settings, 'MONGODB_ATLAS_DATABASE', 'adwise_campaigns')
        else:
            # Local development connection
            if hasattr(settings, 'MONGODB_USERNAME') and settings.MONGODB_USERNAME:
                connection_url = (
                    f"mongodb://{settings.MONGODB_USERNAME}:"
                    f"{quote_plus(settings.MONGODB_PASSWORD)}@"
                    f"{settings.MONGODB_URL.split('://')[-1]}"
                )
            else:
                connection_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
            
            database_name = getattr(settings, 'MONGODB_DATABASE', 'adwise_campaigns')
        
        # Create async client with optimized settings
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            connection_url,
            maxPoolSize=getattr(settings, 'MONGODB_MAX_CONNECTIONS', 100),
            minPoolSize=getattr(settings, 'MONGODB_MIN_CONNECTIONS', 10),
            maxIdleTimeMS=getattr(settings, 'MONGODB_MAX_IDLE_TIME', 30000),
            connectTimeoutMS=getattr(settings, 'MONGODB_CONNECT_TIMEOUT', 10000),
            serverSelectionTimeoutMS=getattr(settings, 'MONGODB_SERVER_SELECTION_TIMEOUT', 5000),
            retryWrites=True,
            retryReads=True,
        )
        
        self.database = self.client[database_name]
        logger.info(f"Async MongoDB client created for database: {database_name}")
    
    def _create_sync_client(self) -> None:
        """Create sync MongoDB client for admin operations"""
        # Use same connection logic as async client
        if settings.app.is_production and hasattr(settings, 'MONGODB_ATLAS_URL'):
            connection_url = settings.MONGODB_ATLAS_URL
        else:
            if hasattr(settings, 'MONGODB_USERNAME') and settings.MONGODB_USERNAME:
                connection_url = (
                    f"mongodb://{settings.MONGODB_USERNAME}:"
                    f"{quote_plus(settings.MONGODB_PASSWORD)}@"
                    f"{settings.MONGODB_URL.split('://')[-1]}"
                )
            else:
                connection_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
        
        self.sync_client = MongoClient(
            connection_url,
            maxPoolSize=50,
            minPoolSize=5,
            connectTimeoutMS=10000,
            serverSelectionTimeoutMS=5000,
        )
        
        logger.info("Sync MongoDB client created")
    
    async def _initialize_beanie(self) -> None:
        """Initialize Beanie ODM with document models"""
        try:
            await init_beanie(
                database=self.database,
                document_models=self._document_models
            )
            logger.info(f"Beanie ODM initialized with {len(self._document_models)} models")
        except Exception as e:
            logger.error(f"Failed to initialize Beanie ODM: {e}")
            raise
    
    async def _verify_connection(self) -> None:
        """Verify MongoDB connection"""
        try:
            # Test async connection
            await self.client.admin.command('ping')
            
            # Test sync connection
            self.sync_client.admin.command('ping')
            
            logger.info("MongoDB connections verified successfully")
        except Exception as e:
            logger.error(f"MongoDB connection verification failed: {e}")
            raise
    
    async def _setup_indexes(self) -> None:
        """Setup database indexes for performance"""
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("username", unique=True, sparse=True)
            await self.database.users.create_index([("role", 1), ("status", 1)])
            
            # Campaigns collection indexes
            await self.database.campaigns.create_index([("owner_id", 1), ("status", 1)])
            await self.database.campaigns.create_index([("team_id", 1), ("status", 1)])
            await self.database.campaigns.create_index([("start_date", 1), ("end_date", 1)])
            await self.database.campaigns.create_index("name", background=True)
            
            # Ads collection indexes
            await self.database.ads.create_index([("campaign_id", 1), ("status", 1)])
            await self.database.ads.create_index([("channel", 1), ("type", 1)])
            await self.database.ads.create_index("ai_generated")
            
            # Analytics collection indexes
            await self.database.analytics.create_index([("ad_id", 1), ("timestamp", -1)])
            await self.database.analytics.create_index([("campaign_id", 1), ("timestamp", -1)])
            await self.database.analytics.create_index("timestamp")
            
            # Teams collection indexes
            await self.database.teams.create_index("slug", unique=True)
            await self.database.teams.create_index("owner_id")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    async def get_database(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get async database instance"""
        if not self._is_initialized:
            raise RuntimeError("MongoDB not initialized")
        return self.database
    
    def get_sync_database(self) -> Any:
        """Get sync database instance"""
        if not self._is_initialized:
            raise RuntimeError("MongoDB not initialized")
        
        database_name = getattr(settings, 'MONGODB_DATABASE', 'adwise_campaigns')
        if settings.app.is_production:
            database_name = getattr(settings, 'MONGODB_ATLAS_DATABASE', 'adwise_campaigns')
        
        return self.sync_client[database_name]
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive MongoDB health check"""
        health_status = {
            "mongodb_async": False,
            "mongodb_sync": False,
            "database_accessible": False,
            "collections_count": 0,
            "connection_info": {}
        }
        
        try:
            # Test async connection
            result = await self.client.admin.command('ping')
            health_status["mongodb_async"] = result.get('ok') == 1
            
            # Test sync connection
            result = self.sync_client.admin.command('ping')
            health_status["mongodb_sync"] = result.get('ok') == 1
            
            # Test database access
            collections = await self.database.list_collection_names()
            health_status["database_accessible"] = True
            health_status["collections_count"] = len(collections)
            
            # Get connection info
            server_info = await self.client.server_info()
            health_status["connection_info"] = {
                "mongodb_version": server_info.get("version"),
                "max_connections": getattr(settings, 'MONGODB_MAX_CONNECTIONS', 100),
                "database_name": self.database.name
            }
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            health_status["error"] = str(e)
        
        return health_status
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get database collection statistics"""
        try:
            stats = {}
            collections = await self.database.list_collection_names()
            
            for collection_name in collections:
                collection = self.database[collection_name]
                count = await collection.count_documents({})
                stats[collection_name] = {
                    "document_count": count,
                    "indexes": await collection.list_indexes().to_list(None)
                }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    async def close(self) -> None:
        """Close MongoDB connections"""
        try:
            if self.client:
                self.client.close()
            if self.sync_client:
                self.sync_client.close()
            
            self._is_initialized = False
            logger.info("MongoDB connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing MongoDB connections: {e}")


# Global MongoDB manager instance
_mongodb_manager: Optional[MongoDBManager] = None


async def get_mongodb_manager() -> MongoDBManager:
    """Get or create global MongoDB manager"""
    global _mongodb_manager
    
    if _mongodb_manager is None:
        _mongodb_manager = MongoDBManager()
    
    return _mongodb_manager


async def initialize_mongodb(document_models: List = None) -> MongoDBManager:
    """Initialize MongoDB with document models"""
    manager = await get_mongodb_manager()
    await manager.initialize(document_models)
    return manager


@asynccontextmanager
async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    """Get MongoDB database instance for dependency injection"""
    manager = await get_mongodb_manager()
    database = await manager.get_database()
    yield database


# Convenience function for FastAPI dependency injection
async def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """FastAPI dependency for getting MongoDB database"""
    manager = await get_mongodb_manager()
    return await manager.get_database()
