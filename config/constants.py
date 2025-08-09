"""
AI News Automation System - Constants
Location: config/constants.py

System-wide constants and enums for the AI News Automation System.
Provides consistent values used across agents, MCP servers, and workflows.
"""

from enum import Enum
from typing import Dict, List

# ============================================================================
# SYSTEM INFORMATION
# ============================================================================
SYSTEM_NAME = "AI News Automation System"
SYSTEM_VERSION = "1.0.0"
SYSTEM_DESCRIPTION = "Multi-agent system for automated AI news discovery, analysis, and reporting"

# ============================================================================
# AGENT CONSTANTS
# ============================================================================
class AgentType(str, Enum):
    """Types of agents in the system"""
    NEWS_DISCOVERY = "news_discovery"
    CONTENT_ANALYSIS = "content_analysis"
    REPORT_GENERATION = "report_generation"
    ALERT = "alert"
    COORDINATION = "coordination"

class AgentStatus(str, Enum):
    """Agent operational status"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

# Agent auto-discovery descriptions (critical for Claude Code co-agents)
AGENT_DESCRIPTIONS = {
    AgentType.NEWS_DISCOVERY: (
        "I am the News Discovery Agent specialized in monitoring 12+ AI news sources "
        "via RSS feeds. I filter articles for AI relevance using keywords like AI, ML, LLM, "
        "neural networks, and maintain a 0.7+ relevance threshold. I deduplicate content "
        "and coordinate with Content Analysis Agent for deep analysis. I use MCP RSS Aggregator tools."
    ),
    
    AgentType.CONTENT_ANALYSIS: (
        "I am the Content Analysis Agent specialized in analyzing AI news articles using "
        "Cohere Command R7B for cost-effective processing. I extract entities, perform sentiment "
        "analysis, score relevance and urgency, and detect emerging trends. I coordinate with "
        "Report Generation and Alert Agents. I use MCP Content Analyzer tools."
    ),
    
    AgentType.REPORT_GENERATION: (
        "I am the Report Generation Agent specialized in creating structured daily (6 AM), "
        "weekly (Sunday), and monthly (5th) AI news reports. I synthesize analyzed articles "
        "into executive summaries, key highlights, and trend analysis. I coordinate with "
        "Email Notifications for delivery. I use MCP Email and Database tools."
    ),
    
    AgentType.ALERT: (
        "I am the Alert Agent specialized in detecting breaking AI news and urgent developments "
        "within 30 minutes. I monitor for major product launches, significant funding (>$50M), "
        "regulatory changes, and research breakthroughs. I coordinate with Email Notifications "
        "for immediate delivery. I use MCP Alert and Email tools."
    ),
    
    AgentType.COORDINATION: (
        "I am the Coordination Agent responsible for orchestrating multi-agent workflows "
        "using LangGraph. I manage daily processing pipelines, coordinate agent handoffs, "
        "handle error recovery, and ensure system health. I coordinate with all agents "
        "and monitor system performance. I use all MCP tools for orchestration."
    )
}

# ============================================================================
# MCP SERVER CONSTANTS
# ============================================================================
class MCPServerType(str, Enum):
    """Types of MCP servers"""
    RSS_AGGREGATOR = "rss_aggregator"
    CONTENT_ANALYZER = "content_analyzer"
    EMAIL_NOTIFICATIONS = "email_notifications"
    DATABASE_OPERATIONS = "database_operations"

MCP_SERVER_NAMES = {
    MCPServerType.RSS_AGGREGATOR: "RSS Aggregator Server",
    MCPServerType.CONTENT_ANALYZER: "Content Analysis Server", 
    MCPServerType.EMAIL_NOTIFICATIONS: "Email Notifications Server",
    MCPServerType.DATABASE_OPERATIONS: "Database Operations Server"
}

# ============================================================================
# NEWS SOURCE CONSTANTS
# ============================================================================
class SourceTier(int, Enum):
    """News source quality tiers"""
    TIER_1 = 1  # Highest quality (academic, primary sources)
    TIER_2 = 2  # High quality (industry leaders, established media)
    TIER_3 = 3  # Good quality (aggregators, secondary sources)

class SourceCategory(str, Enum):
    """News source categories"""
    ACADEMIC_RESEARCH = "Academic Research"
    INDUSTRY_RESEARCH = "Industry Research"
    INDUSTRY_NEWS = "Industry News"
    AI_NEWS_AGGREGATOR = "AI News Aggregator"
    EDUCATIONAL = "Educational"

# Default news sources configuration (12+ sources as per PRP)
DEFAULT_NEWS_SOURCES = [
    # Tier 1 Sources (Highest Quality)
    {
        "name": "MIT AI News",
        "url": "https://news.mit.edu/topic/artificial-intelligence2",
        "rss_feed_url": "https://news.mit.edu/rss/topic/artificial-intelligence2",
        "tier": SourceTier.TIER_1,
        "category": SourceCategory.ACADEMIC_RESEARCH
    },
    {
        "name": "Google AI Research",
        "url": "https://research.google/blog/",
        "rss_feed_url": "https://research.googleblog.com/feeds/posts/default/-/AI",
        "tier": SourceTier.TIER_1,
        "category": SourceCategory.INDUSTRY_RESEARCH
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/",
        "rss_feed_url": "https://openai.com/blog/rss.xml",
        "tier": SourceTier.TIER_1,
        "category": SourceCategory.INDUSTRY_RESEARCH
    },
    {
        "name": "Berkeley BAIR",
        "url": "https://bair.berkeley.edu/blog/",
        "rss_feed_url": "https://bair.berkeley.edu/blog/feed.xml",
        "tier": SourceTier.TIER_1,
        "category": SourceCategory.ACADEMIC_RESEARCH
    },
    
    # Tier 2 Sources (High Quality)
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "rss_feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "tier": SourceTier.TIER_2,
        "category": SourceCategory.INDUSTRY_NEWS
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/ai/",
        "rss_feed_url": "https://feeds.feedburner.com/venturebeat/SZYF",
        "tier": SourceTier.TIER_2,
        "category": SourceCategory.INDUSTRY_NEWS
    },
    {
        "name": "Stanford HAI",
        "url": "https://hai.stanford.edu/news",
        "rss_feed_url": "https://hai.stanford.edu/news/rss.xml",
        "tier": SourceTier.TIER_2,
        "category": SourceCategory.ACADEMIC_RESEARCH
    },
    {
        "name": "NVIDIA AI Blog",
        "url": "https://blogs.nvidia.com/blog/category/deep-learning/",
        "rss_feed_url": "https://blogs.nvidia.com/feed/",
        "tier": SourceTier.TIER_2,
        "category": SourceCategory.INDUSTRY_RESEARCH
    },
    
    # Tier 3 Sources (Good Coverage)
    {
        "name": "MarkTechPost",
        "url": "https://www.marktechpost.com/",
        "rss_feed_url": "https://www.marktechpost.com/feed/",
        "tier": SourceTier.TIER_3,
        "category": SourceCategory.AI_NEWS_AGGREGATOR
    },
    {
        "name": "Unite.AI",
        "url": "https://www.unite.ai/",
        "rss_feed_url": "https://www.unite.ai/feed/",
        "tier": SourceTier.TIER_3,
        "category": SourceCategory.AI_NEWS_AGGREGATOR
    },
    {
        "name": "Analytics Vidhya",
        "url": "https://www.analyticsvidhya.com/blog/",
        "rss_feed_url": "https://www.analyticsvidhya.com/blog/feed/",
        "tier": SourceTier.TIER_3,
        "category": SourceCategory.EDUCATIONAL
    },
    {
        "name": "Axios AI",
        "url": "https://www.axios.com/technology/artificial-intelligence",
        "rss_feed_url": "https://api.axios.com/feed/artificial-intelligence",
        "tier": SourceTier.TIER_3,
        "category": SourceCategory.INDUSTRY_NEWS
    }
]

# ============================================================================
# CONTENT PROCESSING CONSTANTS
# ============================================================================
class ProcessingStage(str, Enum):
    """Article processing stages"""
    DISCOVERED = "discovered"
    FETCHED = "fetched"
    ANALYZED = "analyzed"
    SUMMARIZED = "summarized"
    CATEGORIZED = "categorized"
    COMPLETED = "completed"
    FAILED = "failed"

class ContentType(str, Enum):
    """Types of content"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    RESEARCH_PAPER = "research_paper"
    PRESS_RELEASE = "press_release"
    NEWS_REPORT = "news_report"

