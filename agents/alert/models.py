"""
Data models for the Alert Agent.

Defines structures for breaking news detection, alert prioritization,
and notification management.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, EmailStr
import json


class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts."""
    BREAKING_NEWS = "breaking_news"
    MAJOR_ANNOUNCEMENT = "major_announcement"
    MARKET_MOVING = "market_moving"
    RESEARCH_BREAKTHROUGH = "research_breakthrough"
    FUNDING_NEWS = "funding_news"
    REGULATORY_CHANGE = "regulatory_change"
    PRODUCT_LAUNCH = "product_launch"
    ACQUISITION = "acquisition"
    PERSONNEL_CHANGE = "personnel_change"
    SECURITY_INCIDENT = "security_incident"


class AlertStatus(str, Enum):
    """Alert processing status."""
    PENDING = "pending"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    THROTTLED = "throttled"


class DeliveryChannel(str, Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"


class AlertTrigger(BaseModel):
    """Conditions that triggered an alert."""
    trigger_type: str = Field(..., description="Type of trigger")
    trigger_value: float = Field(..., description="Trigger threshold value")
    actual_value: float = Field(..., description="Actual value that exceeded threshold")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in trigger")
    
    # Trigger context
    keywords_matched: List[str] = Field(default_factory=list)
    entities_detected: List[str] = Field(default_factory=list)
    sentiment_indicators: Dict[str, float] = Field(default_factory=dict)
    market_indicators: Dict[str, Any] = Field(default_factory=dict)
    
    # Timing information
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    article_age_minutes: int = Field(..., ge=0, description="Minutes since article was published")


class AlertContent(BaseModel):
    """Content for the alert notification."""
    headline: str = Field(..., max_length=150, description="Alert headline")
    summary: str = Field(..., max_length=500, description="Alert summary")
    full_description: str = Field(..., max_length=2000, description="Detailed description")
    
    # Key information
    key_points: List[str] = Field(default_factory=list, max_items=5)
    impact_analysis: str = Field(..., max_length=300, description="Why this matters")
    context: str = Field(default="", max_length=400, description="Additional context")
    
    # Rich content
    quotes: List[str] = Field(default_factory=list, max_items=3)
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    related_links: List[str] = Field(default_factory=list, max_items=5)
    
    # Media
    images: List[str] = Field(default_factory=list, max_items=3)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('headline')
    def validate_headline(cls, v):
        """Ensure headline is impactful and clear."""
        if not v or not v.strip():
            raise ValueError("Headline cannot be empty")
        
        # Check for weak words that reduce impact
        weak_words = ['maybe', 'might', 'could', 'possibly', 'potentially']
        if any(word in v.lower() for word in weak_words):
            raise ValueError(f"Headline contains weak language: {v}")
        
        return v.strip()
    
    @validator('key_points')
    def validate_key_points(cls, v):
        """Ensure key points are meaningful."""
        if not v:
            return v
        
        # Remove empty or very short points
        valid_points = [point.strip() for point in v if point.strip() and len(point.strip()) > 10]
        return valid_points[:5]  # Limit to 5 points


class AlertRecipient(BaseModel):
    """Alert recipient configuration."""
    recipient_id: str = Field(..., description="Unique recipient identifier")
    name: str = Field(..., description="Recipient name")
    
    # Contact information
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    slack_user_id: Optional[str] = None
    teams_user_id: Optional[str] = None
    
    # Preferences
    preferred_channels: List[DeliveryChannel] = Field(default_factory=lambda: [DeliveryChannel.EMAIL])
    alert_types: List[AlertType] = Field(default_factory=list, description="Alert types to receive")
    priority_filter: AlertPriority = Field(default=AlertPriority.MEDIUM, description="Minimum priority to receive")
    
    # Delivery settings
    immediate_delivery: bool = Field(default=True, description="Send alerts immediately")
    digest_mode: bool = Field(default=False, description="Group alerts into digest")
    quiet_hours_start: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    quiet_hours_end: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    timezone: str = Field(default="UTC", description="Recipient timezone")
    
    # Throttling
    max_alerts_per_hour: int = Field(default=10, ge=1, le=100)
    max_alerts_per_day: int = Field(default=50, ge=1, le=500)
    
    @validator('alert_types')
    def validate_alert_types(cls, v):
        """Set default alert types if none specified."""
        if not v:
            return [AlertType.BREAKING_NEWS, AlertType.MAJOR_ANNOUNCEMENT, AlertType.RESEARCH_BREAKTHROUGH]
        return v


class Alert(BaseModel):
    """Complete alert with all metadata."""
    alert_id: UUID = Field(default_factory=uuid4)
    article_id: UUID = Field(..., description="Source article ID")
    
    # Alert classification
    alert_type: AlertType = Field(..., description="Type of alert")
    priority: AlertPriority = Field(..., description="Alert priority")
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="Urgency score")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Impact score")
    
    # Content
    content: AlertContent = Field(..., description="Alert content")
    
    # Trigger information
    triggers: List[AlertTrigger] = Field(..., min_items=1, description="What triggered this alert")
    
    # Source information
    source_url: str = Field(..., description="Original article URL")
    source_name: str = Field(..., description="Source publication")
    author: Optional[str] = None
    published_at: datetime = Field(..., description="When article was published")
    
    # Processing metadata
    status: AlertStatus = Field(default=AlertStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    evaluated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    # Evaluation results
    human_review_required: bool = Field(default=False)
    evaluation_reasoning: str = Field(default="", description="Why alert was approved/rejected")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Delivery tracking
    recipients: List[AlertRecipient] = Field(default_factory=list)
    delivery_channels: List[DeliveryChannel] = Field(default_factory=list)
    successful_deliveries: int = Field(default=0, ge=0)
    failed_deliveries: int = Field(default=0, ge=0)
    delivery_errors: List[str] = Field(default_factory=list)
    
    # Throttling and deduplication
    is_duplicate: bool = Field(default=False)
    duplicate_of: Optional[UUID] = None
    is_throttled: bool = Field(default=False)
    throttle_reason: Optional[str] = None
    
    # Performance metrics
    processing_time: float = Field(default=0.0, ge=0.0, description="Processing time in seconds")
    alert_cost: float = Field(default=0.0, ge=0.0, description="Cost to generate and send alert")
    
    @property
    def overall_priority_score(self) -> float:
        """Calculate overall priority score combining urgency and impact."""
        return (self.urgency_score * 0.6) + (self.impact_score * 0.4)
    
    @property
    def time_to_alert(self) -> timedelta:
        """Calculate time from article publication to alert creation."""
        return self.created_at - self.published_at
    
    @property
    def delivery_success_rate(self) -> float:
        """Calculate delivery success rate."""
        total_deliveries = self.successful_deliveries + self.failed_deliveries
        if total_deliveries == 0:
            return 0.0
        return (self.successful_deliveries / total_deliveries) * 100


class AlertRequest(BaseModel):
    """Request to evaluate article for alerts."""
    article_id: UUID
    article_content: str = Field(..., min_length=50)
    article_url: str
    source_name: str
    author: Optional[str] = None
    published_at: datetime
    
    # Analysis data
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    entities: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    
    # Alert configuration
    min_priority: AlertPriority = Field(default=AlertPriority.MEDIUM)
    max_alerts_per_hour: int = Field(default=5, ge=1, le=20)
    check_duplicates: bool = Field(default=True)
    require_human_review: bool = Field(default=False)


class AlertResponse(BaseModel):
    """Response from alert evaluation."""
    success: bool
    alert_generated: bool = Field(default=False)
    alert: Optional[Alert] = None
    
    # Evaluation details
    evaluation_score: float = Field(default=0.0, ge=0.0, le=1.0)
    rejection_reason: Optional[str] = None
    triggers_detected: List[str] = Field(default_factory=list)
    
    # Processing metrics
    processing_time: float = Field(..., description="Evaluation time in seconds")
    evaluation_cost: float = Field(default=0.0, description="Cost to evaluate")
    
    # Next steps
    human_review_required: bool = Field(default=False)
    scheduled_for_review: Optional[datetime] = None
    auto_send_scheduled: Optional[datetime] = None


class AlertDigest(BaseModel):
    """Daily/weekly digest of alerts."""
    digest_id: UUID = Field(default_factory=uuid4)
    digest_type: str = Field(..., pattern="^(daily|weekly|emergency)$")
    
    # Time period
    period_start: datetime
    period_end: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Content
    title: str = Field(..., description="Digest title")
    summary: str = Field(..., description="Executive summary")
    
    # Alerts included
    alerts: List[Alert] = Field(default_factory=list)
    alert_count_by_priority: Dict[AlertPriority, int] = Field(default_factory=dict)
    alert_count_by_type: Dict[AlertType, int] = Field(default_factory=dict)
    
    # Statistics
    total_alerts: int = Field(default=0, ge=0)
    avg_urgency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    top_topics: List[str] = Field(default_factory=list)
    
    # Delivery
    recipients: List[AlertRecipient] = Field(default_factory=list)
    delivery_status: AlertStatus = Field(default=AlertStatus.PENDING)


class AlertConfiguration(BaseModel):
    """System-wide alert configuration."""
    
    # Thresholds
    urgency_threshold_high: float = Field(default=0.8, ge=0.0, le=1.0)
    urgency_threshold_medium: float = Field(default=0.6, ge=0.0, le=1.0)
    impact_threshold_critical: float = Field(default=0.9, ge=0.0, le=1.0)
    
    # Rate limiting
    max_alerts_per_hour_global: int = Field(default=20, ge=1, le=100)
    max_alerts_per_day_global: int = Field(default=100, ge=1, le=1000)
    
    # Trigger keywords by category
    breaking_news_keywords: List[str] = Field(default_factory=lambda: [
        "breaking", "urgent", "just announced", "developing", "confirmed",
        "exclusive", "first reported", "sources say"
    ])
    
    funding_keywords: List[str] = Field(default_factory=lambda: [
        "raises", "funding", "investment", "series", "valuation", "ipo",
        "acquisition", "merger", "bought", "purchased"
    ])
    
    research_keywords: List[str] = Field(default_factory=lambda: [
        "breakthrough", "discovery", "first", "novel", "revolutionary",
        "significant advance", "major finding", "achieves"
    ])
    
    product_keywords: List[str] = Field(default_factory=lambda: [
        "launches", "introduces", "unveils", "releases", "announces",
        "debuts", "available", "beta", "general availability"
    ])
    
    # Companies and entities to monitor
    high_priority_companies: List[str] = Field(default_factory=lambda: [
        "OpenAI", "Google", "Microsoft", "Amazon", "Meta", "Apple",
        "NVIDIA", "Tesla", "Anthropic", "DeepMind"
    ])
    
    # Alert suppression rules
    duplicate_window_hours: int = Field(default=6, ge=1, le=48)
    similar_content_threshold: float = Field(default=0.8, ge=0.5, le=1.0)
    
    # Business hours for non-critical alerts
    business_hours_start: str = Field(default="09:00", pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    business_hours_end: str = Field(default="17:00", pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    business_timezone: str = Field(default="America/New_York")


class AlertMetrics(BaseModel):
    """Performance metrics for alert system."""
    
    # Time period
    period_start: datetime
    period_end: datetime
    
    # Volume metrics
    total_articles_evaluated: int = Field(default=0, ge=0)
    total_alerts_generated: int = Field(default=0, ge=0)
    alert_generation_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Quality metrics
    true_positive_alerts: int = Field(default=0, ge=0)
    false_positive_alerts: int = Field(default=0, ge=0)
    precision: float = Field(default=0.0, ge=0.0, le=1.0)
    user_engagement_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Delivery metrics
    successful_deliveries: int = Field(default=0, ge=0)
    failed_deliveries: int = Field(default=0, ge=0)
    delivery_success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    avg_delivery_time_seconds: float = Field(default=0.0, ge=0.0)
    
    # Performance metrics
    avg_processing_time_seconds: float = Field(default=0.0, ge=0.0)
    avg_time_to_alert_minutes: float = Field(default=0.0, ge=0.0)
    cost_per_alert: float = Field(default=0.0, ge=0.0)
    
    # Breakdown by priority
    alerts_by_priority: Dict[AlertPriority, int] = Field(default_factory=dict)
    alerts_by_type: Dict[AlertType, int] = Field(default_factory=dict)
    alerts_by_hour: Dict[int, int] = Field(default_factory=dict)


# Export all models
__all__ = [
    "AlertPriority",
    "AlertType",
    "AlertStatus", 
    "DeliveryChannel",
    "AlertTrigger",
    "AlertContent",
    "AlertRecipient",
    "Alert",
    "AlertRequest",
    "AlertResponse",
    "AlertDigest",
    "AlertConfiguration",
    "AlertMetrics",
]