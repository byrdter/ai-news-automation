"""
RSS Aggregator MCP Server.

Provides RSS feed fetching, parsing, and content extraction tools
for the News Discovery Agent.
"""

import asyncio
import aiohttp
import feedparser
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializeRequest
from pydantic import BaseModel, Field, HttpUrl
from newspaper import Article as NewspaperArticle

from config.settings import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("RSS Aggregator")


class FeedFetchRequest(BaseModel):
    """Request to fetch RSS feed."""
    feed_url: HttpUrl
    max_articles: int = Field(default=50, ge=1, le=200)
    timeout: int = Field(default=30, ge=5, le=120)
    user_agent: str = Field(default="AI News System/1.0")


class ArticleExtractionRequest(BaseModel):
    """Request to extract article content."""
    article_url: HttpUrl
    timeout: int = Field(default=30, ge=5, le=120)
    extract_images: bool = Field(default=False)
    extract_authors: bool = Field(default=True)


class RSSFeedResult(BaseModel):
    """Result from RSS feed fetch."""
    feed_url: str
    title: str
    description: str
    articles: List[Dict[str, Any]]
    fetch_time: float
    error: Optional[str] = None


class ArticleContent(BaseModel):
    """Extracted article content."""
    url: str
    title: str
    content: str
    summary: str
    authors: List[str]
    publish_date: Optional[datetime]
    images: List[str]
    meta_keywords: List[str]
    extraction_time: float
    word_count: int
    error: Optional[str] = None


