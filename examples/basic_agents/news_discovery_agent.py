"""
Example Pydantic AI Agent for News Discovery
Location: examples/basic_agents/news_discovery_agent.py

This demonstrates the basic pattern for creating Pydantic AI agents with:
- Auto-discovery descriptions
- Context isolation
- Dependency injection
- Error handling
- MCP tool integration
"""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

# Models for agent communication
class NewsSource(BaseModel):
    """News source configuration"""
    name: str
    url: str
    rss_feed: Optional[str] = None
    tier: int = Field(ge=1, le=3, description="Source quality tier (1=highest)")
    active: bool = True
    last_checked: Optional[datetime] = None

class NewsArticle(BaseModel):
    """Discovered news article"""
    title: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    summary: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    processed: bool = False

class DiscoveryContext(BaseModel):
    """Context for news discovery operations"""
    sources: List[NewsSource]
    max_articles_per_source: int = 50
    relevance_threshold: float = 0.7
    keywords: List[str] = ["artificial intelligence", "AI", "machine learning", "LLM"]

# Pydantic AI Agent with auto-discovery
news_discovery_agent = Agent(
    model="openai:gpt-4o-mini",  # Cost-optimized model choice
    result_type=List[NewsArticle],
    system_prompt="""
    You are a specialized AI News Discovery Agent responsible for monitoring and discovering 
    relevant AI news articles from configured sources.
    
    Your core responsibilities:
    1. Monitor RSS feeds and web sources for new AI-related content
    2. Filter articles based on relevance keywords and quality thresholds
    3. Extract key metadata (title, URL, publication date, summary)
    4. Score articles for relevance to AI/ML topics
    5. Coordinate with Content Analysis Agent for deeper processing
    
    AGENT AUTO-DISCOVERY DESCRIPTION:
    "I am the News Discovery Agent. I monitor AI news sources, filter for relevance, 
    and discover new articles. I provide discovered articles to the Content Analysis Agent 
    and report status to the Coordinator Agent. I use MCP RSS tools for efficient monitoring."
    
    Context Isolation Rules:
    - Only access sources defined in my context
    - Never modify other agents' data directly
    - Communicate through structured message passing
    - Maintain my own state and error boundaries
    
    Cost Optimization:
    - Use efficient prompts to minimize token usage
    - Batch process multiple articles when possible
    - Cache results to avoid redundant processing
    """,
    deps_type=DiscoveryContext
)

@news_discovery_agent.tool_plain
def get_rss_feeds(ctx: RunContext[DiscoveryContext]) -> Dict[str, Any]:
    """
    Get RSS feeds from configured sources using MCP RSS server
    This would integrate with your MCP RSS aggregator server
    """
    # This is where you'd call your MCP RSS server tools
    # Example integration pattern:
    active_sources = [s for s in ctx.deps.sources if s.active]
    
    return {
        "status": "success",
        "sources_checked": len(active_sources),
        "sources": [{"name": s.name, "url": s.rss_feed} for s in active_sources if s.rss_feed]
    }

@news_discovery_agent.tool_plain
def calculate_relevance_score(article_text: str, keywords: List[str]) -> float:
    """
    Calculate relevance score for an article
    Simple keyword-based scoring (could be enhanced with embeddings)
    """
    if not article_text:
        return 0.0
    
    text_lower = article_text.lower()
    keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    
    # Simple relevance scoring
    base_score = min(keyword_matches / len(keywords), 1.0)
    
    # Boost for AI-specific terms
    ai_terms = ["artificial intelligence", "machine learning", "neural network", "llm", "gpt", "claude"]
    ai_matches = sum(1 for term in ai_terms if term.lower() in text_lower)
    ai_boost = min(ai_matches * 0.1, 0.3)
    
    return min(base_score + ai_boost, 1.0)

# Main agent function
async def discover_news(context: DiscoveryContext) -> List[NewsArticle]:
    """
    Main function to discover news using the agent
    """
    try:
        # Run the agent with context
        result = await news_discovery_agent.run(
            "Discover and filter relevant AI news articles from configured sources",
            deps=context
        )
        
        # Log discovery results
        logging.info(f"Discovered {len(result.data)} relevant articles")
        
        return result.data
        
    except Exception as e:
        logging.error(f"News discovery failed: {e}")
        raise

# Example usage and testing
async def main():
    """Example usage of the news discovery agent"""
    
    # Configure sources (Tier 1 and 2 from your project)
    sources = [
        NewsSource(name="OpenAI Blog", url="https://openai.com/blog", rss_feed="https://openai.com/blog/rss.xml", tier=1),
        NewsSource(name="Google AI Blog", url="https://ai.googleblog.com", rss_feed="https://ai.googleblog.com/feeds/posts/default", tier=1),
        NewsSource(name="MIT AI News", url="https://news.mit.edu/topic/artificial-intelligence2", tier=1),
        NewsSource(name="TechCrunch AI", url="https://techcrunch.com/category/artificial-intelligence/", tier=2),
    ]
    
    # Create context
    context = DiscoveryContext(
        sources=sources,
        max_articles_per_source=25,
        relevance_threshold=0.6,
        keywords=["AI", "artificial intelligence", "machine learning", "LLM", "GPT", "neural networks"]
    )
    
    # Discover news
    articles = await discover_news(context)
    
    # Display results
    print(f"Discovered {len(articles)} relevant articles:")
    for article in articles:
        print(f"- {article.title} (Score: {article.relevance_score:.2f})")

if __name__ == "__main__":
    asyncio.run(main())