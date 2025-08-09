"""
RSS Aggregator MCP Server
Location: mcp_servers/rss_aggregator/server.py

MCP server implementation for RSS feed aggregation and article discovery.
Provides tools for News Discovery Agent to fetch and process AI news from 12+ sources.
"""

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    Tool, 
    TextContent, 
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import ValidationError

from config.settings import get_settings
from config.constants import MCPServerType, DEFAULT_NEWS_SOURCES
from .schemas import BatchFetchRequest, RSSSourceConfig
from .tools import (
    initialize_sources,
    fetch_all_sources,
    get_cached_articles,
    fetch_article_content,
    get_server_status,
    cleanup_cache
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server(MCPServerType.RSS_AGGREGATOR)

# ============================================================================
# MCP TOOL REGISTRATION
# ============================================================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Register available RSS aggregator tools with detailed schemas"""
    
    return [
        Tool(
            name="initialize_sources",
            description="Initialize RSS news sources from default configuration (12+ AI news sources)",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        
        Tool(
            name="fetch_all_sources",
            description="Fetch articles from multiple RSS sources with filtering and deduplication",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific source names to fetch (optional)"
                    },
                    "tier_filter": {
                        "type": "array", 
                        "items": {"type": "integer", "minimum": 1, "maximum": 3},
                        "description": "Filter by source tiers (1=highest quality, 3=lowest)"
                    },
                    "category_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories (Academic Research, Industry News, etc.)"
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Bypass cache and force fresh fetch",
                        "default": False
                    },
                    "max_articles_per_source": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 200,
                        "description": "Maximum articles to fetch per source"
                    },
                    "parallel_limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "description": "Maximum parallel requests",
                        "default": 5
                    },
                    "keywords_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Required keywords for article inclusion"
                    },
                    "exclude_duplicates": {
                        "type": "boolean",
                        "description": "Remove duplicate articles",
                        "default": True
                    },
                    "since_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Only fetch articles after this date (ISO format)"
                    },
                    "max_age_hours": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 168,
                        "description": "Maximum article age in hours"
                    }
                },
                "additionalProperties": False
            }
        ),
        
        Tool(
            name="get_cached_articles",
            description="Retrieve cached articles from memory for fast access",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_name": {
                        "type": "string",
                        "description": "Specific source name to get articles from (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 500,
                        "description": "Maximum number of articles to return",
                        "default": 50
                    }
                },
                "additionalProperties": False
            }
        ),
        
        Tool(
            name="fetch_article_content",
            description="Fetch full content for a specific article URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL of the article to fetch"
                    },
                    "source_name": {
                        "type": "string",
                        "description": "Source name for tracking (optional)"
                    }
                },
                "required": ["article_url"],
                "additionalProperties": False
            }
        ),
        
        Tool(
            name="get_server_status",
            description="Get RSS aggregator server status, statistics, and health information",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        
        Tool(
            name="configure_sources",
            description="Add or update RSS source configurations",
            inputSchema={
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "minLength": 1, "maxLength": 255},
                                "url": {"type": "string", "format": "uri"},
                                "rss_feed_url": {"type": "string", "format": "uri"},
                                "tier": {"type": "integer", "minimum": 1, "maximum": 3, "default": 2},
                                "category": {"type": "string", "maxLength": 100, "default": "Industry News"},
                                "active": {"type": "boolean", "default": True},
                                "fetch_interval": {"type": "integer", "minimum": 300, "maximum": 86400, "default": 3600},
                                "max_articles_per_fetch": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
                                "keywords": {"type": "array", "items": {"type": "string"}},
                                "exclude_keywords": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "url", "rss_feed_url"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["sources"],
                "additionalProperties": False
            }
        ),
        
        Tool(
            name="cleanup_cache",
            description="Clean up expired cache entries to free memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_age_hours": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 168,
                        "description": "Maximum age for cache entries in hours",
                        "default": 24
                    }
                },
                "additionalProperties": False
            }
        )
    ]

