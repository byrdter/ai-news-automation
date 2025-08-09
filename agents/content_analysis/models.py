"""
Data models for the Content Analysis Agent.

Defines structures for content analysis, entity extraction,
and semantic analysis operations.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, validator
import json


class AnalysisStatus(str, Enum):
    """Content analysis status."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ContentType(str, Enum):
    """Type of content being analyzed."""
    ARTICLE = "article"
    SUMMARY = "summary"
    TITLE = "title"
    ABSTRACT = "abstract"
    PRESS_RELEASE = "press_release"
    BLOG_POST = "blog_post"


class SentimentType(str, Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class ImpactLevel(str, Enum):
    """Impact level classification."""
    BREAKTHROUGH = "breakthrough"
    MAJOR = "major"
    SIGNIFICANT = "significant"
    MODERATE = "moderate"
    MINOR = "minor"


class EntityType(str, Enum):
    """Types of entities that can be extracted."""
    PERSON = "person"
    ORGANIZATION = "organization"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    LOCATION = "location"
    FUNDING = "funding"
    METRIC = "metric"
    DATE = "date"
    MODEL = "model"
    RESEARCH_AREA = "research_area"


class Entity(BaseModel):
    """Extracted entity with metadata."""
    text: str = Field(..., description="Entity text as found in content")
    entity_type: EntityType = Field(..., description="Type of entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    start_pos: Optional[int] = Field(None, description="Character position in text")
    end_pos: Optional[int] = Field(None, description="End character position")
    canonical_form: Optional[str] = Field(None, description="Normalized entity name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional entity data")


class Topic(BaseModel):
    """Identified topic with relevance score."""
    name: str = Field(..., description="Topic name")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance to content")
    keywords: List[str] = Field(default_factory=list, description="Associated keywords")
    category: Optional[str] = Field(None, description="Topic category")


class ContentAnalysis(BaseModel):
    """Complete content analysis results."""
    
    # Input content
    content_id: Optional[UUID] = None
    content_type: ContentType = Field(default=ContentType.ARTICLE)
    content: str = Field(..., description="Content being analyzed")
    
    # Analysis metadata
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    analyzed_at: Optional[datetime] = None
    analysis_model: str = Field(..., description="Model used for analysis")
    analysis_version: str = Field(default="1.0", description="Analysis pipeline version")
    
    # Core analysis results
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="AI relevance score")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Content quality score")
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0, description="Sentiment (-1 to 1)")
    sentiment_type: SentimentType = Field(default=SentimentType.NEUTRAL)
    
    # Impact and importance
    impact_level: ImpactLevel = Field(default=ImpactLevel.MINOR)
    impact_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Industry impact score")
    urgency_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Time sensitivity")
    novelty_score: float = Field(default=0.0, ge=0.0, le=1.0, description="How novel/unique")
    
    # Content structure analysis
    word_count: int = Field(default=0, description="Total word count")
    sentence_count: int = Field(default=0, description="Number of sentences")
    paragraph_count: int = Field(default=0, description="Number of paragraphs")
    readability_score: float = Field(default=0.0, description="Readability index")
    
    # Extracted information
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    topics: List[Topic] = Field(default_factory=list, description="Identified topics")
    key_phrases: List[str] = Field(default_factory=list, description="Important phrases")
    technical_terms: List[str] = Field(default_factory=list, description="Technical vocabulary")
    
    # Categories and classification
    primary_category: Optional[str] = Field(None, description="Main content category")
    secondary_categories: List[str] = Field(default_factory=list, description="Additional categories")
    ai_domains: List[str] = Field(default_factory=list, description="Relevant AI domains")
    industry_sectors: List[str] = Field(default_factory=list, description="Relevant industries")
    
    # Research classification (if applicable)
    is_research_paper: bool = Field(default=False, description="Is this a research paper?")
    research_type: Optional[str] = Field(None, description="Type of research")
    methodology: Optional[str] = Field(None, description="Research methodology")
    key_findings: List[str] = Field(default_factory=list, description="Key research findings")
    
    # Business relevance
    market_impact: Optional[str] = Field(None, description="Market implications")
    competitive_implications: List[str] = Field(default_factory=list, description="Competitive analysis")
    investment_relevance: float = Field(default=0.0, ge=0.0, le=1.0, description="Investment relevance")
    
    # Content quality indicators
    has_data_charts: bool = Field(default=False, description="Contains data visualizations")
    has_expert_quotes: bool = Field(default=False, description="Contains expert opinions")
    source_credibility: float = Field(default=0.5, ge=0.0, le=1.0, description="Source credibility")
    fact_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Density of factual information")
    
    # Analysis reasoning
    analysis_reasoning: str = Field(default="", description="Explanation of analysis results")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence in analysis")
    
    # Processing metadata
    processing_time: float = Field(default=0.0, description="Analysis time in seconds")
    analysis_cost: float = Field(default=0.0, description="API cost for analysis")
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")
    
    @validator('sentiment_score')
    def validate_sentiment_alignment(cls, v, values):
        """Ensure sentiment score aligns with sentiment type."""
        if 'sentiment_type' in values:
            sentiment_type = values['sentiment_type']
            if sentiment_type == SentimentType.VERY_POSITIVE and v < 0.5:
                raise ValueError("Very positive sentiment should have score > 0.5")
            elif sentiment_type == SentimentType.POSITIVE and v < 0.1:
                raise ValueError("Positive sentiment should have score > 0.1")
            elif sentiment_type == SentimentType.NEGATIVE and v > -0.1:
                raise ValueError("Negative sentiment should have score < -0.1")
            elif sentiment_type == SentimentType.VERY_NEGATIVE and v > -0.5:
                raise ValueError("Very negative sentiment should have score < -0.5")
        return v
    
    @property
    def entity_summary(self) -> Dict[EntityType, int]:
        """Get count of entities by type."""
        summary = {}
        for entity in self.entities:
            if entity.entity_type not in summary:
                summary[entity.entity_type] = 0
            summary[entity.entity_type] += 1
        return summary
    
    @property
    def top_entities(self, limit: int = 5) -> List[Entity]:
        """Get top entities by confidence score."""
        return sorted(self.entities, key=lambda e: e.confidence, reverse=True)[:limit]
    
    @property
    def top_topics(self, limit: int = 5) -> List[Topic]:
        """Get top topics by relevance."""
        return sorted(self.topics, key=lambda t: t.relevance, reverse=True)[:limit]
    
    @property
    def overall_score(self) -> float:
        """Calculate composite score for ranking."""
        weights = {
            'relevance': 0.30,
            'quality': 0.25,
            'impact': 0.20,
            'novelty': 0.15,
            'urgency': 0.10
        }
        
        return (
            weights['relevance'] * self.relevance_score +
            weights['quality'] * self.quality_score +
            weights['impact'] * self.impact_score +
            weights['novelty'] * self.novelty_score +
            weights['urgency'] * self.urgency_score
        )


