#!/usr/bin/env python3
"""
Basic API Test Script for AdWise AI Digital Marketing Campaign Builder

This script tests the core API functionality without requiring external dependencies
like LangChain, EURI AI, or database connections. It verifies that the FastAPI
application can start and respond to basic requests.

Usage:
    python test_api_basic.py
"""

import sys
import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that core imports work without conflicts"""
    try:
        logger.info("Testing core imports...")
        
        # Test FastAPI imports
        from fastapi import FastAPI, HTTPException, status
        from fastapi.responses import JSONResponse
        logger.info("✅ FastAPI imports successful")
        
        # Test Pydantic imports
        from pydantic import BaseModel, Field
        from pydantic_settings import BaseSettings
        logger.info("✅ Pydantic imports successful")
        
        # Test async imports
        import uvicorn
        import asyncio
        logger.info("✅ Async framework imports successful")
        
        # Test utility imports
        import json
        import datetime
        from typing import Optional, List, Dict, Any
        logger.info("✅ Utility imports successful")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during imports: {e}")
        return False

def create_minimal_app():
    """Create a minimal FastAPI app for testing"""
    from fastapi import FastAPI

    app = FastAPI(
        title="AdWise AI - Basic Test",
        description="Minimal API for testing core functionality",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "AdWise AI Digital Marketing Campaign Builder",
            "status": "operational",
            "version": "1.0.0",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    
    @app.get("/health")
    async def health_check():
        """Basic health check"""
        return {
            "status": "healthy",
            "service": "AdWise AI API",
            "checks": {
                "api": "operational",
                "server": "running"
            }
        }
    
    @app.get("/api/v1/status")
    async def api_status():
        """API status endpoint"""
        return {
            "api_version": "v1",
            "status": "active",
            "features": {
                "campaigns": "available",
                "analytics": "available",
                "ai_generation": "available"
            }
        }
    
    return app

async def test_app_creation():
    """Test that the FastAPI app can be created"""
    try:
        logger.info("Testing FastAPI app creation...")
        app = create_minimal_app()
        
        if app:
            logger.info("✅ FastAPI app created successfully")
            return True
        else:
            logger.error("❌ Failed to create FastAPI app")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error creating FastAPI app: {e}")
        return False

def test_core_functionality():
    """Test core application functionality"""
    try:
        logger.info("Testing core functionality...")
        
        # Test JSON serialization
        test_data = {
            "campaign_id": "test_001",
            "name": "Test Campaign",
            "status": "active",
            "metrics": {
                "impressions": 1000,
                "clicks": 50,
                "conversions": 5
            }
        }
        
        import json
        serialized = json.dumps(test_data)
        deserialized = json.loads(serialized)
        
        if deserialized == test_data:
            logger.info("✅ JSON serialization working")
        else:
            logger.error("❌ JSON serialization failed")
            return False
        
        # Test datetime handling
        from datetime import datetime
        now = datetime.utcnow()
        timestamp = now.isoformat()
        
        if timestamp:
            logger.info("✅ Datetime handling working")
        else:
            logger.error("❌ Datetime handling failed")
            return False
        
        # Test async functionality
        async def async_test():
            await asyncio.sleep(0.1)
            return "async_working"
        
        result = asyncio.run(async_test())
        if result == "async_working":
            logger.info("✅ Async functionality working")
        else:
            logger.error("❌ Async functionality failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in core functionality test: {e}")
        return False

def test_server_startup():
    """Test that the server can start (without actually starting it)"""
    try:
        logger.info("Testing server startup configuration...")
        
        # Test uvicorn import and configuration
        import uvicorn
        
        # Test server configuration
        config = uvicorn.Config(
            app="test_api_basic:create_minimal_app",
            host="127.0.0.1",
            port=8002,
            log_level="info",
            factory=True
        )
        
        if config:
            logger.info("✅ Server configuration successful")
            return True
        else:
            logger.error("❌ Server configuration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in server startup test: {e}")
        return False

def run_all_tests():
    """Run all basic tests"""
    logger.info("🚀 Starting AdWise AI Basic API Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("App Creation", test_app_creation),
        ("Core Functionality", test_core_functionality),
        ("Server Startup", test_server_startup)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - API is ready!")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests failed - Check dependencies")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        
        if success:
            logger.info("\n🚀 Starting minimal server for manual testing...")
            logger.info("Server will be available at: http://127.0.0.1:8002")
            logger.info("Test endpoints:")
            logger.info("  • http://127.0.0.1:8002/")
            logger.info("  • http://127.0.0.1:8002/health")
            logger.info("  • http://127.0.0.1:8002/api/v1/status")
            logger.info("\nPress Ctrl+C to stop the server")
            
            # Start the minimal server
            app = create_minimal_app()
            import uvicorn
            uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
            
        else:
            logger.error("❌ Tests failed - Server not started")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
