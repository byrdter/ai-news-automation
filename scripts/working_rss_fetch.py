#!/usr/bin/env python3
"""
Working RSS Fetch Script

Uses the ACTUAL API from mcp_servers.rss_aggregator to fetch real articles.
This script uses the correct function names and parameters that actually exist.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich console for better output
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False
    print("Rich not available, using basic output")


def print_info(message: str):
    """Print info message with or without Rich."""
    if HAS_RICH and console:
        console.print(f"[cyan]{message}[/cyan]")
    else:
        print(f"ℹ️  {message}")


def print_success(message: str):
    """Print success message with or without Rich."""
    if HAS_RICH and console:
        console.print(f"[green]✅ {message}[/green]")
    else:
        print(f"✅ {message}")


def print_error(message: str):
    """Print error message with or without Rich."""
    if HAS_RICH and console:
        console.print(f"[red]❌ {message}[/red]")
    else:
        print(f"❌ {message}")


def print_warning(message: str):
    """Print warning message with or without Rich."""
    if HAS_RICH and console:
        console.print(f"[yellow]⚠️  {message}[/yellow]")
    else:
        print(f"⚠️  {message}")


class WorkingRSSFetcher:
    """RSS fetcher using the correct API calls."""
    
    def __init__(self):
        """Initialize the fetcher."""
        self.database_session = None
        self.Session = None
        
    def setup_database(self) -> bool:
        """Setup database connection."""
        try:
            from config.settings import get_settings
            from database.models import NewsSource, Article
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            settings = get_settings()
            
            # Create database URL
            db_url = (
                f"postgresql://{settings.database.user}:"
                f"{settings.database.password}@"
                f"{settings.database.host}:"
                f"{settings.database.port}/"
                f"{settings.database.name}"
            )
            
            # Create engine and session
            engine = create_engine(db_url, echo=False)
            self.Session = sessionmaker(bind=engine)
            
            # Test connection
            with self.Session() as session:
                source_count = session.query(NewsSource).count()
                article_count = session.query(Article).count()
                
            print_success(f"Database connected: {source_count} sources, {article_count} articles")
            return True
            
        except Exception as e:
            print_error(f"Database setup failed: {e}")
            return False
    
    async def test_rss_api(self) -> bool:
        """Test the RSS aggregator API."""
        try:
            print_info("Testing RSS aggregator imports...")
            
            # Test imports using the correct path
            from mcp_servers.rss_aggregator import initialize_sources, fetch_all_sources, BatchFetchRequest
            
            print_success("RSS aggregator imports successful")
            
            # Test initialization
            print_info("Initializing RSS sources...")
            init_result = await initialize_sources()
            
            if init_result.get('success', False):
                source_count = init_result.get('source_count', 0)
                print_success(f"RSS sources initialized: {source_count} sources")
            else:
                print_error(f"RSS initialization failed: {init_result.get('error', 'Unknown error')}")
                return False
            
            return True
            
        except Exception as e:
            print_error(f"RSS API test failed: {e}")
            return False
    
    async def fetch_articles(self, max_sources: int = None) -> Dict[str, Any]:
        """Fetch articles using the correct API."""
        try:
            from mcp_servers.rss_aggregator import fetch_all_sources, BatchFetchRequest, get_cached_articles
            
            print_info("Creating batch fetch request...")
            
            # Create request with correct parameters
            request = BatchFetchRequest(
                force_refresh=True,  # Get fresh articles
                max_articles_per_source=20,  # Limit per source
                include_content=True,  # Get full article content
                timeout_seconds=30
            )
            
            print_info("Fetching articles from RSS sources...")
            result = await fetch_all_sources(request)
            
            if not result.success:
                print_error(f"Article fetch failed: {result.error}")
                return {"success": False, "error": result.error}
            
            articles = result.articles
            print_success(f"Fetched {len(articles)} articles from {len(result.sources_processed)} sources")
            
            # Show some statistics
            if HAS_RICH and console:
                table = Table(title="Fetch Results", box=box.ROUNDED)
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green", justify="right")
                
                table.add_row("Total Articles", str(len(articles)))
                table.add_row("Sources Processed", str(len(result.sources_processed)))
                table.add_row("Successful Sources", str(result.successful_sources))
                table.add_row("Failed Sources", str(result.failed_sources))
                table.add_row("Processing Time", f"{result.processing_time_seconds:.2f}s")
                
                console.print(table)
            else:
                print(f"  Total Articles: {len(articles)}")
                print(f"  Sources Processed: {len(result.sources_processed)}")
                print(f"  Successful: {result.successful_sources}")
                print(f"  Failed: {result.failed_sources}")
            
            return {
                "success": True,
                "articles": articles,
                "result": result
            }
            
        except Exception as e:
            print_error(f"Article fetching failed: {e}")
            return {"success": False, "error": str(e)}
    
    def save_articles_to_database(self, articles: List[Any]) -> Dict[str, int]:
        """Save articles to database."""
        if not self.Session:
            print_error("Database not initialized")
            return {"saved": 0, "skipped": 0, "errors": 0}
        
        try:
            from database.models import Article, NewsSource
            
            stats = {"saved": 0, "skipped": 0, "errors": 0}
            
            with self.Session() as session:
                # Get source mapping
                sources = {source.name: source.id for source in session.query(NewsSource).all()}
                
                print_info(f"Processing {len(articles)} articles for database...")
                
                for article_data in articles:
                    try:
                        # Check if article already exists
                        existing = session.query(Article).filter(
                            Article.url == article_data.url
                        ).first()
                        
                        if existing:
                            stats["skipped"] += 1
                            continue
                        
                        # Find source ID
                        source_id = sources.get(article_data.source_name)
                        if not source_id:
                            print_warning(f"Unknown source: {article_data.source_name}")
                            continue
                        
                        # Create article
                        article = Article(
                            title=article_data.title[:500],  # Limit length
                            url=article_data.url,
                            content=article_data.content,
                            summary=article_data.summary or article_data.content[:500],
                            source_id=source_id,
                            published_at=article_data.published_date or datetime.now(timezone.utc),
                            author=article_data.author,
                            word_count=len(article_data.content.split()) if article_data.content else 0,
                            content_hash=article_data.content_hash,
                            
                            # Processing status
                            processed=False,
                            processing_stage='discovered',
                            
                            # Default scores
                            relevance_score=0.5,
                            quality_score=0.5,
                            sentiment_score=0.0,
                            urgency_score=0.0
                        )
                        
                        session.add(article)
                        stats["saved"] += 1
                        
                        if stats["saved"] % 10 == 0:
                            print_info(f"Processed {stats['saved']} articles...")
                    
                    except Exception as e:
                        print_warning(f"Error processing article: {e}")
                        stats["errors"] += 1
                
                # Commit all changes
                session.commit()
                print_success(f"Database update complete: {stats['saved']} saved, {stats['skipped']} skipped")
                
            return stats
            
        except Exception as e:
            print_error(f"Database save failed: {e}")
            return {"saved": 0, "skipped": 0, "errors": len(articles)}
    
    async def run_complete_fetch(self, max_sources: int = None) -> bool:
        """Run complete article fetch and database update."""
        print_info("🚀 Starting RSS article fetch process...")
        
        # Setup database
        if not self.setup_database():
            return False
        
        # Test RSS API
        if not await self.test_rss_api():
            return False
        
        # Fetch articles
        fetch_result = await self.fetch_articles(max_sources)
        if not fetch_result["success"]:
            return False
        
        articles = fetch_result["articles"]
        if not articles:
            print_warning("No articles fetched")
            return False
        
        # Save to database
        save_stats = self.save_articles_to_database(articles)
        
        if save_stats["saved"] > 0:
            print_success("🎉 RSS fetch completed successfully!")
            
            if HAS_RICH and console:
                panel_content = f"""
