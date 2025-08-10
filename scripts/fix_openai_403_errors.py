#!/usr/bin/env python3
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
import random
sys.path.append('.')

async def retry_openai_403_errors():
    """Retry OpenAI articles that failed with 403 errors using different headers"""
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from config.settings import get_settings
    
    settings = get_settings()
    engine = create_engine(settings.database_url.get_secret_value())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🔍 Finding OpenAI Blog articles that still have NULL content...")
    
    # Get remaining OpenAI articles with NULL content
    query = text("""
        SELECT a.id, a.title, a.url, a.published_at
        FROM articles a 
        JOIN news_sources ns ON a.source_id = ns.id
        WHERE ns.name = 'OpenAI Blog'
        AND (a.content IS NULL OR a.content = '')
        AND a.url IS NOT NULL
        ORDER BY a.published_at DESC
        LIMIT 10
    """)
    
    null_articles = session.execute(query).fetchall()
    print(f"📰 Found {len(null_articles)} OpenAI articles still with NULL content")
    
    if not null_articles:
        print("✅ All OpenAI articles now have content!")
        session.close()
        return
    
    # Multiple user agents to try
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    success_count = 0
    
    for article_id, title, url, published_at in null_articles:
        try:
            print(f"\n📡 Retrying: {title[:60]}...")
            
            # Try different user agents
            for i, user_agent in enumerate(user_agents):
                try:
                    headers = {
                        'User-Agent': user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0'
                    }
                    
                    async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=20),
                        headers=headers
                    ) as http_session:
                        
                        # Add random delay to seem more human
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        async with http_session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                content = extract_openai_content_enhanced(soup, url)
                                
                                if content and len(content) > 200:
                                    # Update database
                                    update_query = text("""
                                        UPDATE articles 
                                        SET content = :content, 
                                            updated_at = CURRENT_TIMESTAMP
                                        WHERE id = :article_id
                                    """)
                                    
                                    session.execute(update_query, {
                                        'content': content[:8000],
                                        'article_id': article_id
                                    })
                                    session.commit()
                                    
                                    success_count += 1
                                    print(f"   ✅ Success with user agent {i+1}! ({len(content)} chars)")
                                    print(f"   📝 Preview: {content[:100]}...")
                                    break  # Success, no need to try other user agents
                                    
                            elif response.status == 403:
                                print(f"   ❌ Still 403 with user agent {i+1}")
                            else:
                                print(f"   ❌ HTTP {response.status} with user agent {i+1}")
                                
                except Exception as e:
                    print(f"   ❌ Error with user agent {i+1}: {str(e)[:50]}")
                    
            else:
                print("   ❌ All user agents failed")
                
        except Exception as e:
            print(f"   ❌ General error: {str(e)[:100]}")
    
    session.close()
    print(f"\n🎉 Retry completed!")
    print(f"✅ Successfully updated {success_count} more articles")

def extract_openai_content_enhanced(soup, url):
    """Enhanced content extraction for OpenAI blog posts"""
    
    # Remove scripts, styles, and other noise early
    for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        unwanted.decompose()
    
    content_selectors = [
        # Try more specific OpenAI selectors first
        'div[data-testid="blog-post-content"]',
        'div.blog-post-content',
        'div.post-content',
        'main .content',
        'article .entry-content',
        '.post-body',
        'main article div',
        
        # Fallbacks
        'article',
        'main',
        '.content'
    ]
    
    for selector in content_selectors:
        content_div = soup.select_one(selector)
        if content_div:
            # Get all text from paragraphs and headers
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)])
                content = ' '.join(content.split())  # Normalize whitespace
                
                if len(content) > 200:
                    return content
    
    # Last resort: get all visible text
    all_text = soup.get_text(separator=' ', strip=True)
    all_text = ' '.join(all_text.split())
    
    if len(all_text) > 500:  # Make sure we have substantial content
        return all_text[:8000]  # Limit length
    
    return ""

if __name__ == "__main__":
    asyncio.run(retry_openai_403_errors())