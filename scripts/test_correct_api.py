#!/usr/bin/env python3
"""
Test Correct RSS API

Simple test to verify the correct RSS aggregator API calls work.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_api():
    """Test the RSS aggregator API step by step."""
    print("🧪 Testing RSS Aggregator API...")
    print("=" * 50)
    
    try:
        # Step 1: Test imports
        print("1. Testing imports...")
        from mcp_servers.rss_aggregator import initialize_sources, fetch_all_sources, BatchFetchRequest
        print("   ✅ Imports successful")
        
        # Step 2: Test initialization
        print("\n2. Testing source initialization...")
        init_result = await initialize_sources()
        print(f"   Result: {init_result}")
        
        if init_result.get('success', False):
            print(f"   ✅ Initialized {init_result.get('source_count', 0)} sources")
        else:
            print(f"   ❌ Initialization failed: {init_result.get('error', 'Unknown')}")
            return False
        
        # Step 3: Test BatchFetchRequest creation
        print("\n3. Testing BatchFetchRequest creation...")
        request = BatchFetchRequest()
        print(f"   ✅ Created request: {type(request)}")
        print(f"   Request attributes: {dir(request)}")
        
        # Step 4: Test article fetching
        print("\n4. Testing article fetching (limited)...")
        # Modify request for testing
        request.max_articles_per_source = 5  # Limit for testing
        request.timeout_seconds = 15
        request.force_refresh = True
        
        result = await fetch_all_sources(request)
        print(f"   Fetch result type: {type(result)}")
        print(f"   Success: {result.success}")
        
        if result.success:
            print(f"   ✅ Fetched {len(result.articles)} articles")
            print(f"   Sources processed: {len(result.sources_processed)}")
            
            # Show sample articles
            if result.articles:
                print(f"\n📰 Sample articles:")
                for i, article in enumerate(result.articles[:3]):
                    print(f"   {i+1}. {article.title[:60]}...")
                    print(f"      Source: {article.source_name}")
                    print(f"      URL: {article.url}")
            
            return True
        else:
            print(f"   ❌ Fetch failed: {result.error}")
            return False
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the project directory and dependencies are installed")
        return False
    
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database():
    """Test database connection."""
    print("\n🗄️  Testing database connection...")
    print("=" * 50)
    
    try:
        from config.settings import get_settings
        from database.models import NewsSource, Article
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        print("   ✅ Settings loaded")
        
        # Create database connection
        db_url = (
            f"postgresql://{settings.database.user}:"
            f"{settings.database.password}@"
            f"{settings.database.host}:"
            f"{settings.database.port}/"
            f"{settings.database.name}"
        )
        
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        
        # Test query
        with Session() as session:
            source_count = session.query(NewsSource).count()
            article_count = session.query(Article).count()
            active_sources = session.query(NewsSource).filter(NewsSource.active == True).count()
        
        print(f"   ✅ Database connected")
        print(f"   Total sources: {source_count}")
        print(f"   Active sources: {active_sources}")
        print(f"   Total articles: {article_count}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 RSS Aggregator API Test")
    print("=" * 50)
    
    # Test API
    api_ok = await test_api()
    
    # Test database
    db_ok = await test_database()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    print(f"RSS API: {'✅ Working' if api_ok else '❌ Failed'}")
    print(f"Database: {'✅ Working' if db_ok else '❌ Failed'}")
    
    if api_ok and db_ok:
        print("\n🎉 All systems operational!")
        print("Ready to run: python scripts/working_rss_fetch.py")
    else:
        print("\n❌ Some systems need attention")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)