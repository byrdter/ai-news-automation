"""
News Discovery Agent using Pydantic AI.

Orchestrates RSS feed aggregation, article discovery, deduplication,
and initial relevance scoring for AI news content.
"""

import asyncio
import json
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
import logging

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model
from pydantic import BaseModel, Field

from config.settings import get_settings
from .models import (
    NewsDiscoveryRequest, NewsDiscoveryResponse, DiscoverySession,
    RSSFeedSource, ProcessedArticle, RawArticle, FeedProcessingResult,
    FeedStatus, ArticleStatus
)
from mcp_servers.rss_aggregator import RSSAggregator, FeedFetchRequest
from database.models import NewsSource, NewsArticle
from utils.cost_tracking import CostTracker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscoveryDeps(BaseModel):
    """Dependencies for the News Discovery Agent."""
    rss_aggregator: RSSAggregator
    cost_tracker: CostTracker
    settings: Any  # Settings object
    session_id: str = Field(default_factory=lambda: str(uuid4()))


class RelevanceAssessment(BaseModel):
    """AI assessment of article relevance."""
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Content quality score (0-1)")
    reasoning: str = Field(..., description="Explanation for the scores")
    key_topics: List[str] = Field(..., description="Main topics identified")
    entities: List[str] = Field(..., description="Key entities mentioned")
    is_breaking_news: bool = Field(..., description="Whether this appears to be breaking news")
    urgency_level: int = Field(..., ge=1, le=5, description="Urgency level (1-5)")


# Create News Discovery Agent
news_discovery_agent = Agent(
    'openai:gpt-5-mini',
    deps_type=DiscoveryDeps,
    result_type=NewsDiscoveryResponse,
    system_prompt="""You are an AI News Discovery Agent specialized in finding, filtering, and evaluating AI-related news content.

Your primary role is to:
1. Coordinate RSS feed aggregation from multiple sources
2. Perform content deduplication and quality filtering
3. Assess article relevance and importance for AI industry professionals
4. Optimize discovery process for cost-effectiveness (target <$3/day)

Key responsibilities:
- Process 50-150 articles daily from 12+ RSS sources
- Maintain >90% relevance accuracy for filtered content
- Identify breaking news and high-impact stories
- Eliminate duplicates and low-quality content
- Track processing costs and optimize for budget

Focus areas for relevance assessment:
- AI research breakthroughs and papers
- New AI model releases and capabilities
- AI company funding, acquisitions, partnerships
- AI regulation and policy developments  
- AI product launches and features
- AI industry analysis and market trends
- Notable AI research from academia and industry

Quality indicators:
- Content depth and technical accuracy
- Source credibility and authority
- Timeliness and newsworthiness
- Relevance to AI professionals
- Uniqueness (not duplicate content)

Always provide clear reasoning for relevance scores and identify key topics/entities for downstream processing."""
)


@news_discovery_agent.system_prompt
async def get_dynamic_prompt(ctx: RunContext[DiscoveryDeps]) -> str:
    """Generate dynamic system prompt based on current context."""
    settings = ctx.deps.settings
    current_hour = datetime.now().hour
    
    # Adjust behavior based on time of day
    if 5 <= current_hour <= 9:
        time_context = "Morning discovery session - prioritize overnight developments and breaking news."
    elif 12 <= current_hour <= 14:
        time_context = "Midday discovery - focus on regular content updates and analysis pieces."
    elif 18 <= current_hour <= 20:
        time_context = "Evening discovery - capture end-of-day announcements and market close analysis."
    else:
        time_context = "Off-hours discovery - maintain standard processing with quality focus."
    
    cost_context = f"Daily budget remaining: ${settings.daily_cost_limit:.2f}. Optimize for cost-effectiveness."
    
    return f"""
Current context: {time_context}
{cost_context}

Adjust your assessment strategy accordingly while maintaining quality standards.
"""


