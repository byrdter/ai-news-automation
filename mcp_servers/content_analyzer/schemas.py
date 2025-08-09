"""
Content Analyzer MCP Server - Data Schemas
Location: mcp_servers/content_analyzer/schemas.py

Pydantic models for content analysis operations using Cohere Command R7B.
Cost-optimized analysis for AI news articles with comprehensive scoring.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator
from pydantic import ConfigDict

class AnalysisStatus(str, Enum):
    """Content analysis status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

class SentimentCategory(str, Enum):
    """Sentiment analysis categories"""
    VERY_NEGATIVE = "very_negative"      # -1.0 to -0.6
    NEGATIVE = "negative"                # -0.6 to -0.2
    NEUTRAL = "neutral"                  # -0.2 to 0.2
    POSITIVE = "positive"                # 0.2 to 0.6
    VERY_POSITIVE = "very_positive"      # 0.6 to 1.0

class UrgencyLevel(str, Enum):
    """Article urgency levels"""
    LOW = "low"           # 0.0 to 0.3
    MEDIUM = "medium"     # 0.3 to 0.6  
    HIGH = "high"         # 0.6 to 0.8
    CRITICAL = "critical" # 0.8 to 1.0

class ContentType(str, Enum):
    """Types of content being analyzed"""
    NEWS_ARTICLE = "news_article"
    BLOG_POST = "blog_post"
    RESEARCH_PAPER = "research_paper"
    PRESS_RELEASE = "press_release"
    OPINION_PIECE = "opinion_piece"
    ANNOUNCEMENT = "announcement"

class EntityType(str, Enum):
    """Named entity types for extraction"""
    PERSON = "person"
    ORGANIZATION = "organization"
    COMPANY = "company"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"
    RESEARCH_PAPER = "research_paper"
    EVENT = "event"

