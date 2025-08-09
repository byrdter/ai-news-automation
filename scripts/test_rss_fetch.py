#!/usr/bin/env python3
"""
Simple RSS Fetch Test Script

Tests RSS fetching without database complexity to troubleshoot issues.
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.rss_aggregator import FeedFetchRequest, fetch_rss_feed, RSSAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test RSS URLs from sources.json
TEST_SOURCES = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml"
    },
    {
        "name": "Google AI Blog", 
        "url": "http://googleaiblog.blogspot.com/atom.xml"
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/ai/feed/"
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml"
    }
]


async def test_single_feed(name: str, url: str) -> dict:
    """Test fetching a single RSS feed."""
    logger.info(f"Testing: {name}")
    logger.info(f"URL: {url}")
    
    try:
        # Create request
        request = FeedFetchRequest(
            feed_url=url,
            max_articles=10,  # Just get first 10 for testing
            timeout=30
        )
        
        # Fetch feed
        result = await fetch_rss_feed(request)
        
        if result.error:
            logger.error(f"❌ {name}: {result.error}")
            return {
                'name': name,
                'url': url,
                'success': False,
                'error': result.error,
                'articles_count': 0
            }
        
        logger.info(f"✅ {name}: {len(result.articles)} articles fetched in {result.fetch_time:.2f}s")
        logger.info(f"   Feed title: {result.title}")
        
        # Show first few articles
        for i, article in enumerate(result.articles[:3]):
            title = article.get('title', 'No title')[:60] + '...' if len(article.get('title', '')) > 60 else article.get('title', 'No title')
            logger.info(f"   Article {i+1}: {title}")
        
        return {
            'name': name,
            'url': url,
            'success': True,
            'feed_title': result.title,
            'articles_count': len(result.articles),
            'fetch_time': result.fetch_time,
            'sample_articles': [
                {
                    'title': article.get('title', '')[:100],
                    'url': article.get('url', ''),
                    'published': article.get('published_date', '')
                }
                for article in result.articles[:3]
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ {name}: Exception - {e}")
        return {
            'name': name,
            'url': url,
            'success': False,
            'error': str(e),
            'articles_count': 0
        }


async def test_all_feeds():
    """Test all RSS feeds."""
    logger.info("Starting RSS feed testing...")
    logger.info(f"Testing {len(TEST_SOURCES)} feeds")
    logger.info("=" * 50)
    
    results = []
    
    for source in TEST_SOURCES:
        try:
            result = await test_single_feed(source['name'], source['url'])
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to test {source['name']}: {e}")
            results.append({
                'name': source['name'],
                'url': source['url'],
                'success': False,
                'error': str(e),
                'articles_count': 0
            })
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("RSS FEED TEST SUMMARY")
    logger.info("=" * 50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    logger.info(f"Successful feeds: {len(successful)}/{len(results)}")
    logger.info(f"Failed feeds: {len(failed)}/{len(results)}")
    
    total_articles = sum(r.get('articles_count', 0) for r in results)
    logger.info(f"Total articles available: {total_articles}")
    
    if successful:
        logger.info("\n✅ WORKING FEEDS:")
        for result in successful:
            logger.info(f"  • {result['name']}: {result['articles_count']} articles")
    
    if failed:
        logger.info("\n❌ FAILED FEEDS:")
        for result in failed:
            logger.info(f"  • {result['name']}: {result['error']}")
    
    return results


async def main():
    """Main test function."""
    aggregator = RSSAggregator()
    
    try:
        results = await test_all_feeds()
        
        # Test if we can access articles
        successful_results = [r for r in results if r['success']]
        if successful_results:
            logger.info(f"\n🎉 SUCCESS! {len(successful_results)} RSS feeds are working")
            logger.info("Sample articles from working feeds:")
            
            for result in successful_results[:2]:  # Show samples from first 2 working feeds
                logger.info(f"\n  📰 {result['name']}:")
                for article in result.get('sample_articles', [])[:2]:
                    logger.info(f"    • {article['title']}")
                    logger.info(f"      {article['url']}")
        else:
            logger.error("❌ No RSS feeds are working. Check your internet connection and feed URLs.")
    
    finally:
        await aggregator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())