# AI-related keywords for relevance filtering
AI_KEYWORDS = [
    "artificial intelligence", "AI", "machine learning", "ML", "deep learning",
    "neural network", "LLM", "large language model", "GPT", "transformer",
    "natural language processing", "NLP", "computer vision", "ChatGPT",
    "generative AI", "foundation model", "Claude", "Gemini", "BERT",
    "reinforcement learning", "supervised learning", "unsupervised learning",
    "AGI", "artificial general intelligence", "robotics", "automation"
]

# Entity types for extraction
ENTITY_TYPES = [
    "PERSON", "ORGANIZATION", "COMPANY", "PRODUCT", "TECHNOLOGY",
    "FUNDING_AMOUNT", "DATE", "LOCATION", "UNIVERSITY", "RESEARCH_PAPER"
]

# ============================================================================
# REPORT CONSTANTS
# ============================================================================
class ReportType(str, Enum):
    """Types of reports generated"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL = "special"

class ReportStatus(str, Enum):
    """Report generation status"""
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    DELIVERED = "delivered"
    FAILED = "failed"
    ARCHIVED = "archived"

class ReportSection(str, Enum):
    """Report sections"""
    EXECUTIVE_SUMMARY = "executive_summary"
    KEY_HIGHLIGHTS = "key_highlights"
    BREAKING_NEWS = "breaking_news"
    RESEARCH_DEVELOPMENTS = "research_developments"
    INDUSTRY_NEWS = "industry_news"
    FUNDING_ANNOUNCEMENTS = "funding_announcements"
    PRODUCT_LAUNCHES = "product_launches"
    TREND_ANALYSIS = "trend_analysis"
    UPCOMING_EVENTS = "upcoming_events"

# Report templates
REPORT_TEMPLATES = {
    ReportType.DAILY: {
        "subject": "Daily AI News Brief - {date}",
        "sections": [
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.BREAKING_NEWS,
            ReportSection.KEY_HIGHLIGHTS,
            ReportSection.RESEARCH_DEVELOPMENTS,
            ReportSection.INDUSTRY_NEWS
        ]
    },
    ReportType.WEEKLY: {
        "subject": "Weekly AI Digest - Week of {date}",
        "sections": [
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.KEY_HIGHLIGHTS,
            ReportSection.RESEARCH_DEVELOPMENTS,
            ReportSection.FUNDING_ANNOUNCEMENTS,
            ReportSection.PRODUCT_LAUNCHES,
            ReportSection.TREND_ANALYSIS
        ]
    },
    ReportType.MONTHLY: {
        "subject": "Monthly AI Analysis - {month} {year}",
        "sections": [
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.TREND_ANALYSIS,
            ReportSection.RESEARCH_DEVELOPMENTS,
            ReportSection.INDUSTRY_NEWS,
            ReportSection.FUNDING_ANNOUNCEMENTS,
            ReportSection.UPCOMING_EVENTS
        ]
    }
}

# ============================================================================
# ALERT CONSTANTS
# ============================================================================
class AlertType(str, Enum):
    """Types of alerts"""
    BREAKING_NEWS = "breaking_news"
    MAJOR_FUNDING = "major_funding"
    PRODUCT_LAUNCH = "product_launch"
    REGULATORY_CHANGE = "regulatory_change"
    RESEARCH_BREAKTHROUGH = "research_breakthrough"
    ACQUISITION = "acquisition"
    PARTNERSHIP = "partnership"

class UrgencyLevel(str, Enum):
    """Alert urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    THROTTLED = "throttled"

