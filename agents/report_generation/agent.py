"""
Report Generation Agent using Pydantic AI.

Generates comprehensive AI news reports with intelligent content organization,
trend analysis, and multi-format output (HTML, email, text).
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
import logging
from collections import defaultdict, Counter
import statistics

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader, Template

from config.settings import get_settings
from .models import (
    ReportGenerationRequest, ReportGenerationResponse, Report, ReportMetadata,
    ReportSectionData, ReportSection, ArticleSummary, TrendData, ReportType,
    ReportStatus, ReportFormat
)
from agents.content_analysis.models import ContentAnalysis
from database.models import NewsArticle, NewsSource
from mcp_servers.email_notifications import TemplateEmailRequest, send_templated_email
from utils.cost_tracking import CostTracker, ServiceType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerationDeps(BaseModel):
    """Dependencies for Report Generation Agent."""
    cost_tracker: CostTracker
    settings: Any
    template_env: Environment


class ReportSummaryData(BaseModel):
    """AI-generated summary data for report sections."""
    executive_summary: str = Field(..., max_length=1000)
    key_insights: List[str] = Field(..., max_items=10)
    trend_analysis: str = Field(..., max_length=800)
    recommendations: List[str] = Field(..., max_items=5)
    market_implications: str = Field(..., max_length=600)
    section_summaries: Dict[str, str] = Field(default_factory=dict)


# Create Report Generation Agent
report_generation_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=ReportGenerationDeps,
    result_type=ReportSummaryData,
    system_prompt="""You are an AI Report Generation Agent specialized in creating comprehensive, professional AI news reports.

Your role is to:
1. Synthesize complex AI news into clear, actionable insights
2. Identify patterns and trends across multiple articles
3. Create executive summaries that capture key developments
4. Provide strategic recommendations for business professionals
5. Ensure reports are well-structured and professionally written

REPORT STRUCTURE GUIDELINES:

Executive Summary (100-150 words):
- Lead with the most significant development
- Highlight 2-3 key themes from the reporting period
- Include quantitative context where available
- End with forward-looking statement

Key Insights (5-10 bullet points):
- Actionable takeaways for business professionals
- Connect developments to broader industry trends
- Include implications for different stakeholders
- Prioritize by impact and relevance

Trend Analysis (100-120 words):
- Identify emerging patterns in the data
- Compare to previous periods where relevant
- Note acceleration or deceleration of trends
- Provide context for trend significance

Recommendations (3-5 strategic points):
- Specific actions for AI professionals
- Investment or research focus areas
- Risk mitigation strategies
- Opportunities to monitor

Market Implications (80-100 words):
- Impact on AI industry dynamics
- Effects on adjacent sectors
- Competitive landscape changes
- Regulatory or policy implications

WRITING STYLE:
- Professional but accessible tone
- Use active voice and clear language
- Include specific examples and data points
- Avoid jargon unless defined
- Maintain objectivity while providing insight
- Use present tense for current developments

