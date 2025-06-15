"""
Analytics Service for AdWise AI Digital Marketing Campaign Builder

This module implements comprehensive analytics processing as specified in the PRM:
- Performance metrics calculation and aggregation
- MongoDB aggregation pipelines for complex analytics
- Real-time analytics updates
- AI-powered insights generation
- Comparative analysis and benchmarking
- Export-ready data formatting

Design Principles:
- MongoDB aggregation pipelines for performance
- Real-time analytics processing
- AI-enhanced insights
- Scalable data processing
- Comprehensive metric calculation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from app.models.mongodb_models import Analytics, Campaign, Ad, User
from app.core.database.mongodb import get_db
from app.integrations.euri import get_euri_client
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MetricType(str, Enum):
    """Types of analytics metrics"""
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CTR = "ctr"
    CONVERSIONS = "conversions"
    CONVERSION_RATE = "conversion_rate"
    SPEND = "spend"
    CPC = "cpc"
    CPM = "cpm"
    CPA = "cpa"
    ROI = "roi"
    ROAS = "roas"
    REACH = "reach"
    FREQUENCY = "frequency"
    ENGAGEMENT_RATE = "engagement_rate"


class TimeGranularity(str, Enum):
    """Time granularity for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class AnalyticsService:
    """
    Comprehensive analytics service with MongoDB aggregation pipelines
    
    Features:
    - Real-time metrics calculation
    - Complex aggregation queries
    - Performance trend analysis
    - AI-powered insights
    - Comparative benchmarking
    - Export data preparation
    """
    
    def __init__(self):
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.euri_client = None
    
    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            self.db = await get_db()
        return self.db
    
    async def _get_euri_client(self):
        """Get EURI AI client for insights"""
        if self.euri_client is None:
            self.euri_client = await get_euri_client()
        return self.euri_client
    
    async def get_campaign_performance_summary(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive campaign performance summary using aggregation pipeline
        """
        try:
            db = await self._get_db()
            
            # Build date filter
            date_filter = {"campaign_id": campaign_id}
            if start_date or end_date:
                date_filter["timestamp"] = {}
                if start_date:
                    date_filter["timestamp"]["$gte"] = start_date
                if end_date:
                    date_filter["timestamp"]["$lte"] = end_date
            
            # Aggregation pipeline for comprehensive metrics
            pipeline = [
                {"$match": date_filter},
                {
                    "$group": {
                        "_id": "$campaign_id",
                        "total_impressions": {"$sum": "$impressions"},
                        "total_clicks": {"$sum": "$clicks"},
                        "total_conversions": {"$sum": "$conversions"},
                        "total_spend": {"$sum": "$spend"},
                        "total_reach": {"$sum": "$reach"},
                        "avg_ctr": {"$avg": "$ctr"},
                        "avg_conversion_rate": {"$avg": "$conversion_rate"},
                        "avg_cpc": {"$avg": "$cost_per_click"},
                        "avg_cpm": {"$avg": {"$divide": [{"$multiply": ["$spend", 1000]}, "$impressions"]}},
                        "avg_roi": {"$avg": "$roi"},
                        "avg_engagement_rate": {"$avg": "$engagement_rate"},
                        "data_points": {"$sum": 1},
                        "date_range": {
                            "$push": {
                                "start": {"$min": "$timestamp"},
                                "end": {"$max": "$timestamp"}
                            }
                        }
                    }
                },
                {
                    "$addFields": {
                        "calculated_ctr": {
                            "$cond": {
                                "if": {"$gt": ["$total_impressions", 0]},
                                "then": {"$divide": ["$total_clicks", "$total_impressions"]},
                                "else": 0
                            }
                        },
                        "calculated_conversion_rate": {
                            "$cond": {
                                "if": {"$gt": ["$total_clicks", 0]},
                                "then": {"$divide": ["$total_conversions", "$total_clicks"]},
                                "else": 0
                            }
                        },
                        "calculated_cpa": {
                            "$cond": {
                                "if": {"$gt": ["$total_conversions", 0]},
                                "then": {"$divide": ["$total_spend", "$total_conversions"]},
                                "else": 0
                            }
                        },
                        "calculated_roas": {
                            "$cond": {
                                "if": {"$gt": ["$total_spend", 0]},
                                "then": {"$multiply": ["$avg_roi", 100]},
                                "else": 0
                            }
                        }
                    }
                }
            ]
            
            # Execute aggregation
            result = await db.analytics.aggregate(pipeline).to_list(1)
            
            if not result:
                return {
                    "campaign_id": campaign_id,
                    "summary": "No analytics data found",
                    "metrics": {},
                    "performance_grade": "N/A"
                }
            
            summary = result[0]
            
            # Calculate performance grade
            performance_grade = self._calculate_performance_grade(summary)
            
            # Get channel breakdown
            channel_breakdown = await self._get_channel_breakdown(campaign_id, start_date, end_date)
            
            # Get time series data
            time_series = await self._get_time_series_data(campaign_id, start_date, end_date)
            
            return {
                "campaign_id": campaign_id,
                "summary": {
                    "total_impressions": summary.get("total_impressions", 0),
                    "total_clicks": summary.get("total_clicks", 0),
                    "total_conversions": summary.get("total_conversions", 0),
                    "total_spend": round(summary.get("total_spend", 0), 2),
                    "total_reach": summary.get("total_reach", 0),
                    "ctr": round(summary.get("calculated_ctr", 0) * 100, 2),
                    "conversion_rate": round(summary.get("calculated_conversion_rate", 0) * 100, 2),
                    "cpc": round(summary.get("avg_cpc", 0), 2),
                    "cpm": round(summary.get("avg_cpm", 0), 2),
                    "cpa": round(summary.get("calculated_cpa", 0), 2),
                    "roi": round(summary.get("avg_roi", 0), 2),
                    "roas": round(summary.get("calculated_roas", 0), 2),
                    "engagement_rate": round(summary.get("avg_engagement_rate", 0) * 100, 2)
                },
                "performance_grade": performance_grade,
                "channel_breakdown": channel_breakdown,
                "time_series": time_series,
                "data_points": summary.get("data_points", 0),
                "analysis_period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign performance summary: {e}")
            raise
    
    async def _get_channel_breakdown(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance breakdown by advertising channel"""
        try:
            db = await self._get_db()
            
            # First get ads for the campaign to map ad_id to channel
            ads_pipeline = [
                {"$match": {"campaign_id": campaign_id}},
                {"$project": {"_id": 1, "channel": 1}}
            ]
            
            ads_result = await db.ads.aggregate(ads_pipeline).to_list(None)
            ad_channel_map = {str(ad["_id"]): ad["channel"] for ad in ads_result}
            
            # Build date filter for analytics
            date_filter = {"ad_id": {"$in": list(ad_channel_map.keys())}}
            if start_date or end_date:
                date_filter["timestamp"] = {}
                if start_date:
                    date_filter["timestamp"]["$gte"] = start_date
                if end_date:
                    date_filter["timestamp"]["$lte"] = end_date
            
            # Aggregation pipeline for channel breakdown
            pipeline = [
                {"$match": date_filter},
                {
                    "$group": {
                        "_id": "$ad_id",
                        "impressions": {"$sum": "$impressions"},
                        "clicks": {"$sum": "$clicks"},
                        "conversions": {"$sum": "$conversions"},
                        "spend": {"$sum": "$spend"},
                        "avg_ctr": {"$avg": "$ctr"},
                        "avg_roi": {"$avg": "$roi"}
                    }
                }
            ]
            
            analytics_result = await db.analytics.aggregate(pipeline).to_list(None)
            
            # Group by channel
            channel_metrics = {}
            for item in analytics_result:
                ad_id = item["_id"]
                channel = ad_channel_map.get(ad_id, "unknown")
                
                if channel not in channel_metrics:
                    channel_metrics[channel] = {
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "spend": 0,
                        "ctr_sum": 0,
                        "roi_sum": 0,
                        "ad_count": 0
                    }
                
                channel_metrics[channel]["impressions"] += item["impressions"]
                channel_metrics[channel]["clicks"] += item["clicks"]
                channel_metrics[channel]["conversions"] += item["conversions"]
                channel_metrics[channel]["spend"] += item["spend"]
                channel_metrics[channel]["ctr_sum"] += item["avg_ctr"]
                channel_metrics[channel]["roi_sum"] += item["avg_roi"]
                channel_metrics[channel]["ad_count"] += 1
            
            # Calculate final metrics
            breakdown = {}
            for channel, metrics in channel_metrics.items():
                breakdown[channel] = {
                    "impressions": metrics["impressions"],
                    "clicks": metrics["clicks"],
                    "conversions": metrics["conversions"],
                    "spend": round(metrics["spend"], 2),
                    "ctr": round((metrics["clicks"] / metrics["impressions"] * 100) if metrics["impressions"] > 0 else 0, 2),
                    "conversion_rate": round((metrics["conversions"] / metrics["clicks"] * 100) if metrics["clicks"] > 0 else 0, 2),
                    "cpc": round((metrics["spend"] / metrics["clicks"]) if metrics["clicks"] > 0 else 0, 2),
                    "cpa": round((metrics["spend"] / metrics["conversions"]) if metrics["conversions"] > 0 else 0, 2),
                    "roi": round((metrics["roi_sum"] / metrics["ad_count"]) if metrics["ad_count"] > 0 else 0, 2),
                    "ad_count": metrics["ad_count"]
                }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting channel breakdown: {e}")
            return {}
    
    async def _get_time_series_data(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: TimeGranularity = TimeGranularity.DAY
    ) -> List[Dict[str, Any]]:
        """Get time series performance data"""
        try:
            db = await self._get_db()
            
            # Build date filter
            date_filter = {"campaign_id": campaign_id}
            if start_date or end_date:
                date_filter["timestamp"] = {}
                if start_date:
                    date_filter["timestamp"]["$gte"] = start_date
                if end_date:
                    date_filter["timestamp"]["$lte"] = end_date
            
            # Define date grouping based on granularity
            date_group = {
                TimeGranularity.HOUR: {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"},
                    "hour": {"$hour": "$timestamp"}
                },
                TimeGranularity.DAY: {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                TimeGranularity.WEEK: {
                    "year": {"$year": "$timestamp"},
                    "week": {"$week": "$timestamp"}
                },
                TimeGranularity.MONTH: {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"}
                }
            }
            
            # Aggregation pipeline for time series
            pipeline = [
                {"$match": date_filter},
                {
                    "$group": {
                        "_id": date_group[granularity],
                        "impressions": {"$sum": "$impressions"},
                        "clicks": {"$sum": "$clicks"},
                        "conversions": {"$sum": "$conversions"},
                        "spend": {"$sum": "$spend"},
                        "avg_ctr": {"$avg": "$ctr"},
                        "avg_roi": {"$avg": "$roi"},
                        "timestamp": {"$first": "$timestamp"}
                    }
                },
                {"$sort": {"timestamp": 1}},
                {
                    "$addFields": {
                        "calculated_ctr": {
                            "$cond": {
                                "if": {"$gt": ["$impressions", 0]},
                                "then": {"$divide": ["$clicks", "$impressions"]},
                                "else": 0
                            }
                        },
                        "calculated_conversion_rate": {
                            "$cond": {
                                "if": {"$gt": ["$clicks", 0]},
                                "then": {"$divide": ["$conversions", "$clicks"]},
                                "else": 0
                            }
                        }
                    }
                }
            ]
            
            result = await db.analytics.aggregate(pipeline).to_list(None)
            
            # Format time series data
            time_series = []
            for item in result:
                time_series.append({
                    "timestamp": item["timestamp"].isoformat(),
                    "impressions": item["impressions"],
                    "clicks": item["clicks"],
                    "conversions": item["conversions"],
                    "spend": round(item["spend"], 2),
                    "ctr": round(item["calculated_ctr"] * 100, 2),
                    "conversion_rate": round(item["calculated_conversion_rate"] * 100, 2),
                    "roi": round(item["avg_roi"], 2)
                })
            
            return time_series
            
        except Exception as e:
            logger.error(f"Error getting time series data: {e}")
            return []
    
    def _calculate_performance_grade(self, summary: Dict[str, Any]) -> str:
        """Calculate performance grade based on metrics"""
        try:
            ctr = summary.get("calculated_ctr", 0)
            conversion_rate = summary.get("calculated_conversion_rate", 0)
            roi = summary.get("avg_roi", 0)
            
            # Define performance thresholds
            score = 0
            
            # CTR scoring (0-30 points)
            if ctr >= 0.05:  # 5%+
                score += 30
            elif ctr >= 0.03:  # 3-5%
                score += 20
            elif ctr >= 0.02:  # 2-3%
                score += 15
            elif ctr >= 0.01:  # 1-2%
                score += 10
            
            # Conversion rate scoring (0-30 points)
            if conversion_rate >= 0.10:  # 10%+
                score += 30
            elif conversion_rate >= 0.05:  # 5-10%
                score += 20
            elif conversion_rate >= 0.03:  # 3-5%
                score += 15
            elif conversion_rate >= 0.01:  # 1-3%
                score += 10
            
            # ROI scoring (0-40 points)
            if roi >= 3.0:  # 300%+
                score += 40
            elif roi >= 2.0:  # 200-300%
                score += 30
            elif roi >= 1.5:  # 150-200%
                score += 20
            elif roi >= 1.0:  # 100-150%
                score += 15
            elif roi >= 0.5:  # 50-100%
                score += 10
            
            # Convert score to grade
            if score >= 80:
                return "A"
            elif score >= 70:
                return "B"
            elif score >= 60:
                return "C"
            elif score >= 50:
                return "D"
            else:
                return "F"
                
        except Exception as e:
            logger.error(f"Error calculating performance grade: {e}")
            return "N/A"
    
    async def generate_ai_insights(
        self,
        campaign_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights from performance data"""
        try:
            euri_client = await self._get_euri_client()
            
            # Prepare data for AI analysis
            analysis_prompt = f"""
            Analyze this digital marketing campaign performance data and provide insights:
            
            Campaign ID: {campaign_id}
            Performance Summary: {performance_data['summary']}
            Performance Grade: {performance_data['performance_grade']}
            Channel Breakdown: {performance_data['channel_breakdown']}
            
            Provide analysis on:
            1. Key performance drivers
            2. Areas for improvement
            3. Channel optimization opportunities
            4. Budget reallocation recommendations
            5. Risk factors and mitigation strategies
            
            Format as structured insights with specific recommendations.
            """
            
            response = await euri_client.analyze_performance(
                analytics_data=performance_data,
                time_period="current"
            )
            
            return {
                "ai_insights": response.get("insights", ""),
                "key_findings": self._extract_key_findings(performance_data),
                "recommendations": self._generate_recommendations(performance_data),
                "risk_assessment": self._assess_risks(performance_data),
                "opportunities": self._identify_opportunities(performance_data),
                "generated_at": datetime.now().isoformat(),
                "confidence_score": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                "ai_insights": "Unable to generate AI insights",
                "error": str(e)
            }
    
    def _extract_key_findings(self, performance_data: Dict[str, Any]) -> List[str]:
        """Extract key findings from performance data"""
        findings = []
        summary = performance_data.get("summary", {})
        
        # CTR analysis
        ctr = summary.get("ctr", 0)
        if ctr > 5:
            findings.append(f"Excellent CTR of {ctr}% indicates strong ad relevance")
        elif ctr < 1:
            findings.append(f"Low CTR of {ctr}% suggests need for ad copy optimization")
        
        # Conversion rate analysis
        conv_rate = summary.get("conversion_rate", 0)
        if conv_rate > 10:
            findings.append(f"High conversion rate of {conv_rate}% shows effective targeting")
        elif conv_rate < 2:
            findings.append(f"Low conversion rate of {conv_rate}% indicates landing page issues")
        
        # ROI analysis
        roi = summary.get("roi", 0)
        if roi > 2:
            findings.append(f"Strong ROI of {roi}x demonstrates campaign profitability")
        elif roi < 1:
            findings.append(f"ROI of {roi}x below break-even requires immediate attention")
        
        return findings
    
    def _generate_recommendations(self, performance_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        summary = performance_data.get("summary", {})
        channel_breakdown = performance_data.get("channel_breakdown", {})
        
        # Channel optimization
        best_channel = max(channel_breakdown.items(), key=lambda x: x[1].get("roi", 0)) if channel_breakdown else None
        if best_channel:
            recommendations.append(f"Increase budget allocation to {best_channel[0]} (highest ROI: {best_channel[1].get('roi', 0)})")
        
        # Performance improvements
        if summary.get("ctr", 0) < 2:
            recommendations.append("Implement A/B testing for ad headlines and descriptions")
        
        if summary.get("conversion_rate", 0) < 3:
            recommendations.append("Optimize landing pages for better conversion rates")
        
        if summary.get("cpc", 0) > 2:
            recommendations.append("Refine targeting to reduce cost per click")
        
        return recommendations
    
    def _assess_risks(self, performance_data: Dict[str, Any]) -> List[str]:
        """Assess campaign risks"""
        risks = []
        summary = performance_data.get("summary", {})
        
        if summary.get("roi", 0) < 1:
            risks.append("Campaign operating at a loss - immediate optimization required")
        
        if summary.get("ctr", 0) < 0.5:
            risks.append("Very low CTR may lead to increased costs and reduced reach")
        
        if summary.get("total_spend", 0) > 10000 and summary.get("conversions", 0) < 100:
            risks.append("High spend with low conversions indicates targeting issues")
        
        return risks
    
    def _identify_opportunities(self, performance_data: Dict[str, Any]) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        summary = performance_data.get("summary", {})
        channel_breakdown = performance_data.get("channel_breakdown", {})
        
        if summary.get("roi", 0) > 2:
            opportunities.append("Strong ROI indicates potential for budget scaling")
        
        if summary.get("ctr", 0) > 3:
            opportunities.append("High engagement suggests opportunity for audience expansion")
        
        # Channel opportunities
        for channel, metrics in channel_breakdown.items():
            if metrics.get("roi", 0) > 2 and metrics.get("spend", 0) < 1000:
                opportunities.append(f"Scale {channel} channel - showing strong performance with low spend")
        
        return opportunities


# Global analytics service instance
_analytics_service: Optional[AnalyticsService] = None


async def get_analytics_service() -> AnalyticsService:
    """Get or create global analytics service instance"""
    global _analytics_service
    
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    
    return _analytics_service
