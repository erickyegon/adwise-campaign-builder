"""
EURI API Integration Module for AdWise AI Digital Marketing Campaign Builder

This module provides integration with the EURI API for AI-powered content generation
as specified in the requirements. It handles:
- AI content generation for ad copy
- Visual suggestions and generation
- Campaign optimization recommendations
- Error handling and retry logic

Design Principles:
- Follows the AI Service Layer from HLD
- Implements generateCopy() and generateVisual() from LDL
- Robust error handling and retries
- Async-first for performance
- Comprehensive logging
"""

from .euri_client import AdWiseEURIClient, get_euri_client

__all__ = [
    "AdWiseEURIClient",
    "get_euri_client"
]
