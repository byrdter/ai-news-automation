"""
Data models for the News Discovery Agent.

Defines Pydantic models for RSS feed processing, article discovery,
and deduplication operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, validator
import hashlib


class FeedStatus(str, Enum):
    """RSS feed processing status."""
    PENDING = "pending"
    FETCHING = "fetching"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    THROTTLED = "throttled"


class ArticleStatus(str, Enum):
    """Article discovery status."""
    DISCOVERED = "discovered"
    DUPLICATE = "duplicate"
    FILTERED = "filtered"
    PROCESSED = "processed"
    ERROR = "error"


class RSSFeedSource(BaseModel):
    """RSS feed source configuration."""
    
    id: Optional[UUID] = None
    name: str = Field(..., description="Human-readable feed name")
    url: HttpUrl = Field(..., description="RSS feed URL")
    category: str = Field(..., description="Content category")
    priority: int = Field(default=3, ge=1, le=5, description="Processing priority (1=highest)")
    enabled: bool = Field(default=True, description="Whether feed is active")
    
    # Processing metadata
    last_fetched: Optional[datetime] = None
    last_success: Optional[datetime] = None
    error_count: int = Field(default=0, description="Consecutive error count")
    last_error: Optional[str] = None
    
    # Performance metrics
    avg_fetch_time: float = Field(default=0.0, description="Average fetch time in seconds")
    total_articles_found: int = Field(default=0, description="Total articles discovered")
    relevant_articles_found: int = Field(default=0, description="Articles above relevance threshold")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RawArticle(BaseModel):
    """Raw article data from RSS feed."""
    
    title: str = Field(..., description="Article title")
    url: HttpUrl = Field(..., description="Article URL")
    description: Optional[str] = Field(None, description="Article summary/description")
    content: Optional[str] = Field(None, description="Full article content")
    author: Optional[str] = Field(None, description="Article author")
    published_date: datetime = Field(..., description="Publication timestamp")
    
    # RSS metadata
    feed_source: str = Field(..., description="Source feed name")
    feed_category: str = Field(..., description="Feed category")
    guid: Optional[str] = Field(None, description="RSS GUID")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    
    # Processing metadata
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    raw_content: Optional[str] = Field(None, description="Raw HTML content")
    
    @validator('title')
    def title_not_empty(cls, v):
        """Ensure title is not empty."""
        if not v or not v.strip():
            raise ValueError("Article title cannot be empty")
        return v.strip()
    
    @validator('url')
    def url_reachable(cls, v):
        """Basic URL validation."""
        url_str = str(v)
        if len(url_str) > 2000:
            raise ValueError("URL too long")
        return v
    
    @property
    def content_hash(self) -> str:
        """Generate content hash for deduplication."""
        content_for_hash = f"{self.title}|{str(self.url)}|{self.description or ''}"
        return hashlib.sha256(content_for_hash.encode()).hexdigest()
    
    @property
    def word_count(self) -> int:
        """Calculate approximate word count."""
        text = self.content or self.description or self.title
        return len(text.split()) if text else 0


class ProcessedArticle(BaseModel):
    """Processed article with enrichment data."""
    
    # Original article data
    raw_article: RawArticle
    
    # Processing results
    status: ArticleStatus = Field(default=ArticleStatus.DISCOVERED)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="AI-determined relevance")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Content quality score")
    duplicate_of: Optional[UUID] = Field(None, description="UUID of original article if duplicate")
    
    # Extracted metadata
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    
    # Processing metadata
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    processing_cost: float = Field(default=0.0, description="API cost in USD")
    error_message: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('relevance_score', 'quality_score')
    def score_range(cls, v):
        """Ensure scores are in valid range."""
        return max(0.0, min(1.0, v))


class FeedProcessingResult(BaseModel):
    """Result of processing an RSS feed."""
    
    feed_source: RSSFeedSource
    status: FeedStatus
    
    # Processing metrics
    articles_found: int = Field(default=0, description="Total articles in feed")
    articles_new: int = Field(default=0, description="New articles discovered")
    articles_duplicates: int = Field(default=0, description="Duplicate articles filtered")
    articles_processed: int = Field(default=0, description="Articles successfully processed")
    articles_errors: int = Field(default=0, description="Articles with processing errors")
    
    # Performance metrics
    fetch_time: float = Field(default=0.0, description="Feed fetch time in seconds")
    processing_time: float = Field(default=0.0, description="Total processing time")
    bandwidth_used: int = Field(default=0, description="Bytes downloaded")
    
    # Results
    processed_articles: List[ProcessedArticle] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate processing success rate."""
        if self.articles_found == 0:
            return 1.0
        return (self.articles_processed / self.articles_found) * 100
    
    @property
    def avg_relevance(self) -> float:
        """Calculate average relevance score."""
        if not self.processed_articles:
            return 0.0
        scores = [a.relevance_score for a in self.processed_articles]
        return sum(scores) / len(scores)


