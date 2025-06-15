#!/usr/bin/env python3
"""
Minimal FastAPI Server for AdWise AI Testing
Guaranteed to work without any database dependencies
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="AdWise AI Campaign Builder",
    description="AI-Powered Digital Marketing Campaign Builder (Minimal Mode)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AdWise AI Campaign Builder",
        "version": "1.0.0",
        "status": "running",
        "mode": "minimal_testing",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AdWise AI Campaign Builder",
        "mode": "minimal",
        "timestamp": "2025-06-15"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test API endpoint"""
    return {
        "message": "API is working!",
        "endpoint": "/api/v1/test",
        "status": "success"
    }

@app.get("/api/v1/langchain/status")
async def langchain_status():
    """LangChain status endpoint"""
    return {
        "langchain": "available",
        "services": ["campaign_generation", "content_optimization"],
        "status": "ready"
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
            "message": "LangChain is working correctly!"
        }
    except Exception as e:
        return {
            "status": "error",
            "langchain_working": False,
            "error": str(e),
            "message": "LangChain test failed"
        }

if __name__ == "__main__":
    print("🎯 Starting AdWise AI Minimal Server")
    print("=" * 50)
    print("🌐 Server will be available at:")
    print("   • Main: http://127.0.0.1:8005")
    print("   • Docs: http://127.0.0.1:8005/docs")
    print("   • Health: http://127.0.0.1:8005/health")
    print("   • Test: http://127.0.0.1:8005/api/v1/test")
    print("=" * 50)
    print("🚀 Starting server...")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8005,
        log_level="info",
        reload=False
    )
