#!/usr/bin/env python3
"""
Simple RSS Fetch Script

Simplified version that works with the available API and handles missing dependencies.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def simple_fetch():
    """Simple RSS fetch using the confirmed working API."""
    
    print("🚀 Simple RSS Fetch Test")
    print("=" * 30)
    
    try:
        # Use the imports you confirmed work
        print("1. Importing RSS aggregator...")
        from mcp_servers.rss_aggregator import initialize_sources, fetch_all_sources, BatchFetchRequest
        print("   ✅ Imports successful")
        
        # Initialize sources
        print("\n2. Initializing RSS sources...")
        init_result = await initialize_sources()
        print(f"   Result: {init_result}")
        
        if not init_result.get('success', False):
            print(f"   ❌ Initialization failed")
            return False
            
        source_count = init_result.get('source_count', 0)
        print(f"   ✅ Initialized {source_count} RSS sources")
        
        # Create fetch request
        print("\n3. Creating fetch request...")
        request = BatchFetchRequest()
        print(f"   ✅ Request created: {type(request)}")
        
        # Fetch articles
        print("\n4. Fetching articles...")
        result = await fetch_all_sources(request)
        print(f"   Success: {result.success}")
        
        if not result.success:
            print(f"   ❌ Fetch failed: {getattr(result, 'error', 'Unknown error')}")
            return False
        
        articles = getattr(result, 'articles', [])
        print(f"   ✅ Fetched {len(articles)} articles")
        
        # Show sample articles
        if articles:
            print(f"\n📰 Sample Articles (first 3):")
            for i, article in enumerate(articles[:3]):
                title = getattr(article, 'title', 'No title')
                source = getattr(article, 'source_name', 'Unknown source')
                url = getattr(article, 'url', 'No URL')
                print(f"   {i+1}. {title[:50]}...")
                print(f"      Source: {source}")
                print(f"      URL: {url}")
        
        print(f"\n✅ SUCCESS! Found {len(articles)} real articles from RSS sources")
        return True, articles
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please install missing dependencies:")
        print("   pip install pydantic pydantic-settings")
        return False, []
    
    except Exception as e:
        print(f"❌ Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []

async def save_to_database(articles):
    """Save articles to database."""
    if not articles:
        print("No articles to save")
        return
    
    print(f"\n💾 Saving {len(articles)} articles to database...")
    
    try:
        # Import database modules
        from config.settings import get_settings
        from database.models import NewsSource, Article
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime, timezone
        
        # Setup database connection
        settings = get_settings()
        db_url = (
            f"postgresql://{settings.database.user}:"
            f"{settings.database.password}@"
            f"{settings.database.host}:"
            f"{settings.database.port}/"
            f"{settings.database.name}"
        )
        
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Get source mapping
            sources = {source.name: source.id for source in session.query(NewsSource).all()}
            print(f"   Found {len(sources)} database sources")
            
            saved_count = 0
            skipped_count = 0
            
            for article_data in articles:
                try:
                    # Get article properties
                    title = getattr(article_data, 'title', '')
                    url = getattr(article_data, 'url', '')
                    content = getattr(article_data, 'content', '')
                    source_name = getattr(article_data, 'source_name', '')
                    
                    if not url:
                        continue
                    
                    # Check if exists
                    existing = session.query(Article).filter(Article.url == url).first()
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Find source
                    source_id = sources.get(source_name)
                    if not source_id:
                        print(f"   Warning: Unknown source '{source_name}'")
                        continue
                    
                    # Create article
                    article = Article(
                        title=title[:500] if title else 'No title',
                        url=url,
                        content=content,
                        summary=content[:500] if content else '',
                        source_id=source_id,
                        published_at=getattr(article_data, 'published_date', None) or datetime.now(timezone.utc),
                        author=getattr(article_data, 'author', ''),
                        word_count=len(content.split()) if content else 0,
                        
                        # Default values
                        processed=False,
                        processing_stage='discovered',
                        relevance_score=0.5,
                        quality_score=0.5,
                        sentiment_score=0.0,
                        urgency_score=0.0
                    )
                    
                    session.add(article)
                    saved_count += 1
                
                except Exception as e:
                    print(f"   Error processing article: {e}")
            
            # Commit changes
            session.commit()
            print(f"   ✅ Saved {saved_count} articles, skipped {skipped_count} duplicates")
    
    except Exception as e:
        print(f"   ❌ Database save failed: {e}")

async def main():
    """Main execution."""
    success, articles = await simple_fetch()
    
    if success and articles:
        print(f"\n🎉 RSS fetch successful!")
        
        # Ask user if they want to save to database
        try:
            save_choice = input(f"\nSave {len(articles)} articles to database? (y/n): ").lower().strip()
            if save_choice in ['y', 'yes']:
                await save_to_database(articles)
                print(f"\n✅ Complete! Your database should now have real articles.")
                print(f"   Check your CLI - it should show real data instead of demo data.")
            else:
                print("   Articles not saved to database.")
        except KeyboardInterrupt:
            print("\n   Operation cancelled.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 RSS fetch completed successfully!")
        else:
            print("\n❌ RSS fetch failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)