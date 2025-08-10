"""
RSS Aggregator MCP Server - Data Schemas
Location: mcp_servers/rss_aggregator/schemas.py

Pydantic models for RSS aggregation data structures.
Used for validation and serialization between MCP tools and agents.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic import ConfigDict

class FeedStatus(str, Enum):
    """RSS feed processing status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"

class ArticleStatus(str, Enum):
    """Article processing status"""
    DISCOVERED = "discovered"
    FETCHED = "fetched"
    PROCESSED = "processed"
    FILTERED_OUT = "filtered_out"
    DUPLICATE = "duplicate"
    ERROR = "error"

class RSSSourceConfig(BaseModel):
    """Configuration for an RSS news source"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Source identification
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable source name")
    url: HttpUrl = Field(..., description="Main website URL")
    rss_feed_url: HttpUrl = Field(..., description="RSS feed URL")
    
    # Classification
    tier: int = Field(default=2, ge=1, le=3, description="Quality tier (1=highest)")
    category: str = Field(default="Industry News", max_length=100, description="Content category")
    
    # Fetch configuration
    active: bool = Field(default=True, description="Whether to fetch from this source")
    fetch_interval: int = Field(default=3600, ge=300, le=86400, description="Fetch interval in seconds")
    max_articles_per_fetch: int = Field(default=50, ge=1, le=200, description="Max articles per fetch")
    
    # Rate limiting
    rate_limit_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between requests")
    timeout: int = Field(default=30, ge=5, le=120, description="Request timeout in seconds")
    
    # Content filtering
    keywords: List[str] = Field(default_factory=list, description="Required keywords for relevance")
    exclude_keywords: List[str] = Field(default_factory=list, description="Keywords to exclude")
    
    # Metadata
    language: str = Field(default="en", max_length=5, description="Expected content language")
    encoding: Optional[str] = Field(default=None, max_length=20, description="Feed encoding")
    user_agent: Optional[str] = Field(default=None, max_length=200, description="Custom User-Agent")
    
    @validator('keywords', 'exclude_keywords')
    def validate_keywords(cls, v):
        """Ensure keywords are lowercase and stripped"""
        if v:
            return [keyword.lower().strip() for keyword in v if keyword.strip()]
        return []

class RSSArticle(BaseModel):
    """Article extracted from RSS feed"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Identification
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique article ID")
    source_name: str = Field(..., description="Source name from RSSSourceConfig")
    
    # Content
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    url: HttpUrl = Field(..., description="Article URL")
    description: Optional[str] = Field(default=None, max_length=2000, description="Article description/summary")
    content: Optional[str] = Field(default=None, description="Full article content")
    
    # Metadata
    published_date: Optional[datetime] = Field(default=None, description="Publication date")
    author: Optional[str] = Field(default=None, max_length=255, description="Article author")
    categories: List[str] = Field(default_factory=list, description="RSS categories/tags")
    
    # Processing metadata
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: Optional[str] = Field(default=None, max_length=64, description="Content hash for deduplication")
    word_count: Optional[int] = Field(default=None, ge=0, description="Estimated word count")
    
    # Status and quality
    status: ArticleStatus = Field(default=ArticleStatus.DISCOVERED)
    relevance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="AI relevance score")
    
    # Error tracking
    processing_errors: List[str] = Field(default_factory=list, description="Processing error messages")
    
    @validator('categories')
    def validate_categories(cls, v):
        """Clean and validate categories"""
        if v:
            return [cat.strip() for cat in v if cat.strip()]
        return []
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