class AnalysisRequest(BaseModel):
    """Request for content analysis."""
    
    content: str = Field(..., min_length=10, description="Content to analyze")
    content_type: ContentType = Field(default=ContentType.ARTICLE)
    content_id: Optional[UUID] = Field(None, description="Optional content identifier")
    
    # Analysis options
    extract_entities: bool = Field(default=True, description="Extract named entities")
    identify_topics: bool = Field(default=True, description="Identify topics")
    analyze_sentiment: bool = Field(default=True, description="Perform sentiment analysis")
    assess_impact: bool = Field(default=True, description="Assess industry impact")
    extract_research_info: bool = Field(default=True, description="Extract research information")
    
    # Processing options
    max_entities: int = Field(default=50, ge=1, le=200, description="Maximum entities to extract")
    max_topics: int = Field(default=20, ge=1, le=50, description="Maximum topics to identify")
    min_entity_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum entity confidence")
    min_topic_relevance: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum topic relevance")
    
    # Cost controls
    max_cost_usd: float = Field(default=0.05, ge=0.001, le=1.0, description="Maximum analysis cost")


class AnalysisResponse(BaseModel):
    """Response from content analysis."""
    
    success: bool = Field(..., description="Whether analysis succeeded")
    analysis: Optional[ContentAnalysis] = Field(None, description="Analysis results")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Processing metadata
    processing_time: float = Field(..., description="Total processing time")
    analysis_cost: float = Field(..., description="Actual analysis cost")
    model_used: str = Field(..., description="AI model used")
    
    # Quality indicators
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Analysis confidence")
    completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Analysis completeness")


