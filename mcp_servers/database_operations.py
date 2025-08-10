#!/usr/bin/env python3
"""
Database Operations MCP Server

Provides database persistence tools for the AI News Automation System.
Handles saving RSS articles, managing sources, and database queries.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

# MCP server imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.session import ServerSession
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR
)

# Project imports
from daemon_database import DaemonDatabase
from mcp_servers.rss_aggregator.schemas import RSSArticle

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server instance
server = Server("database_operations")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available database operation tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="save_rss_articles",
                description="Save RSS articles to database with duplicate detection and source mapping",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "articles": {
                            "type": "array",
                            "description": "Array of RSS articles to save",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Article title"},
                                    "url": {"type": "string", "description": "Article URL"},
                                    "description": {"type": "string", "description": "Article description"},
                                    "content": {"type": "string", "description": "Full article content"},
                                    "source_name": {"type": "string", "description": "Source name"},
                                    "published_date": {"type": "string", "description": "Publication date ISO string"},
                                    "author": {"type": "string", "description": "Article author"},
                                    "categories": {"type": "array", "items": {"type": "string"}, "description": "Article categories"},
                                    "content_hash": {"type": "string", "description": "Content hash for deduplication"},
                                    "word_count": {"type": "integer", "description": "Word count"},
                                    "relevance_score": {"type": "number", "description": "AI relevance score"}
                                },
                                "required": ["title", "url", "source_name"]
                            }
                        }
                    },
                    "required": ["articles"]
                }
            ),
            Tool(
                name="get_database_stats",
                description="Get database statistics including article counts and source status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="get_unanalyzed_articles",
                description="Get articles that need content analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of articles to return",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200
                        }
                    }
                }
            ),
            Tool(
                name="get_recent_articles",
                description="Get recent articles from the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer", 
                            "description": "Hours back to search",
                            "default": 24,
                            "minimum": 1,
                            "maximum": 168
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of articles to return",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 500
                        }
                    }
                }
            ),
            Tool(
                name="check_database_health",
                description="Check database connectivity and health status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for database operations."""
    try:
        if name == "save_rss_articles":
            return await save_rss_articles_tool(arguments)
        elif name == "get_database_stats":
            return await get_database_stats_tool(arguments)
        elif name == "get_unanalyzed_articles":
            return await get_unanalyzed_articles_tool(arguments)
        elif name == "get_recent_articles":
            return await get_recent_articles_tool(arguments)
        elif name == "check_database_health":
            return await check_database_health_tool(arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True
            )
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Tool execution failed: {str(e)}")],
            isError=True
        )

