"""
RSS Aggregator MCP Server Package
Location: mcp_servers/rss_aggregator/__init__.py

MCP server for RSS feed aggregation and article discovery.
Provides tools for News Discovery Agent to fetch AI news from 12+ sources.
"""

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

from .tools import (
    initialize_sources,
    fetch_all_sources,
    get_cached_articles,
    fetch_article_content,
    get_server_status,
    cleanup_cache,
    fetch_single_rss_feed
)

from .server import (
    server,
    startup,
    shutdown,
    health_check,
    main
)

__all__ = [
    # Schemas
    'RSSSourceConfig',
    'RSSArticle',
    'FeedFetchResult', 
    'BatchFetchRequest',
    'BatchFetchResult',
    'FeedStatus',
    'ArticleStatus',
    'CacheEntry',
    'RSSServerStats',
    
    # Tools
    'initialize_sources',
    'fetch_all_sources',
    'get_cached_articles', 
    'fetch_article_content',
    'get_server_status',
    'cleanup_cache',
    'fetch_single_rss_feed',
    
    # Server
    'server',
    'startup',
    'shutdown',
    'health_check',
    'main'
]

# Package metadata
__version__ = "1.0.0"
__description__ = "RSS Aggregator MCP Server for AI News Automation System"