[green]Articles successfully fetched and saved![/green]

📊 **Results:**
• Articles fetched: {len(articles)}
• Articles saved: {save_stats['saved']}
• Articles skipped (duplicates): {save_stats['skipped']}
• Processing errors: {save_stats['errors']}

🎯 **Next Steps:**
• Check your database - it should now have real articles
• Test your CLI: it should show real data instead of demo data
• Run content analysis on the new articles
                """.strip()
                console.print(Panel(panel_content, title="Success!", border_style="green"))
            else:
                print(f"✅ Articles fetched: {len(articles)}")
                print(f"✅ Articles saved: {save_stats['saved']}")
                print(f"✅ Articles skipped: {save_stats['skipped']}")
            
            return True
        else:
            print_error("No articles were saved to database")
            return False


async def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch RSS articles using correct API')
    parser.add_argument('--max-sources', type=int, help='Maximum sources to fetch from')
    parser.add_argument('--test-only', action='store_true', help='Test API without saving to database')
    
    args = parser.parse_args()
    
    fetcher = WorkingRSSFetcher()
    
    try:
        if args.test_only:
            print_info("Running API test only...")
            db_ok = fetcher.setup_database()
            api_ok = await fetcher.test_rss_api()
            
            if db_ok and api_ok:
                print_success("🎉 All systems working! Ready to fetch articles.")
            else:
                print_error("❌ Some systems have issues")
        else:
            success = await fetcher.run_complete_fetch(args.max_sources)
            if success:
                print_success("🎉 RSS article fetch completed successfully!")
            else:
                print_error("❌ RSS article fetch failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print_warning("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())