# Alert trigger rules
ALERT_RULES = {
    AlertType.BREAKING_NEWS: {
        "keywords": ["breaking", "announcement", "launches", "releases"],
        "urgency_threshold": 0.8,
        "companies": ["OpenAI", "Google", "Microsoft", "Meta", "Anthropic", "Amazon"]
    },
    AlertType.MAJOR_FUNDING: {
        "keywords": ["funding", "investment", "raises", "Series A", "Series B", "Series C"],
        "amount_threshold": 50000000,  # $50M+
        "urgency_threshold": 0.7
    },
    AlertType.PRODUCT_LAUNCH: {
        "keywords": ["launch", "introduces", "unveils", "announces", "releases"],
        "companies": ["OpenAI", "Google", "Microsoft", "Meta", "Anthropic"],
        "urgency_threshold": 0.8
    },
    AlertType.RESEARCH_BREAKTHROUGH: {
        "keywords": ["breakthrough", "achievement", "milestone", "record", "first"],
        "sources": ["MIT AI News", "Google AI Research", "Berkeley BAIR", "Stanford HAI"],
        "urgency_threshold": 0.7
    }
}

# ============================================================================
# WORKFLOW CONSTANTS
# ============================================================================
class WorkflowType(str, Enum):
    """Types of LangGraph workflows"""
    CONTENT_PIPELINE = "content_pipeline"
    DAILY_AUTOMATION = "daily_automation"
    WEEKLY_DIGEST = "weekly_digest"
    MONTHLY_ANALYSIS = "monthly_analysis"
    ALERT_DETECTION = "alert_detection"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class NodeStatus(str, Enum):
    """Individual workflow node status"""
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# ============================================================================
# COST TRACKING CONSTANTS
# ============================================================================
class CostCategory(str, Enum):
    """Cost tracking categories"""
    LLM_API_CALLS = "llm_api_calls"
    EMBEDDING_GENERATION = "embedding_generation"
    CONTENT_ANALYSIS = "content_analysis"
    EMAIL_DELIVERY = "email_delivery"
    DATABASE_OPERATIONS = "database_operations"
    INFRASTRUCTURE = "infrastructure"

