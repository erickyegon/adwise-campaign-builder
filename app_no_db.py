"""
AdWise AI Digital Marketing Campaign Builder - No Database Mode
Modified version that runs without database dependencies for testing
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Set environment to skip database initialization
os.environ['SKIP_DATABASE_INIT'] = 'true'
os.environ['ENVIRONMENT'] = 'development'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan_no_db(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Simplified lifespan manager that skips database initialization
    """
    logger.info("🚀 Starting AdWise AI Campaign Builder - No Database Mode")
    
    try:
        # Skip database initialization
        logger.info("⚠️ Skipping database initialization for testing mode")
        
        # Initialize basic services that don't require database
        logger.info("✅ Basic services initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🔄 Shutting down AdWise AI Campaign Builder...")
        logger.info("✅ Application shutdown complete")


def create_app_no_db() -> FastAPI:
    """
    Create FastAPI application without database dependencies
    """
    
    app = FastAPI(
        title=settings.app.APP_NAME,
        description=settings.app.APP_DESCRIPTION + " (No Database Mode)",
        version=settings.app.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan_no_db,
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

    # Add API routes
    try:
        from app.api.v1.router import api_router
        app.include_router(api_router, prefix="/api/v1")
        logger.info("✅ API routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Some API routes may not be available: {e}")

    # Serve static files if frontend build exists
    frontend_dist = Path("frontend/dist")
    if frontend_dist.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")
        
        @app.get("/")
        async def serve_frontend():
            """Serve the React frontend"""
            return FileResponse(str(frontend_dist / "index.html"))
        
        logger.info("✅ Frontend static files mounted")
    else:
        @app.get("/")
        async def root():
            """Root endpoint when no frontend is available"""
            return {
                "message": f"Welcome to {settings.app.APP_NAME}",
                "version": settings.app.APP_VERSION,
                "mode": "no_database_testing",
                "docs_url": "/docs",
                "api_prefix": "/api/v1",
                "frontend_status": "not_built",
                "note": "Run 'cd frontend && npm run build' to enable frontend"
            }

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "mode": "no_database",
            "database": "skipped",
            "services": "basic_only",
            "timestamp": "2025-06-15"
        }

    # Add some test endpoints
    @app.get("/api/v1/test")
    async def test_endpoint():
        """Test API endpoint"""
        return {
            "message": "API is working!",
            "endpoint": "/api/v1/test",
            "status": "success",
            "mode": "no_database"
        }

    @app.get("/api/v1/langchain/status")
    async def langchain_status():
        """LangChain status endpoint"""
        return {
            "langchain": "available",
            "services": ["campaign_generation", "content_optimization"],
            "status": "ready",
            "mode": "no_database"
        }

    # Test LangChain imports
    @app.get("/api/v1/langchain/test")
    async def test_langchain():
        """Test LangChain functionality"""
        try:
            from langchain_core.prompts import PromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            # Create a simple prompt
            prompt = PromptTemplate.from_template("Hello {name}!")
            result = prompt.format(name="AdWise AI")
            
            return {
                "status": "success",
                "langchain_working": True,
                "test_prompt": result,
                "message": "LangChain is working correctly!",
                "mode": "no_database"
            }
        except Exception as e:
            return {
                "status": "error",
                "langchain_working": False,
                "error": str(e),
                "message": "LangChain test failed",
                "mode": "no_database"
            }

    return app


# Create the application instance
app = create_app_no_db()


if __name__ == "__main__":
    import uvicorn
    
    print("🎯 AdWise AI - No Database Mode")
    print("=" * 50)
    print("🌐 Server will be available at:")
    print("   • Main: http://127.0.0.1:8006")
    print("   • Docs: http://127.0.0.1:8006/docs")
    print("   • Health: http://127.0.0.1:8006/health")
    print("=" * 50)
    print("🚀 Starting server...")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8006,
        log_level="info",
        reload=False
    )
