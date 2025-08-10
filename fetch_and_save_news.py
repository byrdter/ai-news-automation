#!/usr/bin/env python3
import asyncio
import os
import sys
sys.path.append('.')

async def fetch_current_news():
    print("🚀 FETCHING & SAVING CURRENT AI NEWS")
    print("=" * 50)
    
    try:
        # Direct database connection using your working credentials
        import asyncpg
        from datetime import datetime
        
        DATABASE_URL = "postgresql://postgres.uwjsockmbxhmirsnozvo:d4gUQh2kZsUF0Ebl@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        
        print("📡 Fetching articles using RSS system...")
        
        # Use your working RSS system
        from mcp_servers.rss_aggregator import fetch_all_sources, BatchFetchRequest, initialize_sources
        
        await initialize_sources()
        
        request = BatchFetchRequest(
            force_refresh=True,
            max_articles_per_source=20
        )
        
        result = await fetch_all_sources(request)
        print(f"✅ Fetched {result.total_articles} articles from RSS")
        
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check current article count
        current_count = await conn.fetchval("SELECT COUNT(*) FROM articles")
        print(f"📊 Current articles in database: {current_count}")
        
        # Get the articles and save manually
        saved_count = 0
        gpt5_count = 0
        
        if hasattr(result, 'articles') and result.articles:
            for article in result.articles:
                try:
                    # Check for GPT-5 content
                    if any(term in article.title.lower() for term in ['gpt-5', 'gpt 5', 'chatgpt-5']):
                        gpt5_count += 1
                        print(f"🎉 GPT-5 article: {article.title}")
                    
                    # Insert article into database
                    await conn.execute("""
                        INSERT INTO articles (title, content, summary, url, source, published_date, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (url) DO NOTHING
                    """, 
                    article.title,
                    getattr(article, 'content', article.summary),
                    article.summary,
                    article.url,
                    article.source,
                    article.published_date,
                    datetime.now(),
                    datetime.now()
                    )
                    saved_count += 1
                    
                except Exception as e:
                    print(f"❌ Error saving article: {e}")
                    continue
        
        # Check final count
        final_count = await conn.fetchval("SELECT COUNT(*) FROM articles")
        new_articles = final_count - current_count
        
        print(f"\n📊 RESULTS:")
        print(f"   🎉 Articles saved to database: {new_articles}")
        print(f"   🔥 GPT-5 articles found: {gpt5_count}")
        print(f"   📰 Total articles now: {final_count}")
        
        # Check for recent GPT-5 articles in database
        gpt5_in_db = await conn.fetchval("""
            SELECT COUNT(*) FROM articles 
            WHERE (title ILIKE '%gpt-5%' OR title ILIKE '%gpt 5%' OR title ILIKE '%chatgpt-5%')
            AND created_at >= NOW() - INTERVAL '2 days'
        """)
        print(f"   💾 GPT-5 articles in database: {gpt5_in_db}")
        
        await conn.close()
        
        if new_articles > 0:
            print("\n✅ SUCCESS! Current news now saved to database")
            print("   Your frontend should now show recent articles")
        else:
            print("\n⚠️  No new articles saved (may already exist)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fetch_current_news())