async def save_rss_articles_tool(arguments: Dict[str, Any]) -> CallToolResult:
    """Save RSS articles to database."""
    try:
        articles_data = arguments.get("articles", [])
        if not articles_data:
            return CallToolResult(
                content=[TextContent(type="text", text="No articles provided")],
                isError=True
            )
        
        # Convert dict data to RSSArticle objects
        rss_articles = []
        for article_data in articles_data:
            try:
                # Handle published_date conversion
                published_date = None
                if "published_date" in article_data and article_data["published_date"]:
                    if isinstance(article_data["published_date"], str):
                        published_date = datetime.fromisoformat(
                            article_data["published_date"].replace("Z", "+00:00")
                        )
                    else:
                        published_date = article_data["published_date"]
                
                # Create RSSArticle object with proper field mapping
                rss_article = RSSArticle(
                    title=article_data["title"],
                    url=article_data["url"],
                    description=article_data.get("description"),
                    content=article_data.get("content"),
                    source_name=article_data["source_name"],
                    published_date=published_date,
                    author=article_data.get("author"),
                    categories=article_data.get("categories", []),
                    content_hash=article_data.get("content_hash"),
                    word_count=article_data.get("word_count"),
                    relevance_score=article_data.get("relevance_score")
                )
                rss_articles.append(rss_article)
                
            except Exception as e:
                logger.error(f"Error creating RSSArticle from data: {e}")
                continue
        
        if not rss_articles:
            return CallToolResult(
                content=[TextContent(type="text", text="No valid articles to save")],
                isError=True
            )
        
        # Save articles to database
        logger.info(f"Saving {len(rss_articles)} articles to database...")
        results = DaemonDatabase.save_rss_articles(rss_articles)
        
        success_message = f"""Database save completed:
- Articles saved: {results['saved']}
- Articles skipped (duplicates): {results['skipped']}
- Errors: {results['errors']}
- Unmapped sources: {results['unmapped']}
- Total processed: {len(rss_articles)}"""
        
        logger.info(f"Database save results: {results}")
        
        return CallToolResult(
            content=[TextContent(type="text", text=success_message)]
        )
        
    except Exception as e:
        error_msg = f"Failed to save articles to database: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def get_database_stats_tool(arguments: Dict[str, Any]) -> CallToolResult:
    """Get database statistics."""
    try:
        stats = await DaemonDatabase.get_database_stats()
        
        stats_message = f"""Database Statistics:
- Total articles: {stats.get('total_articles', 0)}
- Analyzed articles: {stats.get('analyzed_articles', 0)}
- Unanalyzed articles: {stats.get('unanalyzed_articles', 0)}
- Recent articles (24h): {stats.get('recent_articles_24h', 0)}
- Active sources: {stats.get('active_sources', 0)}
- Average relevance score: {stats.get('avg_relevance_score', 0.0):.3f}
- Analysis completion rate: {stats.get('analysis_completion_rate', 0.0):.1f}%"""
        
        return CallToolResult(
            content=[TextContent(type="text", text=stats_message)]
        )
        
    except Exception as e:
        error_msg = f"Failed to get database stats: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def get_unanalyzed_articles_tool(arguments: Dict[str, Any]) -> CallToolResult:
    """Get unanalyzed articles."""
    try:
        limit = arguments.get("limit", 50)
        articles = await DaemonDatabase.get_unanalyzed_articles(limit)
        
        if not articles:
            return CallToolResult(
                content=[TextContent(type="text", text="No unanalyzed articles found")]
            )
        
        # Format articles for response
        articles_data = []
        for article in articles:
            article_info = {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source.name if hasattr(article, 'source') else "Unknown",
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "word_count": article.word_count
            }
            articles_data.append(article_info)
        
        result_message = f"Found {len(articles)} unanalyzed articles:\n" + \
                        json.dumps(articles_data, indent=2, default=str)
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_message)]
        )
        
    except Exception as e:
        error_msg = f"Failed to get unanalyzed articles: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def get_recent_articles_tool(arguments: Dict[str, Any]) -> CallToolResult:
    """Get recent articles."""
    try:
        hours = arguments.get("hours", 24)
        limit = arguments.get("limit", 100)
        
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles = await DaemonDatabase.get_articles_since(since, limit)
        
        if not articles:
            return CallToolResult(
                content=[TextContent(type="text", text=f"No articles found in the last {hours} hours")]
            )
        
        # Format articles for response
        articles_data = []
        for article in articles:
            article_info = {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "source": article.source.name if hasattr(article, 'source') else "Unknown",
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "relevance_score": getattr(article, 'relevance_score', 0.0)
            }
            articles_data.append(article_info)
        
        result_message = f"Found {len(articles)} articles from the last {hours} hours:\n" + \
                        json.dumps(articles_data, indent=2, default=str)
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_message)]
        )
        
    except Exception as e:
        error_msg = f"Failed to get recent articles: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def check_database_health_tool(arguments: Dict[str, Any]) -> CallToolResult:
    """Check database health."""
    try:
        is_healthy = await DaemonDatabase.check_database_health()
        
        if is_healthy:
            return CallToolResult(
                content=[TextContent(type="text", text="Database is healthy and accessible")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="Database health check failed")],
                isError=True
            )
        
    except Exception as e:
        error_msg = f"Database health check failed: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def main():
    """Main function to run the database operations MCP server."""
    # Configure session options
    session_options = {
        "server_name": "Database Operations Server",
        "server_version": "1.0.0"
    }
    
    logger.info("Starting Database Operations MCP Server...")
    
    async with ServerSession(
        server,
        InitializationOptions(
            server_name=session_options["server_name"],
            server_version=session_options["server_version"],
            capabilities={}
        )
    ) as session:
        logger.info("Database Operations MCP Server started successfully")
        await session.run()

if __name__ == "__main__":
    asyncio.run(main())