# Model pricing (per 1M tokens) - Updated for 2025
MODEL_PRICING = {
    # OpenAI models
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    
    # Cohere models (cost-optimized choice)
    "command-r7b-12-2024": {"input": 0.15, "output": 0.60},
    "command-r": {"input": 0.50, "output": 1.50},
    
    # Embedding models
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
}

# ============================================================================
# HTTP AND API CONSTANTS
# ============================================================================
HTTP_TIMEOUT = 30  # seconds
HTTP_RETRIES = 3
HTTP_BACKOFF_FACTOR = 1.0

# HTTP headers
DEFAULT_HEADERS = {
    "User-Agent": f"{SYSTEM_NAME}/{SYSTEM_VERSION}",
    "Accept": "application/json, text/html, application/xml, text/xml, */*",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

# ============================================================================
# ERROR CONSTANTS
# ============================================================================
class ErrorType(str, Enum):
    """Types of errors in the system"""
    CONFIGURATION_ERROR = "configuration_error"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"
    WORKFLOW_ERROR = "workflow_error"

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# SYSTEM LIMITS
# ============================================================================
# Processing limits (aligned with $100/month budget)
MAX_DAILY_ARTICLES = 150
MAX_WEEKLY_ARTICLES = 1050  # 150 * 7
MAX_MONTHLY_ARTICLES = 4500  # 150 * 30

# Content limits
MAX_ARTICLE_LENGTH = 50000  # characters
MAX_SUMMARY_LENGTH = 500    # characters
MAX_TITLE_LENGTH = 500      # characters

# Time limits
MAX_PROCESSING_TIME = 300   # 5 minutes per article
MAX_WORKFLOW_TIME = 1800    # 30 minutes per workflow
MAX_REPORT_GENERATION_TIME = 600  # 10 minutes per report

# ============================================================================
# SYSTEM HEALTH CONSTANTS
# ============================================================================
HEALTH_CHECK_ENDPOINTS = [
    "/health",
    "/health/database",
    "/health/agents", 
    "/health/mcp-servers",
    "/health/workflows"
]

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "article_processing_time": 30.0,    # seconds
    "report_generation_time": 300.0,    # seconds
    "alert_detection_time": 300.0,      # seconds
    "database_query_time": 5.0,         # seconds
    "api_response_time": 10.0            # seconds
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_tier_sources(tier: SourceTier) -> List[Dict]:
    """Get news sources by tier"""
    return [source for source in DEFAULT_NEWS_SOURCES if source["tier"] == tier]

def get_category_sources(category: SourceCategory) -> List[Dict]:
    """Get news sources by category"""
    return [source for source in DEFAULT_NEWS_SOURCES if source["category"] == category]

def get_alert_keywords(alert_type: AlertType) -> List[str]:
    """Get keywords for alert type"""
    return ALERT_RULES.get(alert_type, {}).get("keywords", [])

def get_model_cost(model_name: str, token_count: int, token_type: str = "input") -> float:
    """Calculate cost for model usage"""
    if model_name not in MODEL_PRICING:
        return 0.0
    
    price_per_million = MODEL_PRICING[model_name].get(token_type, 0.0)
    return (token_count / 1_000_000) * price_per_million

def is_tier_1_source(source_name: str) -> bool:
    """Check if source is tier 1 (highest quality)"""
    for source in DEFAULT_NEWS_SOURCES:
        if source["name"] == source_name:
            return source["tier"] == SourceTier.TIER_1
    return False