class RSSAggregator:
    """RSS feed aggregation and content extraction."""
    
    def __init__(self):
        """Initialize RSS aggregator."""
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.last_request_time = 0.0
        self.request_count = 0
        self.rate_limit_window = 60.0  # seconds
        
        # User agent for requests
        self.user_agent = "Mozilla/5.0 (compatible; AI News System/1.0)"
        
        # Cache for feed metadata
        self.feed_cache = {}
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=60)
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                connector=aiohttp.TCPConnector(limit=10)
            )
        return self.session
    
    async def rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        
        # Reset counter if window expired
        if current_time - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
        
        # Check rate limit
        if self.request_count >= self.settings.rss.requests_per_minute:
            wait_time = self.rate_limit_window - (current_time - self.last_request_time)
            if wait_time > 0:
                logger.info(f"Rate limiting: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.request_count = 0
        
        self.request_count += 1
        self.last_request_time = current_time
        
        # Add small delay between requests
        await asyncio.sleep(0.5)
    
    async def fetch_feed_raw(self, feed_url: str, timeout: int = 30) -> Dict[str, Any]:
        """Fetch raw RSS feed content."""
        session = await self.get_session()
        
        try:
            await self.rate_limit()
            
            async with session.get(str(feed_url), timeout=timeout) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"HTTP {response.status}"
                    )
                
                content = await response.text()
                content_type = response.headers.get('content-type', '')
                
                return {
                    'content': content,
                    'content_type': content_type,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'size': len(content.encode('utf-8'))
                }
                
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            raise
    
    def parse_feed(self, feed_content: str, feed_url: str) -> Dict[str, Any]:
        """Parse RSS feed content using feedparser."""
        start_time = time.time()
        
        try:
            # Parse feed
            parsed = feedparser.parse(feed_content)
            
            # Extract feed metadata
            feed_info = {
                'title': getattr(parsed.feed, 'title', 'Unknown Feed'),
                'description': getattr(parsed.feed, 'description', ''),
                'link': getattr(parsed.feed, 'link', feed_url),
                'language': getattr(parsed.feed, 'language', 'en'),
                'updated': getattr(parsed.feed, 'updated', None),
                'generator': getattr(parsed.feed, 'generator', ''),
            }
            
            # Extract articles
            articles = []
            for entry in parsed.entries[:50]:  # Limit to 50 entries
                try:
                    article = self._extract_article_from_entry(entry, feed_url)
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Error parsing entry: {e}")
                    continue
            
            parse_time = time.time() - start_time
            
            return {
                'feed_info': feed_info,
                'articles': articles,
                'article_count': len(articles),
                'parse_time': parse_time,
                'raw_entry_count': len(parsed.entries),
                'parser_version': feedparser.__version__
            }
            
        except Exception as e:
            logger.error(f"Error parsing feed: {e}")
            raise
    
    def _extract_article_from_entry(self, entry: Any, feed_url: str) -> Dict[str, Any]:
        """Extract article data from feedparser entry."""
        
        # Basic article info
        title = getattr(entry, 'title', '').strip()
        link = getattr(entry, 'link', '')
        summary = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
        
        # Publication date
        published = None
        for date_attr in ['published_parsed', 'updated_parsed']:
            if hasattr(entry, date_attr):
                time_struct = getattr(entry, date_attr)
                if time_struct:
                    try:
                        published = datetime(*time_struct[:6], tzinfo=timezone.utc)
                        break
                    except (TypeError, ValueError):
                        continue
        
        # If no date found, use current time
        if not published:
            published = datetime.now(timezone.utc)
        
        # Author information
        author = ''
        if hasattr(entry, 'author'):
            author = entry.author
        elif hasattr(entry, 'authors') and entry.authors:
            author = entry.authors[0].get('name', '') if isinstance(entry.authors[0], dict) else str(entry.authors[0])
        
        # Tags/categories
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
        
        # Content (prefer content over summary)
        content = summary
        if hasattr(entry, 'content') and entry.content:
            if isinstance(entry.content, list) and entry.content:
                content = entry.content[0].get('value', summary)
            else:
                content = str(entry.content)
        
        # Clean HTML from content
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()
        
        # Generate content hash for deduplication
        content_for_hash = f"{title}|{link}|{summary}"
        content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
        
        return {
            'title': title,
            'url': link,
            'summary': summary,
            'content': content,
            'author': author,
            'published_date': published.isoformat() if published else None,
            'tags': tags,
            'guid': getattr(entry, 'id', '') or getattr(entry, 'guid', ''),
            'content_hash': content_hash,
            'word_count': len(content.split()) if content else 0,
            'source_feed': feed_url
        }
    
    async def extract_article_content(self, article_url: str, timeout: int = 30) -> Dict[str, Any]:
        """Extract full content from article URL using newspaper3k."""
        start_time = time.time()
        
        try:
            # Use newspaper3k for content extraction
            article = NewspaperArticle(article_url)
            article.config.request_timeout = timeout
            article.config.browser_user_agent = self.user_agent
            
            # Download and parse
            article.download()
            article.parse()
            
            # Extract NLP features
            try:
                article.nlp()
            except Exception as nlp_error:
                logger.warning(f"NLP extraction failed for {article_url}: {nlp_error}")
            
            extraction_time = time.time() - start_time
            
            return {
                'url': article_url,
                'title': article.title or '',
                'content': article.text or '',
                'summary': article.summary or '',
                'authors': article.authors or [],
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'images': list(article.images) if hasattr(article, 'images') else [],
                'meta_keywords': article.keywords or [],
                'extraction_time': extraction_time,
                'word_count': len(article.text.split()) if article.text else 0,
                'top_image': article.top_image or '',
                'canonical_link': article.canonical_link or article_url,
                'meta_description': article.meta_description or '',
                'meta_lang': article.meta_lang or 'en'
            }
            
        except Exception as e:
            logger.error(f"Error extracting article {article_url}: {e}")
            return {
                'url': article_url,
                'error': str(e),
                'extraction_time': time.time() - start_time
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()


# Global aggregator instance
aggregator = RSSAggregator()


@mcp.tool()
async def fetch_rss_feed(request: FeedFetchRequest) -> RSSFeedResult:
    """
    Fetch and parse RSS feed.
    
    Returns parsed articles with metadata from RSS feed.
    """
    start_time = time.time()
    feed_url = str(request.feed_url)
    
    try:
        logger.info(f"Fetching RSS feed: {feed_url}")
        
        # Fetch raw feed content
        raw_data = await aggregator.fetch_feed_raw(feed_url, request.timeout)
        
        # Parse feed content
        parsed_data = aggregator.parse_feed(raw_data['content'], feed_url)
        
        # Limit articles
        articles = parsed_data['articles'][:request.max_articles]
        
        fetch_time = time.time() - start_time
        
        logger.info(f"Successfully fetched {len(articles)} articles from {feed_url} in {fetch_time:.2f}s")
        
        return RSSFeedResult(
            feed_url=feed_url,
            title=parsed_data['feed_info']['title'],
            description=parsed_data['feed_info']['description'],
            articles=articles,
            fetch_time=fetch_time
        )
        
    except Exception as e:
        error_msg = f"Failed to fetch RSS feed {feed_url}: {str(e)}"
        logger.error(error_msg)
        
        return RSSFeedResult(
            feed_url=feed_url,
            title="",
            description="",
            articles=[],
            fetch_time=time.time() - start_time,
            error=error_msg
        )


@mcp.tool()
async def extract_article_content(request: ArticleExtractionRequest) -> ArticleContent:
    """
    Extract full content from article URL.
    
    Uses newspaper3k to extract clean article text, metadata, and images.
    """
    article_url = str(request.article_url)
    
    try:
        logger.info(f"Extracting content from: {article_url}")
        
        # Extract content using newspaper3k
        result = await aggregator.extract_article_content(article_url, request.timeout)
        
        if 'error' in result:
            logger.error(f"Content extraction failed for {article_url}: {result['error']}")
            return ArticleContent(
                url=article_url,
                title="",
                content="",
                summary="",
                authors=[],
                publish_date=None,
                images=[],
                meta_keywords=[],
                extraction_time=result['extraction_time'],
                word_count=0,
                error=result['error']
            )
        
        logger.info(f"Successfully extracted {result['word_count']} words from {article_url}")
        
        return ArticleContent(
            url=result['url'],
            title=result['title'],
            content=result['content'],
            summary=result['summary'],
            authors=result['authors'],
            publish_date=datetime.fromisoformat(result['publish_date']) if result['publish_date'] else None,
            images=result['images'] if request.extract_images else [],
            meta_keywords=result['meta_keywords'],
            extraction_time=result['extraction_time'],
            word_count=result['word_count']
        )
        
    except Exception as e:
        error_msg = f"Failed to extract content from {article_url}: {str(e)}"
        logger.error(error_msg)
        
        return ArticleContent(
            url=article_url,
            title="",
            content="",
            summary="",
            authors=[],
            publish_date=None,
            images=[],
            meta_keywords=[],
            extraction_time=0.0,
            word_count=0,
            error=error_msg
        )


@mcp.tool()
async def batch_fetch_feeds(feed_urls: List[str], max_concurrent: int = 5) -> List[RSSFeedResult]:
    """
    Batch fetch multiple RSS feeds concurrently.
    
    Processes multiple feeds with concurrency control and rate limiting.
    """
    logger.info(f"Batch fetching {len(feed_urls)} RSS feeds with max_concurrent={max_concurrent}")
    
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_single_feed(url: str) -> RSSFeedResult:
        async with semaphore:
            request = FeedFetchRequest(feed_url=url)
            return await fetch_rss_feed(request)
    
    # Execute all fetches
    tasks = [fetch_single_feed(url) for url in feed_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(RSSFeedResult(
                feed_url=feed_urls[i],
                title="",
                description="",
                articles=[],
                fetch_time=0.0,
                error=str(result)
            ))
        else:
            final_results.append(result)
    
    successful = sum(1 for r in final_results if not r.error)
    total_articles = sum(len(r.articles) for r in final_results)
    
    logger.info(f"Batch fetch completed: {successful}/{len(feed_urls)} feeds successful, {total_articles} total articles")
    
    return final_results


@mcp.tool()
async def validate_feed_url(url: str) -> Dict[str, Any]:
    """
    Validate RSS feed URL and return metadata.
    
    Checks if URL is accessible and contains valid RSS content.
    """
    try:
        logger.info(f"Validating RSS feed URL: {url}")
        
        # Fetch basic info
        raw_data = await aggregator.fetch_feed_raw(url, timeout=15)
        
        # Check content type
        content_type = raw_data['content_type'].lower()
        is_feed = any(feed_type in content_type for feed_type in [
            'rss', 'atom', 'xml', 'feed'
        ])
        
        # Try parsing
        parse_result = aggregator.parse_feed(raw_data['content'], url)
        
        return {
            'valid': True,
            'accessible': True,
            'is_feed_content': is_feed,
            'content_type': content_type,
            'feed_title': parse_result['feed_info']['title'],
            'feed_description': parse_result['feed_info']['description'],
            'article_count': parse_result['article_count'],
            'size_bytes': raw_data['size'],
            'response_time': parse_result['parse_time']
        }
        
    except Exception as e:
        logger.error(f"Feed validation failed for {url}: {e}")
        return {
            'valid': False,
            'accessible': False,
            'error': str(e)
        }


# Server lifecycle management
@mcp.on_shutdown
async def cleanup():
    """Clean up resources on server shutdown."""
    await aggregator.cleanup()


if __name__ == "__main__":
    # Run the MCP server
    import uvicorn
    from mcp.server.fastmcp import FastMCPServer
    
    settings = get_settings()
    port = settings.system.mcp_rss_server_port if hasattr(settings.system, 'mcp_rss_server_port') else 3001
    
    logger.info(f"Starting RSS Aggregator MCP Server on port {port}")
    
    # Create FastMCP server instance
    app = FastMCPServer(mcp)
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        reload=False
    )