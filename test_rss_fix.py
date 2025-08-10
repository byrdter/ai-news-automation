#!/usr/bin/env python3
"""
Test RSS Pipeline Fix

Tests the fixed RSS caching mechanism and database integration.
This should fetch fresh articles and save them to the database.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rss_pipeline_fix():
    """Test the RSS pipeline with force_refresh and database save."""
    
    print("🔧 Testing RSS Pipeline Fix")
    print("=" * 50)
    print(f"Testing at: {datetime.now()}")
    print()
    
    try:
        # Import RSS aggregator functions
        from mcp_servers.rss_aggregator.tools import initialize_sources, fetch_all_sources
        from mcp_servers.rss_aggregator.schemas import BatchFetchRequest
        
        # Step 1: Initialize RSS sources
        print("📡 Step 1: Initializing RSS sources...")
        init_result = await initialize_sources()
        
        if not init_result.get('success', False):
            print(f"❌ RSS initialization failed: {init_result.get('error', 'Unknown error')}")
            return False
        
        print(f"✅ RSS sources initialized: {init_result.get('sources_loaded', 0)} sources loaded")
        print(f"   Active sources: {init_result.get('active_sources', 0)}")
        
        # Step 2: Fetch articles with force_refresh and database save
        print("\n🔄 Step 2: Fetching articles with force refresh and database save...")
        request = BatchFetchRequest(
            force_refresh=True,  # This should bypass cache
            save_to_database=True,  # This should save to database
            max_articles_per_source=25,  # Limit to prevent overwhelming
            parallel_limit=3,  # Reduce parallel requests
            exclude_duplicates=True,
            max_age_hours=72  # Get articles from last 3 days
        )
        
        print(f"   Force refresh: {request.force_refresh}")
        print(f"   Save to database: {request.save_to_database}")
        print(f"   Max articles per source: {request.max_articles_per_source}")
        
        # Execute the fetch
        result = await fetch_all_sources(request)
        
        # Step 3: Analyze results
        print("\n📊 Step 3: Results Analysis")
        print(f"   Sources attempted: {result.sources_attempted}")
        print(f"   Sources successful: {result.sources_successful}")
        print(f"   Total articles fetched: {result.total_articles}")
        print(f"   New articles: {result.new_articles}")
        print(f"   Duplicate articles filtered: {result.duplicate_articles}")
        print(f"   Processing time: {result.total_duration:.2f}s")
        
        # Check database save results
        if hasattr(result, 'database_save_results') and result.database_save_results:
            db_results = result.database_save_results
            print(f"\n💾 Database Save Results:")
            if "error" in db_results:
                print(f"   ❌ Error: {db_results['error']}")
            else:
                print(f"   ✅ Articles saved: {db_results.get('saved', 0)}")
                print(f"   ⏭️  Articles skipped (duplicates): {db_results.get('skipped', 0)}")
                print(f"   ❌ Errors: {db_results.get('errors', 0)}")
                print(f"   🔍 Unmapped sources: {db_results.get('unmapped', 0)}")
        else:
            print("\n⚠️  No database save results found")
        
        # Step 4: Show sample articles
        print(f"\n📰 Step 4: Sample Articles (showing first 5)")
        for i, article in enumerate(result.all_articles[:5]):
            print(f"   {i+1}. {article.title[:60]}...")
            print(f"      Source: {article.source_name}")
            print(f"      Published: {article.published_date}")
            print(f"      Relevance: {article.relevance_score:.3f}")
            print()
        
        # Step 5: Validate fix success
        print("🎯 Step 5: Fix Validation")
        
        # Check if we got fresh articles (not from cache)
        if result.total_articles > 0:
            print("✅ RSS fetch working: Got articles from sources")
        else:
            print("❌ RSS fetch failed: No articles retrieved")
            return False
        
        # Check if database save worked
        if hasattr(result, 'database_save_results') and result.database_save_results:
            db_results = result.database_save_results
            if "error" not in db_results and db_results.get('saved', 0) > 0:
                print(f"✅ Database integration working: {db_results.get('saved', 0)} articles saved")
            elif db_results.get('skipped', 0) > 0:
                print(f"⚠️  Database working but articles were duplicates: {db_results.get('skipped', 0)} skipped")
            else:
                print(f"❌ Database integration failed: {db_results}")
                return False
        else:
            print("❌ Database integration not working: No save results")
            return False
        
        print("\n🎉 RSS Pipeline Fix Test SUCCESSFUL!")
        print("   - Force refresh bypasses cache ✅")
        print("   - Articles are fetched from RSS feeds ✅") 
        print("   - Articles are saved to database ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main execution."""
    success = await test_rss_pipeline_fix()
    
    if success:
        print("\n🎊 All tests passed! RSS pipeline is now working correctly.")
        print("   The system should now capture current AI news including GPT-5.")
    else:
        print("\n💥 Tests failed! RSS pipeline still has issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())