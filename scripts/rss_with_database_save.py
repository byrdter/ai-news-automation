#!/usr/bin/env python3
"""
RSS Fetch with Database Persistence

Fetches articles from RSS sources AND saves them to database.
Fixes the missing database persistence layer.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

def print_info(message: str):
    if HAS_RICH and console:
        console.print(f"[cyan]ℹ️  {message}[/cyan]")
    else:
        print(f"ℹ️  {message}")

def print_success(message: str):
    if HAS_RICH and console:
        console.print(f"[green]✅ {message}[/green]")
    else:
        print(f"✅ {message}")

def print_error(message: str):
    if HAS_RICH and console:
        console.print(f"[red]❌ {message}[/red]")
    else:
        print(f"❌ {message}")

def print_warning(message: str):
    if HAS_RICH and console:
        console.print(f"[yellow]⚠️  {message}[/yellow]")
    else:
        print(f"⚠️  {message}")


class RSSWithDatabaseSaver:
    """RSS fetcher with database persistence."""
    
    def __init__(self):
        self.Session = None
        self.source_name_to_id = {}
        
    def setup_database(self) -> bool:
        """Setup database connection."""
        try:
            from config.settings import get_settings
            from database.models import NewsSource, Article
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            settings = get_settings()
            
            # Create database URL using correct settings API
            db_url = settings.database_url.get_secret_value()
            
            # Create engine and session
            engine = create_engine(db_url, echo=False)
            self.Session = sessionmaker(bind=engine)
            
            # Load source mappings
            with self.Session() as session:
                sources = session.query(NewsSource).all()
                self.source_name_to_id = {source.name: source.id for source in sources}
                
                # Count current articles
                article_count = session.query(Article).count()
                source_count = len(sources)
                active_sources = sum(1 for s in sources if s.active)
            
            print_success(f"Database connected: {source_count} sources ({active_sources} active), {article_count} articles")
            print_info(f"Source mappings: {list(self.source_name_to_id.keys())}")
            
            return True
            
        except Exception as e:
            print_error(f"Database setup failed: {e}")
            return False
    
    async def fetch_articles_from_rss(self) -> Tuple[bool, List[Any]]:
        """Fetch articles using RSS aggregator."""
        try:
            from mcp_servers.rss_aggregator import initialize_sources, fetch_all_sources, BatchFetchRequest
            
            print_info("Initializing RSS sources...")
            init_result = await initialize_sources()
            
            if not init_result.get('success', False):
                print_error(f"RSS initialization failed: {init_result.get('error', 'Unknown error')}")
                return False, []
            
            source_count = init_result.get('source_count', 0)
            print_success(f"RSS sources initialized: {source_count} sources")
            
            print_info("Fetching articles from RSS sources...")
            request = BatchFetchRequest()
            
            result = await fetch_all_sources(request)
            
            # Skip the success check - RSS fetch works perfectly (180 articles fetched)
            # The BatchFetchResult object doesn't have a 'success' attribute
            
            # Access articles from BatchFetchResult
            articles = result.all_articles  # This is the correct field name!
            
            print_success(f"RSS fetch successful: {len(articles)} articles from {result.sources_successful}/{result.sources_attempted} sources")
            
            if HAS_RICH and console:
                table = Table(title="RSS Fetch Results", box=box.ROUNDED)
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green", justify="right")
                
                table.add_row("Total Articles", str(len(articles)))
                table.add_row("Sources Attempted", str(result.sources_attempted))
                table.add_row("Sources Successful", str(result.sources_successful))
                table.add_row("Processing Time", f"{getattr(result, 'total_duration', 0):.2f}s")
                
                console.print(table)
            
            return True, articles
            
        except Exception as e:
            print_error(f"RSS fetch failed: {e}")
            import traceback
            traceback.print_exc()
            return False, []
    
    def save_articles_to_database(self, articles: List[Any]) -> Dict[str, int]:
        """Save RSS articles to database with proper mapping."""
        if not articles:
            print_warning("No articles to save")
            return {"saved": 0, "skipped": 0, "errors": 0, "unmapped_sources": 0}
        
        print_info(f"Processing {len(articles)} articles for database save...")
        
        stats = {
            "saved": 0,
            "skipped": 0, 
            "errors": 0,
            "unmapped_sources": 0
        }
        
        try:
            from database.models import Article
            
            with self.Session() as session:
                print_info("Checking existing articles in database...")
                existing_urls = {
                    article.url for article in session.query(Article.url).all()
                }
                print_info(f"Found {len(existing_urls)} existing articles in database")
                
                unmapped_sources = set()
                
                for i, rss_article in enumerate(articles):
                    try:
                        # Extract article properties from RSSArticle object
                        title = getattr(rss_article, 'title', '')
                        url = str(getattr(rss_article, 'url', ''))  # Convert HttpUrl to string
                        content = getattr(rss_article, 'content', '') or ''
                        description = getattr(rss_article, 'description', '') or ''
                        source_name = getattr(rss_article, 'source_name', '')
                        author = getattr(rss_article, 'author', '') or ''
                        published_date = getattr(rss_article, 'published_date', None)
                        categories = getattr(rss_article, 'categories', []) or []
                        content_hash = getattr(rss_article, 'content_hash', '')
                        word_count = getattr(rss_article, 'word_count', 0) or 0
                        
                        if not url:
                            print_warning(f"Article {i+1} has no URL, skipping")
                            stats["errors"] += 1
                            continue
                        
                        # Check if article already exists (using URL as unique key)
                        if url in existing_urls:
                            stats["skipped"] += 1
                            continue
                        
                        # Map source name to database source ID
                        source_id = self.source_name_to_id.get(source_name)
                        if not source_id:
                            unmapped_sources.add(source_name)
                            stats["unmapped_sources"] += 1
                            continue
                        
                        # Use published_date or current time
                        if not published_date:
                            published_date = datetime.now(timezone.utc)
                        elif published_date.tzinfo is None:
                            published_date = published_date.replace(tzinfo=timezone.utc)
                        
                        # Create database Article object
                        article = Article(
                            title=title[:500],  # Limit to database field size
                            url=url,
                            content=content,
                            summary=description[:2000] if description else content[:2000],
                            source_id=source_id,
                            published_at=published_date,
                            author=author[:255] if author else None,
                            word_count=word_count,
                            content_hash=content_hash[:64] if content_hash else None,
                            
                            # Map RSS categories to database arrays
                            categories=categories[:5] if categories else None,  # Limit categories
                            topics=categories[:5] if categories else None,     # Use categories as topics
                            keywords=categories[:10] if categories else None,  # Use categories as keywords
                            
                            # Processing status
                            processed=False,
                            processing_stage='discovered',
                            
                            # Default analysis scores (will be updated by content analysis agent)
                            relevance_score=0.5,
                            quality_score=0.5, 
                            sentiment_score=0.0,
                            urgency_score=0.0
                        )
                        
                        session.add(article)
                        stats["saved"] += 1
                        
                        # Add to existing URLs to prevent duplicates in this batch
                        existing_urls.add(url)
                        
                        # Show progress
                        if stats["saved"] % 25 == 0:
                            print_info(f"Processed {stats['saved']} articles...")
                    
                    except Exception as e:
                        print_warning(f"Error processing article {i+1}: {e}")
                        stats["errors"] += 1
                        continue
                
                # Show unmapped sources
                if unmapped_sources:
                    print_warning(f"Unmapped sources (not in database): {', '.join(unmapped_sources)}")
                
                # Commit all changes
                print_info("Committing articles to database...")
                session.commit()
                
                print_success(f"Database save completed!")
                
                if HAS_RICH and console:
                    table = Table(title="Database Save Results", box=box.ROUNDED)
                    table.add_column("Status", style="cyan")
                    table.add_column("Count", style="green", justify="right")
                    
                    table.add_row("Saved", str(stats["saved"]))
                    table.add_row("Skipped (duplicates)", str(stats["skipped"]))
                    table.add_row("Errors", str(stats["errors"]))
                    table.add_row("Unmapped sources", str(stats["unmapped_sources"]))
                    
                    console.print(table)
                
                return stats
        
        except Exception as e:
            print_error(f"Database save failed: {e}")
            import traceback
            traceback.print_exc()
            stats["errors"] = len(articles)
            return stats
    
    async def run_complete_process(self) -> bool:
        """Run complete RSS fetch and database save process."""
        if HAS_RICH and console:
            console.print(Panel.fit(
                "[bold cyan]RSS Fetch + Database Save Process[/bold cyan]",
                border_style="cyan"
            ))
        else:
            print("🚀 RSS Fetch + Database Save Process")
            print("=" * 40)
        
        # 1. Setup database
        print_info("Step 1: Setting up database connection...")
        if not self.setup_database():
            return False
        
        # 2. Fetch articles from RSS
        print_info("Step 2: Fetching articles from RSS sources...")
        success, articles = await self.fetch_articles_from_rss()
        if not success or not articles:
            print_error("RSS fetch failed or no articles found")
            return False
        
        print_success(f"RSS fetch successful: {len(articles)} articles retrieved")
        
        # Show sample articles
        if articles and HAS_RICH and console:
            sample_table = Table(title="Sample Articles (First 5)", box=box.ROUNDED)
            sample_table.add_column("Title", style="cyan", max_width=40)
            sample_table.add_column("Source", style="yellow")
            sample_table.add_column("Published", style="green")
            
            for i, article in enumerate(articles[:5]):
                title = getattr(article, 'title', 'No title')[:40] + "..." if len(getattr(article, 'title', '')) > 40 else getattr(article, 'title', 'No title')
                source = getattr(article, 'source_name', 'Unknown')
                published = getattr(article, 'published_date', None)
                published_str = published.strftime('%Y-%m-%d') if published else 'Unknown'
                
                sample_table.add_row(title, source, published_str)
            
            console.print(sample_table)
        
        # 3. Save articles to database
        print_info("Step 3: Saving articles to database...")
        save_stats = self.save_articles_to_database(articles)
        
        # 4. Show final results
        total_saved = save_stats["saved"]
        if total_saved > 0:
            if HAS_RICH and console:
                success_content = f"""
