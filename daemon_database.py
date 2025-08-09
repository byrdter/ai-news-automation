#!/usr/bin/env python3
"""
Daemon Database Helper

Provides database operations for the automation daemon.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, select, and_, or_, desc, func
from sqlalchemy.orm import sessionmaker, selectinload

from database.models import Article, NewsSource
from config.settings import get_settings
from mcp_servers.rss_aggregator.schemas import RSSArticle

logger = logging.getLogger(__name__)


class DaemonDatabase:
    """Database operations for the automation daemon."""
    
    _engine = None
    _Session = None
    
    @classmethod
    def _get_session(cls):
        """Get database session, creating engine if needed."""
        if cls._Session is None:
            settings = get_settings()
            db_url = settings.database_url.get_secret_value()
            cls._engine = create_engine(db_url, echo=False)
            cls._Session = sessionmaker(bind=cls._engine)
        return cls._Session()

    @staticmethod
    def save_rss_articles(rss_articles: List[RSSArticle]) -> Dict[str, int]:
        """
        Save RSS articles to database, avoiding duplicates.
        
        Args:
            rss_articles: List of RSSArticle objects
            
        Returns:
            Dict with counts: {'saved': int, 'skipped': int, 'errors': int}
        """
        results = {'saved': 0, 'skipped': 0, 'errors': 0, 'unmapped': 0}
        
        try:
            with DaemonDatabase._get_session() as session:
                # Get all sources for mapping
                sources = session.query(NewsSource).all()
                source_url_map = {source.rss_url: source for source in sources if source.rss_url}
                source_name_map = {source.name.lower(): source for source in sources}
                
                for rss_article in rss_articles:
                    try:
                        # Find matching source
                        source = source_url_map.get(rss_article.source_url)
                        if not source:
                            # Try mapping by source name
                            source = source_name_map.get(rss_article.source_name.lower())
                        
                        if not source:
                            logger.warning(f"No database source found for: {rss_article.source_name}")
                            results['unmapped'] += 1
                            continue
                        
                        # Check if article already exists
                        existing = session.query(Article).filter(
                            and_(
                                Article.source_id == source.id,
                                or_(
                                    Article.url == rss_article.link,
                                    and_(
                                        Article.title == rss_article.title,
                                        Article.published_at == rss_article.published
                                    )
                                )
                            )
                        ).first()
                        
                        if existing:
                            results['skipped'] += 1
                            continue
                        
                        # Create new article
                        article = Article(
                            title=rss_article.title[:500] if rss_article.title else "Untitled",
                            url=rss_article.link,
                            content=rss_article.description,
                            summary=rss_article.summary or (rss_article.description[:500] if rss_article.description else None),
                            author=rss_article.author,
                            published_at=rss_article.published,
                            fetched_at=datetime.utcnow(),
                            source_id=source.id,
                            # Set defaults for analysis fields
                            relevance_score=0.0,
                            quality_score=0.0,
                            sentiment_score=0.0,
                            is_analyzed=False
                        )
                        
                        session.add(article)
                        results['saved'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error saving article '{rss_article.title}': {e}")
                        results['errors'] += 1
                        continue
                
                # Commit all changes
                session.commit()
                logger.info(f"Database save completed: {results}")
                
        except Exception as e:
            logger.error(f"Database save operation failed: {e}")
            results['errors'] = len(rss_articles)
            
        return results

    @staticmethod
    async def get_unanalyzed_articles(limit: int = 50) -> List[Article]:
        """
        Get articles that haven't been analyzed yet.
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of unanalyzed Article objects
        """
        try:
            async with get_database_session() as session:
                result = await session.execute(
                    select(Article)
                    .options(selectinload(Article.source))
                    .where(Article.is_analyzed == False)
                    .where(Article.content.isnot(None))  # Only articles with content
                    .order_by(desc(Article.published_at))
                    .limit(limit)
                )
                
                articles = result.scalars().all()
                logger.info(f"Found {len(articles)} unanalyzed articles")
                return list(articles)
                
        except Exception as e:
            logger.error(f"Failed to get unanalyzed articles: {e}")
            return []

    @staticmethod
    async def update_article_analysis(article_id: int, analysis_data: Any) -> bool:
        """
        Update article with analysis results.
        
        Args:
            article_id: ID of article to update
            analysis_data: Analysis results from ContentAnalysis
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with get_database_session() as session:
                # Get the article
                result = await session.execute(
                    select(Article).where(Article.id == article_id)
                )
                article = result.scalars().first()
                
                if not article:
                    logger.error(f"Article {article_id} not found")
                    return False
                
                # Update with analysis results
                article.relevance_score = analysis_data.relevance_score
                article.quality_score = analysis_data.quality_score
                article.sentiment_score = analysis_data.sentiment_score
                article.impact_score = getattr(analysis_data, 'impact_score', 0.0)
                article.urgency_score = getattr(analysis_data, 'urgency_score', 0.0)
                article.novelty_score = getattr(analysis_data, 'novelty_score', 0.0)
                article.primary_category = analysis_data.primary_category
                article.ai_domains = analysis_data.ai_domains
                article.key_entities = [e.text for e in analysis_data.entities] if analysis_data.entities else []
                article.key_topics = [t.name for t in analysis_data.topics] if analysis_data.topics else []
                article.is_analyzed = True
                article.analyzed_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated analysis for article {article_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update article analysis: {e}")
            return False

    @staticmethod
    async def get_articles_since(since: datetime, limit: int = 100) -> List[Article]:
        """
        Get articles published since given datetime.
        
        Args:
            since: Datetime to filter from
            limit: Maximum number of articles
            
        Returns:
            List of Article objects
        """
        try:
            async with get_database_session() as session:
                result = await session.execute(
                    select(Article)
                    .options(selectinload(Article.source))
                    .where(Article.published_at >= since)
                    .order_by(desc(Article.published_at))
                    .limit(limit)
                )
                
                articles = result.scalars().all()
                logger.info(f"Found {len(articles)} articles since {since}")
                return list(articles)
                
        except Exception as e:
            logger.error(f"Failed to get recent articles: {e}")
            return []

    @staticmethod
    async def get_top_articles_by_relevance(since: datetime, limit: int = 10) -> List[Article]:
        """
        Get top articles by relevance score since given datetime.
        
        Args:
            since: Datetime to filter from
            limit: Maximum number of articles
            
        Returns:
            List of top-relevance Article objects
        """
        try:
            async with get_database_session() as session:
                result = await session.execute(
                    select(Article)
                    .options(selectinload(Article.source))
                    .where(Article.published_at >= since)
                    .where(Article.is_analyzed == True)
                    .where(Article.relevance_score > 0.5)  # Only relevant articles
                    .order_by(desc(Article.relevance_score))
                    .limit(limit)
                )
                
                articles = result.scalars().all()
                logger.info(f"Found {len(articles)} top articles since {since}")
                return list(articles)
                
        except Exception as e:
            logger.error(f"Failed to get top articles: {e}")
            return []

    @staticmethod
    async def get_breaking_news(urgency_threshold: float = 0.8) -> List[Article]:
        """
        Get breaking news articles based on urgency score.
        
        Args:
            urgency_threshold: Minimum urgency score
            
        Returns:
            List of breaking news Article objects
        """
        try:
            # Get articles from last 24 hours with high urgency
            since = datetime.utcnow() - timedelta(hours=24)
            
            async with get_database_session() as session:
                result = await session.execute(
                    select(Article)
                    .options(selectinload(Article.source))
                    .where(Article.published_at >= since)
                    .where(Article.is_analyzed == True)
                    .where(Article.urgency_score >= urgency_threshold)
                    .order_by(desc(Article.urgency_score))
                    .limit(10)
                )
                
                articles = result.scalars().all()
                logger.info(f"Found {len(articles)} breaking news articles")
                return list(articles)
                
        except Exception as e:
            logger.error(f"Failed to get breaking news: {e}")
            return []

    @staticmethod
    async def get_database_stats() -> Dict[str, Any]:
        """
        Get database statistics for monitoring.
        
        Returns:
            Dictionary with database stats
        """
        try:
            async with get_database_session() as session:
                # Total articles
                total_articles_result = await session.execute(
                    select(func.count(Article.id))
                )
                total_articles = total_articles_result.scalar()
                
                # Analyzed articles
                analyzed_result = await session.execute(
                    select(func.count(Article.id)).where(Article.is_analyzed == True)
                )
                analyzed_articles = analyzed_result.scalar()
                
                # Recent articles (last 24 hours)
                since_24h = datetime.utcnow() - timedelta(hours=24)
                recent_result = await session.execute(
                    select(func.count(Article.id)).where(Article.published_at >= since_24h)
                )
                recent_articles = recent_result.scalar()
                
                # Active sources
                sources_result = await session.execute(
                    select(func.count(NewsSource.id)).where(NewsSource.is_active == True)
                )
                active_sources = sources_result.scalar()
                
                # Average relevance score
                avg_relevance_result = await session.execute(
                    select(func.avg(Article.relevance_score))
                    .where(Article.is_analyzed == True)
                )
                avg_relevance = avg_relevance_result.scalar() or 0.0
                
                return {
                    'total_articles': total_articles,
                    'analyzed_articles': analyzed_articles,
                    'unanalyzed_articles': total_articles - analyzed_articles,
                    'recent_articles_24h': recent_articles,
                    'active_sources': active_sources,
                    'avg_relevance_score': float(avg_relevance),
                    'analysis_completion_rate': (analyzed_articles / max(total_articles, 1)) * 100
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    @staticmethod
    async def check_database_health() -> bool:
        """
        Check database connectivity and basic health.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            async with get_database_session() as session:
                # Simple query to test connectivity
                result = await session.execute(select(func.now()))
                db_time = result.scalar()
                
                logger.debug(f"Database health check successful: {db_time}")
                return True
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    @staticmethod
    async def cleanup_old_articles(days_to_keep: int = 90) -> int:
        """
        Clean up articles older than specified days.
        
        Args:
            days_to_keep: Number of days of articles to retain
            
        Returns:
            Number of articles deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            async with get_database_session() as session:
                # Get count first
                count_result = await session.execute(
                    select(func.count(Article.id))
                    .where(Article.published_at < cutoff_date)
                )
                count_to_delete = count_result.scalar()
                
                if count_to_delete > 0:
                    # Delete old articles
                    delete_result = await session.execute(
                        select(Article)
                        .where(Article.published_at < cutoff_date)
                    )
                    old_articles = delete_result.scalars().all()
                    
                    for article in old_articles:
                        await session.delete(article)
                    
                    await session.commit()
                    logger.info(f"Cleaned up {count_to_delete} articles older than {days_to_keep} days")
                
                return count_to_delete
                
        except Exception as e:
            logger.error(f"Failed to cleanup old articles: {e}")
            return 0