class AnalysisRequest(BaseModel):
    """Request for content analysis"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Content identification
    content_id: str = Field(..., description="Unique identifier for content")
    title: str = Field(..., min_length=1, max_length=500, description="Content title")
    content: str = Field(..., min_length=10, description="Content text to analyze")
    
    # Content metadata
    url: Optional[str] = Field(default=None, description="Source URL")
    source_name: Optional[str] = Field(default=None, description="Source publication name")
    author: Optional[str] = Field(default=None, description="Content author")
    published_date: Optional[datetime] = Field(default=None, description="Publication date")
    content_type: ContentType = Field(default=ContentType.NEWS_ARTICLE)
    
    # Analysis configuration
    include_sentiment: bool = Field(default=True, description="Include sentiment analysis")
    include_entities: bool = Field(default=True, description="Include entity extraction")
    include_keywords: bool = Field(default=True, description="Include keyword extraction")
    include_categories: bool = Field(default=True, description="Include categorization")
    include_trends: bool = Field(default=True, description="Include trend detection")
    include_urgency: bool = Field(default=True, description="Include urgency scoring")
    
    # Custom parameters
    relevance_keywords: List[str] = Field(default_factory=list, description="Keywords for relevance scoring")
    custom_entities: List[str] = Field(default_factory=list, description="Custom entities to look for")
    
    # Processing options
    use_cache: bool = Field(default=True, description="Use cached results if available")
    max_tokens: int = Field(default=4000, ge=100, le=8000, description="Maximum tokens for analysis")
    
    @validator('content')
    def validate_content_length(cls, v):
        """Ensure content is not too long for analysis"""
        if len(v) > 50000:  # ~50k characters limit
            v = v[:49997] + "..."
        return v

class ExtractedEntity(BaseModel):
    """Extracted named entity with confidence"""
    model_config = ConfigDict(validate_assignment=True)
    
    text: str = Field(..., description="Entity text as it appears")
    label: EntityType = Field(..., description="Entity type/category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    start_pos: Optional[int] = Field(default=None, description="Start position in text")
    end_pos: Optional[int] = Field(default=None, description="End position in text")
    
    # Additional entity information
    normalized_text: Optional[str] = Field(default=None, description="Normalized entity text")
    description: Optional[str] = Field(default=None, description="Entity description")
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    
    # Context information
    context: Optional[str] = Field(default=None, description="Surrounding context")
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance to AI/tech")

class KeywordExtraction(BaseModel):
    """Extracted keyword with importance score"""
    model_config = ConfigDict(validate_assignment=True)
    
    keyword: str = Field(..., description="Extracted keyword")
    score: float = Field(..., ge=0.0, le=1.0, description="Importance score")
    frequency: int = Field(..., ge=1, description="Frequency in text")
    context: List[str] = Field(default_factory=list, description="Context sentences")
    
    # Keyword classification
    is_ai_related: bool = Field(default=False, description="Whether keyword is AI-related")
    is_trending: bool = Field(default=False, description="Whether keyword is trending")
    category: Optional[str] = Field(default=None, description="Keyword category")

class SentimentAnalysis(BaseModel):
    """Sentiment analysis results"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Overall sentiment
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score (-1 negative, +1 positive)")
    sentiment_category: SentimentCategory = Field(..., description="Categorical sentiment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    
    # Aspect-based sentiment
    aspect_sentiments: Dict[str, float] = Field(default_factory=dict, description="Sentiment by aspect")
    
    # Emotional analysis
    emotions: Dict[str, float] = Field(default_factory=dict, description="Detected emotions with scores")
    
    # Context
    positive_phrases: List[str] = Field(default_factory=list, description="Positive sentiment phrases")
    negative_phrases: List[str] = Field(default_factory=list, description="Negative sentiment phrases")
    neutral_phrases: List[str] = Field(default_factory=list, description="Neutral sentiment phrases")

class TrendAnalysis(BaseModel):
    """Trend detection and analysis"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Trend indicators
    is_trending_topic: bool = Field(default=False, description="Whether content discusses trending topics")
    trend_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Trending relevance score")
    
    # Identified trends
    trending_keywords: List[str] = Field(default_factory=list, description="Trending keywords found")
    emerging_technologies: List[str] = Field(default_factory=list, description="Emerging tech mentioned")
    market_trends: List[str] = Field(default_factory=list, description="Market trends discussed")
    
    # Temporal indicators
    time_sensitive: bool = Field(default=False, description="Whether content is time-sensitive")
    future_predictions: List[str] = Field(default_factory=list, description="Future predictions made")
    
    # Industry impact
    affected_industries: List[str] = Field(default_factory=list, description="Industries that may be affected")
    competitive_implications: List[str] = Field(default_factory=list, description="Competitive implications")

class UrgencyAssessment(BaseModel):
    """Urgency and importance assessment"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Urgency scoring
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="Urgency score (0=low, 1=critical)")
    urgency_level: UrgencyLevel = Field(..., description="Categorical urgency level")
    
    # Urgency factors
    breaking_news_indicators: List[str] = Field(default_factory=list, description="Breaking news signals")
    time_sensitivity_factors: List[str] = Field(default_factory=list, description="Time-sensitive elements")
    impact_indicators: List[str] = Field(default_factory=list, description="High-impact indicators")
    
    # Market impact
    market_moving_potential: float = Field(default=0.0, ge=0.0, le=1.0, description="Potential market impact")
    regulatory_implications: bool = Field(default=False, description="Has regulatory implications")
    competitive_impact: bool = Field(default=False, description="Has competitive implications")
    
    # Alert triggers
    should_alert: bool = Field(default=False, description="Whether this should trigger an alert")
    alert_reasons: List[str] = Field(default_factory=list, description="Reasons for alerting")