async def discover_news(request: NewsDiscoveryRequest, deps: DiscoveryDeps) -> NewsDiscoveryResponse:
    """
    Main news discovery function.
    
    Orchestrates the complete news discovery pipeline from RSS feeds to processed articles.
    """
    session = DiscoverySession(
        config=request.session_config,
        session_id=uuid4(),
        status=FeedStatus.PENDING
    )
    
    start_time = time.time()
    total_cost = 0.0
    
    try:
        logger.info(f"Starting news discovery session {session.session_id}")
        session.status = FeedStatus.FETCHING
        
        # Process feeds concurrently
        feed_tasks = []
        semaphore = asyncio.Semaphore(request.session_config.max_sources_concurrent)
        
        for feed_source in request.session_config.feed_sources:
            if not feed_source.enabled:
                continue
                
            task = asyncio.create_task(
                _process_single_feed(feed_source, request.session_config, deps, semaphore)
            )
            feed_tasks.append(task)
        
        # Wait for all feeds to complete
        feed_results = await asyncio.gather(*feed_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        successful_results = []
        for i, result in enumerate(feed_results):
            if isinstance(result, Exception):
                logger.error(f"Feed processing failed: {result}")
                session.errors.append(f"Feed {request.session_config.feed_sources[i].name}: {str(result)}")
            else:
                successful_results.append(result)
                session.feed_results.append(result)
        
        session.status = FeedStatus.PROCESSING
        
        # Aggregate metrics
        session.total_articles_discovered = sum(r.articles_found for r in successful_results)
        session.total_articles_processed = sum(r.articles_processed for r in successful_results)
        session.total_articles_relevant = sum(
            len([a for a in r.processed_articles if a.relevance_score >= request.session_config.min_relevance_score])
            for r in successful_results
        )
        session.total_duplicates_filtered = sum(r.articles_duplicates for r in successful_results)
        
        # Calculate performance metrics
        session.total_processing_time = time.time() - start_time
        session.total_cost_usd = total_cost
        
        if session.total_processing_time > 0:
            session.avg_articles_per_second = session.total_articles_processed / session.total_processing_time
        
        session.status = FeedStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        
        # Generate recommendations
        recommendations = _generate_recommendations(session, successful_results)
        
        # Calculate next run time
        next_run = _calculate_next_run_time(session, request.session_config)
        
        logger.info(f"Discovery session completed: {session.total_articles_relevant} relevant articles found")
        
        return NewsDiscoveryResponse(
            success=True,
            session=session,
            message=f"Successfully discovered {session.total_articles_relevant} relevant articles from {len(successful_results)} sources",
            articles_found=session.total_articles_discovered,
            articles_relevant=session.total_articles_relevant,
            processing_time=session.total_processing_time,
            cost_usd=session.total_cost_usd,
            recommendations=recommendations,
            next_run_recommended=next_run
        )
        
    except Exception as e:
        logger.error(f"News discovery session failed: {e}")
        session.status = FeedStatus.FAILED
        session.errors.append(str(e))
        
        return NewsDiscoveryResponse(
            success=False,
            session=session,
            message=f"News discovery failed: {str(e)}",
            articles_found=0,
            articles_relevant=0,
            processing_time=time.time() - start_time,
            cost_usd=total_cost,
            recommendations=["Check system logs", "Verify feed URLs", "Check API key limits"]
        )


async def _process_single_feed(
    feed_source: RSSFeedSource, 
    config: Any, 
    deps: DiscoveryDeps,
    semaphore: asyncio.Semaphore
) -> FeedProcessingResult:
    """Process a single RSS feed."""
    async with semaphore:
        start_time = time.time()
        result = FeedProcessingResult(
            feed_source=feed_source,
            status=FeedStatus.FETCHING,
            started_at=datetime.utcnow()
        )
        
        try:
            # Fetch RSS feed
            fetch_request = FeedFetchRequest(
                feed_url=feed_source.url,
                max_articles=config.max_articles_per_source,
                timeout=config.request_timeout
            )
            
            # Import and use the MCP tool directly
            from mcp_servers.rss_aggregator import fetch_rss_feed
            rss_result = await fetch_rss_feed(fetch_request)
            
            if rss_result.error:
                result.status = FeedStatus.FAILED
                result.errors.append(rss_result.error)
                return result
            
            result.articles_found = len(rss_result.articles)
            result.fetch_time = rss_result.fetch_time
            result.status = FeedStatus.PROCESSING
            
            # Process each article
            processed_articles = []
            for article_data in rss_result.articles:
                try:
                    raw_article = RawArticle(
                        title=article_data['title'],
                        url=article_data['url'],
                        description=article_data.get('summary', ''),
                        content=article_data.get('content', ''),
                        author=article_data.get('author', ''),
                        published_date=datetime.fromisoformat(article_data['published_date']) if article_data.get('published_date') else datetime.now(timezone.utc),
                        feed_source=feed_source.name,
                        feed_category=feed_source.category,
                        tags=article_data.get('tags', [])
                    )
                    
                    # Check for duplicates (simplified - would use database in production)
                    is_duplicate = await _check_duplicate(raw_article, deps)
                    
                    if is_duplicate:
                        result.articles_duplicates += 1
                        continue
                    
                    # Assess relevance using AI
                    assessment = await _assess_article_relevance(raw_article, deps)
                    
                    processed_article = ProcessedArticle(
                        raw_article=raw_article,
                        status=ArticleStatus.PROCESSED,
                        relevance_score=assessment.relevance_score,
                        quality_score=assessment.quality_score,
                        extracted_entities={
                            'topics': assessment.key_topics,
                            'entities': assessment.entities
                        },
                        processing_time=time.time() - start_time,
                        processing_cost=0.01  # Estimated cost per analysis
                    )
                    
                    processed_articles.append(processed_article)
                    result.articles_processed += 1
                    
                    # Rate limiting
                    await asyncio.sleep(config.delay_between_requests)
                    
                except Exception as e:
                    logger.warning(f"Error processing article {article_data.get('title', 'Unknown')}: {e}")
                    result.articles_errors += 1
                    continue
            
            result.processed_articles = processed_articles
            result.status = FeedStatus.COMPLETED
            result.completed_at = datetime.utcnow()
            result.processing_time = time.time() - start_time
            
            logger.info(f"Processed feed {feed_source.name}: {result.articles_processed}/{result.articles_found} articles")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process feed {feed_source.name}: {e}")
            result.status = FeedStatus.FAILED
            result.errors.append(str(e))
            result.processing_time = time.time() - start_time
            return result


async def _check_duplicate(article: RawArticle, deps: DiscoveryDeps) -> bool:
    """Check if article is a duplicate."""
    # Simplified duplicate check - would use database and content similarity in production
    return False


async def _assess_article_relevance(article: RawArticle, deps: DiscoveryDeps) -> RelevanceAssessment:
    """Use AI to assess article relevance and quality."""
    
    # Create assessment agent
    assessment_agent = Agent(
        'openai:gpt-5-mini',
        result_type=RelevanceAssessment,
        system_prompt="""You are an AI content evaluator specialized in assessing news articles for relevance to AI industry professionals.

Evaluate articles based on:

RELEVANCE (0.0-1.0):
- 0.9-1.0: Major AI breakthroughs, company news, policy changes
- 0.7-0.8: Important research, product launches, industry analysis  
- 0.5-0.6: General AI news, educational content, minor updates
- 0.3-0.4: Tangentially related, broad tech news mentioning AI
- 0.0-0.2: Not AI-related or very low relevance

QUALITY (0.0-1.0):
- Technical accuracy and depth
- Source credibility
- Timeliness and newsworthiness
- Writing quality and clarity
- Uniqueness of information

URGENCY (1-5):
- 5: Breaking news requiring immediate attention
- 4: Important developments within 24 hours
- 3: Significant news within a few days
- 2: Regular updates and analysis
- 1: General educational or background content

Always provide clear reasoning for your assessment."""
    )
    
    # Prepare article content for evaluation
    content_summary = f"""
Title: {article.title}
Description: {article.description or 'N/A'}
Source: {article.feed_source} ({article.feed_category})
Author: {article.author or 'N/A'}
Published: {article.published_date}
Content Preview: {(article.content or article.description or '')[:500]}...
Tags: {', '.join(article.tags) if article.tags else 'None'}
"""
    
    try:
        # Get AI assessment
        assessment = await assessment_agent.run(
            f"Assess this AI news article for relevance and quality:\n\n{content_summary}"
        )
        
        # Track cost
        deps.cost_tracker.track_operation(
            operation_type="relevance_assessment",
            model="gpt-5-mini",
            input_tokens=len(content_summary.split()) * 1.3,  # Rough estimate
            output_tokens=50,  # Approximate
            cost_usd=0.01
        )
        
        return assessment.data
        
    except Exception as e:
        logger.warning(f"AI assessment failed for article {article.title}: {e}")
        
        # Fallback assessment based on keywords
        return _fallback_relevance_assessment(article)


def _fallback_relevance_assessment(article: RawArticle) -> RelevanceAssessment:
    """Fallback relevance assessment using keyword matching."""
    content = f"{article.title} {article.description or ''} {article.content or ''}".lower()
    
    # AI-related keywords with weights
    ai_keywords = {
        'artificial intelligence': 0.9, 'ai': 0.8, 'machine learning': 0.85, 'deep learning': 0.85,
        'neural network': 0.8, 'transformer': 0.8, 'gpt': 0.9, 'llm': 0.9, 'large language model': 0.9,
        'openai': 0.85, 'google ai': 0.8, 'deepmind': 0.85, 'anthropic': 0.85,
        'computer vision': 0.75, 'natural language': 0.75, 'nlp': 0.75,
        'generative ai': 0.9, 'chatgpt': 0.85, 'claude': 0.8, 'gemini': 0.8
    }
    
    relevance_score = 0.0
    quality_score = 0.5  # Default
    key_topics = []
    entities = []
    
    # Calculate relevance based on keyword presence
    for keyword, weight in ai_keywords.items():
        if keyword in content:
            relevance_score = max(relevance_score, weight)
            key_topics.append(keyword)
    
    # Adjust quality based on source and content length
    if article.feed_category in ['AI Research', 'Academic Research']:
        quality_score += 0.2
    if len(content) > 1000:
        quality_score += 0.1
    if article.author:
        quality_score += 0.1
    
    quality_score = min(1.0, quality_score)
    
    # Determine urgency (simplified)
    is_breaking = any(word in content for word in ['breaking', 'announces', 'launches', 'releases'])
    urgency = 3 if is_breaking else 2
    
    return RelevanceAssessment(
        relevance_score=relevance_score,
        quality_score=quality_score,
        reasoning=f"Keyword-based assessment: found {len(key_topics)} AI-related terms",
        key_topics=key_topics,
        entities=entities,
        is_breaking_news=is_breaking,
        urgency_level=urgency
    )


def _generate_recommendations(session: DiscoverySession, results: List[FeedProcessingResult]) -> List[str]:
    """Generate recommendations based on session results."""
    recommendations = []
    
    # Success rate recommendations
    if session.success_rate < 80:
        recommendations.append("Success rate below 80% - check feed URLs and network connectivity")
    
    # Cost optimization
    if session.cost_per_article > 0.02:
        recommendations.append("Cost per article above target - consider using smaller models or batch processing")
    
    # Relevance rate
    if session.relevance_rate < 60:
        recommendations.append("Low relevance rate - review and tune relevance assessment criteria")
    
    # Processing time
    if session.total_processing_time > 300:  # 5 minutes
        recommendations.append("Processing time high - consider increasing concurrency or optimizing feed selection")
    
    # Feed-specific recommendations
    failed_feeds = [r for r in results if r.status == FeedStatus.FAILED]
    if failed_feeds:
        recommendations.append(f"{len(failed_feeds)} feeds failed - review feed URLs and error logs")
    
    return recommendations or ["All systems operating optimally"]


def _calculate_next_run_time(session: DiscoverySession, config: Any) -> datetime:
    """Calculate recommended next run time."""
    # Base interval (1 hour default)
    base_interval = 3600
    
    # Adjust based on success rate
    if session.success_rate > 90:
        base_interval = int(base_interval * 0.9)  # Run more frequently if successful
    elif session.success_rate < 70:
        base_interval = int(base_interval * 1.2)  # Run less frequently if having issues
    
    # Adjust based on article discovery rate
    if session.total_articles_relevant < 10:
        base_interval = int(base_interval * 1.1)  # Run less frequently if not finding much
    elif session.total_articles_relevant > 50:
        base_interval = int(base_interval * 0.95)  # Run more frequently if finding lots
    
    return datetime.utcnow() + timedelta(seconds=base_interval)


# Agent wrapper function for external use
async def run_news_discovery(request: NewsDiscoveryRequest) -> NewsDiscoveryResponse:
    """
    Main entry point for news discovery operations.
    """
    settings = get_settings()
    
    # Initialize dependencies
    deps = DiscoveryDeps(
        rss_aggregator=RSSAggregator(),
        cost_tracker=CostTracker(),
        settings=settings
    )
    
    try:
        # Run the discovery session
        response = await discover_news(request, deps)
        return response
        
    except Exception as e:
        logger.error(f"News discovery failed: {e}")
        raise
    
    finally:
        # Cleanup
        await deps.rss_aggregator.cleanup()


# Export main components
__all__ = [
    'news_discovery_agent',
    'run_news_discovery',
    'DiscoveryDeps',
    'RelevanceAssessment'
]