#!/usr/bin/env python3
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
sys.path.append('.')

async def fix_techcrunch_content():
    """Fix NULL content for TechCrunch AI articles by scraping full content"""
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from config.settings import get_settings
    
    settings = get_settings()
    engine = create_engine(settings.database_url.get_secret_value())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🔍 Finding TechCrunch AI articles with NULL content...")
    
    # Get TechCrunch articles with NULL content
    query = text("""
        SELECT a.id, a.title, a.url, a.published_at
        FROM articles a 
        JOIN news_sources ns ON a.source_id = ns.id
        WHERE ns.name = 'TechCrunch AI'
        AND (a.content IS NULL OR a.content = '')
        AND a.url IS NOT NULL
        ORDER BY a.published_at DESC
        LIMIT 15
    """)
    
    null_articles = session.execute(query).fetchall()
    print(f"📰 Found {len(null_articles)} TechCrunch articles with NULL content")
    
    if not null_articles:
        print("✅ No NULL content articles found!")
        session.close()
        return
    
    success_count = 0
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=15),
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    ) as http_session:
        
        for article_id, title, url, published_at in null_articles:
            try:
                print(f"\n📡 Fetching: {title[:60]}...")
                print(f"   URL: {url}")
                
                async with http_session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # TechCrunch specific content extraction
                        content = extract_techcrunch_content(soup, url)
                        
                        if content and len(content) > 200:
                            # Update database with extracted content
                            update_query = text("""
                                UPDATE articles 
                                SET content = :content, 
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE id = :article_id
                            """)
                            
                            session.execute(update_query, {
                                'content': content[:8000],  # Limit content length
                                'article_id': article_id
                            })
                            session.commit()
                            
                            success_count += 1
                            print(f"   ✅ Updated! ({len(content)} chars)")
                            
                            # Show sample of content
                            print(f"   📝 Preview: {content[:100]}...")
                        else:
                            print(f"   ❌ No content extracted (got {len(content) if content else 0} chars)")
                    else:
                        print(f"   ❌ HTTP {response.status}")
                        
            except asyncio.TimeoutError:
                print(f"   ⏱️ Timeout")
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                
            # Small delay to be respectful
            await asyncio.sleep(1)
    
    session.close()
    print(f"\n🎉 Content extraction completed!")
    print(f"✅ Successfully updated {success_count}/{len(null_articles)} articles")

def extract_techcrunch_content(soup, url):
    """Extract content from TechCrunch articles"""
    
    content_selectors = [
        # Primary content areas for TechCrunch
        'div.article-content',
        'div.entry-content',
        '.post-content',
        'article .content',
        '.article-entry',
        'div.content-wrapper',
        
        # TechCrunch specific selectors
        '.wp-content',
        '.single-post-content',
        'main article',
        
        # Fallback selectors
        'article',
        '.content'
    ]
    
    for selector in content_selectors:
        content_div = soup.select_one(selector)
        if content_div:
            # Remove unwanted elements
            for unwanted in content_div.find_all([
                'script', 'style', 'nav', 'footer', 'aside', 
                '.advertisement', '.ad', '.social-share',
                '.related-articles', '.newsletter-signup'
            ]):
                unwanted.decompose()
            
            # Extract text content
            content = content_div.get_text(separator=' ', strip=True)
            
            # Clean up the content
            content = ' '.join(content.split())  # Normalize whitespace
            
            if len(content) > 200:  # Minimum content length
                return content
    
    # If no content found with selectors, try getting all paragraphs in main content
    main_content = soup.find('main') or soup.find('article') or soup
    if main_content:
        paragraphs = main_content.find_all('p')
        if paragraphs:
            content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            content = ' '.join(content.split())
            if len(content) > 200:
                return content
    
    return ""

if __name__ == "__main__":
    asyncio.run(fix_techcrunch_content())