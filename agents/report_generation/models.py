"""
Data models for the Report Generation Agent.

Defines structures for report creation, formatting, and delivery.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, EmailStr
import json


class ReportType(str, Enum):
    """Types of reports that can be generated."""
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    BREAKING = "breaking"
    CUSTOM = "custom"
    TREND_ANALYSIS = "trend_analysis"
    SUMMARY = "summary"


class ReportStatus(str, Enum):
    """Report generation and delivery status."""
    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    FORMATTING = "formatting"
    READY = "ready"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReportFormat(str, Enum):
    """Report output formats."""
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"
    PDF = "pdf"
    EMAIL = "email"
    JSON = "json"


class ReportSection(str, Enum):
    """Standard report sections."""
    EXECUTIVE_SUMMARY = "executive_summary"
    BREAKING_NEWS = "breaking_news"
    KEY_DEVELOPMENTS = "key_developments" 
    RESEARCH_HIGHLIGHTS = "research_highlights"
    INDUSTRY_ANALYSIS = "industry_analysis"
    FUNDING_NEWS = "funding_news"
    PRODUCT_LAUNCHES = "product_launches"
    REGULATORY_UPDATES = "regulatory_updates"
    TREND_ANALYSIS = "trend_analysis"
    MARKET_IMPACT = "market_impact"
    UPCOMING_EVENTS = "upcoming_events"
    METHODOLOGY = "methodology"


class ArticleSummary(BaseModel):
    """Article summary for inclusion in reports."""
    article_id: UUID
    title: str = Field(..., max_length=200)
    url: str
    source: str
    published_date: datetime
    author: Optional[str] = None
    
    # Analysis scores
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    impact_score: float = Field(..., ge=0.0, le=1.0)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    
    # Content
    summary: str = Field(..., max_length=500)
    key_points: List[str] = Field(default_factory=list, max_items=5)
    entities: List[str] = Field(default_factory=list, max_items=10)
    topics: List[str] = Field(default_factory=list, max_items=5)
    
    # Metadata
    word_count: int = Field(default=0, ge=0)
    reading_time_minutes: int = Field(default=0, ge=0)
    
    @validator('reading_time_minutes', pre=True, always=True)
    def calculate_reading_time(cls, v, values):
        """Calculate reading time based on word count."""
        if 'word_count' in values and values['word_count'] > 0:
            return max(1, values['word_count'] // 200)  # Assume 200 WPM
        return v


class ReportSectionData(BaseModel):
    """Data for a specific report section."""
    section_type: ReportSection
    title: str
    content: str = Field(default="", description="Main section content")
    articles: List[ArticleSummary] = Field(default_factory=list)
    
    # Section statistics
    article_count: int = Field(default=0, ge=0)
    avg_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    avg_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Section metadata
    priority: int = Field(default=5, ge=1, le=10, description="Display priority")
    include_charts: bool = Field(default=False)
    chart_data: Optional[Dict[str, Any]] = Field(None, description="Data for visualizations")
    
    # Custom formatting
    template_name: Optional[str] = Field(None, description="Custom template")
    styling: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('article_count', pre=True, always=True)
    def update_article_count(cls, v, values):
        """Update article count based on articles list."""
        if 'articles' in values:
            return len(values['articles'])
        return v
    
    @validator('avg_relevance', 'avg_quality', pre=True, always=True)
    def calculate_averages(cls, v, values, field):
        """Calculate average scores from articles."""
        if 'articles' in values and values['articles']:
            if field.name == 'avg_relevance':
                return sum(a.relevance_score for a in values['articles']) / len(values['articles'])
            elif field.name == 'avg_quality':
                return sum(a.quality_score for a in values['articles']) / len(values['articles'])
        return v


class TrendData(BaseModel):
    """Trend analysis data."""
    trend_name: str
    trend_type: str = Field(..., description="Type of trend (topic, sentiment, etc.)")
    current_value: float
    previous_value: float
    change_percentage: float
    change_direction: str = Field(..., pattern="^(up|down|stable)$")
    
    # Trend details
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    time_period: str = Field(..., description="Time period for trend analysis")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    
    # Context
    description: str = Field(..., max_length=200)
    implications: List[str] = Field(default_factory=list, max_items=3)
    supporting_articles: List[UUID] = Field(default_factory=list)
    
    @validator('change_percentage', pre=True, always=True)
    def calculate_change(cls, v, values):
        """Calculate percentage change."""
        if 'current_value' in values and 'previous_value' in values:
            current = values['current_value']
            previous = values['previous_value']
            if previous != 0:
                return ((current - previous) / previous) * 100
        return v
    
    @validator('change_direction', pre=True, always=True)
    def determine_direction(cls, v, values):
        """Determine trend direction."""
        if 'change_percentage' in values:
            change = values['change_percentage']
            if change > 2:
                return "up"
            elif change < -2:
                return "down"
            else:
                return "stable"
        return v


class ReportMetadata(BaseModel):
    """Report metadata and generation information."""
    report_id: UUID = Field(default_factory=uuid4)
    report_type: ReportType
    title: str
    subtitle: Optional[str] = None
    
    # Time period
    period_start: datetime
    period_end: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Content statistics
    total_articles: int = Field(default=0, ge=0)
    sources_covered: int = Field(default=0, ge=0)
    avg_relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    avg_quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Generation details
    generation_model: str = Field(default="gpt-4o-mini")
    generation_time: float = Field(default=0.0, ge=0.0, description="Generation time in seconds")
    generation_cost: float = Field(default=0.0, ge=0.0, description="Cost in USD")
    template_version: str = Field(default="1.0")
    
    # Quality metrics
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    readability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Delivery information
    status: ReportStatus = Field(default=ReportStatus.PENDING)
    recipients: List[EmailStr] = Field(default_factory=list)
    delivery_scheduled: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivery_attempts: int = Field(default=0, ge=0)
    delivery_errors: List[str] = Field(default_factory=list)


class Report(BaseModel):
    """Complete report with all sections and metadata."""
    metadata: ReportMetadata
    sections: List[ReportSectionData] = Field(default_factory=list)
    trends: List[TrendData] = Field(default_factory=list)
    
    # Generated content
    executive_summary: str = Field(default="", max_length=1000)
    key_insights: List[str] = Field(default_factory=list, max_items=10)
    recommendations: List[str] = Field(default_factory=list, max_items=5)
    
    # Formatted outputs
    html_content: Optional[str] = None
    markdown_content: Optional[str] = None
    text_content: Optional[str] = None
    
    # Attachments and resources
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    external_links: List[str] = Field(default_factory=list)
    
    @property
    def total_word_count(self) -> int:
        """Calculate total word count across all sections."""
        total = len(self.executive_summary.split())
        for section in self.sections:
            total += len(section.content.split())
        return total
    
    @property
    def estimated_reading_time(self) -> int:
        """Estimate reading time in minutes."""
        return max(1, self.total_word_count // 200)
    
    @property
    def section_by_type(self) -> Dict[ReportSection, ReportSectionData]:
        """Get sections indexed by type."""
        return {section.section_type: section for section in self.sections}
    
    @property
    def top_articles(self) -> List[ArticleSummary]:
        """Get top articles across all sections by relevance."""
        all_articles = []
        for section in self.sections:
            all_articles.extend(section.articles)
        
        # Remove duplicates and sort by relevance
        seen_ids = set()
        unique_articles = []
        for article in all_articles:
            if article.article_id not in seen_ids:
                seen_ids.add(article.article_id)
                unique_articles.append(article)
        
        return sorted(unique_articles, key=lambda a: a.relevance_score, reverse=True)[:10]


class ReportGenerationRequest(BaseModel):
    """Request for report generation."""
    report_type: ReportType
    title: Optional[str] = None
    subtitle: Optional[str] = None
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    # Content filters
    min_relevance_score: float = Field(default=0.7, ge=0.0, le=1.0)
    min_quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    max_articles_per_section: int = Field(default=10, ge=1, le=50)
    
    # Section configuration
    included_sections: List[ReportSection] = Field(default_factory=lambda: [
        ReportSection.EXECUTIVE_SUMMARY,
        ReportSection.KEY_DEVELOPMENTS,
        ReportSection.RESEARCH_HIGHLIGHTS,
        ReportSection.INDUSTRY_ANALYSIS
    ])
    
    # Output configuration
    output_formats: List[ReportFormat] = Field(default_factory=lambda: [ReportFormat.HTML, ReportFormat.EMAIL])
    include_trends: bool = Field(default=True)
    include_charts: bool = Field(default=False)
    include_full_articles: bool = Field(default=False)
    
    # Delivery options
    recipients: List[EmailStr] = Field(default_factory=list)
    schedule_delivery: Optional[datetime] = None
    send_immediately: bool = Field(default=False)
    
    # Generation options
    max_generation_cost: float = Field(default=0.50, ge=0.01, le=5.0)
    generation_model: str = Field(default="gpt-4o-mini")
    template_name: Optional[str] = None
    custom_styling: Dict[str, Any] = Field(default_factory=dict)


class ReportGenerationResponse(BaseModel):
    """Response from report generation."""
    success: bool
    report: Optional[Report] = None
    error_message: Optional[str] = None
    
    # Generation metrics
    processing_time: float = Field(..., description="Total processing time in seconds")
    generation_cost: float = Field(..., description="Actual generation cost")
    articles_processed: int = Field(default=0, description="Number of articles processed")
    sections_generated: int = Field(default=0, description="Number of sections generated")
    
    # Quality indicators
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    content_quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Next steps
    delivery_scheduled: bool = Field(default=False)
    delivery_time: Optional[datetime] = None
    warnings: List[str] = Field(default_factory=list)


class ReportDeliveryRequest(BaseModel):
    """Request for report delivery."""
    report_id: UUID
    recipients: List[EmailStr]
    delivery_time: Optional[datetime] = None
    
    # Email configuration
    email_subject: Optional[str] = None
    custom_message: Optional[str] = None
    include_attachments: bool = Field(default=True)
    
    # Delivery options
    retry_on_failure: bool = Field(default=True)
    max_retries: int = Field(default=3, ge=1, le=10)
    notification_webhook: Optional[str] = None


class ReportDeliveryResponse(BaseModel):
    """Response from report delivery."""
    success: bool
    delivered_count: int = Field(default=0, description="Number of successful deliveries")
    failed_count: int = Field(default=0, description="Number of failed deliveries")
    
    # Delivery details
    delivery_id: UUID = Field(default_factory=uuid4)
    delivered_at: Optional[datetime] = None
    delivery_errors: List[str] = Field(default_factory=list)
    
    # Metrics
    delivery_time: float = Field(default=0.0, description="Delivery time in seconds")
    email_size_kb: float = Field(default=0.0, description="Email size in KB")


class ReportTemplate(BaseModel):
    """Template configuration for report generation."""
    template_name: str = Field(..., pattern="^[a-zA-Z0-9_-]+$")
    template_version: str = Field(default="1.0")
    description: str
    
    # Template structure
    sections_order: List[ReportSection]
    section_templates: Dict[ReportSection, str] = Field(default_factory=dict)
    
    # Styling
    css_styles: Optional[str] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    
    # Configuration
    default_settings: Dict[str, Any] = Field(default_factory=dict)
    supported_formats: List[ReportFormat] = Field(default_factory=lambda: [ReportFormat.HTML, ReportFormat.EMAIL])
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system")
    tags: List[str] = Field(default_factory=list)


class ReportAnalytics(BaseModel):
    """Analytics data for report performance."""
    report_id: UUID
    
    # Delivery metrics
    open_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    click_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    read_time_seconds: float = Field(default=0.0, ge=0.0)
    
    # Engagement metrics
    links_clicked: Dict[str, int] = Field(default_factory=dict)
    sections_viewed: Dict[ReportSection, int] = Field(default_factory=dict)
    feedback_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    
    # Technical metrics
    delivery_time_seconds: float = Field(default=0.0, ge=0.0)
    email_size_kb: float = Field(default=0.0, ge=0.0)
    rendering_issues: List[str] = Field(default_factory=list)
    
    # Timestamps
    sent_at: datetime
    first_opened_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None


# Export all models
__all__ = [
    "ReportType",
    "ReportStatus", 
    "ReportFormat",
    "ReportSection",
    "ArticleSummary",
    "ReportSectionData",
    "TrendData",
    "ReportMetadata",
    "Report",
    "ReportGenerationRequest",
    "ReportGenerationResponse",
    "ReportDeliveryRequest",
    "ReportDeliveryResponse",
    "ReportTemplate",
    "ReportAnalytics",
]