Focus on creating reports that busy professionals can quickly scan for key information while providing enough depth for strategic decision-making."""
)


class ReportGenerationService:
    """Service for generating comprehensive news reports."""
    
    def __init__(self):
        """Initialize report generation service."""
        self.settings = get_settings()
        self.cost_tracker = CostTracker()
        
        # Setup template environment
        self.template_env = self._setup_templates()
        
        # Report cache
        self.report_cache = {}
        
        # Standard sections for different report types
        self.standard_sections = {
            ReportType.DAILY: [
                ReportSection.EXECUTIVE_SUMMARY,
                ReportSection.BREAKING_NEWS,
                ReportSection.KEY_DEVELOPMENTS,
                ReportSection.RESEARCH_HIGHLIGHTS,
                ReportSection.INDUSTRY_ANALYSIS
            ],
            ReportType.WEEKLY: [
                ReportSection.EXECUTIVE_SUMMARY,
                ReportSection.KEY_DEVELOPMENTS,
                ReportSection.RESEARCH_HIGHLIGHTS,
                ReportSection.INDUSTRY_ANALYSIS,
                ReportSection.FUNDING_NEWS,
                ReportSection.TREND_ANALYSIS,
                ReportSection.MARKET_IMPACT
            ],
            ReportType.MONTHLY: [
                ReportSection.EXECUTIVE_SUMMARY,
                ReportSection.KEY_DEVELOPMENTS,
                ReportSection.RESEARCH_HIGHLIGHTS,
                ReportSection.INDUSTRY_ANALYSIS,
                ReportSection.FUNDING_NEWS,
                ReportSection.PRODUCT_LAUNCHES,
                ReportSection.REGULATORY_UPDATES,
                ReportSection.TREND_ANALYSIS,
                ReportSection.MARKET_IMPACT,
                ReportSection.UPCOMING_EVENTS
            ]
        }
    
    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment."""
        from pathlib import Path
        template_dir = Path(__file__).parent.parent.parent / "templates" / "reports"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def generate_report(self, request: ReportGenerationRequest) -> ReportGenerationResponse:
        """Generate comprehensive news report."""
        start_time = time.time()
        generation_cost = 0.0
        
        try:
            logger.info(f"Generating {request.report_type.value} report for {request.period_start} to {request.period_end}")
            
            # Initialize report metadata
            metadata = ReportMetadata(
                report_type=request.report_type,
                title=request.title or self._generate_title(request),
                subtitle=request.subtitle,
                period_start=request.period_start,
                period_end=request.period_end,
                generation_model=request.generation_model,
                recipients=request.recipients,
                status=ReportStatus.GENERATING
            )
            
            # Fetch articles for the time period
            articles = await self._fetch_articles(request)
            logger.info(f"Fetched {len(articles)} articles for analysis")
            
            if not articles:
                return ReportGenerationResponse(
                    success=False,
                    report=None,
                    error_message="No articles found for the specified time period",
                    processing_time=time.time() - start_time,
                    generation_cost=0.0,
                    articles_processed=0,
                    sections_generated=0
                )
            
            # Update metadata with article stats
            metadata.total_articles = len(articles)
            metadata.sources_covered = len(set(article.source for article in articles))
            metadata.avg_relevance_score = statistics.mean(article.relevance_score for article in articles)
            metadata.avg_quality_score = statistics.mean(article.quality_score for article in articles)
            
            # Create article summaries
            article_summaries = [self._create_article_summary(article) for article in articles]
            
            # Organize articles into sections
            sections = await self._organize_into_sections(
                article_summaries, 
                request.included_sections,
                request.max_articles_per_section
            )
            
            # Generate trends if requested
            trends = []
            if request.include_trends:
                trends = await self._analyze_trends(article_summaries, request)
            
            # Generate AI summaries and insights
            summary_data = await self._generate_ai_summaries(
                article_summaries, 
                sections, 
                trends, 
                request
            )
            generation_cost += 0.15  # Estimated cost for AI generation
            
            # Create complete report
            report = Report(
                metadata=metadata,
                sections=sections,
                trends=trends,
                executive_summary=summary_data.executive_summary,
                key_insights=summary_data.key_insights,
                recommendations=summary_data.recommendations
            )
            
            # Generate formatted content
            if ReportFormat.HTML in request.output_formats:
                report.html_content = await self._generate_html_content(report, request)
            
            if ReportFormat.MARKDOWN in request.output_formats:
                report.markdown_content = self._generate_markdown_content(report)
            
            if ReportFormat.TEXT in request.output_formats:
                report.text_content = self._generate_text_content(report)
            
            # Update metadata
            report.metadata.status = ReportStatus.READY
            report.metadata.generation_time = time.time() - start_time
            report.metadata.generation_cost = generation_cost
            report.metadata.completeness_score = self._calculate_completeness(report)
            report.metadata.readability_score = self._calculate_readability(report)
            
            # Schedule delivery if requested
            if request.send_immediately and request.recipients:
                delivery_response = await self._deliver_report(report, request)
                if delivery_response.success:
                    report.metadata.status = ReportStatus.DELIVERED
                    report.metadata.delivered_at = datetime.utcnow()
                else:
                    report.metadata.delivery_errors.extend(delivery_response.delivery_errors)
            
            # Cache successful report
            self.report_cache[str(report.metadata.report_id)] = report
            
            # Track costs
            self.cost_tracker.track_operation(
                operation="report_generation",
                service=ServiceType.OPENAI,
                model=request.generation_model,
                input_tokens=sum(len(a.summary.split()) for a in article_summaries) * 1.3,
                output_tokens=len(summary_data.executive_summary.split()) * 10,
                cost_usd=generation_cost
            )
            
            logger.info(f"Report generation completed: {len(sections)} sections, {len(trends)} trends")
            
            return ReportGenerationResponse(
                success=True,
                report=report,
                processing_time=report.metadata.generation_time,
                generation_cost=generation_cost,
                articles_processed=len(article_summaries),
                sections_generated=len(sections),
                completeness_score=report.metadata.completeness_score,
                content_quality_score=report.metadata.readability_score,
                delivery_scheduled=request.schedule_delivery is not None,
                delivery_time=request.schedule_delivery
            )
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            
            return ReportGenerationResponse(
                success=False,
                report=None,
                error_message=str(e),
                processing_time=time.time() - start_time,
                generation_cost=generation_cost,
                articles_processed=0,
                sections_generated=0
            )
    
    def _generate_title(self, request: ReportGenerationRequest) -> str:
        """Generate report title based on type and period."""
        type_titles = {
            ReportType.DAILY: "Daily AI News Digest",
            ReportType.WEEKLY: "Weekly AI Industry Report", 
            ReportType.MONTHLY: "Monthly AI Market Analysis",
            ReportType.BREAKING: "Breaking AI News Alert",
            ReportType.CUSTOM: "AI News Report"
        }
        
        base_title = type_titles.get(request.report_type, "AI News Report")
        
        # Add date context
        if request.report_type == ReportType.DAILY:
            date_str = request.period_end.strftime("%B %d, %Y")
            return f"{base_title} - {date_str}"
        elif request.report_type == ReportType.WEEKLY:
            week_start = request.period_start.strftime("%B %d")
            week_end = request.period_end.strftime("%B %d, %Y")
            return f"{base_title} - {week_start} to {week_end}"
        elif request.report_type == ReportType.MONTHLY:
            month_year = request.period_end.strftime("%B %Y")
            return f"{base_title} - {month_year}"
        
        return base_title
    
    async def _fetch_articles(self, request: ReportGenerationRequest) -> List[Any]:
        """Fetch articles for the report time period."""
        # In a real implementation, this would query the database
        # For now, return mock data structure
        mock_articles = []
        
        # This would be replaced with actual database query:
        # from sqlalchemy.orm import sessionmaker
        # session = sessionmaker()
        # articles = session.query(NewsArticle).filter(
        #     NewsArticle.published_date.between(request.period_start, request.period_end),
        #     NewsArticle.relevance_score >= request.min_relevance_score,
        #     NewsArticle.quality_score >= request.min_quality_score
        # ).order_by(NewsArticle.relevance_score.desc()).all()
        
        return mock_articles
    
    def _create_article_summary(self, article) -> ArticleSummary:
        """Create article summary from database article."""
        # Mock implementation - would use real article data
        return ArticleSummary(
            article_id=article.id if hasattr(article, 'id') else "mock-id",
            title="Sample AI Article",
            url="https://example.com/article",
            source="TechCrunch",
            published_date=datetime.now(timezone.utc),
            summary="This is a sample article summary for testing purposes.",
            relevance_score=0.85,
            quality_score=0.75,
            impact_score=0.60,
            sentiment_score=0.3,
            key_points=["AI advancement", "Industry impact", "Future implications"],
            entities=["OpenAI", "GPT-4", "Machine Learning"],
            topics=["Natural Language Processing", "AI Research"],
            word_count=1200
        )
    
    async def _organize_into_sections(self, 
                                    articles: List[ArticleSummary], 
                                    included_sections: List[ReportSection],
                                    max_per_section: int) -> List[ReportSectionData]:
        """Organize articles into report sections."""
        sections = []
        
        # Section categorization logic
        section_keywords = {
            ReportSection.BREAKING_NEWS: ["breaking", "urgent", "alert", "just in"],
            ReportSection.KEY_DEVELOPMENTS: ["announces", "launches", "releases", "introduces"],
            ReportSection.RESEARCH_HIGHLIGHTS: ["research", "study", "paper", "findings", "arxiv"],
            ReportSection.INDUSTRY_ANALYSIS: ["market", "industry", "analysis", "trends", "outlook"],
            ReportSection.FUNDING_NEWS: ["funding", "investment", "raises", "series", "valuation"],
            ReportSection.PRODUCT_LAUNCHES: ["product", "launch", "feature", "release", "beta"],
            ReportSection.REGULATORY_UPDATES: ["regulation", "policy", "law", "compliance", "government"]
        }
        
        for section_type in included_sections:
            if section_type == ReportSection.EXECUTIVE_SUMMARY:
                continue  # Handled separately
            
            # Filter articles for this section
            section_articles = []
            keywords = section_keywords.get(section_type, [])
            
            for article in articles:
                # Check if article matches section criteria
                content_text = f"{article.title} {article.summary}".lower()
                if any(keyword in content_text for keyword in keywords):
                    section_articles.append(article)
                elif section_type == ReportSection.KEY_DEVELOPMENTS and article.impact_score > 0.7:
                    section_articles.append(article)
                elif section_type == ReportSection.RESEARCH_HIGHLIGHTS and "research" in article.topics:
                    section_articles.append(article)
            
            # Sort by relevance and limit
            section_articles.sort(key=lambda a: a.relevance_score, reverse=True)
            section_articles = section_articles[:max_per_section]
            
            if section_articles:  # Only include sections with articles
                section_data = ReportSectionData(
                    section_type=section_type,
                    title=self._get_section_title(section_type),
                    articles=section_articles,
                    priority=self._get_section_priority(section_type)
                )
                sections.append(section_data)
        
        # Sort sections by priority
        sections.sort(key=lambda s: s.priority)
        
        return sections
    
    def _get_section_title(self, section_type: ReportSection) -> str:
        """Get display title for section type."""
        titles = {
            ReportSection.BREAKING_NEWS: "🚨 Breaking News",
            ReportSection.KEY_DEVELOPMENTS: "🔑 Key Developments",
            ReportSection.RESEARCH_HIGHLIGHTS: "🔬 Research Highlights",
            ReportSection.INDUSTRY_ANALYSIS: "📊 Industry Analysis",
            ReportSection.FUNDING_NEWS: "💰 Funding & Investments",
            ReportSection.PRODUCT_LAUNCHES: "🚀 Product Launches",
            ReportSection.REGULATORY_UPDATES: "⚖️ Regulatory Updates",
            ReportSection.TREND_ANALYSIS: "📈 Trend Analysis",
            ReportSection.MARKET_IMPACT: "🎯 Market Impact"
        }
        return titles.get(section_type, section_type.value.replace("_", " ").title())
    
    def _get_section_priority(self, section_type: ReportSection) -> int:
        """Get display priority for section (lower = higher priority)."""
        priorities = {
            ReportSection.EXECUTIVE_SUMMARY: 1,
            ReportSection.BREAKING_NEWS: 2,
            ReportSection.KEY_DEVELOPMENTS: 3,
            ReportSection.RESEARCH_HIGHLIGHTS: 4,
            ReportSection.INDUSTRY_ANALYSIS: 5,
            ReportSection.FUNDING_NEWS: 6,
            ReportSection.PRODUCT_LAUNCHES: 7,
            ReportSection.REGULATORY_UPDATES: 8,
            ReportSection.TREND_ANALYSIS: 9,
            ReportSection.MARKET_IMPACT: 10
        }
        return priorities.get(section_type, 5)
    
    async def _analyze_trends(self, 
                            articles: List[ArticleSummary], 
                            request: ReportGenerationRequest) -> List[TrendData]:
        """Analyze trends in the articles."""
        trends = []
        
        # Topic frequency analysis
        topic_counts = Counter()
        for article in articles:
            for topic in article.topics:
                topic_counts[topic] += 1
        
        # Entity frequency analysis
        entity_counts = Counter()
        for article in articles:
            for entity in article.entities:
                entity_counts[entity] += 1
        
        # Sentiment trend analysis
        daily_sentiment = defaultdict(list)
        for article in articles:
            day = article.published_date.date()
            daily_sentiment[day].append(article.sentiment_score)
        
        # Create trend data (simplified)
        for topic, count in topic_counts.most_common(5):
            if count >= 3:  # Minimum threshold
                trend = TrendData(
                    trend_name=f"{topic} Coverage",
                    trend_type="topic_frequency",
                    current_value=float(count),
                    previous_value=float(count * 0.8),  # Mock previous value
                    time_period=f"{request.period_start.date()} to {request.period_end.date()}",
                    confidence_score=0.8,
                    description=f"Increased coverage of {topic} with {count} articles",
                    implications=[f"Growing interest in {topic}"]
                )
                trends.append(trend)
        
        return trends[:5]  # Limit to top 5 trends
    
    async def _generate_ai_summaries(self, 
                                   articles: List[ArticleSummary],
                                   sections: List[ReportSectionData],
                                   trends: List[TrendData],
                                   request: ReportGenerationRequest) -> ReportSummaryData:
        """Generate AI-powered summaries and insights."""
        
        # Prepare context for AI agent
        article_context = "\n".join([
            f"- {article.title} ({article.source}): {article.summary}"
            for article in articles[:20]  # Limit context size
        ])
        
        trend_context = "\n".join([
            f"- {trend.trend_name}: {trend.description}"
            for trend in trends
        ])
        
        section_context = "\n".join([
            f"- {section.title}: {len(section.articles)} articles"
            for section in sections
        ])
        
        analysis_prompt = f"""
Generate comprehensive summaries and insights for this {request.report_type.value} AI news report:

REPORTING PERIOD: {request.period_start.strftime('%B %d, %Y')} to {request.period_end.strftime('%B %d, %Y')}

ARTICLES ANALYZED ({len(articles)} total):
{article_context}

SECTIONS GENERATED:
{section_context}

TRENDS IDENTIFIED:
{trend_context}

Generate professional report content including executive summary, key insights, trend analysis, recommendations, and market implications.
"""
        
        try:
            # Create dependencies
            deps = ReportGenerationDeps(
                cost_tracker=self.cost_tracker,
                settings=self.settings,
                template_env=self.template_env
            )
            
            # Run AI analysis
            result = await report_generation_agent.run(analysis_prompt, deps=deps)
            return result.data
            
        except Exception as e:
            logger.warning(f"AI summary generation failed, using fallback: {e}")
            return self._generate_fallback_summaries(articles, sections, trends)
    
    def _generate_fallback_summaries(self, 
                                   articles: List[ArticleSummary],
                                   sections: List[ReportSectionData],
                                   trends: List[TrendData]) -> ReportSummaryData:
        """Generate fallback summaries without AI."""
        
        # Simple extractive summary
        top_articles = sorted(articles, key=lambda a: a.relevance_score, reverse=True)[:3]
        
        executive_summary = f"""
This report covers {len(articles)} AI-related articles from {len(set(a.source for a in articles))} sources. 
Key developments include {', '.join(article.title[:50] + '...' for article in top_articles[:2])}.
The analysis shows continued growth in AI research and industry applications.
        """.strip()
        
        key_insights = [
            f"Analyzed {len(articles)} articles with average relevance score of {statistics.mean(a.relevance_score for a in articles):.2f}",
            f"Top sources include {', '.join(Counter(a.source for a in articles).most_common(3)[0])}",
            "AI research and development continues to accelerate across multiple domains",
            "Industry adoption of AI technologies remains a key focus area"
        ]
        
        return ReportSummaryData(
            executive_summary=executive_summary,
            key_insights=key_insights,
            trend_analysis="Trend analysis based on article frequency and topic distribution shows continued growth in AI coverage.",
            recommendations=[
                "Monitor developments in top trending AI topics",
                "Track key industry players and their announcements",
                "Stay informed on regulatory and policy changes"
            ],
            market_implications="The AI market continues to evolve rapidly with significant implications for multiple industries."
        )
    
    async def _generate_html_content(self, report: Report, request: ReportGenerationRequest) -> str:
        """Generate HTML content for the report."""
        try:
            # Use template if available
            template_name = request.template_name or f"{request.report_type.value}_report.html"
            
            try:
                template = self.template_env.get_template(template_name)
            except:
                # Use default template
                template = self._get_default_html_template()
            
            return template.render(
                report=report,
                metadata=report.metadata,
                sections=report.sections,
                trends=report.trends,
                **request.custom_styling
            )
            
        except Exception as e:
            logger.warning(f"HTML generation failed, using simple format: {e}")
            return self._generate_simple_html(report)
    
    def _get_default_html_template(self) -> Template:
        """Get default HTML template."""
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ metadata.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 40px; }
        .article { border-left: 3px solid #e5e7eb; padding-left: 15px; margin-bottom: 20px; }
        .metrics { background: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .trend { background: #fef3c7; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ metadata.title }}</h1>
        <p>{{ metadata.period_start.strftime('%B %d, %Y') }} - {{ metadata.period_end.strftime('%B %d, %Y') }}</p>
        <div class="metrics">
            {{ metadata.total_articles }} articles | {{ metadata.sources_covered }} sources | 
            Avg relevance: {{ "%.1f"|format(metadata.avg_relevance_score * 100) }}%
        </div>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{{ report.executive_summary }}</p>
    </div>
    
    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        {% for article in section.articles %}
        <div class="article">
            <h3><a href="{{ article.url }}">{{ article.title }}</a></h3>
            <p><strong>{{ article.source }}</strong> | {{ article.published_date.strftime('%B %d, %Y') }}</p>
            <p>{{ article.summary }}</p>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
    
    {% if trends %}
    <div class="section">
        <h2>Trend Analysis</h2>
        {% for trend in trends %}
        <div class="trend">
            <h3>{{ trend.trend_name }}</h3>
            <p>{{ trend.description }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
        """
        return Template(template_content)
    
    def _generate_simple_html(self, report: Report) -> str:
        """Generate simple HTML fallback."""
        html = f"""
        <html>
        <body>
        <h1>{report.metadata.title}</h1>
        <p><strong>Period:</strong> {report.metadata.period_start.strftime('%B %d, %Y')} - {report.metadata.period_end.strftime('%B %d, %Y')}</p>
        <h2>Executive Summary</h2>
        <p>{report.executive_summary}</p>
        """
        
        for section in report.sections:
            html += f"<h2>{section.title}</h2>"
            for article in section.articles[:3]:
                html += f"""
                <div>
                    <h3><a href="{article.url}">{article.title}</a></h3>
                    <p><strong>{article.source}</strong> | {article.published_date.strftime('%B %d, %Y')}</p>
                    <p>{article.summary}</p>
                </div>
                """
        
        html += "</body></html>"
        return html
    
    def _generate_markdown_content(self, report: Report) -> str:
        """Generate markdown content."""
        md = f"""# {report.metadata.title}

**Period:** {report.metadata.period_start.strftime('%B %d, %Y')} - {report.metadata.period_end.strftime('%B %d, %Y')}

**Report Metrics:** {report.metadata.total_articles} articles | {report.metadata.sources_covered} sources | Avg relevance: {report.metadata.avg_relevance_score*100:.1f}%

## Executive Summary

{report.executive_summary}

"""
        
        for section in report.sections:
            md += f"\n## {section.title}\n\n"
            for article in section.articles:
                md += f"""### [{article.title}]({article.url})
**{article.source}** | {article.published_date.strftime('%B %d, %Y')}

{article.summary}

"""
        
        if report.trends:
            md += "\n## Trend Analysis\n\n"
            for trend in report.trends:
                md += f"**{trend.trend_name}:** {trend.description}\n\n"
        
        return md
    
    def _generate_text_content(self, report: Report) -> str:
        """Generate plain text content."""
        text = f"""{report.metadata.title}
{'='*len(report.metadata.title)}

Period: {report.metadata.period_start.strftime('%B %d, %Y')} - {report.metadata.period_end.strftime('%B %d, %Y')}

EXECUTIVE SUMMARY
-----------------
{report.executive_summary}

"""
        
        for section in report.sections:
            text += f"\n{section.title.upper()}\n{'-'*len(section.title)}\n\n"
            for article in section.articles:
                text += f"{article.title}\n{article.source} | {article.published_date.strftime('%B %d, %Y')}\n{article.url}\n\n{article.summary}\n\n"
        
        return text
    
    async def _deliver_report(self, report: Report, request: ReportGenerationRequest):
        """Deliver report via email."""
        if not request.recipients:
            return None
        
        # Create email request
        email_request = TemplateEmailRequest(
            template_name="daily_report",  # Would be dynamic based on report type
            to_addresses=request.recipients,
            subject=report.metadata.title,
            template_data={
                "report": report,
                "metadata": report.metadata,
                "sections": report.sections,
                "trends": report.trends,
                "title": report.metadata.title,
                "period_start": report.metadata.period_start,
                "period_end": report.metadata.period_end,
                "total_articles": report.metadata.total_articles,
                "sources_covered": report.metadata.sources_covered,
                "avg_relevance": report.metadata.avg_relevance_score,
                "executive_summary": report.executive_summary,
                "key_insights": report.key_insights
            }
        )
        
        return await send_templated_email(email_request)
    
    def _calculate_completeness(self, report: Report) -> float:
        """Calculate report completeness score."""
        completeness_factors = [
            bool(report.executive_summary),
            bool(report.key_insights),
            len(report.sections) > 0,
            bool(report.html_content),
            len(report.sections) >= 3,
            bool(report.trends),
            bool(report.recommendations)
        ]
        
        return sum(completeness_factors) / len(completeness_factors)
    
    def _calculate_readability(self, report: Report) -> float:
        """Calculate report readability score."""
        # Simple readability metric based on sentence length and complexity
        total_words = 0
        total_sentences = 0
        
        for section in report.sections:
            words = len(section.content.split())
            sentences = section.content.count('.') + section.content.count('!') + section.content.count('?')
            total_words += words
            total_sentences += sentences
        
        if total_sentences == 0:
            return 0.5
        
        avg_sentence_length = total_words / total_sentences
        
        # Score based on ideal sentence length (15-20 words)
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length <= 25:
            return 0.8
        elif 8 <= avg_sentence_length <= 30:
            return 0.6
        else:
            return 0.4


# Global service instance
_report_generation_service: Optional[ReportGenerationService] = None


def get_report_generation_service() -> ReportGenerationService:
    """Get global report generation service."""
    global _report_generation_service
    if _report_generation_service is None:
        _report_generation_service = ReportGenerationService()
    return _report_generation_service


# Main entry point
async def generate_report(request: ReportGenerationRequest) -> ReportGenerationResponse:
    """Generate news report using the Report Generation Agent."""
    service = get_report_generation_service()
    return await service.generate_report(request)


# Export main components
__all__ = [
    'report_generation_agent',
    'ReportGenerationService',
    'generate_report',
    'get_report_generation_service'
]