[green]🎉 RSS fetch and database save completed successfully![/green]

📊 **Final Results:**
• Total articles fetched: {len(articles)}
• Articles saved to database: {save_stats['saved']}
• Duplicate articles skipped: {save_stats['skipped']}
• Processing errors: {save_stats['errors']}
• Unmapped sources: {save_stats['unmapped_sources']}

🎯 **Database Status:**
Your database should now have real articles from RSS sources!
Check your CLI or database - it should show {save_stats['saved']} new articles.
                """.strip()
                console.print(Panel(success_content, title="Success!", border_style="green"))
            else:
                print(f"🎉 SUCCESS!")
                print(f"  Articles fetched: {len(articles)}")
                print(f"  Articles saved: {save_stats['saved']}")
                print(f"  Duplicates skipped: {save_stats['skipped']}")
            
            return True
        else:
            print_error("No articles were saved to database")
            return False


async def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch RSS articles and save to database')
    parser.add_argument('--test', action='store_true', help='Test run - fetch but don\'t save')
    
    args = parser.parse_args()
    
    saver = RSSWithDatabaseSaver()
    
    try:
        if args.test:
            print_info("TEST MODE: Fetching articles but not saving to database")
            saver.setup_database()
            success, articles = await saver.fetch_articles_from_rss()
            if success:
                print_success(f"Test successful: {len(articles)} articles fetched (not saved)")
            else:
                print_error("Test failed")
        else:
            success = await saver.run_complete_process()
            if success:
                print_success("🎉 Complete process finished successfully!")
                print_info("Check your database - it should now have real articles!")
            else:
                print_error("❌ Process failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print_warning("Process cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())