class ContentCategorization(BaseModel):
    """Content categorization results"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Primary categorization
    primary_category: str = Field(..., description="Main content category")
    category_confidence: float = Field(..., ge=0.0, le=1.0, description="Categorization confidence")
    
    # Secondary categories
    secondary_categories: List[str] = Field(default_factory=list, description="Additional relevant categories")
    
    # AI/Tech specific categories
    ai_subcategory: Optional[str] = Field(default=None, description="AI-specific subcategory")
    technology_areas: List[str] = Field(default_factory=list, description="Relevant technology areas")
    research_areas: List[str] = Field(default_factory=list, description="Relevant research areas")
    
    # Content classification
    content_complexity: str = Field(default="medium", description="Content complexity level")
    target_audience: str = Field(default="general", description="Intended audience")
    content_format: str = Field(default="article", description="Content format type")

class AnalysisResult(BaseModel):
    """Complete content analysis result"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Request metadata
    request_id: str = Field(..., description="Original request ID")
    content_id: str = Field(..., description="Content identifier")
    
    # Processing metadata
    analysis_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_duration: float = Field(..., ge=0.0, description="Analysis duration in seconds")
    status: AnalysisStatus = Field(default=AnalysisStatus.COMPLETED)
    
    # Model information
    model_used: str = Field(default="command-r7b-12-2024", description="Analysis model used")
    model_version: Optional[str] = Field(default=None, description="Model version")
    
    # Analysis results
    sentiment: Optional[SentimentAnalysis] = Field(default=None)
    entities: List[ExtractedEntity] = Field(default_factory=list)
    keywords: List[KeywordExtraction] = Field(default_factory=list)
    categories: Optional[ContentCategorization] = Field(default=None)
    trends: Optional[TrendAnalysis] = Field(default=None)
    urgency: Optional[UrgencyAssessment] = Field(default=None)
    
    # Scoring summary
    overall_relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall AI relevance")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Content quality score")
    engagement_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Predicted engagement")
    
    # Processing metadata
    tokens_used: int = Field(default=0, description="Tokens consumed for analysis")
    cache_hit: bool = Field(default=False, description="Whether result was cached")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Cost tracking
    estimated_cost_usd: float = Field(default=0.0, ge=0.0, description="Estimated analysis cost")

class BatchAnalysisRequest(BaseModel):
    """Request for batch content analysis"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Batch metadata
    batch_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique batch ID")
    batch_name: Optional[str] = Field(default=None, description="Optional batch name")
    
    # Content to analyze
    requests: List[AnalysisRequest] = Field(..., min_items=1, max_items=50, description="Analysis requests")
    
    # Batch processing options
    parallel_limit: int = Field(default=5, ge=1, le=10, description="Max parallel analyses")
    fail_fast: bool = Field(default=False, description="Stop on first failure")
    use_cache: bool = Field(default=True, description="Use cached results where available")
    
    # Cost controls
    max_cost_usd: Optional[float] = Field(default=None, ge=0.0, description="Maximum batch cost")
    cost_per_request_limit: Optional[float] = Field(default=None, ge=0.0, description="Max cost per request")
    
    @validator('requests')
    def validate_unique_content_ids(cls, v):
        """Ensure content IDs are unique within batch"""
        content_ids = [req.content_id for req in v]
        if len(content_ids) != len(set(content_ids)):
            raise ValueError("Content IDs must be unique within batch")
        return v

class BatchAnalysisResult(BaseModel):
    """Result of batch content analysis"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Batch metadata
    batch_id: str = Field(..., description="Batch identifier")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)
    total_duration: Optional[float] = Field(default=None, ge=0.0)
    
    # Request summary
    total_requests: int = Field(..., ge=0, description="Total requests in batch")
    completed_requests: int = Field(default=0, ge=0, description="Successfully completed")
    failed_requests: int = Field(default=0, ge=0, description="Failed requests")
    cached_requests: int = Field(default=0, ge=0, description="Cache hits")
    
    # Results
    results: List[AnalysisResult] = Field(default_factory=list, description="Individual analysis results")
    failed_content_ids: List[str] = Field(default_factory=list, description="Failed content IDs")
    
    # Aggregated statistics
    total_tokens_used: int = Field(default=0, ge=0, description="Total tokens consumed")
    total_cost_usd: float = Field(default=0.0, ge=0.0, description="Total batch cost")
    average_processing_time: Optional[float] = Field(default=None, ge=0.0, description="Average processing time")
    
    # Quality metrics
    average_relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average relevance")
    high_relevance_count: int = Field(default=0, ge=0, description="Count of high-relevance items")
    urgent_content_count: int = Field(default=0, ge=0, description="Count of urgent items")
    
    # Error summary
    error_summary: Dict[str, int] = Field(default_factory=dict, description="Error types and counts")
    
    def add_result(self, result: AnalysisResult) -> None:
        """Add analysis result and update statistics"""
        self.results.append(result)
        self.completed_requests += 1
        self.total_tokens_used += result.tokens_used
        self.total_cost_usd += result.estimated_cost_usd
        
        if result.cache_hit:
            self.cached_requests += 1
        
        if result.overall_relevance_score >= 0.7:
            self.high_relevance_count += 1
        
        if result.urgency and result.urgency.urgency_score >= 0.8:
            self.urgent_content_count += 1
    
    def add_failure(self, content_id: str, error: str) -> None:
        """Add failed request and update statistics"""
        self.failed_content_ids.append(content_id)
        self.failed_requests += 1
        self.error_summary[error] = self.error_summary.get(error, 0) + 1
    
    def finalize(self) -> None:
        """Finalize batch processing with computed statistics"""
        self.completed_at = datetime.now(timezone.utc)
        
        if self.started_at and self.completed_at:
            self.total_duration = (self.completed_at - self.started_at).total_seconds()
        
        if self.completed_requests > 0:
            processing_times = [r.processing_duration for r in self.results if r.processing_duration > 0]
            if processing_times:
                self.average_processing_time = sum(processing_times) / len(processing_times)
            
            relevance_scores = [r.overall_relevance_score for r in self.results]
            if relevance_scores:
                self.average_relevance_score = sum(relevance_scores) / len(relevance_scores)

