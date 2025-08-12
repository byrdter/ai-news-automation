"""
RSS Aggregator MCP Server - Tool Implementations
Location: mcp_servers/rss_aggregator/tools.py

MCP tool implementations for RSS feed aggregation and processing.
Used by News Discovery Agent and other agents for content collection.
Enhanced with full article content extraction and perfect database integration.
"""

import asyncio
import hashlib
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp
import feedparser
from bs4 import BeautifulSoup
import uuid
from pydantic import ValidationError

from config.constants import DEFAULT_NEWS_SOURCES, AI_KEYWORDS
from config.settings import get_settings
from .schemas import (
    RSSSourceConfig, 
    RSSArticle, 
    FeedFetchResult, 
    BatchFetchRequest, 
    BatchFetchResult,
    FeedStatus, 
    ArticleStatus,
    CacheEntry,
    RSSServerStats
)

# Configure logging
logger = logging.getLogger(__name__)

# Global state for RSS aggregator
_source_configs: Dict[str, RSSSourceConfig] = {}
_cache: Dict[str, CacheEntry] = {}
_stats = RSSServerStats()
_session: Optional[aiohttp.ClientSession] = None
_server_start_time = time.time()

# ============================================================================
# ENHANCED CONTENT EXTRACTION FUNCTIONS
# ============================================================================

async def extract_full_article_content_enhanced(url: str, source_name: str, session: aiohttp.ClientSession) -> Optional[str]:
    """
    Extract full article content from URL when RSS only provides summary
    Source-specific extraction logic for OpenAI, TechCrunch, DeepMind, etc.
    """
    if not url:
        return None
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove unwanted elements
                for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                    unwanted.decompose()
                
                # Source-specific content extraction
                content = None
                
                if "openai.com" in url:
                    content = extract_openai_content(soup)
                elif "techcrunch.com" in url:
                    content = extract_techcrunch_content(soup)
                elif "deepmind.com" in url:
                    content = extract_deepmind_content(soup)
                elif "mit.edu" in url:
                    content = extract_mit_content(soup)
                elif "marktechpost.com" in url:
                    content = extract_marktechpost_content(soup)
                elif "arxiv.org" in url:
                    content = extract_arxiv_content(soup)
                elif "nvidia.com" in url:
                    content = extract_nvidia_content(soup)
                elif "anthropic.com" in url:
                    content = extract_anthropic_content(soup)
                else:
                    content = extract_generic_content(soup)
                
                if content and len(content) > 200:
                    return content[:8000]  # Limit content length
                    
    except Exception as e:
        logger.warning(f"Failed to extract content from {url}: {str(e)[:100]}")
    
    return None

