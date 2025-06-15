"""
EURI AI Client for AdWise AI Digital Marketing Campaign Builder

This module provides the EURI AI client using the official euriai SDK
as specified in the requirements. It implements the AI Service Layer
from the HLD with the official EURI AI Python SDK.

Features:
- Official EURI AI SDK integration
- LangChain integration support
- Embedding model support
- Content generation for campaigns
- Visual generation capabilities
- Error handling and logging
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from euriai import EuriaiClient
from euriai.langchain_embed import EuriaiEmbeddings
from euriai import EuriaiLangChainLLM

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EURIAPIError(Exception):
    """Base exception for EURI API errors"""
    pass


class EURIAuthenticationError(EURIAPIError):
    """Authentication error with EURI API"""
    pass


class EURIRateLimitError(EURIAPIError):
    """Rate limit exceeded error"""
    pass


class EURIServiceUnavailableError(EURIAPIError):
    """EURI service unavailable error"""
    pass


class EURIClient:
    """
    EURI AI client implementing the AI Service interface from LDL using official SDK

    Provides methods:
    - generateCopy() - Generate ad copy text using EURI AI
    - generateVisual() - Generate visual suggestions
    - optimizeCampaign() - Get optimization recommendations
    - Embedding support for similarity search
    """

    def __init__(self):
        self.api_key = settings.ai.EURI_API_KEY
        self.default_model = settings.ai.DEFAULT_AI_MODEL
        self.content_model = settings.ai.CONTENT_GENERATION_MODEL
        self.analytics_model = settings.ai.ANALYTICS_MODEL

        # Initialize EURI AI clients
        self._content_client: Optional[EuriaiClient] = None
        self._analytics_client: Optional[EuriaiClient] = None
        self._langchain_llm: Optional[EuriaiLangChainLLM] = None
        self._embeddings: Optional[EuriaiEmbeddings] = None

    def _get_content_client(self) -> EuriaiClient:
        """Get or create content generation client"""
        if self._content_client is None:
            self._content_client = EuriaiClient(
                api_key=self.api_key,
                model=self.content_model
            )
        return self._content_client

    def _get_analytics_client(self) -> EuriaiClient:
        """Get or create analytics client"""
        if self._analytics_client is None:
            self._analytics_client = EuriaiClient(
                api_key=self.api_key,
                model=self.analytics_model
            )
        return self._analytics_client

    def _get_langchain_llm(self) -> EuriaiLangChainLLM:
        """Get or create LangChain LLM"""
        if self._langchain_llm is None:
            self._langchain_llm = EuriaiLangChainLLM(
                api_key=self.api_key,
                model=self.content_model,
                temperature=0.7,
                max_tokens=settings.ai.MAX_CONTENT_LENGTH
            )
        return self._langchain_llm

    def _get_embeddings(self) -> EuriaiEmbeddings:
        """Get or create embeddings client"""
        if self._embeddings is None:
            self._embeddings = EuriaiEmbeddings(api_key=self.api_key)
        return self._embeddings

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to EURI API with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            Response data as dictionary

        Raises:
            EURIAPIError: For various API errors
        """
        await self._ensure_client()

        # Check rate limiting
        if self._rate_limit_reset and datetime.now() < self._rate_limit_reset:
            if self._requests_remaining and self._requests_remaining <= 0:
                wait_time = (self._rate_limit_reset -
                             datetime.now()).total_seconds()
                logger.warning(
                    f"Rate limit exceeded, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)

        try:
            logger.debug(f"Making {method} request to {endpoint}")

            response = await self._client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params
            )

            # Update rate limiting info
            self._update_rate_limit_info(response)

            # Handle different response status codes
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Successful response from {endpoint}")
                return result

            elif response.status_code == 401:
                logger.error("EURI API authentication failed")
                raise EURIAuthenticationError(
                    "Invalid API key or authentication failed")

            elif response.status_code == 429:
                logger.warning("EURI API rate limit exceeded")
                if retry_count < self.max_retries:
                    wait_time = self._calculate_retry_delay(retry_count)
                    logger.info(
                        f"Retrying after {wait_time} seconds (attempt {retry_count + 1})")
                    await asyncio.sleep(wait_time)
                    return await self._make_request(method, endpoint, data, params, retry_count + 1)
                else:
                    raise EURIRateLimitError(
                        "Rate limit exceeded and max retries reached")

            elif response.status_code >= 500:
                logger.error(f"EURI API server error: {response.status_code}")
                if retry_count < self.max_retries:
                    wait_time = self._calculate_retry_delay(retry_count)
                    logger.info(
                        f"Retrying after {wait_time} seconds (attempt {retry_count + 1})")
                    await asyncio.sleep(wait_time)
                    return await self._make_request(method, endpoint, data, params, retry_count + 1)
                else:
                    raise EURIServiceUnavailableError(
                        f"EURI API server error: {response.status_code}")

            else:
                logger.error(
                    f"Unexpected EURI API response: {response.status_code}")
                response.raise_for_status()

        except HTTPStatusError as e:
            logger.error(f"HTTP error in EURI API request: {e}")
            raise EURIAPIError(f"HTTP error: {e}")

        except RequestError as e:
            logger.error(f"Request error in EURI API: {e}")
            if retry_count < self.max_retries:
                wait_time = self._calculate_retry_delay(retry_count)
                logger.info(
                    f"Retrying after {wait_time} seconds (attempt {retry_count + 1})")
                await asyncio.sleep(wait_time)
                return await self._make_request(method, endpoint, data, params, retry_count + 1)
            else:
                raise EURIAPIError(
                    f"Request failed after {self.max_retries} retries: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in EURI API request: {e}")
            raise EURIAPIError(f"Unexpected error: {e}")

    def _update_rate_limit_info(self, response: Response) -> None:
        """Update rate limiting information from response headers"""
        try:
            if "X-RateLimit-Remaining" in response.headers:
                self._requests_remaining = int(
                    response.headers["X-RateLimit-Remaining"])

            if "X-RateLimit-Reset" in response.headers:
                reset_timestamp = int(response.headers["X-RateLimit-Reset"])
                self._rate_limit_reset = datetime.fromtimestamp(
                    reset_timestamp)
        except (ValueError, KeyError) as e:
            logger.debug(f"Could not parse rate limit headers: {e}")

    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate exponential backoff delay"""
        base_delay = 1.0
        max_delay = 60.0
        delay = min(base_delay * (2 ** retry_count), max_delay)
        return delay

    # Core AI Service methods as per LDL interface

    async def generate_copy(
        self,
        prompt: str,
        ad_type: str,
        channel: str,
        target_audience: Optional[Dict[str, Any]] = None,
        brand_guidelines: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate ad copy using EURI API (generateCopy from LDL)

        Args:
            prompt: Content generation prompt
            ad_type: Type of ad (text, image, video, etc.)
            channel: Advertising channel (google_ads, facebook_ads, etc.)
            target_audience: Target audience specifications
            brand_guidelines: Brand guidelines and tone
            **kwargs: Additional parameters

        Returns:
            Generated content response
        """
        data = {
            "prompt": prompt,
            "ad_type": ad_type,
            "channel": channel,
            "target_audience": target_audience or {},
            "brand_guidelines": brand_guidelines or {},
            "max_length": kwargs.get("max_length", settings.ai.MAX_CONTENT_LENGTH),
            "creativity": kwargs.get("creativity", 0.7),
            "tone": kwargs.get("tone", "professional"),
            **kwargs
        }

        logger.info(f"Generating copy for {ad_type} ad on {channel}")
        return await self._make_request("POST", "/generate/copy", data)

    async def generate_visual(
        self,
        description: str,
        style: str,
        dimensions: Dict[str, int],
        brand_colors: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate visual suggestions using EURI API (generateVisual from LDL)

        Args:
            description: Visual description prompt
            style: Visual style (modern, classic, minimalist, etc.)
            dimensions: Image dimensions (width, height)
            brand_colors: Brand color palette
            **kwargs: Additional parameters

        Returns:
            Generated visual response
        """
        data = {
            "description": description,
            "style": style,
            "dimensions": dimensions,
            "brand_colors": brand_colors or [],
            "quality": kwargs.get("quality", "high"),
            "format": kwargs.get("format", "png"),
            **kwargs
        }

        logger.info(f"Generating visual with style: {style}")
        return await self._make_request("POST", "/generate/visual", data)

    async def optimize_campaign(
        self,
        campaign_data: Dict[str, Any],
        performance_data: Optional[Dict[str, Any]] = None,
        goals: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get campaign optimization recommendations

        Args:
            campaign_data: Current campaign configuration
            performance_data: Historical performance metrics
            goals: Campaign goals and KPIs
            **kwargs: Additional parameters

        Returns:
            Optimization recommendations
        """
        data = {
            "campaign": campaign_data,
            "performance": performance_data or {},
            "goals": goals or {},
            "optimization_type": kwargs.get("optimization_type", "performance"),
            **kwargs
        }

        logger.info("Generating campaign optimization recommendations")
        return await self._make_request("POST", "/optimize/campaign", data)

    async def analyze_performance(
        self,
        analytics_data: Dict[str, Any],
        time_period: str = "30d",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance with AI insights

        Args:
            analytics_data: Performance analytics data
            time_period: Analysis time period
            **kwargs: Additional parameters

        Returns:
            AI-generated performance insights
        """
        data = {
            "analytics": analytics_data,
            "time_period": time_period,
            "insight_type": kwargs.get("insight_type", "comprehensive"),
            **kwargs
        }

        logger.info(f"Analyzing performance for {time_period} period")
        return await self._make_request("POST", "/analyze/performance", data)

    async def health_check(self) -> Dict[str, Any]:
        """Check EURI API health status"""
        try:
            return await self._make_request("GET", "/health")
        except Exception as e:
            logger.error(f"EURI API health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Global EURI client instance
_euri_client: Optional[EURIClient] = None


async def get_euri_client() -> EURIClient:
    """Get or create global EURI client instance"""
    global _euri_client

    if _euri_client is None:
        _euri_client = EURIClient()

    return _euri_client
