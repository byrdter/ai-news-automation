#!/usr/bin/env python3
"""
Simple test to fetch articles from updated RSS sources
"""
import asyncio
import sys
sys.path.append('.')

async def test_updated_sources():
    """Test fetching from the RSS sources we just updated"""
    
    from sqlalchemy import create_engine, text
    from config.settings import get_settings
    import aiohttp
    import feedparser
    
    settings = get_settings()
    engine = create_engine(settings.database_url.get_secret_value())
    
    # Test the sources we just updated
    test_sources = [
        ('Google AI Blog', 'https://blog.research.google/rss'),
        ('DeepMind Blog', 'https://www.deepmind.com/blog/rss.xml'),
        ('Stanford HAI', 'https://hai.stanford.edu/news/rss'),
        ('BAIR Blog', 'https://bair.berkeley.edu/blog/feed.xml'),
        ('Unite.AI', 'https://unite.ai/feed/'),
        ('VentureBeat AI', 'https://feeds.feedburner.com/venturebeat/SZYF'),
    ]
    
    print("🔍 Testing updated RSS sources...")
    
    working_sources = []
    broken_sources = []
    
    async with aiohttp.ClientSession() as session:
        for source_name, rss_url in test_sources:
            try:
                print(f"\n📡 Testing {source_name}...")
                print(f"   URL: {rss_url}")
                
                async with session.get(rss_url, timeout=10) as response:
                    if response.status == 200:
                        rss_content = await response.text()
                        feed = feedparser.parse(rss_content)
                        
                        if feed.entries:
                            article_count = len(feed.entries)
                            latest_title = feed.entries[0].get('title', 'No title')
                            print(f"   ✅ Working! {article_count} articles found")
                            print(f"   📰 Latest: {latest_title[:60]}...")
                            working_sources.append((source_name, article_count))
                        else:
                            print(f"   ❌ No articles found in feed")
                            broken_sources.append((source_name, "No articles"))
                    else:
                        print(f"   ❌ HTTP {response.status}")
                        broken_sources.append((source_name, f"HTTP {response.status}"))
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:50]}")
                broken_sources.append((source_name, str(e)[:50]))
                
            # Small delay between requests
            await asyncio.sleep(1)
    
    print(f"\n📊 RSS SOURCE TEST RESULTS:")
    print("=" * 50)
    
    print(f"\n✅ WORKING SOURCES ({len(working_sources)}):")
    total_articles = 0
    for source_name, article_count in working_sources:
        print(f"  • {source_name}: {article_count} articles")
        total_articles += article_count
    
    print(f"\n❌ BROKEN SOURCES ({len(broken_sources)}):")
    for source_name, error in broken_sources:
        print(f"  • {source_name}: {error}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Working sources: {len(working_sources)}/{len(test_sources)}")
    print(f"  Total articles available: {total_articles}")
    
    if len(working_sources) >= 4:
        print(f"  🎉 Great! Most sources are working")
    elif len(working_sources) >= 2:
        print(f"  ⚠️  Some sources working, need to fix others")
    else:
        print(f"  ❌ Most sources broken, need URL fixes")

if __name__ == "__main__":
    asyncio.run(test_updated_sources())