class FeedFetchResult(BaseModel):
    """Result of fetching an RSS feed"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Source information
    source_name: str = Field(..., description="Source name")
    source_url: str = Field(..., description="RSS feed URL")
    
    # Fetch metadata
    fetch_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fetch_duration: float = Field(..., ge=0.0, description="Fetch duration in seconds")
    status: FeedStatus = Field(..., description="Fetch status")
    
    # Results
    articles: List[RSSArticle] = Field(default_factory=list, description="Extracted articles")
    articles_count: int = Field(default=0, ge=0, description="Number of articles found")
    new_articles_count: int = Field(default=0, ge=0, description="Number of new articles")
    
    # Feed metadata
    feed_title: Optional[str] = Field(default=None, description="RSS feed title")
    feed_description: Optional[str] = Field(default=None, description="RSS feed description")
    feed_language: Optional[str] = Field(default=None, description="Feed language")
    feed_last_updated: Optional[datetime] = Field(default=None, description="Feed last build date")
    
    # Error information
    error_message: Optional[str] = Field(default=None, description="Error message if fetch failed")
    http_status_code: Optional[int] = Field(default=None, description="HTTP response status code")
    
    # Performance metrics
    bytes_downloaded: Optional[int] = Field(default=None, ge=0, description="Bytes downloaded")
    articles_per_second: Optional[float] = Field(default=None, ge=0.0, description="Processing rate")
    
    @validator('articles_count', always=True)
    def set_articles_count(cls, v, values):
        """Auto-set articles count from articles list"""
        articles = values.get('articles', [])
        return len(articles)

class BatchFetchRequest(BaseModel):
    """Request for fetching multiple RSS feeds"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Source selection
    source_names: Optional[List[str]] = Field(default=None, description="Specific sources to fetch")
    tier_filter: Optional[List[int]] = Field(default=None, description="Filter by source tiers")
    category_filter: Optional[List[str]] = Field(default=None, description="Filter by categories")
    
    # Fetch configuration
    force_refresh: bool = Field(default=False, description="Bypass cache and force fresh fetch")
    max_articles_per_source: Optional[int] = Field(default=None, ge=1, le=200, description="Override max articles")
    parallel_limit: int = Field(default=5, ge=1, le=20, description="Max parallel requests")
    save_to_database: bool = Field(default=False, description="Automatically save articles to database after fetching")
    
    # Content filtering
    keywords_filter: Optional[List[str]] = Field(default=None, description="Required keywords for inclusion")
    exclude_duplicates: bool = Field(default=True, description="Remove duplicate articles")
    
    # Time filtering
    since_date: Optional[datetime] = Field(default=None, description="Only fetch articles after this date")
    max_age_hours: Optional[int] = Field(default=None, ge=1, le=168, description="Max article age in hours")
    
    @validator('tier_filter')
    def validate_tier_filter(cls, v):
        """Validate tier filter values"""
        if v:
            for tier in v:
                if tier not in [1, 2, 3]:
                    raise ValueError(f"Invalid tier: {tier}. Must be 1, 2, or 3")
        return v

