#!/usr/bin/env python3
"""
Emergency News Fetch Script
Manually fetch latest AI news to diagnose system issues
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
import json

# Key AI news sources with their RSS feeds
EMERGENCY_SOURCES = {
    "OpenAI Blog": "https://openai.com/blog/rss/",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/ai/feed/",
    "MIT Technology Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "The Verge AI": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "Ars Technica AI": "https://arstechnica.com/tag/artificial-intelligence/feed/",
    "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default",
    "Microsoft AI Blog": "https://blogs.microsoft.com/ai/feed/",
    "NVIDIA AI Blog": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
    "Anthropic News": "https://www.anthropic.com/news/rss"
}

async def fetch_feed(session, name, url):
    """Fetch and parse a single RSS feed"""
    try:
        print(f"📡 Fetching {name}...")
        
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:5]:  # Get latest 5 articles
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    # Check if recent (last 7 days)
                    is_recent = pub_date and pub_date > datetime.now() - timedelta(days=7)
                    
                    article = {
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', ''),
                        'published': pub_date.isoformat() if pub_date else 'Unknown',
                        'summary': entry.get('summary', '')[:200],
                        'recent': is_recent
                    }
                    articles.append(article)
                
                return {
                    'source': name,
                    'status': 'success',
                    'articles_count': len(articles),
                    'articles': articles,
                    'feed_title': feed.feed.get('title', name)
                }
            else:
                return {
                    'source': name,
                    'status': 'error',
                    'error': f"HTTP {response.status}"
                }
                
    except Exception as e:
        return {
            'source': name,
            'status': 'error',
            'error': str(e)
        }

async def emergency_news_fetch():
    """Fetch news from all emergency sources"""
    print("🚨 EMERGENCY NEWS FETCH STARTING...")
    print(f"📅 Checking for articles from last 7 days")
    print("=" * 60)
    
    results = []
    gpt5_mentions = []
    recent_ai_news = []
    
    async with aiohttp.ClientSession() as session:
        # Fetch all sources concurrently
        tasks = [
            fetch_feed(session, name, url) 
            for name, url in EMERGENCY_SOURCES.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n📊 EMERGENCY FETCH RESULTS:")
    print("=" * 60)
    
    total_articles = 0
    working_sources = 0
    
    for result in results:
        if isinstance(result, dict) and result.get('status') == 'success':
            working_sources += 1
            articles_count = result['articles_count']
            total_articles += articles_count
            
            print(f"✅ {result['source']}: {articles_count} articles")
            
            # Check for GPT-5 mentions
            for article in result['articles']:
                if any(term in article['title'].lower() for term in ['gpt-5', 'gpt 5', 'chatgpt-5']):
                    gpt5_mentions.append({
                        'source': result['source'],
                        'title': article['title'],
                        'link': article['link'],
                        'published': article['published']
                    })
                
                # Collect recent articles
                if article['recent']:
                    recent_ai_news.append({
                        'source': result['source'],
                        'title': article['title'],
                        'published': article['published']
                    })
        else:
            print(f"❌ {result.get('source', 'Unknown')}: {result.get('error', 'Failed')}")
    
    print("\n🔍 GPT-5 DETECTION RESULTS:")
    print("=" * 60)
    if gpt5_mentions:
        print(f"🎉 FOUND {len(gpt5_mentions)} GPT-5 mentions!")
        for mention in gpt5_mentions:
            print(f"  • {mention['source']}: {mention['title']}")
            print(f"    📅 {mention['published']}")
            print(f"    🔗 {mention['link']}")
            print()
    else:
        print("❌ NO GPT-5 mentions found in recent feeds")
        print("   This suggests either:")
        print("   - Sources aren't capturing the news")
        print("   - RSS feeds are delayed")
        print("   - Your system needs different sources")
    
    print(f"\n📊 SUMMARY:")
    print(f"  • Working sources: {working_sources}/{len(EMERGENCY_SOURCES)}")
    print(f"  • Total articles fetched: {total_articles}")
    print(f"  • Recent articles (7 days): {len(recent_ai_news)}")
    print(f"  • GPT-5 mentions: {len(gpt5_mentions)}")
    
    if len(recent_ai_news) < 20:
        print("\n⚠️  WARNING: Very few recent articles found!")
        print("   Your system may need additional or different sources")
    
    return {
        'working_sources': working_sources,
        'total_articles': total_articles,
        'gpt5_mentions': gpt5_mentions,
        'recent_articles': recent_ai_news
    }

if __name__ == "__main__":
    asyncio.run(emergency_news_fetch())