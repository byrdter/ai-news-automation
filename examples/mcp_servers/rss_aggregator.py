"""
Example MCP Server for RSS Aggregation
Location: examples/mcp_servers/rss_aggregator.py

This demonstrates:
- MCP server implementation patterns
- Tool registration and validation
- Error handling and rate limiting
- Async operations with proper resource management
- Integration with external RSS feeds
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import feedparser
import aiohttp
from pydantic import BaseModel, Field, ValidationError

# MCP imports (adjust based on actual MCP library)
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configuration models
class RSSSource(BaseModel):
    """RSS source configuration"""
    name: str
    url: str
    feed_url: str
    tier: int = Field(ge=1, le=3)
    active: bool = True
    last_fetched: Optional[datetime] = None
    fetch_interval: int = Field(default=3600, description="Fetch interval in seconds")
    max_articles: int = Field(default=50, description="Maximum articles to fetch")

class Article(BaseModel):
    """Article data structure"""
    title: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = []
    fetched_at: datetime = Field(default_factory=datetime.now)

class RSSAggregatorConfig(BaseModel):
    """Configuration for RSS aggregator"""
    sources: List[RSSSource]
    rate_limit_delay: float = 1.0  # Seconds between requests
    timeout: int = 30  # Request timeout
    max_concurrent: int = 5  # Max concurrent requests
    user_agent: str = "AI-News-Aggregator/1.0"

# Initialize MCP server
server = Server("rss-aggregator")

# Global configuration and state
config: Optional[RSSAggregatorConfig] = None
article_cache: Dict[str, List[Article]] = {}
rate_limit_tracker: Dict[str, datetime] = {}

# HTTP session for efficient connection reuse
http_session: Optional[aiohttp.ClientSession] = None

async def get_http_session() -> aiohttp.ClientSession:
    """Get or create HTTP session"""
    global http_session
    if http_session is None or http_session.closed:
        timeout = aiohttp.ClientTimeout(total=config.timeout if config else 30)
        http_session = aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": config.user_agent if config else "AI-News-Aggregator/1.0"}
        )
    return http_session

async def cleanup_http_session():
    """Cleanup HTTP session"""
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()

def should_fetch_source(source: RSSSource) -> bool:
    """Check if source should be fetched based on rate limiting"""
    if not source.active:
        return False
    
    last_fetch = rate_limit_tracker.get(source.name)
    if last_fetch is None:
        return True
    
    next_fetch = last_fetch + timedelta(seconds=source.fetch_interval)
    return datetime.now() >= next_fetch

async def fetch_rss_feed(source: RSSSource) -> List[Article]:
    """Fetch and parse RSS feed from a source"""
    try:
        # Check rate limiting
        if not should_fetch_source(source):
            logging.info(f"Skipping {source.name} due to rate limiting")
            return article_cache.get(source.name, [])
        
        # Apply rate limiting delay
        if config and config.rate_limit_delay > 0:
            await asyncio.sleep(config.rate_limit_delay)
        
        # Fetch RSS feed
        session = await get_http_session()
        async with session.get(source.feed_url) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch {source.name}: HTTP {response.status}")
                return []
            
            content = await response.text()
        
        # Parse RSS feed
        feed = feedparser.parse(content)
        
        if feed.bozo and feed.bozo_exception:
            logging.warning(f"RSS parsing warning for {source.name}: {feed.bozo_exception}")
        
        # Convert to Article objects
        articles = []
        for entry in feed.entries[:source.max_articles]:
            try:
                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])
                
                # Extract content
                content = None
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                # Extract summary
                summary = getattr(entry, 'summary', content)
                if summary and len(summary) > 500:
                    summary = summary[:497] + "..."
                
                # Create Article
                article = Article(
                    title=getattr(entry, 'title', 'No Title'),
                    url=getattr(entry, 'link', ''),
                    source=source.name,
                    published_date=published_date,
                    summary=summary,
                    content=content,
                    tags=getattr(entry, 'tags', [])
                )
                
                articles.append(article)
                
            except Exception as e:
                logging.error(f"Error processing article from {source.name}: {e}")
                continue
        
        # Update cache and rate limiting
        article_cache[source.name] = articles
        rate_limit_tracker[source.name] = datetime.now()
        
        logging.info(f"Fetched {len(articles)} articles from {source.name}")
        return articles
        
    except Exception as e:
        logging.error(f"Error fetching RSS feed from {source.name}: {e}")
        return []

# MCP Tool Definitions
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available RSS aggregator tools"""
    return [
        Tool(
            name="fetch_all_sources",
            description="Fetch articles from all configured RSS sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh even if rate limited",
                        "default": False
                    },
                    "sources_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of source names to fetch"
                    }
                }
            }
        ),
        Tool(
            name="get_cached_articles",
            description="Get cached articles from memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source name to get articles from"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of articles to return",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="configure_sources",
            description="Configure RSS sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "url": {"type": "string"},
                                "feed_url": {"type": "string"},
                                "tier": {"type": "integer", "minimum": 1, "maximum": 3},
                                "active": {"type": "boolean", "default": True}
                            },
                            "required": ["name", "url", "feed_url"]
                        }
                    }
                }
            }
        ),
        Tool(
            name="get_source_status",
            description="Get status of all configured sources",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "fetch_all_sources":
            return await handle_fetch_all_sources(arguments)
        elif name == "get_cached_articles":
            return await handle_get_cached_articles(arguments)
        elif name == "configure_sources":
            return await handle_configure_sources(arguments)
        elif name == "get_source_status":
            return await handle_get_source_status(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logging.error(f"Error handling tool call {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_fetch_all_sources(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle fetch_all_sources tool call"""
    if not config:
        return [TextContent(type="text", text="RSS aggregator not configured")]
    
    force_refresh = arguments.get("force_refresh", False)
    sources_filter = arguments.get("sources_filter", [])
    
    # Determine which sources to fetch
    sources_to_fetch = config.sources
    if sources_filter:
        sources_to_fetch = [s for s in config.sources if s.name in sources_filter]
    
    # Temporarily override rate limiting if force_refresh
    if force_refresh:
        rate_limit_tracker.clear()
    
    # Fetch articles concurrently with rate limiting
    semaphore = asyncio.Semaphore(config.max_concurrent)
    
    async def fetch_with_semaphore(source: RSSSource):
        async with semaphore:
            return await fetch_rss_feed(source)
    
    # Execute fetches
    tasks = [fetch_with_semaphore(source) for source in sources_to_fetch]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Compile results
    total_articles = 0
    successful_sources = 0
    errors = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"{sources_to_fetch[i].name}: {str(result)}")
        else:
            total_articles += len(result)
            successful_sources += 1
    
    # Format response
    response = f"Fetched {total_articles} articles from {successful_sources}/{len(sources_to_fetch)} sources"
    if errors:
        response += f"\nErrors: {'; '.join(errors)}"
    
    return [TextContent(type="text", text=response)]

async def handle_get_cached_articles(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_cached_articles tool call"""
    source = arguments.get("source")
    limit = arguments.get("limit", 50)
    
    if source:
        articles = article_cache.get(source, [])
    else:
        # Get all cached articles
        articles = []
        for source_articles in article_cache.values():
            articles.extend(source_articles)
    
    # Apply limit
    articles = articles[:limit]
    
    # Format response
    if not articles:
        return [TextContent(type="text", text="No cached articles found")]
    
    response = f"Found {len(articles)} cached articles:\n\n"
    for article in articles:
        response += f"• {article.title}\n"
        response += f"  Source: {article.source}\n"
        response += f"  URL: {article.url}\n"
        if article.published_date:
            response += f"  Published: {article.published_date.strftime('%Y-%m-%d %H:%M')}\n"
        response += "\n"
    
    return [TextContent(type="text", text=response)]

async def handle_configure_sources(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle configure_sources tool call"""
    global config
    
    try:
        sources_data = arguments.get("sources", [])
        sources = [RSSSource(**source_data) for source_data in sources_data]
        
        config = RSSAggregatorConfig(sources=sources)
        
        return [TextContent(
            type="text", 
            text=f"Configured {len(sources)} RSS sources successfully"
        )]
        
    except ValidationError as e:
        return [TextContent(type="text", text=f"Configuration error: {str(e)}")]

async def handle_get_source_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_source_status tool call"""
    if not config:
        return [TextContent(type="text", text="RSS aggregator not configured")]
    
    response = "RSS Source Status:\n\n"
    
    for source in config.sources:
        response += f"• {source.name} (Tier {source.tier})\n"
        response += f"  Status: {'Active' if source.active else 'Inactive'}\n"
        response += f"  URL: {source.feed_url}\n"
        
        last_fetch = rate_limit_tracker.get(source.name)
        if last_fetch:
            response += f"  Last Fetched: {last_fetch.strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            response += f"  Last Fetched: Never\n"
        
        cached_count = len(article_cache.get(source.name, []))
        response += f"  Cached Articles: {cached_count}\n"
        response += "\n"
    
    return [TextContent(type="text", text=response)]

# Server startup and cleanup
async def main():
    """Main server function"""
    try:
        logging.info("Starting RSS Aggregator MCP Server")
        
        # Initialize with default configuration
        default_sources = [
            RSSSource(
                name="OpenAI Blog",
                url="https://openai.com/blog",
                feed_url="https://openai.com/blog/rss.xml",
                tier=1
            ),
            RSSSource(
                name="Google AI Blog",
                url="https://ai.googleblog.com",
                feed_url="https://ai.googleblog.com/feeds/posts/default",
                tier=1
            ),
            RSSSource(
                name="MIT AI News",
                url="https://news.mit.edu/topic/artificial-intelligence2",
                feed_url="https://news.mit.edu/rss/topic/artificial-intelligence2",
                tier=1
            )
        ]
        
        global config
        config = RSSAggregatorConfig(sources=default_sources)
        
        # Run server
        await server.run()
        
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        await cleanup_http_session()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())