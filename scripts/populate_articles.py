#!/usr/bin/env python3
"""
Article Population Script

Fetches real articles from configured RSS sources and populates the database.
Fixes the object structure issues and connects MCP server to database.
"""

import asyncio
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import UUID

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from config.settings import get_settings
from database.models import NewsSource, Article, Base
from mcp_servers.rss_aggregator import FeedFetchRequest, fetch_rss_feed, RSSAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticlePopulator:
    """Populate database with real articles from RSS sources."""
    
    def __init__(self):
        """Initialize article populator."""
        self.settings = get_settings()
        self.engine = None
        self.Session = None
        self.aggregator = RSSAggregator()
    
    def setup_database(self):
        """Setup database connection."""
        try:
            # Create database URL
            db_url = (
                f"postgresql://{self.settings.database.user}:"
                f"{self.settings.database.password}@"
                f"{self.settings.database.host}:"
                f"{self.settings.database.port}/"
                f"{self.settings.database.name}"
            )
            
            logger.info("Connecting to database...")
            
            # Create engine and session factory
            self.engine = create_engine(db_url, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            logger.info("Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_active_sources(self) -> List[NewsSource]:
        """Get active RSS sources from database."""
        with self.Session() as session:
            sources = session.query(NewsSource).filter(
                NewsSource.active == True,
                NewsSource.rss_feed_url.isnot(None)
            ).order_by(NewsSource.tier, NewsSource.name).all()
            
            logger.info(f"Found {len(sources)} active RSS sources")
            return sources
    
    async def fetch_articles_from_source(self, source: NewsSource) -> Dict[str, Any]:
        """Fetch articles from a single RSS source."""
        logger.info(f"Fetching articles from: {source.name}")
        
        try:
            # Create proper request object
            request = FeedFetchRequest(
                feed_url=source.rss_feed_url,
                max_articles=source.max_articles_per_fetch or 50,
                timeout=30
            )
            
            # Fetch articles using MCP tool
            result = await fetch_rss_feed(request)
            
            if result.error:
                logger.error(f"Feed fetch failed for {source.name}: {result.error}")
                return {
                    'success': False,
                    'source_id': source.id,
                    'source_name': source.name,
                    'error': result.error,
                    'articles_fetched': 0
                }
            
            logger.info(f"Successfully fetched {len(result.articles)} articles from {source.name}")
            
            return {
                'success': True,
                'source_id': source.id,
                'source_name': source.name,
                'feed_title': result.title,
                'feed_description': result.description,
                'articles': result.articles,
                'articles_fetched': len(result.articles),
                'fetch_time': result.fetch_time
            }
            
        except Exception as e:
            logger.error(f"Error fetching from {source.name}: {e}")
            return {
                'success': False,
                'source_id': source.id,
                'source_name': source.name,
                'error': str(e),
                'articles_fetched': 0
            }
    
    def save_articles_to_database(self, fetch_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save fetched articles to database."""
        stats = {
            'total_articles': 0,
            'new_articles': 0,
            'duplicate_articles': 0,
            'failed_articles': 0
        }
        
        with self.Session() as session:
            for result in fetch_results:
                if not result['success']:
                    continue
                
                source_id = result['source_id']
                
                # Update source metadata
                source = session.get(NewsSource, source_id)
                if source:
                    source.last_fetched_at = datetime.now(timezone.utc)
                    source.last_successful_fetch_at = datetime.now(timezone.utc)
                    source.consecutive_failures = 0
                
                # Process each article
                for article_data in result['articles']:
                    try:
                        stats['total_articles'] += 1
                        
                        # Check if article already exists
                        existing_article = session.query(Article).filter(
                            Article.url == article_data['url']
                        ).first()
                        
                        if existing_article:
                            stats['duplicate_articles'] += 1
                            continue
                        
                        # Parse published date
                        published_at = None
                        if article_data.get('published_date'):
                            try:
                                if isinstance(article_data['published_date'], str):
                                    published_at = datetime.fromisoformat(
                                        article_data['published_date'].replace('Z', '+00:00')
                                    )
                                else:
                                    published_at = article_data['published_date']
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Invalid date format for article {article_data.get('title', 'Unknown')}: {e}")
                                published_at = datetime.now(timezone.utc)
                        else:
                            published_at = datetime.now(timezone.utc)
                        
                        # Create new article
                        article = Article(
                            title=article_data.get('title', '').strip()[:500],  # Limit title length
                            url=article_data['url'],
                            content=article_data.get('content', ''),
                            summary=article_data.get('summary', ''),
                            source_id=source_id,
                            published_at=published_at,
                            author=article_data.get('author', ''),
                            word_count=article_data.get('word_count', 0),
                            content_hash=article_data.get('content_hash', ''),
                            
                            # Set default analysis scores (will be updated by content analysis)
                            relevance_score=0.5,  # Default until analyzed
                            quality_score=0.5,
                            sentiment_score=0.0,
                            urgency_score=0.0,
                            
                            # Processing status
                            processed=False,
                            processing_stage='discovered',
                            
                            # Categories and topics from RSS tags
                            categories=[article_data.get('tags', [])[:3]] if article_data.get('tags') else None,
                            topics=article_data.get('tags', [])[:5] if article_data.get('tags') else None,
                            keywords=article_data.get('tags', [])[:10] if article_data.get('tags') else None,
                        )
                        
                        session.add(article)
                        stats['new_articles'] += 1
                        
                        if stats['new_articles'] % 10 == 0:
                            logger.info(f"Processed {stats['new_articles']} new articles...")
                    
                    except Exception as e:
                        logger.error(f"Error saving article {article_data.get('title', 'Unknown')}: {e}")
                        stats['failed_articles'] += 1
                
                # Update source total article count
                if source:
                    source.total_articles_fetched = (source.total_articles_fetched or 0) + result['articles_fetched']
            
            # Commit all changes
            try:
                session.commit()
                logger.info(f"Successfully committed {stats['new_articles']} new articles to database")
            except Exception as e:
                logger.error(f"Database commit failed: {e}")
                session.rollback()
                raise
        
        return stats
    
    async def populate_articles(self, max_sources: Optional[int] = None) -> Dict[str, Any]:
        """Main method to populate articles from all active sources."""
        logger.info("Starting article population process...")
        
        # Setup database connection
        if not self.setup_database():
            return {'success': False, 'error': 'Database connection failed'}
        
        # Get active sources
        sources = self.get_active_sources()
        if not sources:
            return {'success': False, 'error': 'No active RSS sources found in database'}
        
        # Limit sources if specified
        if max_sources:
            sources = sources[:max_sources]
        
        logger.info(f"Processing {len(sources)} RSS sources...")
        
        # Fetch articles from all sources
        fetch_results = []
        
        for source in sources:
            try:
                result = await self.fetch_articles_from_source(source)
                fetch_results.append(result)
                
                # Small delay between sources to be respectful
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to process source {source.name}: {e}")
                fetch_results.append({
                    'success': False,
                    'source_id': source.id,
                    'source_name': source.name,
                    'error': str(e),
                    'articles_fetched': 0
                })
        
        # Save articles to database
        try:
            stats = self.save_articles_to_database(fetch_results)
        except Exception as e:
            logger.error(f"Failed to save articles to database: {e}")
            return {'success': False, 'error': f'Database save failed: {e}'}
        
        # Calculate summary statistics
        successful_sources = sum(1 for r in fetch_results if r['success'])
        failed_sources = len(fetch_results) - successful_sources
        total_fetched = sum(r.get('articles_fetched', 0) for r in fetch_results)
        
        summary = {
            'success': True,
            'sources_processed': len(sources),
            'sources_successful': successful_sources,
            'sources_failed': failed_sources,
            'total_articles_fetched': total_fetched,
            'new_articles_saved': stats['new_articles'],
            'duplicate_articles_skipped': stats['duplicate_articles'],
            'failed_articles': stats['failed_articles'],
            'processing_results': fetch_results
        }
        
        logger.info(f"Article population completed!")
        logger.info(f"Sources: {successful_sources}/{len(sources)} successful")
        logger.info(f"Articles: {stats['new_articles']} new, {stats['duplicate_articles']} duplicates")
        
        return summary
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.aggregator.cleanup()
    
    def test_single_source(self, source_name: str) -> None:
        """Test fetching from a single source (for debugging)."""
        with self.Session() as session:
            source = session.query(NewsSource).filter(
                NewsSource.name == source_name,
                NewsSource.active == True
            ).first()
            
            if not source:
                logger.error(f"Source '{source_name}' not found or inactive")
                return
            
            logger.info(f"Testing source: {source.name}")
            logger.info(f"URL: {source.rss_feed_url}")
            
            async def _test():
                result = await self.fetch_articles_from_source(source)
                if result['success']:
                    logger.info(f"Test successful: {result['articles_fetched']} articles fetched")
                    
                    # Show first few articles
                    for i, article in enumerate(result['articles'][:3]):
                        logger.info(f"Article {i+1}: {article.get('title', 'No title')}")
                else:
                    logger.error(f"Test failed: {result['error']}")
                
                await self.cleanup()
            
            asyncio.run(_test())


async def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate database with RSS articles')
    parser.add_argument('--max-sources', type=int, help='Maximum number of sources to process')
    parser.add_argument('--test-source', type=str, help='Test a single source by name')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without saving')
    
    args = parser.parse_args()
    
    populator = ArticlePopulator()
    
    try:
        if args.test_source:
            # Test single source
            populator.test_single_source(args.test_source)
        else:
            # Run full population
            result = await populator.populate_articles(max_sources=args.max_sources)
            
            if result['success']:
                print("\n" + "="*50)
                print("ARTICLE POPULATION SUMMARY")
                print("="*50)
                print(f"Sources processed: {result['sources_processed']}")
                print(f"Sources successful: {result['sources_successful']}")
                print(f"Sources failed: {result['sources_failed']}")
                print(f"Total articles fetched: {result['total_articles_fetched']}")
                print(f"New articles saved: {result['new_articles_saved']}")
                print(f"Duplicate articles skipped: {result['duplicate_articles_skipped']}")
                print(f"Failed articles: {result['failed_articles']}")
                print("="*50)
                
                # Show per-source results
                print("\nPER-SOURCE RESULTS:")
                for r in result['processing_results']:
                    status = "✅" if r['success'] else "❌"
                    articles = r.get('articles_fetched', 0)
                    print(f"{status} {r['source_name']}: {articles} articles")
                    if not r['success']:
                        print(f"   Error: {r.get('error', 'Unknown error')}")
            else:
                print(f"❌ Population failed: {result.get('error', 'Unknown error')}")
    
    finally:
        await populator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())