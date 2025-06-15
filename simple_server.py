#!/usr/bin/env python3
"""
Simple server startup script for AdWise AI
Bypasses database initialization for quick testing
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AdWise AI Campaign Builder",
    description="AI-powered digital marketing campaign builder",
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

# Health check endpoint


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AdWise AI Campaign Builder",
        "version": "1.0.0",
        "environment": "development"
    }

# Root endpoint


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AdWise AI Campaign Builder",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_prefix": "/api/v1",
        "environment": "development"
    }

if __name__ == "__main__":
    print("🚀 Starting AdWise AI Simple Server on port 8001")
    uvicorn.run(
        "simple_server:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