def extract_openai_content(soup):
    """Extract content from OpenAI blog posts"""
    selectors = [
        'div[data-testid="blog-post-content"]',
        'div.blog-post-content',
        'div.post-content',
        'main .content',
        'article .entry-content',
        '.post-body',
        'main article div',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_techcrunch_content(soup):
    """Extract content from TechCrunch articles"""
    selectors = [
        'div.article-content',
        'div.entry-content', 
        'div.single-post-content',
        'div.post-content',
        'article .content',
        'main .wp-content',
        '.post-body-content',
        'div[data-module="ArticleBody"]',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            # Remove ads and social elements
            for unwanted in content_div.find_all([
                'div[class*="ad"]', 'div[class*="advertisement"]',
                'div[class*="social"]', 'div[class*="share"]',
                'div[class*="related"]', 'div[class*="newsletter"]'
            ]):
                unwanted.decompose()
            
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if text_elements:
                texts = [elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20]
                content = ' '.join(texts)
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_deepmind_content(soup):
    """Extract content from DeepMind blog posts"""
    selectors = [
        '.article-content',
        '.post-content',
        'main article',
        '.blog-post-content',
        'article .content',
        'main .content',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_mit_content(soup):
    """Extract content from MIT News"""
    selectors = [
        '.news-article--body',
        '.field-name-body',
        '.article-body',
        '.post-content',
        'article .content',
        'main .content',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_marktechpost_content(soup):
    """Extract content from MarkTechPost"""
    selectors = [
        '.entry-content',
        '.post-content',
        '.article-content',
        '.content-area',
        'article .content',
        'main .content',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_arxiv_content(soup):
    """Extract content from arXiv papers"""
    selectors = [
        '.abstract',
        '#abstract',
        '.ltx_abstract',
        '.abstract-content',
        'blockquote.abstract',
        'main',
        'article'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            # For arXiv, we primarily want the abstract
            content = content_div.get_text(strip=True)
            if len(content) > 100:
                return ' '.join(content.split())
    return ""

def extract_nvidia_content(soup):
    """Extract content from NVIDIA blog posts"""
    selectors = [
        '.blog-content',
        '.post-content',
        '.article-content',
        '.entry-content',
        'article .content',
        'main .content',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_anthropic_content(soup):
    """Extract content from Anthropic blog posts"""
    selectors = [
        '.post-content',
        '.blog-content',
        '.article-content',
        '.entry-content',
        'article .content',
        'main .content',
        'article',
        'main'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            text_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if text_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

def extract_generic_content(soup):
    """Generic content extraction for unknown sources"""
    selectors = [
        'article',
        'div.content',
        'div.post-content',
        'div.entry-content',
        'main',
        '.article-body',
        '.post-body',
        '.blog-content',
        '.single-post-content'
    ]
    
    for selector in selectors:
        content_div = soup.select_one(selector)
        if content_div:
            paragraphs = content_div.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                content = ' '.join(content.split())
                if len(content) > 200:
                    return content
    return ""

# ============================================================================
# DATABASE INTEGRATION FUNCTIONS
# ============================================================================

async def save_article_to_database(article_data: dict, source_id: str) -> bool:
    """
    Save article to database using exact schema structure
    """
    try:
        import asyncpg
        
        settings = get_settings()
        database_url = settings.database_url.get_secret_value()
        
        conn = await asyncpg.connect(database_url)
        
        # Generate UUID for article
        article_id = str(uuid.uuid4())
        
        # Prepare data with exact column names from schema
        await conn.execute("""
            INSERT INTO articles (
                id, title, url, content, summary, source_id, 
                published_at, author, word_count, 
                relevance_score, content_hash,
                created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, 
                $7, $8, $9, 
                $10, $11,
                $12, $13
            )
            ON CONFLICT (url) DO UPDATE SET
                content = EXCLUDED.content,
                summary = EXCLUDED.summary,
                word_count = EXCLUDED.word_count,
                updated_at = EXCLUDED.updated_at
        """,
        article_id,                                           # id
        article_data.get('title', '')[:500],                 # title (max 500 chars)
        article_data.get('url', '')[:1000],                  # url (max 1000 chars)
        article_data.get('content'),                         # content (text)
        article_data.get('summary'),                         # summary (text)
        source_id,                                           # source_id (uuid)
        article_data.get('published_at'),                    # published_at
        article_data.get('author', '')[:255] if article_data.get('author') else None,  # author (max 255 chars)
        len(article_data.get('content', '').split()) if article_data.get('content') else None,  # word_count
        article_data.get('relevance_score', 0.0),            # relevance_score
        article_data.get('content_hash'),                    # content_hash
        datetime.now(timezone.utc),                          # created_at
        datetime.now(timezone.utc)                           # updated_at
        )
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error saving article to database: {e}")
        return False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash of content for deduplication"""
    if not content:
        return ""
    
    # Normalize content for hashing
    normalized = content.strip().lower()
    normalized = ' '.join(normalized.split())  # Normalize whitespace
    
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def calculate_relevance_score(article: RSSArticle, keywords: List[str] = None) -> float:
    """Calculate relevance score for an article based on AI keywords"""
    if keywords is None:
        keywords = AI_KEYWORDS
    
    # Combine title and description for scoring
    text_content = ""
    if article.title:
        text_content += article.title.lower() + " "
    if article.description:
        text_content += article.description.lower() + " "
    
    if not text_content:
        return 0.0
    
    # Count keyword matches
    keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_content)
    
    # Base score from keyword density
    base_score = min(keyword_matches / len(keywords), 1.0)
    
    # Boost for high-value terms
    high_value_terms = ["artificial intelligence", "machine learning", "neural network", 
                       "deep learning", "LLM", "GPT", "transformer", "AI breakthrough"]
    high_value_matches = sum(1 for term in high_value_terms if term.lower() in text_content)
    high_value_boost = min(high_value_matches * 0.15, 0.3)
    
    # Title boost (articles with AI terms in title are more relevant)
    title_boost = 0.0
    if article.title:
        title_lower = article.title.lower()
        if any(keyword.lower() in title_lower for keyword in ["AI", "artificial intelligence", "machine learning"]):
            title_boost = 0.2
    
    final_score = min(base_score + high_value_boost + title_boost, 1.0)
    return round(final_score, 3)

def is_duplicate_article(article: RSSArticle, existing_articles: List[RSSArticle], 
                        similarity_threshold: float = 0.9) -> bool:
    """Check if article is a duplicate of existing articles"""
    if not article.content_hash:
        return False
    
    # Exact hash match
    for existing in existing_articles:
        if existing.content_hash == article.content_hash:
            return True
    
    # URL match (different feeds might have same article)
    article_url = str(article.url).lower()
    for existing in existing_articles:
        if str(existing.url).lower() == article_url:
            return True
    
    # Title similarity match (for very similar titles)
    if article.title and len(article.title) > 20:
        for existing in existing_articles:
            if existing.title and len(existing.title) > 20:
                # Simple similarity check
                title1_words = set(article.title.lower().split())
                title2_words = set(existing.title.lower().split())
                if title1_words and title2_words:
                    overlap = len(title1_words & title2_words)
                    similarity = overlap / min(len(title1_words), len(title2_words))
                    if similarity >= similarity_threshold:
                        return True
    
    return False

async def get_http_session() -> aiohttp.ClientSession:
    """Get or create HTTP session for RSS requests"""
    global _session
    settings = get_settings()
    
    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(total=settings.rss_timeout)
        headers = {
            "User-Agent": getattr(settings, 'user_agent', 'AI-News-Automation/1.0'),
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        _session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
        )
    
    return _session

def get_cache_key(source_name: str, force_refresh: bool = False) -> str:
    """Generate cache key for RSS source"""
    base_key = f"rss_feed:{source_name}"
    if force_refresh:
        base_key += f":{int(time.time())}"
    return base_key

def is_cache_valid(cache_entry: CacheEntry) -> bool:
    """Check if cache entry is still valid"""
    return not cache_entry.is_expired

# ============================================================================
# CORE RSS PROCESSING FUNCTIONS (ENHANCED)
# ============================================================================

async def fetch_single_rss_feed(source: RSSSourceConfig, 
                               max_articles: Optional[int] = None,
                               force_refresh: bool = False) -> FeedFetchResult:
    """Fetch and process a single RSS feed with enhanced content extraction"""
    start_time = time.time()
    result = FeedFetchResult(
        source_name=source.name,
        source_url=str(source.rss_feed_url),
        fetch_duration=0.0,
        status=FeedStatus.ACTIVE
    )
    
    try:
        # Check cache first (skip if force_refresh is True)
        if not force_refresh:
            cache_key = get_cache_key(source.name)
            if cache_key in _cache and is_cache_valid(_cache[cache_key]):
                cached_result = _cache[cache_key]
                cached_result.access()
                logger.info(f"Cache hit for {source.name}")
                _stats.cache_hit_rate = (_stats.cache_hit_rate + 1.0) / 2  # Simple moving average
                return cached_result.feed_result
        else:
            logger.info(f"Force refresh requested for {source.name}, bypassing cache")
        
        # Apply rate limiting
        await asyncio.sleep(source.rate_limit_delay)
        
        # Fetch RSS feed
        session = await get_http_session()
        logger.info(f"Fetching RSS feed from {source.name}: {source.rss_feed_url}")
        
        async with session.get(str(source.rss_feed_url)) as response:
            result.http_status_code = response.status
            
            if response.status != 200:
                result.status = FeedStatus.ERROR
                result.error_message = f"HTTP {response.status}"
                logger.error(f"HTTP error {response.status} for {source.name}")
                return result
            
            content = await response.text()
            result.bytes_downloaded = len(content.encode('utf-8'))
        
        # Parse RSS feed
        logger.debug(f"Parsing RSS content for {source.name}")
        feed = feedparser.parse(content)
        
        if feed.bozo and feed.bozo_exception:
            logger.warning(f"RSS parsing warning for {source.name}: {feed.bozo_exception}")
        
        # Extract feed metadata
        result.feed_title = getattr(feed.feed, 'title', None)
        result.feed_description = getattr(feed.feed, 'description', None)
        result.feed_language = getattr(feed.feed, 'language', None)
        
        # Parse feed last updated
        if hasattr(feed.feed, 'updated_parsed') and feed.feed.updated_parsed:
            try:
                result.feed_last_updated = datetime(*feed.feed.updated_parsed[:6], tzinfo=timezone.utc)
            except (ValueError, TypeError) as e:
                logger.debug(f"Could not parse feed update time for {source.name}: {e}")
        
        # Process articles
        max_articles = max_articles or source.max_articles_per_fetch
        articles = []
        seen_urls: Set[str] = set()
        
        for entry in feed.entries[:max_articles]:
            try:
                # Skip if URL already seen (within this fetch)
                entry_url = getattr(entry, 'link', '')
                if entry_url in seen_urls or not entry_url:
                    continue
                seen_urls.add(entry_url)
                
                # Parse publication date
                published_date = None
                for date_field in ['published_parsed', 'updated_parsed']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        try:
                            date_tuple = getattr(entry, date_field)
                            published_date = datetime(*date_tuple[:6], tzinfo=timezone.utc)
                            break
                        except (ValueError, TypeError):
                            continue
                
                # Extract content (ENHANCED VERSION)
                content = None
                description = None
                
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                
                # Clean HTML from description
                if description:
                    soup = BeautifulSoup(description, 'html.parser')
                    description = soup.get_text().strip()
                    if len(description) > 2000:
                        description = description[:1997] + "..."
                
                # ENHANCED: If content is short or missing, extract full article
                if not content or len(content) < 500:
                    logger.info(f"Extracting full content for: {getattr(entry, 'title', 'No title')[:50]}...")
                    full_content = await extract_full_article_content_enhanced(
                        entry_url, 
                        source.name, 
                        session
                    )
                    if full_content:
                        content = full_content
                        logger.info(f"✅ Extracted {len(full_content)} chars")
                    else:
                        logger.warning(f"❌ Could not extract content, using description")
                        content = description  # Fallback to description
                
                # Extract categories
                categories = []
                if hasattr(entry, 'tags'):
                    categories = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
                
                # Create article
                article = RSSArticle(
                    source_name=source.name,
                    title=getattr(entry, 'title', 'No Title'),
                    url=entry_url,
                    description=description,
                    content=content,
                    published_date=published_date,
                    author=getattr(entry, 'author', None),
                    categories=categories,
                    status=ArticleStatus.DISCOVERED
                )
                
                # Generate content hash for deduplication
                hash_content = f"{article.title} {article.description or ''} {article.content or ''}"
                article.content_hash = generate_content_hash(hash_content)
                
                # Calculate word count
                if article.content:
                    article.word_count = len(article.content.split())
                elif article.description:
                    article.word_count = len(article.description.split())
                
                # Calculate relevance score
                article.relevance_score = calculate_relevance_score(article)
                
                # Filter by relevance if keywords specified
                if source.keywords:
                    search_text = f"{article.title} {article.description or ''} {article.content or ''}"
                    if not any(keyword.lower() in search_text.lower() for keyword in source.keywords):
                        continue
                
                # Filter by exclude keywords
                if source.exclude_keywords:
                    search_text = f"{article.title} {article.description or ''} {article.content or ''}".lower()
                    if any(keyword.lower() in search_text for keyword in source.exclude_keywords):
                        continue
                
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error processing article from {source.name}: {e}")
                continue
        
        # Update result
        result.articles = articles
        result.articles_count = len(articles)
        result.new_articles_count = len(articles)  # All are new in this context
        result.fetch_duration = time.time() - start_time
        
        if articles:
            result.articles_per_second = len(articles) / result.fetch_duration
        
        # Cache successful result
        cache_key = get_cache_key(source.name)  # Get standard cache key for storage
        cache_entry = CacheEntry(
            cache_key=cache_key,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=source.fetch_interval),
            feed_result=result
        )
        _cache[cache_key] = cache_entry
        
        # Update statistics
        _stats.total_fetches += 1
        _stats.successful_fetches += 1
        _stats.total_articles_discovered += len(articles)
        
        logger.info(f"Successfully fetched {len(articles)} articles from {source.name} with enhanced content")
        return result
        
    except asyncio.TimeoutError:
        result.status = FeedStatus.TIMEOUT
        result.error_message = "Request timeout"
        result.fetch_duration = time.time() - start_time
        _stats.total_fetches += 1
        _stats.failed_fetches += 1
        logger.error(f"Timeout fetching {source.name}")
        
    except aiohttp.ClientError as e:
        result.status = FeedStatus.ERROR
        result.error_message = f"Network error: {str(e)}"
        result.fetch_duration = time.time() - start_time
        _stats.total_fetches += 1
        _stats.failed_fetches += 1
        logger.error(f"Network error fetching {source.name}: {e}")
        
    except Exception as e:
        result.status = FeedStatus.ERROR
        result.error_message = f"Unexpected error: {str(e)}"
        result.fetch_duration = time.time() - start_time
        _stats.total_fetches += 1
        _stats.failed_fetches += 1
        logger.error(f"Unexpected error fetching {source.name}: {e}")
    
    return result

async def fetch_article_content(article_url: str, source_name: str = "") -> Dict[str, Any]:
    """Fetch full content for a specific article using enhanced extraction"""
    start_time = time.time()
    result = {
        "url": article_url,
        "source_name": source_name,
        "success": False,
        "content": None,
        "title": None,
        "author": None,
        "published_date": None,
        "word_count": 0,
        "fetch_duration": 0.0,
        "error_message": None
    }
    
    try:
        session = await get_http_session()
        
        # Use enhanced content extraction
        content = await extract_full_article_content_enhanced(article_url, source_name, session)
        
        if content:
            result["content"] = content
            result["word_count"] = len(content.split())
            result["success"] = True
        else:
            result["error_message"] = "Could not extract content"
        
        result["fetch_duration"] = time.time() - start_time
        
        logger.info(f"Enhanced content extraction for {article_url}: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        return result
        
    except Exception as e:
        result["error_message"] = f"Error fetching article: {str(e)}"
        result["fetch_duration"] = time.time() - start_time
        logger.error(f"Error fetching article {article_url}: {e}")
        return result

# ============================================================================
# MCP TOOL FUNCTIONS (EXISTING FUNCTIONS REMAIN THE SAME)
# ============================================================================

async def initialize_sources() -> Dict[str, Any]:
    """Initialize RSS sources from configuration"""
    global _source_configs, _stats
    
    try:
        # Load default sources from constants
        _source_configs.clear()
        
        for source_data in DEFAULT_NEWS_SOURCES:
            try:
                source_config = RSSSourceConfig(
                    name=source_data["name"],
                    url=source_data["url"],
                    rss_feed_url=source_data["rss_feed_url"],
                    tier=source_data["tier"].value,
                    category=source_data["category"].value
                )
                _source_configs[source_config.name] = source_config
                
            except ValidationError as e:
                logger.error(f"Invalid source configuration for {source_data.get('name', 'unknown')}: {e}")
                continue
        
        # Update statistics
        _stats.total_sources = len(_source_configs)
        _stats.active_sources = sum(1 for source in _source_configs.values() if source.active)
        
        logger.info(f"Initialized {len(_source_configs)} RSS sources with enhanced content extraction")
        
        return {
            "success": True,
            "sources_loaded": len(_source_configs),
            "active_sources": _stats.active_sources,
            "sources": list(_source_configs.keys()),
            "enhanced_extraction": True
        }
        
    except Exception as e:
        logger.error(f"Error initializing RSS sources: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def fetch_all_sources(request: BatchFetchRequest) -> BatchFetchResult:
    """Fetch articles from multiple RSS sources with enhanced content extraction"""
    global _stats
    
    result = BatchFetchResult(request=request)
    
    try:
        # Determine which sources to fetch
        sources_to_fetch = []
        
        if request.source_names:
            # Specific sources requested
            for source_name in request.source_names:
                if source_name in _source_configs:
                    sources_to_fetch.append(_source_configs[source_name])
                else:
                    logger.warning(f"Unknown source requested: {source_name}")
        else:
            # All sources, with optional filtering
            sources_to_fetch = list(_source_configs.values())
            
            # Apply tier filter
            if request.tier_filter:
                sources_to_fetch = [s for s in sources_to_fetch if s.tier in request.tier_filter]
            
            # Apply category filter
            if request.category_filter:
                sources_to_fetch = [s for s in sources_to_fetch if s.category in request.category_filter]
        
        # Filter to only active sources
        sources_to_fetch = [s for s in sources_to_fetch if s.active]
        
        if not sources_to_fetch:
            logger.warning("No active sources to fetch")
            result.finalize()
            return result
        
        logger.info(f"Fetching from {len(sources_to_fetch)} sources with enhanced content extraction")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(request.parallel_limit)
        
        async def fetch_with_semaphore(source: RSSSourceConfig):
            async with semaphore:
                return await fetch_single_rss_feed(
                    source, 
                    max_articles=request.max_articles_per_source,
                    force_refresh=request.force_refresh
                )
        
        # Execute fetches concurrently
        tasks = [fetch_with_semaphore(source) for source in sources_to_fetch]
        feed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_articles = []
        for i, feed_result in enumerate(feed_results):
            if isinstance(feed_result, Exception):
                # Create error result for failed fetch
                error_result = FeedFetchResult(
                    source_name=sources_to_fetch[i].name,
                    source_url=str(sources_to_fetch[i].rss_feed_url),
                    fetch_duration=0.0,
                    status=FeedStatus.ERROR,
                    error_message=str(feed_result)
                )
                result.add_feed_result(error_result)
            else:
                result.add_feed_result(feed_result)
                all_articles.extend(feed_result.articles)
        
        # Apply time filtering
        if request.since_date:
            all_articles = [
                article for article in all_articles 
                if article.published_date and article.published_date >= request.since_date
            ]
        
        if request.max_age_hours:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=request.max_age_hours)
            all_articles = [
                article for article in all_articles
                if article.published_date and article.published_date >= cutoff_time
            ]
        
        # Apply keyword filtering
        if request.keywords_filter:
            filtered_articles = []
            for article in all_articles:
                text_content = f"{article.title} {article.description or ''} {article.content or ''}".lower()
                if any(keyword.lower() in text_content for keyword in request.keywords_filter):
                    filtered_articles.append(article)
                else:
                    result.filtered_articles += 1
            all_articles = filtered_articles
        
        # Remove duplicates if requested
        if request.exclude_duplicates:
            unique_articles = []
            for article in all_articles:
                if not is_duplicate_article(article, unique_articles):
                    unique_articles.append(article)
                else:
                    result.duplicate_articles += 1
            all_articles = unique_articles
        
        # Update final statistics
        result.all_articles = all_articles
        result.finalize()
        
        # Update global statistics
        _stats.unique_articles += result.new_articles
        _stats.filtered_articles += result.filtered_articles
        
        # Save articles to database if requested
        database_save_results = None
        if request.save_to_database and all_articles:
            try:
                from daemon_database import DaemonDatabase
                logger.info(f"Saving {len(all_articles)} articles to database...")
                database_save_results = DaemonDatabase.save_rss_articles(all_articles)
                logger.info(f"Database save results: {database_save_results}")
            except Exception as e:
                logger.error(f"Failed to save articles to database: {e}")
                database_save_results = {"error": str(e)}
        
        # Add database results to the batch result
        if database_save_results:
            result.database_save_results = database_save_results
        
        logger.info(
            f"Enhanced batch fetch completed: {result.total_articles} articles, "
            f"{result.new_articles} new, {result.duplicate_articles} duplicates, "
            f"{result.sources_successful}/{result.sources_attempted} sources successful"
        )
        
        if database_save_results and "error" not in database_save_results:
            logger.info(
                f"Database save: {database_save_results.get('saved', 0)} saved, "
                f"{database_save_results.get('skipped', 0)} skipped"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced batch fetch: {e}")
        result.error_count += 1
        result.error_summary["batch_error"] = 1
        result.finalize()
        return result

async def get_cached_articles(source_name: Optional[str] = None, 
                             limit: int = 50) -> Dict[str, Any]:
    """Get cached articles from memory"""
    try:
        cached_articles = []
        
        if source_name:
            # Get articles for specific source
            cache_key = get_cache_key(source_name)
            if cache_key in _cache and is_cache_valid(_cache[cache_key]):
                cached_entry = _cache[cache_key]
                cached_entry.access()
                cached_articles = cached_entry.feed_result.articles[:limit]
        else:
            # Get articles from all cached sources
            for cache_entry in _cache.values():
                if is_cache_valid(cache_entry):
                    cache_entry.access()
                    cached_articles.extend(cache_entry.feed_result.articles)
            
            # Sort by fetch time (newest first) and limit
            cached_articles.sort(key=lambda x: x.fetched_at, reverse=True)
            cached_articles = cached_articles[:limit]
        
        return {
            "success": True,
            "articles_count": len(cached_articles),
            "articles": [article.dict() for article in cached_articles],
            "cache_entries": len(_cache),
            "source_name": source_name,
            "enhanced_extraction": True
        }
        
    except Exception as e:
        logger.error(f"Error getting cached articles: {e}")
        return {
            "success": False,
            "error": str(e),
            "articles_count": 0,
            "articles": []
        }

async def get_server_status() -> Dict[str, Any]:
    """Get RSS aggregator server status and statistics"""
    global _stats, _server_start_time
    
    try:
        # Update uptime
        _stats.uptime_seconds = time.time() - _server_start_time
        
        # Update source counts
        _stats.total_sources = len(_source_configs)
        _stats.active_sources = sum(1 for s in _source_configs.values() if s.active)
        _stats.error_sources = _stats.total_sources - _stats.active_sources
        
        # Update cache statistics
        _stats.cache_entries = len(_cache)
        
        # Calculate error rate
        if _stats.total_fetches > 0:
            _stats.error_rate = _stats.failed_fetches / _stats.total_fetches
        
        # Calculate articles per hour
        if _stats.uptime_seconds > 0:
            _stats.articles_per_hour = (_stats.total_articles_discovered * 3600) / _stats.uptime_seconds
        
        return {
            "success": True,
            "server_status": "healthy",
            "uptime_hours": _stats.uptime_seconds / 3600,
            "enhanced_extraction": True,
            "statistics": _stats.dict(),
            "source_summary": {
                "total": _stats.total_sources,
                "active": _stats.active_sources,
                "inactive": _stats.error_sources
            },
            "performance": {
                "total_fetches": _stats.total_fetches,
                "success_rate": _stats.success_rate,
                "articles_per_hour": _stats.articles_per_hour,
                "cache_hit_rate": _stats.cache_hit_rate
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting server status: {e}")
        return {
            "success": False,
            "server_status": "error",
            "error": str(e)
        }

async def cleanup_cache(max_age_hours: int = 24) -> Dict[str, Any]:
    """Clean up expired cache entries"""
    global _cache
    
    try:
        initial_count = len(_cache)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        # Remove expired entries
        expired_keys = [
            key for key, entry in _cache.items()
            if entry.is_expired or entry.cached_at < cutoff_time
        ]
        
        for key in expired_keys:
            del _cache[key]
        
        cleaned_count = len(expired_keys)
        remaining_count = len(_cache)
        
        logger.info(f"Cache cleanup: removed {cleaned_count} entries, {remaining_count} remaining")
        
        return {
            "success": True,
            "initial_entries": initial_count,
            "cleaned_entries": cleaned_count,
            "remaining_entries": remaining_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning cache: {e}")
        return {
            "success": False,
            "error": str(e)
        }