class BatchAnalysisRequest(BaseModel):
    """Request for batch content analysis."""
    
    requests: List[AnalysisRequest] = Field(..., min_items=1, max_items=100)
    max_concurrent: int = Field(default=5, ge=1, le=20, description="Maximum concurrent analyses")
    max_total_cost: float = Field(default=1.0, ge=0.01, le=10.0, description="Maximum total cost")
    stop_on_error: bool = Field(default=False, description="Stop batch on first error")


class BatchAnalysisResponse(BaseModel):
    """Response from batch analysis."""
    
    success: bool = Field(..., description="Whether batch succeeded")
    results: List[AnalysisResponse] = Field(default_factory=list, description="Individual analysis results")
    
    # Batch statistics
    total_processed: int = Field(default=0, description="Number of items processed")
    successful_analyses: int = Field(default=0, description="Number of successful analyses")
    failed_analyses: int = Field(default=0, description="Number of failed analyses")
    
    # Performance metrics
    total_processing_time: float = Field(default=0.0, description="Total batch processing time")
    total_cost: float = Field(default=0.0, description="Total analysis cost")
    avg_processing_time: float = Field(default=0.0, description="Average processing time per item")
    avg_cost_per_analysis: float = Field(default=0.0, description="Average cost per analysis")
    
    # Quality metrics
    avg_confidence: float = Field(default=0.0, description="Average confidence score")
    avg_relevance: float = Field(default=0.0, description="Average relevance score")
    
    @property
    def success_rate(self) -> float:
        """Calculate batch success rate."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_analyses / self.total_processed) * 100


class AnalysisComparison(BaseModel):
    """Comparison between two content analyses."""
    
    content_a: ContentAnalysis
    content_b: ContentAnalysis
    
    # Similarity metrics
    content_similarity: float = Field(..., ge=0.0, le=1.0, description="Content similarity score")
    topic_overlap: float = Field(..., ge=0.0, le=1.0, description="Topic overlap score")
    entity_overlap: float = Field(..., ge=0.0, le=1.0, description="Entity overlap score")
    
    # Score differences
    relevance_diff: float = Field(..., description="Relevance score difference")
    quality_diff: float = Field(..., description="Quality score difference")
    impact_diff: float = Field(..., description="Impact score difference")
    
    # Comparison insights
    is_duplicate: bool = Field(..., description="Whether content appears to be duplicate")
    similarity_explanation: str = Field(..., description="Explanation of similarity assessment")
    key_differences: List[str] = Field(default_factory=list, description="Key differences identified")
    
    @property
    def overall_similarity(self) -> float:
        """Calculate overall similarity score."""
        return (self.content_similarity + self.topic_overlap + self.entity_overlap) / 3


# Export all models
__all__ = [
    "AnalysisStatus",
    "ContentType", 
    "SentimentType",
    "ImpactLevel",
    "EntityType",
    "Entity",
    "Topic",
    "ContentAnalysis",
    "AnalysisRequest",
    "AnalysisResponse",
    "BatchAnalysisRequest",
    "BatchAnalysisResponse",
    "AnalysisComparison",
]