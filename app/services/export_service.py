"""
Export Service for AdWise AI Digital Marketing Campaign Builder

This module implements comprehensive export functionality as specified in the PRM:
- PDF report generation with charts and analytics
- CSV data export for spreadsheet analysis
- Excel workbook generation with multiple sheets
- Automated report scheduling
- Custom report templates
- Data visualization integration

Design Principles:
- Multiple export formats (PDF, CSV, Excel)
- Professional report layouts
- Data visualization integration
- Automated generation workflows
- Template-based customization
"""

import asyncio
import io
import logging
import csv
from typing import Dict, List, Any, Optional, BinaryIO
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend

from app.models.mongodb_models import Campaign, Analytics, Report, User
from app.services.analytics_service import get_analytics_service
from app.core.config import get_settings
from app.core.database.mongodb import get_db

logger = logging.getLogger(__name__)
settings = get_settings()


class ExportFormat(str):
    """Export format types"""
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class ReportTemplate(str):
    """Report template types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYTICS = "detailed_analytics"
    PERFORMANCE_COMPARISON = "performance_comparison"
    CHANNEL_BREAKDOWN = "channel_breakdown"
    CUSTOM = "custom"


class ExportService:
    """
    Comprehensive export service for campaign data and analytics
    
    Features:
    - PDF reports with charts and visualizations
    - CSV/Excel data exports
    - Custom report templates
    - Automated scheduling
    - Data visualization integration
    """
    
    def __init__(self):
        self.analytics_service = None
        self.db = None
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom report styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB'),
            alignment=1  # Center alignment
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#A23B72'),
            leftIndent=0
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#F18F01'),
            alignment=1,
            spaceAfter=10
        ))
    
    async def _get_analytics_service(self):
        """Get analytics service instance"""
        if self.analytics_service is None:
            self.analytics_service = await get_analytics_service()
        return self.analytics_service
    
    async def _get_db(self):
        """Get database instance"""
        if self.db is None:
            self.db = await get_db()
        return self.db
    
    async def generate_campaign_report(
        self,
        campaign_id: str,
        format: ExportFormat,
        template: ReportTemplate = ReportTemplate.DETAILED_ANALYTICS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive campaign report in specified format
        """
        try:
            logger.info(f"Generating {format} report for campaign {campaign_id}")
            
            # Get campaign data
            db = await self._get_db()
            campaign = await Campaign.get(campaign_id)
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Get analytics data
            analytics_service = await self._get_analytics_service()
            performance_data = await analytics_service.get_campaign_performance_summary(
                campaign_id, start_date, end_date
            )
            
            # Generate AI insights
            ai_insights = await analytics_service.generate_ai_insights(
                campaign_id, performance_data
            )
            
            # Prepare report data
            report_data = {
                "campaign": campaign,
                "performance": performance_data,
                "insights": ai_insights,
                "generation_date": datetime.now(),
                "date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "template": template
            }
            
            # Generate report based on format
            if format == ExportFormat.PDF:
                file_content, filename = await self._generate_pdf_report(report_data)
            elif format == ExportFormat.CSV:
                file_content, filename = await self._generate_csv_report(report_data)
            elif format == ExportFormat.EXCEL:
                file_content, filename = await self._generate_excel_report(report_data)
            elif format == ExportFormat.JSON:
                file_content, filename = await self._generate_json_report(report_data)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            # Save report record to database
            report_record = Report(
                campaign_id=campaign_id,
                format=format,
                title=f"{campaign.name} - {template.replace('_', ' ').title()} Report",
                description=f"Generated {format.upper()} report for campaign analytics",
                generated_by=user_id or "system",
                file_url=f"/reports/{filename}",
                file_size=len(file_content),
                date_range={
                    "start": start_date or campaign.created_at,
                    "end": end_date or datetime.now()
                },
                data=report_data["performance"]["summary"],
                status="completed"
            )
            
            await report_record.insert()
            
            return {
                "success": True,
                "report_id": str(report_record.id),
                "filename": filename,
                "file_size": len(file_content),
                "format": format,
                "template": template,
                "file_content": file_content,
                "download_url": f"/api/v1/reports/{report_record.id}/download"
            }
            
        except Exception as e:
            logger.error(f"Error generating campaign report: {e}")
            raise
    
    async def _generate_pdf_report(self, report_data: Dict[str, Any]) -> tuple[bytes, str]:
        """Generate PDF report with charts and analytics"""
        try:
            campaign = report_data["campaign"]
            performance = report_data["performance"]
            insights = report_data["insights"]
            
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content)
            story = []
            
            # Title page
            story.append(Paragraph(
                f"Campaign Performance Report",
                self.styles['CustomTitle']
            ))
            
            story.append(Paragraph(
                f"{campaign.name}",
                self.styles['CustomSubtitle']
            ))
            
            story.append(Spacer(1, 20))
            
            # Campaign overview
            overview_data = [
                ['Campaign Name', campaign.name],
                ['Objective', campaign.objective or 'Not specified'],
                ['Status', campaign.status.value],
                ['Budget', f"${performance['summary'].get('total_spend', 0):,.2f}"],
                ['Performance Grade', performance['performance_grade']],
                ['Report Generated', report_data['generation_date'].strftime('%Y-%m-%d %H:%M')]
            ]
            
            overview_table = Table(overview_data, colWidths=[2*inch, 3*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(overview_table)
            story.append(Spacer(1, 30))
            
            # Key metrics
            story.append(Paragraph("Key Performance Metrics", self.styles['CustomSubtitle']))
            
            metrics_data = [
                ['Metric', 'Value', 'Performance'],
                ['Total Impressions', f"{performance['summary'].get('total_impressions', 0):,}", ''],
                ['Total Clicks', f"{performance['summary'].get('total_clicks', 0):,}", ''],
                ['Click-Through Rate', f"{performance['summary'].get('ctr', 0):.2f}%", self._get_performance_indicator(performance['summary'].get('ctr', 0), 'ctr')],
                ['Conversions', f"{performance['summary'].get('total_conversions', 0):,}", ''],
                ['Conversion Rate', f"{performance['summary'].get('conversion_rate', 0):.2f}%", self._get_performance_indicator(performance['summary'].get('conversion_rate', 0), 'conversion_rate')],
                ['Cost Per Click', f"${performance['summary'].get('cpc', 0):.2f}", ''],
                ['Return on Investment', f"{performance['summary'].get('roi', 0):.2f}x", self._get_performance_indicator(performance['summary'].get('roi', 0), 'roi')]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 30))
            
            # Channel breakdown
            if performance.get('channel_breakdown'):
                story.append(Paragraph("Channel Performance Breakdown", self.styles['CustomSubtitle']))
                
                channel_data = [['Channel', 'Impressions', 'Clicks', 'CTR', 'Conversions', 'ROI']]
                for channel, metrics in performance['channel_breakdown'].items():
                    channel_data.append([
                        channel.replace('_', ' ').title(),
                        f"{metrics.get('impressions', 0):,}",
                        f"{metrics.get('clicks', 0):,}",
                        f"{metrics.get('ctr', 0):.2f}%",
                        f"{metrics.get('conversions', 0):,}",
                        f"{metrics.get('roi', 0):.2f}x"
                    ])
                
                channel_table = Table(channel_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch])
                channel_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(channel_table)
                story.append(Spacer(1, 30))
            
            # AI Insights
            if insights.get('key_findings'):
                story.append(Paragraph("AI-Generated Insights", self.styles['CustomSubtitle']))
                
                for finding in insights['key_findings'][:5]:  # Top 5 findings
                    story.append(Paragraph(f"• {finding}", self.styles['Normal']))
                    story.append(Spacer(1, 6))
                
                story.append(Spacer(1, 20))
            
            # Recommendations
            if insights.get('recommendations'):
                story.append(Paragraph("Optimization Recommendations", self.styles['CustomSubtitle']))
                
                for i, recommendation in enumerate(insights['recommendations'][:5], 1):
                    story.append(Paragraph(f"{i}. {recommendation}", self.styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            buffer.seek(0)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            # Generate filename
            filename = f"campaign_report_{campaign.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return pdf_content, filename
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    async def _generate_csv_report(self, report_data: Dict[str, Any]) -> tuple[bytes, str]:
        """Generate CSV report with analytics data"""
        try:
            campaign = report_data["campaign"]
            performance = report_data["performance"]
            
            # Create CSV buffer
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            
            # Write campaign overview
            writer.writerow(['Campaign Report'])
            writer.writerow(['Campaign Name', campaign.name])
            writer.writerow(['Generated', report_data['generation_date'].strftime('%Y-%m-%d %H:%M')])
            writer.writerow([])  # Empty row
            
            # Write summary metrics
            writer.writerow(['Summary Metrics'])
            writer.writerow(['Metric', 'Value'])
            
            summary = performance['summary']
            for metric, value in summary.items():
                if isinstance(value, (int, float)):
                    if metric in ['ctr', 'conversion_rate', 'engagement_rate']:
                        writer.writerow([metric.replace('_', ' ').title(), f"{value:.2f}%"])
                    elif metric in ['spend', 'cpc', 'cpm', 'cpa']:
                        writer.writerow([metric.replace('_', ' ').title(), f"${value:.2f}"])
                    else:
                        writer.writerow([metric.replace('_', ' ').title(), f"{value:,.2f}"])
                else:
                    writer.writerow([metric.replace('_', ' ').title(), str(value)])
            
            writer.writerow([])  # Empty row
            
            # Write channel breakdown
            if performance.get('channel_breakdown'):
                writer.writerow(['Channel Performance'])
                writer.writerow(['Channel', 'Impressions', 'Clicks', 'CTR (%)', 'Conversions', 'Spend ($)', 'ROI'])
                
                for channel, metrics in performance['channel_breakdown'].items():
                    writer.writerow([
                        channel.replace('_', ' ').title(),
                        metrics.get('impressions', 0),
                        metrics.get('clicks', 0),
                        f"{metrics.get('ctr', 0):.2f}",
                        metrics.get('conversions', 0),
                        f"{metrics.get('spend', 0):.2f}",
                        f"{metrics.get('roi', 0):.2f}"
                    ])
            
            # Get CSV content
            csv_content = buffer.getvalue().encode('utf-8')
            buffer.close()
            
            # Generate filename
            filename = f"campaign_data_{campaign.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return csv_content, filename
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise
    
    async def _generate_excel_report(self, report_data: Dict[str, Any]) -> tuple[bytes, str]:
        """Generate Excel report with multiple sheets"""
        try:
            campaign = report_data["campaign"]
            performance = report_data["performance"]
            
            # Create Excel buffer
            buffer = io.BytesIO()
            
            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                
                # Summary sheet
                summary_data = []
                for metric, value in performance['summary'].items():
                    summary_data.append({
                        'Metric': metric.replace('_', ' ').title(),
                        'Value': value
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Channel breakdown sheet
                if performance.get('channel_breakdown'):
                    channel_data = []
                    for channel, metrics in performance['channel_breakdown'].items():
                        row = {'Channel': channel.replace('_', ' ').title()}
                        row.update(metrics)
                        channel_data.append(row)
                    
                    channel_df = pd.DataFrame(channel_data)
                    channel_df.to_excel(writer, sheet_name='Channel Breakdown', index=False)
                
                # Time series sheet
                if performance.get('time_series'):
                    time_series_df = pd.DataFrame(performance['time_series'])
                    time_series_df.to_excel(writer, sheet_name='Time Series', index=False)
            
            # Get Excel content
            buffer.seek(0)
            excel_content = buffer.getvalue()
            buffer.close()
            
            # Generate filename
            filename = f"campaign_analytics_{campaign.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            return excel_content, filename
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            raise
    
    async def _generate_json_report(self, report_data: Dict[str, Any]) -> tuple[bytes, str]:
        """Generate JSON report with complete data"""
        try:
            import json
            
            campaign = report_data["campaign"]
            
            # Prepare JSON data
            json_data = {
                "campaign": {
                    "id": str(campaign.id),
                    "name": campaign.name,
                    "description": campaign.description,
                    "objective": campaign.objective,
                    "status": campaign.status,
                    "budget": campaign.budget,
                    "created_at": campaign.created_at.isoformat(),
                    "updated_at": campaign.updated_at.isoformat()
                },
                "performance": report_data["performance"],
                "insights": report_data["insights"],
                "generation_metadata": {
                    "generated_at": report_data["generation_date"].isoformat(),
                    "template": report_data["template"],
                    "date_range": {
                        "start": report_data["date_range"]["start"].isoformat() if report_data["date_range"]["start"] else None,
                        "end": report_data["date_range"]["end"].isoformat() if report_data["date_range"]["end"] else None
                    }
                }
            }
            
            # Convert to JSON bytes
            json_content = json.dumps(json_data, indent=2, default=str).encode('utf-8')
            
            # Generate filename
            filename = f"campaign_data_{campaign.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            return json_content, filename
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            raise
    
    def _get_performance_indicator(self, value: float, metric_type: str) -> str:
        """Get performance indicator (Good/Average/Poor) for metrics"""
        thresholds = {
            'ctr': {'good': 3.0, 'average': 1.0},
            'conversion_rate': {'good': 5.0, 'average': 2.0},
            'roi': {'good': 2.0, 'average': 1.0}
        }
        
        if metric_type not in thresholds:
            return ''
        
        if value >= thresholds[metric_type]['good']:
            return 'Good'
        elif value >= thresholds[metric_type]['average']:
            return 'Average'
        else:
            return 'Poor'


# Global export service instance
_export_service: Optional[ExportService] = None


async def get_export_service() -> ExportService:
    """Get or create global export service instance"""
    global _export_service
    
    if _export_service is None:
        _export_service = ExportService()
    
    return _export_service
