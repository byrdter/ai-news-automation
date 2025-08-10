#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.')

async def force_save_recent_articles():
    """Use your existing working RSS system to fetch and save new articles"""
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from config.settings import get_settings
    from database.models import Article, NewsSource
    import uuid
    from datetime import datetime, timezone
    import aiohttp
    import feedparser
    
    settings = get_settings()
    engine = create_engine(settings.database_url.get_secret_value())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🚀 Fetching articles using direct RSS approach...")
    
    # Get active news sources
    sources = session.query(NewsSource).filter_by(active=True).all()
    print(f"📡 Found {len(sources)} active sources")
    
    all_articles = []
    
    # Fetch from each source
    async with aiohttp.ClientSession() as http_session:
        for source in sources:
            try:
                print(f"📡 Fetching from {source.name}...")
                
                async with http_session.get(source.rss_feed_url, timeout=10) as response:
                    if response.status == 200:
                        rss_content = await response.text()
                        feed = feedparser.parse(rss_content)
                        
                        for entry in feed.entries[:10]:  # Limit to 10 most recent
                            # Check if article already exists
                            existing = session.execute(text("""
                                SELECT id FROM articles 
                                WHERE (url = :url OR title = :title)
                                AND source_id = :source_id
                            """), {
                                'url': getattr(entry, 'link', ''),
                                'title': getattr(entry, 'title', ''),
                                'source_id': source.id
                            }).fetchone()
                            
                            if not existing:
                                # Parse published date
                                try:
                                    from datetime import datetime
                                    import time
                                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now(timezone.utc)
                                except:
                                    published = datetime.now(timezone.utc)
                                
                                # Create article object for tracking
                                article_data = {
                                    'title': getattr(entry, 'title', ''),
                                    'content': getattr(entry, 'content', [{}])[0].get('value', '') if hasattr(entry, 'content') else getattr(entry, 'summary', ''),
                                    'summary': getattr(entry, 'summary', ''),
                                    'url': getattr(entry, 'link', ''),
                                    'source_id': source.id,
                                    'source_name': source.name,
                                    'published': published
                                }
                                all_articles.append(article_data)
                        
                        print(f"   ✅ Found {len([a for a in all_articles if a['source_name'] == source.name])} new articles")
                    else:
                        print(f"   ❌ HTTP {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Error fetching {source.name}: {str(e)[:50]}")
    
    print(f"\n📰 Total new articles found: {len(all_articles)}")
    
    if not all_articles:
        print("⚠️ No new articles to save")
        session.close()
        return
    
    # Save articles to database
    saved_count = 0
    error_count = 0
    
    for article_data in all_articles:
        try:
            new_article = Article(
                id=str(uuid.uuid4()),
                title=article_data['title'],
                content=article_data['content'],
                summary=article_data['summary'],
                url=article_data['url'],
                source_id=article_data['source_id'],
                published_at=article_data['published'],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            session.add(new_article)
            saved_count += 1
            
            print(f"💾 Saving: {article_data['title'][:60]}... ({article_data['source_name']})")
            
        except Exception as e:
            print(f"❌ Error saving article: {str(e)[:100]}")
            error_count += 1
    
    # Commit all changes
    try:
        session.commit()
        print(f"\n🎉 Successfully saved {saved_count} new articles!")
        print(f"📊 Summary:")
        print(f"  ✅ Saved: {saved_count}")
        print(f"  ❌ Errors: {error_count}")
        
        # Show what was saved by source
        if saved_count > 0:
            result = session.execute(text("""
                SELECT ns.name, COUNT(a.id) as new_articles
                FROM articles a 
                JOIN news_sources ns ON a.source_id = ns.id
                WHERE a.created_at >= NOW() - INTERVAL '10 minutes'
                GROUP BY ns.name
                ORDER BY new_articles DESC
            """)).fetchall()
            
            print(f"\n📈 New articles by source (last 10 minutes):")
            for source_name, count in result:
                print(f"  {source_name}: {count} articles")
                
    except Exception as e:
        session.rollback()
        print(f"❌ Error committing articles: {e}")
    
    session.close()

if __name__ == "__main__":
    asyncio.run(force_save_recent_articles())