class DiscoverySessionConfig(BaseModel):
    """Configuration for a discovery session."""
    
    # Source selection
    feed_sources: List[RSSFeedSource]
    max_sources_concurrent: int = Field(default=5, ge=1, le=20)
    
    # Processing limits
    max_articles_per_source: int = Field(default=50, ge=1, le=200)
    max_total_articles: int = Field(default=500, ge=1, le=2000)
    
    # Quality filters
    min_relevance_score: float = Field(default=0.7, ge=0.0, le=1.0)
    min_quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Rate limiting
    delay_between_requests: float = Field(default=1.0, ge=0.1, le=10.0)
    request_timeout: int = Field(default=30, ge=5, le=120)
    
    # Deduplication
    similarity_threshold: float = Field(default=0.85, ge=0.5, le=1.0)
    content_hash_window_hours: int = Field(default=24, ge=1, le=168)
    
    # Cost controls
    max_cost_usd: float = Field(default=1.0, ge=0.0)
    cost_per_analysis: float = Field(default=0.01, ge=0.001)


class DiscoverySession(BaseModel):
    """Complete discovery session with results."""
    
    config: DiscoverySessionConfig
    session_id: UUID
    
    # Session status
    status: FeedStatus = Field(default=FeedStatus.PENDING)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Results by feed
    feed_results: List[FeedProcessingResult] = Field(default_factory=list)
    
    # Aggregated metrics
    total_articles_discovered: int = Field(default=0)
    total_articles_processed: int = Field(default=0)
    total_articles_relevant: int = Field(default=0)
    total_duplicates_filtered: int = Field(default=0)
    
    # Performance metrics
    total_processing_time: float = Field(default=0.0)
    total_cost_usd: float = Field(default=0.0)
    avg_articles_per_second: float = Field(default=0.0)
    
    # Errors and warnings
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Overall session success rate."""
        if self.total_articles_discovered == 0:
            return 1.0
        return (self.total_articles_processed / self.total_articles_discovered) * 100
    
    @property
    def relevance_rate(self) -> float:
        """Percentage of relevant articles."""
        if self.total_articles_processed == 0:
            return 0.0
        return (self.total_articles_relevant / self.total_articles_processed) * 100
    
    @property
    def cost_per_article(self) -> float:
        """Average cost per processed article."""
        if self.total_articles_processed == 0:
            return 0.0
        return self.total_cost_usd / self.total_articles_processed


# Agent response models
class NewsDiscoveryRequest(BaseModel):
    """Request to discover news articles."""
    
    session_config: DiscoverySessionConfig
    force_refresh: bool = Field(default=False, description="Ignore cache and fetch fresh")
    dry_run: bool = Field(default=False, description="Validate config without processing")


class NewsDiscoveryResponse(BaseModel):
    """Response from news discovery operation."""
    
    success: bool
    session: DiscoverySession
    message: str
    
    # Quick stats
    articles_found: int
    articles_relevant: int
    processing_time: float
    cost_usd: float
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Agent suggestions")
    next_run_recommended: Optional[datetime] = Field(None, description="Recommended next run time")


# Export all models
__all__ = [
    "FeedStatus",
    "ArticleStatus", 
    "RSSFeedSource",
    "RawArticle",
    "ProcessedArticle",
    "FeedProcessingResult",
    "DiscoverySessionConfig",
    "DiscoverySession",
    "NewsDiscoveryRequest",
    "NewsDiscoveryResponse",
]