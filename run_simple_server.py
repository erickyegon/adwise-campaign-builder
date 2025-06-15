#!/usr/bin/env python3
"""
Simple Development Server for AdWise AI - No Database Dependencies
Runs the server without requiring MongoDB/Redis connections for testing
"""

import os
import sys
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Set environment variable to skip database initialization
os.environ['SKIP_DATABASE_INIT'] = 'true'
os.environ['ENVIRONMENT'] = 'development'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def simple_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Simple lifespan manager that skips database initialization
    """
    print("🚀 Starting AdWise AI Campaign Builder - Simple Mode")
    print("⚠️ Running without database connections for testing")
    
    # Startup
    try:
        print("✅ Application started successfully")
        yield
    finally:
        # Shutdown
        print("🔄 Shutting down AdWise AI Campaign Builder...")
        print("✅ Application shutdown complete")


def create_simple_app() -> FastAPI:
    """
    Create FastAPI application without database dependencies
    """
    app = FastAPI(
        title=settings.app.APP_NAME,
        description=settings.app.APP_DESCRIPTION + " (Simple Mode - No Database)",
        version=settings.app.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=simple_lifespan,
        debug=True,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add basic routes
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": f"Welcome to {settings.app.APP_NAME} (Simple Mode)",
            "version": settings.app.APP_VERSION,
            "mode": "development_simple",
            "docs_url": "/docs",
            "status": "running_without_database"
        }

    @app.get("/health", tags=["Health"])
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "mode": "simple_development",
            "database": "skipped",
            "timestamp": "2025-06-15T19:36:00Z"
        }

    # Import and add API routes (without database dependencies)
    try:
        from app.api.v1.router import api_router
        app.include_router(api_router, prefix="/api/v1")
        print("✅ API routes loaded successfully")
    except Exception as e:
        print(f"⚠️ Some API routes may not be available: {e}")

    return app


async def main():
    """Main server runner"""
    print("🎯 AdWise AI Simple Development Server")
    print("=" * 60)
    print("Running in simple mode without database dependencies")
    print("=" * 60)

    # Create the app
    app = create_simple_app()

    # Server configuration
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8004,  # Use different port to avoid conflicts
        log_level="info",
        reload=False,
        workers=1,
        access_log=True,
    )

    # Display server info
    print("\n📊 Server Information:")
    print(f"🌐 URL: http://127.0.0.1:8004")
    print(f"📚 API Docs: http://127.0.0.1:8004/docs")
    print(f"💚 Health Check: http://127.0.0.1:8004/health")
    print(f"🔧 Mode: Simple Development (No Database)")
    print("\n🚀 Starting server...")
    print("Press Ctrl+C to stop\n")

    # Start server
    server = uvicorn.Server(config)
    try:
        await server.serve()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
