"""
Example Database Models for AI News System
Location: examples/database/models.py

This demonstrates:
- SQLAlchemy models with PostgreSQL + pgvector integration
- Supabase connection patterns
- Vector embeddings for semantic search
- Relationships between entities
- Migration-friendly model structure
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
import uuid

# Base class for all models
Base = declarative_base()

class TimestampMixin:
    """Mixin for created/updated timestamps"""
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

class NewsSource(Base, TimestampMixin):
    """News sources configuration table"""
    __tablename__ = 'news_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    rss_feed_url = Column(String(500))
    
    # Source classification
    tier = Column(Integer, nullable=False)  # 1=highest quality, 3=lowest
    category = Column(String(100))  # e.g., "AI Research", "Industry News"
    
    # Status and configuration
    active = Column(Boolean, default=True)
    fetch_interval = Column(Integer, default=3600)  # seconds
    max_articles_per_fetch = Column(Integer, default=50)
    
    # Monitoring
    last_fetched_at = Column(DateTime(timezone=True))
    last_successful_fetch_at = Column(DateTime(timezone=True))
    consecutive_failures = Column(Integer, default=0)
    
    # Metadata
    metadata_json = Column(JSON)  # Additional configuration
    
    # Relationships
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")
    source_stats = relationship("SourceStatistics", back_populates="source", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('tier >= 1 AND tier <= 3', name='valid_tier'),
        CheckConstraint('fetch_interval >= 60', name='min_fetch_interval'),
        Index('idx_news_sources_active_tier', 'active', 'tier'),
    )

    def __repr__(self):
        return f"<NewsSource(name='{self.name}', tier={self.tier}, active={self.active})>"

class Article(Base, TimestampMixin):
    """Articles table with vector embeddings"""
    __tablename__ = 'articles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic article data
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    content = Column(Text)
    summary = Column(Text)
    
    # Source relationship
    source_id = Column(UUID(as_uuid=True), ForeignKey('news_sources.id'), nullable=False)
    source = relationship("NewsSource", back_populates="articles")
    
    # Publication info
    published_at = Column(DateTime(timezone=True))
    author = Column(String(255))
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_errors = Column(JSON)  # List of processing errors
    
    # AI analysis results
    relevance_score = Column(Float)  # 0.0 to 1.0
    sentiment_score = Column(Float)  # -1.0 to 1.0
    quality_score = Column(Float)  # 0.0 to 1.0
    
    # Categories and entities
    categories = Column(ARRAY(String(100)))  # e.g., ["AI Research", "GPT", "OpenAI"]
    entities = Column(JSON)  # Named entities extracted from content
    keywords = Column(ARRAY(String(100)))  # Key terms
    
    # Vector embeddings for semantic search
    title_embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small dimension
    content_embedding = Column(Vector(1536))
    
    # Engagement metrics (for future social media phases)
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Duplicate detection
    content_hash = Column(String(64))  # SHA-256 of normalized content
    duplicate_of_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'))
    duplicate_of = relationship("Article", remote_side=[id])
    
    # Relationships
    reports = relationship("ReportArticle", back_populates="article")
    social_posts = relationship("SocialMediaPost", back_populates="article")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_articles_source_published', 'source_id', 'published_at'),
        Index('idx_articles_processed_relevance', 'processed', 'relevance_score'),
        Index('idx_articles_content_hash', 'content_hash'),
        Index('idx_articles_categories', 'categories', postgresql_using='gin'),
        # Vector similarity indexes
        Index('idx_articles_title_embedding', 'title_embedding', postgresql_using='hnsw', 
              postgresql_with={'m': 16, 'ef_construction': 64}),
        Index('idx_articles_content_embedding', 'content_embedding', postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64}),
    )

    def __repr__(self):
        return f"<Article(title='{self.title[:50]}...', relevance={self.relevance_score})>"

class Report(Base, TimestampMixin):
    """Generated reports (daily, weekly, monthly)"""
    __tablename__ = 'reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report metadata
    report_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    report_date = Column(DateTime(timezone=True), nullable=False)
    title = Column(String(500), nullable=False)
    
    # Report content
    executive_summary = Column(Text)
    key_highlights = Column(JSON)  # List of key points
    trend_analysis = Column(Text)
    full_content = Column(Text)
    
    # Generation metadata
    generation_model = Column(String(100))  # e.g., "gpt-4o-mini"
    generation_cost = Column(Float)  # USD cost
    generation_duration = Column(Float)  # seconds
    
    # Status
    status = Column(String(50), default='draft')  # 'draft', 'published', 'archived'
    
    # Relationships
    report_articles = relationship("ReportArticle", back_populates="report", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('report_type', 'report_date', name='unique_report_per_date'),
        Index('idx_reports_type_date', 'report_type', 'report_date'),
    )

    def __repr__(self):
        return f"<Report(type='{self.report_type}', date='{self.report_date}', status='{self.status}')>"

class ReportArticle(Base):
    """Many-to-many relationship between reports and articles"""
    __tablename__ = 'report_articles'
    
    report_id = Column(UUID(as_uuid=True), ForeignKey('reports.id'), primary_key=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), primary_key=True)
    
    # Article's role in the report
    section = Column(String(100))  # e.g., "breaking_news", "key_developments", "trends"
    importance_score = Column(Float)  # 0.0 to 1.0
    summary_snippet = Column(Text)  # Custom summary for this report
    
    # Relationships
    report = relationship("Report", back_populates="report_articles")
    article = relationship("Article", back_populates="reports")

class Alert(Base, TimestampMixin):
    """Breaking news alerts"""
    __tablename__ = 'alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Alert content
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    urgency_level = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    
    # Associated article
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'))
    article = relationship("Article")
    
    # Delivery tracking
    sent_at = Column(DateTime(timezone=True))
    delivery_method = Column(String(50))  # 'email', 'webhook', 'slack'
    delivery_status = Column(String(50), default='pending')  # 'pending', 'sent', 'delivered', 'failed'
    
    # Alert rules that triggered this
    triggered_by_rules = Column(JSON)  # List of rule IDs that triggered this alert

    __table_args__ = (
        Index('idx_alerts_urgency_sent', 'urgency_level', 'sent_at'),
    )

class SocialMediaPost(Base, TimestampMixin):
    """Social media posts (for future phases)"""
    __tablename__ = 'social_media_posts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Post content
    platform = Column(String(50), nullable=False)  # 'twitter', 'linkedin', 'youtube'
    post_type = Column(String(50))  # 'tweet', 'thread', 'video', 'article'
    content = Column(Text, nullable=False)
    media_urls = Column(JSON)  # List of media URLs
    
    # Source article
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'))
    article = relationship("Article", back_populates="social_posts")
    
    # Publishing
    scheduled_for = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    platform_post_id = Column(String(255))  # ID from the social platform
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default='draft')  # 'draft', 'scheduled', 'published', 'failed'

class SourceStatistics(Base, TimestampMixin):
    """Daily statistics for news sources"""
    __tablename__ = 'source_statistics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source and date
    source_id = Column(UUID(as_uuid=True), ForeignKey('news_sources.id'), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Fetch statistics
    articles_fetched = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    articles_relevant = Column(Integer, default=0)
    
    # Quality metrics
    avg_relevance_score = Column(Float)
    avg_quality_score = Column(Float)
    
    # Performance metrics
    fetch_duration = Column(Float)  # seconds
    processing_duration = Column(Float)  # seconds
    error_count = Column(Integer, default=0)
    
    # Relationships
    source = relationship("NewsSource", back_populates="source_stats")
    
    __table_args__ = (
        UniqueConstraint('source_id', 'date', name='unique_source_date_stats'),
        Index('idx_source_stats_date', 'date'),
    )

class SystemMetrics(Base, TimestampMixin):
    """System-wide metrics and monitoring"""
    __tablename__ = 'system_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Timestamp (minute-level granularity)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Processing metrics
    articles_processed_per_minute = Column(Integer, default=0)
    avg_processing_time = Column(Float)  # seconds per article
    
    # Cost tracking
    llm_api_calls = Column(Integer, default=0)
    llm_tokens_used = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    
    # System health
    active_agents = Column(Integer, default=0)
    mcp_server_status = Column(JSON)  # Status of each MCP server
    error_rate = Column(Float, default=0.0)  # Errors per minute
    
    # Resource usage
    cpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    disk_usage_mb = Column(Float)
    
    __table_args__ = (
        Index('idx_system_metrics_timestamp', 'timestamp'),
    )

# Utility functions for database operations
class DatabaseService:
    """Service class for common database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_article_with_embedding(self, article_data: Dict[str, Any], 
                                    title_embedding: List[float], 
                                    content_embedding: List[float]) -> Article:
        """Create article with vector embeddings"""
        article = Article(
            **article_data,
            title_embedding=title_embedding,
            content_embedding=content_embedding
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def find_similar_articles(self, query_embedding: List[float], 
                            limit: int = 10, 
                            similarity_threshold: float = 0.8) -> List[Article]:
        """Find articles similar to query embedding"""
        # Using pgvector cosine similarity
        return (
            self.session.query(Article)
            .filter(Article.processed == True)
            .order_by(Article.content_embedding.cosine_distance(query_embedding))
            .limit(limit)
            .all()
        )
    
    def get_articles_for_report(self, start_date: datetime, 
                              end_date: datetime,
                              min_relevance: float = 0.7) -> List[Article]:
        """Get articles for report generation"""
        return (
            self.session.query(Article)
            .filter(
                Article.published_at.between(start_date, end_date),
                Article.relevance_score >= min_relevance,
                Article.processed == True
            )
            .order_by(Article.relevance_score.desc())
            .all()
        )
    
    def get_source_performance(self, days: int = 7) -> Dict[str, Any]:
        """Get source performance metrics"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        results = (
            self.session.query(NewsSource, SourceStatistics)
            .join(SourceStatistics)
            .filter(SourceStatistics.date >= cutoff_date)
            .all()
        )
        
        # Aggregate performance data
        performance = {}
        for source, stats in results:
            if source.name not in performance:
                performance[source.name] = {
                    'total_articles': 0,
                    'avg_relevance': 0.0,
                    'error_count': 0,
                    'tier': source.tier
                }
            
            performance[source.name]['total_articles'] += stats.articles_fetched
            performance[source.name]['avg_relevance'] += stats.avg_relevance_score or 0
            performance[source.name]['error_count'] += stats.error_count
        
        return performance

# Example usage and testing
def create_sample_data(session: Session):
    """Create sample data for testing"""
    
    # Create news sources
    sources = [
        NewsSource(
            name="OpenAI Blog",
            url="https://openai.com/blog",
            rss_feed_url="https://openai.com/blog/rss.xml",
            tier=1,
            category="AI Research"
        ),
        NewsSource(
            name="Google AI Blog", 
            url="https://ai.googleblog.com",
            rss_feed_url="https://ai.googleblog.com/feeds/posts/default",
            tier=1,
            category="AI Research"
        ),
        NewsSource(
            name="TechCrunch AI",
            url="https://techcrunch.com/category/artificial-intelligence/",
            tier=2,
            category="Industry News"
        )
    ]
    
    for source in sources:
        session.add(source)
    
    session.commit()
    print(f"Created {len(sources)} news sources")

if __name__ == "__main__":
    # This would typically be in a separate migration or setup script
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Example connection (replace with your Supabase connection string)
    DATABASE_URL = "postgresql://user:pass@localhost/ai_news_db"
    
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        create_sample_data(session)
        db_service = DatabaseService(session)
        performance = db_service.get_source_performance()
        print(f"Source performance: {performance}")
    finally:
        session.close()