class AnalysisCache(BaseModel):
    """Cache entry for analysis results"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Cache metadata
    cache_key: str = Field(..., description="Unique cache key")
    cached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(..., description="Cache expiration time")
    
    # Cached data
    result: AnalysisResult = Field(..., description="Cached analysis result")
    
    # Usage statistics
    hit_count: int = Field(default=0, description="Number of cache hits")
    last_accessed: Optional[datetime] = Field(default=None, description="Last access time")
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now(timezone.utc) >= self.expires_at
    
    def access(self) -> None:
        """Mark cache entry as accessed"""
        self.hit_count += 1
        self.last_accessed = datetime.now(timezone.utc)

class ContentAnalysisStats(BaseModel):
    """Statistics for content analyzer server"""
    model_config = ConfigDict(validate_assignment=True)
    
    # Server information
    server_id: str = Field(default="content-analyzer", description="Server identifier")
    uptime_seconds: float = Field(default=0.0, ge=0.0, description="Server uptime")
    
    # Processing statistics
    total_analyses: int = Field(default=0, ge=0, description="Total analyses performed")
    successful_analyses: int = Field(default=0, ge=0, description="Successful analyses")
    failed_analyses: int = Field(default=0, ge=0, description="Failed analyses")
    cached_analyses: int = Field(default=0, ge=0, description="Cache hits")
    
    # Performance metrics
    average_processing_time: float = Field(default=0.0, ge=0.0, description="Average processing time")
    analyses_per_hour: float = Field(default=0.0, ge=0.0, description="Analyses per hour")
    
    # Cost tracking
    total_tokens_used: int = Field(default=0, ge=0, description="Total tokens consumed")
    total_cost_usd: float = Field(default=0.0, ge=0.0, description="Total cost")
    average_cost_per_analysis: float = Field(default=0.0, ge=0.0, description="Average cost per analysis")
    
    # Quality metrics
    average_relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average relevance")
    high_relevance_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of high-relevance content")
    urgent_content_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of urgent content")
    
    # Cache statistics
    cache_entries: int = Field(default=0, ge=0, description="Number of cache entries")
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Cache hit rate")
    
    # Model usage
    model_usage: Dict[str, int] = Field(default_factory=dict, description="Usage count by model")
    
    @property
    def success_rate(self) -> float:
        """Calculate analysis success rate"""
        if self.total_analyses == 0:
            return 0.0
        return self.successful_analyses / self.total_analyses