# ============================================================================
# MCP TOOL HANDLERS
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MCP tool calls with comprehensive error handling"""
    
    logger.info(f"RSS Aggregator tool called: {name} with args: {json.dumps(arguments, default=str)}")
    
    try:
        if name == "initialize_sources":
            result = await initialize_sources()
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "fetch_all_sources":
            # Validate and create request
            try:
                # Parse datetime if provided
                if "since_date" in arguments and arguments["since_date"]:
                    arguments["since_date"] = datetime.fromisoformat(arguments["since_date"].replace('Z', '+00:00'))
                
                request = BatchFetchRequest(**arguments)
                result = await fetch_all_sources(request)
                
                # Convert to JSON-serializable format
                result_dict = result.dict()
                result_dict["success"] = True
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result_dict, indent=2, default=str)
                )]
                
            except ValidationError as e:
                error_msg = f"Invalid request parameters: {e}"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": error_msg}, indent=2)
                )]
        
        elif name == "get_cached_articles":
            source_name = arguments.get("source_name")
            limit = arguments.get("limit", 50)
            
            result = await get_cached_articles(source_name, limit)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "fetch_article_content":
            article_url = arguments.get("article_url")
            source_name = arguments.get("source_name", "")
            
            if not article_url:
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": "article_url is required"})
                )]
            
            result = await fetch_article_content(article_url, source_name)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_server_status":
            result = await get_server_status()
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "configure_sources":
            try:
                sources_data = arguments.get("sources", [])
                
                # Validate source configurations
                new_sources = []
                for source_data in sources_data:
                    source_config = RSSSourceConfig(**source_data)
                    new_sources.append(source_config)
                
                # Update global source configurations
                from .tools import _source_configs
                for source in new_sources:
                    _source_configs[source.name] = source
                
                result = {
                    "success": True,
                    "sources_configured": len(new_sources),
                    "total_sources": len(_source_configs),
                    "new_sources": [s.name for s in new_sources]
                }
                
                logger.info(f"Configured {len(new_sources)} RSS sources")
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except ValidationError as e:
                error_msg = f"Invalid source configuration: {e}"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": error_msg}, indent=2)
                )]
        
        elif name == "cleanup_cache":
            max_age_hours = arguments.get("max_age_hours", 24)
            result = await cleanup_cache(max_age_hours)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": error_msg})
            )]
    
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": error_msg,
                "tool": name,
                "arguments": arguments
            }, indent=2, default=str)
        )]

# ============================================================================
# SERVER LIFECYCLE MANAGEMENT
# ============================================================================

@server.list_resources()
async def list_resources() -> List[EmbeddedResource]:
    """List available resources (currently none for RSS aggregator)"""
    return []

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content (currently not implemented)"""
    raise NotImplementedError("Resource reading not implemented for RSS aggregator")

# ============================================================================
# SERVER STARTUP AND MAIN FUNCTION
# ============================================================================

async def startup():
    """Initialize the RSS aggregator server"""
    try:
        logger.info("Starting RSS Aggregator MCP Server...")
        
        # Load settings
        settings = get_settings()
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"RSS fetch interval: {settings.rss_fetch_interval}s")
        logger.info(f"Max concurrent requests: {settings.rss_max_concurrent}")
        
        # Initialize default sources
        result = await initialize_sources()
        if result["success"]:
            logger.info(f"Initialized {result['sources_loaded']} RSS sources")
        else:
            logger.error(f"Failed to initialize sources: {result.get('error', 'Unknown error')}")
        
        # Log available sources
        from .tools import _source_configs
        for tier in [1, 2, 3]:
            tier_sources = [s for s in _source_configs.values() if s.tier == tier]
            logger.info(f"Tier {tier} sources: {[s.name for s in tier_sources]}")
        
        logger.info("RSS Aggregator MCP Server started successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to start RSS Aggregator server: {e}", exc_info=True)
        return False

async def shutdown():
    """Clean shutdown of the RSS aggregator server"""
    try:
        logger.info("Shutting down RSS Aggregator MCP Server...")
        
        # Close HTTP session
        from .tools import _session
        if _session and not _session.closed:
            await _session.close()
            logger.info("HTTP session closed")
        
        # Clear cache
        from .tools import _cache
        _cache.clear()
        logger.info("Cache cleared")
        
        logger.info("RSS Aggregator MCP Server shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during RSS Aggregator shutdown: {e}", exc_info=True)

async def main():
    """Main function to run the RSS aggregator MCP server"""
    try:
        # Initialize server
        if not await startup():
            logger.error("Failed to start server")
            return 1
        
        # Run server
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        return 1
    finally:
        await shutdown()
    
    return 0

# ============================================================================
# HEALTH CHECK AND UTILITY FUNCTIONS
# ============================================================================

async def health_check() -> Dict[str, Any]:
    """Perform health check of RSS aggregator"""
    try:
        from .tools import _source_configs, _cache, _stats
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server_type": MCPServerType.RSS_AGGREGATOR,
            "uptime_seconds": _stats.uptime_seconds,
            "sources": {
                "total": len(_source_configs),
                "active": sum(1 for s in _source_configs.values() if s.active),
                "configured": list(_source_configs.keys())
            },
            "cache": {
                "entries": len(_cache),
                "valid_entries": sum(1 for entry in _cache.values() if not entry.is_expired)
            },
            "statistics": {
                "total_fetches": _stats.total_fetches,
                "successful_fetches": _stats.successful_fetches,
                "failed_fetches": _stats.failed_fetches,
                "success_rate": _stats.success_rate,
                "total_articles": _stats.total_articles_discovered,
                "articles_per_hour": _stats.articles_per_hour
            }
        }
        
        # Check if any sources are in error state
        error_sources = sum(1 for s in _source_configs.values() if not s.active)
        if error_sources > len(_source_configs) * 0.5:  # More than 50% in error
            health_data["status"] = "degraded"
            health_data["warning"] = f"{error_sources} sources are inactive"
        
        return health_data
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/rss_aggregator.log', mode='a')
        ]
    )
    
    # Run server
    exit_code = asyncio.run(main())
    sys.exit(exit_code)