class BatchFetchResult(BaseModel):
    """Result of batch RSS feed fetch operation"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Operation metadata
    operation_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique operation ID")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    total_duration: Optional[float] = Field(default=None, ge=0.0, description="Total operation duration")
    
    # Request summary
    request: BatchFetchRequest = Field(..., description="Original request")
    sources_attempted: int = Field(default=0, ge=0, description="Number of sources attempted")
    sources_successful: int = Field(default=0, ge=0, description="Number of successful fetches")
    
    # Results
    feed_results: List[FeedFetchResult] = Field(default_factory=list, description="Individual feed results")
    all_articles: List[RSSArticle] = Field(default_factory=list, description="All articles combined")
    
    # Aggregated statistics
    total_articles: int = Field(default=0, ge=0, description="Total articles found")
    new_articles: int = Field(default=0, ge=0, description="New articles discovered")
    duplicate_articles: int = Field(default=0, ge=0, description="Duplicate articles filtered")
    filtered_articles: int = Field(default=0, ge=0, description="Articles filtered out")
    
    # Performance metrics
    average_fetch_time: Optional[float] = Field(default=None, ge=0.0, description="Average fetch time per source")
    articles_per_minute: Optional[float] = Field(default=None, ge=0.0, description="Processing rate")
    total_bytes_downloaded: Optional[int] = Field(default=None, ge=0, description="Total bytes downloaded")
    
    # Error summary
    error_count: int = Field(default=0, ge=0, description="Number of errors encountered")
    error_summary: Dict[str, int] = Field(default_factory=dict, description="Error types and counts")
    
    # Database save results
    database_save_results: Optional[Dict[str, Any]] = Field(default=None, description="Database save operation results")
    
    def add_feed_result(self, result: FeedFetchResult) -> None:
        """Add a feed result and update statistics"""
        self.feed_results.append(result)
        self.sources_attempted += 1
        
        if result.status == FeedStatus.ACTIVE:
            self.sources_successful += 1
            self.all_articles.extend(result.articles)
            self.total_articles += result.articles_count
            self.new_articles += result.new_articles_count
        else:
            self.error_count += 1
            error_type = result.status.value
            self.error_summary[error_type] = self.error_summary.get(error_type, 0) + 1
    
    def finalize(self) -> None:
        """Finalize the batch operation with computed statistics"""
        self.completed_at = datetime.now(timezone.utc)
        
        if self.started_at and self.completed_at:
            self.total_duration = (self.completed_at - self.started_at).total_seconds()
        
        # Calculate performance metrics
        if self.feed_results:
            fetch_times = [r.fetch_duration for r in self.feed_results if r.fetch_duration > 0]
            if fetch_times:
                self.average_fetch_time = sum(fetch_times) / len(fetch_times)
        
        if self.total_duration and self.total_duration > 0:
            self.articles_per_minute = (self.total_articles * 60) / self.total_duration
        
        # Calculate total bytes
        bytes_list = [r.bytes_downloaded for r in self.feed_results if r.bytes_downloaded]
        if bytes_list:
            self.total_bytes_downloaded = sum(bytes_list)

class CacheEntry(BaseModel):
    """Cache entry for RSS feed data"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Cache metadata
    cache_key: str = Field(..., description="Unique cache key")
    cached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(..., description="Cache expiration time")
    
    # Cached data
    feed_result: FeedFetchResult = Field(..., description="Cached feed result")
    
    # Cache statistics
    hit_count: int = Field(default=0, ge=0, description="Number of cache hits")
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now(timezone.utc) >= self.expires_at
    
    @property
    def age_seconds(self) -> float:
        """Get cache entry age in seconds"""
        return (datetime.now(timezone.utc) - self.cached_at).total_seconds()
    
    def access(self) -> None:
        """Mark cache entry as accessed"""
        self.hit_count += 1
        self.last_accessed = datetime.now(timezone.utc)

class RSSServerStats(BaseModel):
    """Statistics for RSS aggregator server"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Server information
    server_id: str = Field(default="rss-aggregator", description="Server identifier")
    uptime_seconds: float = Field(default=0.0, ge=0.0, description="Server uptime")
    
    # Source statistics
    total_sources: int = Field(default=0, ge=0, description="Total configured sources")
    active_sources: int = Field(default=0, ge=0, description="Currently active sources")
    error_sources: int = Field(default=0, ge=0, description="Sources in error state")
    
    # Fetch statistics
    total_fetches: int = Field(default=0, ge=0, description="Total fetch operations")
    successful_fetches: int = Field(default=0, ge=0, description="Successful fetch operations")
    failed_fetches: int = Field(default=0, ge=0, description="Failed fetch operations")
    
    # Article statistics
    total_articles_discovered: int = Field(default=0, ge=0, description="Total articles discovered")
    unique_articles: int = Field(default=0, ge=0, description="Unique articles (after deduplication)")
    filtered_articles: int = Field(default=0, ge=0, description="Articles filtered out")
    
    # Performance metrics
    average_fetch_duration: float = Field(default=0.0, ge=0.0, description="Average fetch duration")
    articles_per_hour: float = Field(default=0.0, ge=0.0, description="Articles processed per hour")
    
    # Cache statistics
    cache_entries: int = Field(default=0, ge=0, description="Number of cache entries")
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Cache hit rate")
    
    # Error statistics
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall error rate")
    common_errors: Dict[str, int] = Field(default_factory=dict, description="Common error types")
    
    # Resource usage
    memory_usage_mb: Optional[float] = Field(default=None, ge=0.0, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="CPU usage percentage")
    
    @property
    def success_rate(self) -> float:
        """Calculate fetch success rate"""
        if self.total_fetches == 0:
            return 0.0
        return self.successful_fetches / self.total_fetches