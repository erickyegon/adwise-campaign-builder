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


class EURIServiceUnavailableError(EURIAPIError):
    """EURI service unavailable error"""
    pass


class AdWiseEURIClient:
    """
    EURI AI client implementing the AI Service interface from LDL using official SDK
    
    Provides methods:
    - generate_copy() - Generate ad copy text using EURI AI
    - generate_visual() - Generate visual suggestions
    - optimize_campaign() - Get optimization recommendations
    - Embedding support for similarity search
    """
    
    def __init__(self):
        self.api_key = settings.ai.EURI_API_KEY
        self.default_model = getattr(settings.ai, 'DEFAULT_AI_MODEL', 'gpt-4.1-nano')
        self.content_model = getattr(settings.ai, 'CONTENT_GENERATION_MODEL', 'gpt-4.1-nano')
        self.analytics_model = getattr(settings.ai, 'ANALYTICS_MODEL', 'gpt-4.1-nano')
        
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
                max_tokens=getattr(settings.ai, 'MAX_CONTENT_LENGTH', 1000)
            )
        return self._langchain_llm
    
    def _get_embeddings(self) -> EuriaiEmbeddings:
        """Get or create embeddings client"""
        if self._embeddings is None:
            self._embeddings = EuriaiEmbeddings(api_key=self.api_key)
        return self._embeddings
    
    def _build_content_prompt(
        self,
        prompt: str,
        ad_type: str,
        channel: str,
        target_audience: Optional[Dict[str, Any]] = None,
        brand_guidelines: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Build comprehensive prompt for content generation"""
        
        # Base prompt structure
        content_prompt = f"""
Generate {ad_type} ad content for {channel} with the following requirements:

Original Request: {prompt}

Ad Type: {ad_type}
Channel: {channel}
"""
        
        # Add target audience information
        if target_audience:
            content_prompt += f"\nTarget Audience: {target_audience}"
        
        # Add brand guidelines
        if brand_guidelines:
            tone = brand_guidelines.get('tone', 'professional')
            content_prompt += f"\nBrand Tone: {tone}"
            
            if 'keywords' in brand_guidelines:
                content_prompt += f"\nKey Terms to Include: {', '.join(brand_guidelines['keywords'])}"
        
        # Add specific requirements based on channel
        channel_requirements = {
            'google_ads': 'Focus on search intent and clear call-to-action. Keep headlines under 30 characters.',
            'facebook_ads': 'Engaging and social. Use emotional hooks and visual descriptions.',
            'instagram_ads': 'Visual-first content. Trendy and authentic tone.',
            'linkedin_ads': 'Professional and business-focused. Highlight value proposition.'
        }
        
        if channel in channel_requirements:
            content_prompt += f"\nChannel Guidelines: {channel_requirements[channel]}"
        
        # Add length constraints
        max_length = kwargs.get('max_length', 300)
        content_prompt += f"\nMaximum Length: {max_length} characters"
        
        content_prompt += "\n\nGenerate compelling ad content that follows these guidelines:"
        
        return content_prompt
    
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
        Generate ad copy using EURI AI (generateCopy from LDL)
        
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
        try:
            client = self._get_content_client()
            
            # Build comprehensive prompt
            full_prompt = self._build_content_prompt(
                prompt, ad_type, channel, target_audience, brand_guidelines, **kwargs
            )
            
            logger.info(f"Generating copy for {ad_type} ad on {channel}")
            
            # Generate content using EURI AI
            response = client.generate_completion(
                prompt=full_prompt,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', getattr(settings.ai, 'MAX_CONTENT_LENGTH', 1000))
            )
            
            return {
                "success": True,
                "content": response,
                "ad_type": ad_type,
                "channel": channel,
                "generated_at": datetime.now().isoformat(),
                "model": self.content_model,
                "parameters": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "max_tokens": kwargs.get('max_tokens', getattr(settings.ai, 'MAX_CONTENT_LENGTH', 1000))
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating copy: {e}")
            raise EURIAPIError(f"Content generation failed: {e}")
    
    async def generate_visual_description(
        self,
        description: str,
        style: str,
        dimensions: Dict[str, int],
        brand_colors: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate visual description using EURI AI
        
        Args:
            description: Visual description prompt
            style: Visual style (modern, classic, minimalist, etc.)
            dimensions: Image dimensions (width, height)
            brand_colors: Brand color palette
            **kwargs: Additional parameters
            
        Returns:
            Generated visual description response
        """
        try:
            client = self._get_content_client()
            
            # Build visual prompt
            visual_prompt = f"""
Generate a detailed visual description for an advertisement with these specifications:

Description: {description}
Style: {style}
Dimensions: {dimensions['width']}x{dimensions['height']}
"""
            
            if brand_colors:
                visual_prompt += f"\nBrand Colors: {', '.join(brand_colors)}"
            
            visual_prompt += """

Create a detailed description that includes:
1. Visual composition and layout
2. Color scheme and mood
3. Typography suggestions
4. Key visual elements
5. Overall aesthetic approach

Focus on creating a description that would help a designer or AI image generator create the perfect ad visual.
"""
            
            logger.info(f"Generating visual description with style: {style}")
            
            response = client.generate_completion(
                prompt=visual_prompt,
                temperature=kwargs.get('temperature', 0.8),
                max_tokens=kwargs.get('max_tokens', 800)
            )
            
            return {
                "success": True,
                "visual_description": response,
                "style": style,
                "dimensions": dimensions,
                "brand_colors": brand_colors,
                "generated_at": datetime.now().isoformat(),
                "model": self.content_model
            }
            
        except Exception as e:
            logger.error(f"Error generating visual description: {e}")
            raise EURIAPIError(f"Visual description generation failed: {e}")
    
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
        try:
            client = self._get_analytics_client()
            
            # Build optimization prompt
            optimization_prompt = f"""
Analyze this digital marketing campaign and provide optimization recommendations:

Campaign Data: {campaign_data}
"""
            
            if performance_data:
                optimization_prompt += f"\nPerformance Data: {performance_data}"
            
            if goals:
                optimization_prompt += f"\nCampaign Goals: {goals}"
            
            optimization_prompt += """

Provide specific recommendations for:
1. Ad copy improvements
2. Targeting optimization
3. Budget allocation
4. Channel performance
5. Creative suggestions
6. A/B testing opportunities

Format the response as actionable insights with priority levels.
"""
            
            logger.info("Generating campaign optimization recommendations")
            
            response = client.generate_completion(
                prompt=optimization_prompt,
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=1500
            )
            
            return {
                "success": True,
                "recommendations": response,
                "campaign_id": campaign_data.get('id'),
                "generated_at": datetime.now().isoformat(),
                "model": self.analytics_model
            }
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            raise EURIAPIError(f"Campaign optimization failed: {e}")
    
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
        try:
            client = self._get_analytics_client()
            
            analysis_prompt = f"""
Analyze this campaign performance data and provide insights:

Analytics Data: {analytics_data}
Time Period: {time_period}

Provide analysis on:
1. Performance trends
2. Key metrics interpretation
3. Areas of concern
4. Success factors
5. Actionable recommendations
6. Comparative benchmarks

Focus on practical insights that can drive campaign improvements.
"""
            
            logger.info(f"Analyzing performance for {time_period} period")
            
            response = client.generate_completion(
                prompt=analysis_prompt,
                temperature=0.4,
                max_tokens=1200
            )
            
            return {
                "success": True,
                "insights": response,
                "time_period": time_period,
                "analyzed_at": datetime.now().isoformat(),
                "model": self.analytics_model
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            raise EURIAPIError(f"Performance analysis failed: {e}")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for similarity search"""
        try:
            embeddings_client = self._get_embeddings()
            return [embeddings_client.embed_query(text) for text in texts]
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise EURIAPIError(f"Embeddings generation failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check EURI AI service health"""
        try:
            client = self._get_content_client()
            # Simple test generation
            test_response = client.generate_completion(
                prompt="Test connection",
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "service": "EURI AI",
                "model": self.content_model,
                "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
            }
        except Exception as e:
            logger.error(f"EURI AI health check failed: {e}")
            return {
                "status": "unhealthy", 
                "service": "EURI AI",
                "error": str(e)
            }


# Global EURI client instance
_euri_client: Optional[AdWiseEURIClient] = None


async def get_euri_client() -> AdWiseEURIClient:
    """Get or create global EURI client instance"""
    global _euri_client
    
    if _euri_client is None:
        _euri_client = AdWiseEURIClient()
    
    return _euri_client
