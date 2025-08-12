"""
Example Configuration and Settings Management
Location: examples/config/settings.py

This demonstrates:
- Pydantic-based configuration management
- Environment variable handling
- Phase-specific configuration
- Cost tracking and limits
- Security and credential management
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseSettings, Field, validator, root_validator
from pydantic.types import SecretStr
from enum import Enum
import os
from pathlib import Path
from datetime import timedelta

class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ProjectPhase(str, Enum):
    """Project development phases"""
    PHASE_1_LOCAL = "phase_1_local"
    PHASE_2_YOUTUBE = "phase_2_youtube" 
    PHASE_3_SOCIAL = "phase_3_social"

class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# Database Configuration
class DatabaseConfig(BaseSettings):
    """Database connection settings"""
    
    # Supabase connection
    database_url: str = Field(..., env="DATABASE_URL")
    database_host: str = Field(..., env="DB_HOST")
    database_port: int = Field(5432, env="DB_PORT")
    database_name: str = Field(..., env="DB_NAME")
    database_user: str = Field(..., env="DB_USER")
    database_password: SecretStr = Field(..., env="DB_PASSWORD")
    
    # Connection pool settings
    pool_size: int = Field(10, env="DB_POOL_SIZE")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(3600, env="DB_POOL_RECYCLE")
    
    # SSL and security
    ssl_require: bool = Field(True, env="DB_SSL_REQUIRE")
    
    @validator("database_url", pre=True)
    def build_database_url(cls, v, values):
        """Build database URL if not provided"""
        if v:
            return v
            
        # Build from components
        password = values.get("database_password")
        if isinstance(password, SecretStr):
            password = password.get_secret_value()
            
        return (
            f"postgresql://{values.get('database_user')}:{password}"
            f"@{values.get('database_host')}:{values.get('database_port')}"
            f"/{values.get('database_name')}"
        )

# LLM API Configuration
class LLMConfig(BaseSettings):
    """Large Language Model API settings"""
    
    # OpenAI Configuration
    openai_api_key: SecretStr = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-5-mini", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(0.1, env="OPENAI_TEMPERATURE")
    
    # Anthropic Configuration
    anthropic_api_key: SecretStr = Field(..., env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-3-haiku-20240307", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(4000, env="ANTHROPIC_MAX_TOKENS")
    
    # Cost management
    daily_cost_limit: float = Field(10.0, env="DAILY_COST_LIMIT")  # USD
    monthly_cost_limit: float = Field(100.0, env="MONTHLY_COST_LIMIT")  # USD
    cost_alert_threshold: float = Field(0.8, env="COST_ALERT_THRESHOLD")  # 80% of limit
    
    # Rate limiting
    requests_per_minute: int = Field(60, env="LLM_REQUESTS_PER_MINUTE")
    requests_per_hour: int = Field(3600, env="LLM_REQUESTS_PER_HOUR")
    
    # Default model selection based on task
    model_for_analysis: str = Field("gpt-4o-mini", env="MODEL_FOR_ANALYSIS")
    model_for_summary: str = Field("claude-3-haiku-20240307", env="MODEL_FOR_SUMMARY")
    model_for_alerts: str = Field("gpt-4o-mini", env="MODEL_FOR_ALERTS")

# News Sources Configuration
class NewsSourceTier(BaseSettings):
    """Configuration for news source tiers"""
    
    # Tier 1 sources (highest quality, most expensive to process)
    tier_1_sources: List[Dict[str, str]] = Field(default=[
        {
            "name": "OpenAI Blog",
            "url": "https://openai.com/blog",
            "rss_feed": "https://openai.com/blog/rss.xml",
            "category": "AI Research"
        },
        {
            "name": "Google AI Blog", 
            "url": "https://ai.googleblog.com",
            "rss_feed": "https://ai.googleblog.com/feeds/posts/default",
            "category": "AI Research"
        },
        {
            "name": "Anthropic News",
            "url": "https://www.anthropic.com/news",
            "rss_feed": "https://www.anthropic.com/news/rss.xml",
            "category": "AI Research"
        },
        {
            "name": "MIT AI News",
            "url": "https://news.mit.edu/topic/artificial-intelligence2",
            "rss_feed": "https://news.mit.edu/rss/topic/artificial-intelligence2",
            "category": "Academic Research"
        }
    ])
    
    # Tier 2 sources (good quality, moderate processing cost)
    tier_2_sources: List[Dict[str, str]] = Field(default=[
        {
            "name": "TechCrunch AI",
            "url": "https://techcrunch.com/category/artificial-intelligence/",
            "rss_feed": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "category": "Industry News"
        },
        {
            "name": "The Verge AI",
            "url": "https://www.theverge.com/ai-artificial-intelligence",
            "rss_feed": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "category": "Industry News"
        },
        {
            "name": "VentureBeat AI",
            "url": "https://venturebeat.com/ai/",
            "rss_feed": "https://venturebeat.com/category/ai/feed/",
            "category": "Industry News"
        }
    ])
    
    # Tier 3 sources (lower quality, minimal processing)
    tier_3_sources: List[Dict[str, str]] = Field(default=[
        {
            "name": "AI News",
            "url": "https://artificialintelligence-news.com",
            "rss_feed": "https://artificialintelligence-news.com/feed/",
            "category": "General News"
        }
    ])
    
    # Processing limits per tier
    tier_1_max_articles_per_day: int = Field(50, env="TIER_1_MAX_DAILY")
    tier_2_max_articles_per_day: int = Field(100, env="TIER_2_MAX_DAILY") 
    tier_3_max_articles_per_day: int = Field(25, env="TIER_3_MAX_DAILY")
    
    # Quality thresholds
    tier_1_relevance_threshold: float = Field(0.8, env="TIER_1_RELEVANCE_THRESHOLD")
    tier_2_relevance_threshold: float = Field(0.7, env="TIER_2_RELEVANCE_THRESHOLD")
    tier_3_relevance_threshold: float = Field(0.6, env="TIER_3_RELEVANCE_THRESHOLD")

# Social Media Configuration (for future phases)
class SocialMediaConfig(BaseSettings):
    """Social media platform configuration"""
    
    # Twitter/X
    twitter_api_key: Optional[SecretStr] = Field(None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[SecretStr] = Field(None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[SecretStr] = Field(None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[SecretStr] = Field(None, env="TWITTER_ACCESS_TOKEN_SECRET")
    twitter_bearer_token: Optional[SecretStr] = Field(None, env="TWITTER_BEARER_TOKEN")
    
    # YouTube
    youtube_api_key: Optional[SecretStr] = Field(None, env="YOUTUBE_API_KEY")
    youtube_client_id: Optional[SecretStr] = Field(None, env="YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[SecretStr] = Field(None, env="YOUTUBE_CLIENT_SECRET")
    
    # LinkedIn
    linkedin_client_id: Optional[SecretStr] = Field(None, env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[SecretStr] = Field(None, env="LINKEDIN_CLIENT_SECRET")
    
    # Publishing schedule
    posts_per_day: int = Field(3, env="POSTS_PER_DAY")
    optimal_posting_hours: List[int] = Field(default=[9, 13, 17], env="OPTIMAL_POSTING_HOURS")
    
    # Content guidelines
    max_hashtags_per_post: int = Field(5, env="MAX_HASHTAGS_PER_POST")
    default_hashtags: List[str] = Field(default=["#AI", "#MachineLearning", "#Technology"])

# Agent Configuration
class AgentConfig(BaseSettings):
    """Pydantic AI agent configuration"""
    
    # Agent behavior settings
    max_concurrent_agents: int = Field(5, env="MAX_CONCURRENT_AGENTS")
    agent_timeout_seconds: int = Field(300, env="AGENT_TIMEOUT_SECONDS")
    
    # Auto-discovery settings
    enable_agent_discovery: bool = Field(True, env="ENABLE_AGENT_DISCOVERY")
    discovery_interval_seconds: int = Field(60, env="DISCOVERY_INTERVAL_SECONDS")
    
    # Context isolation
    max_context_size: int = Field(8000, env="MAX_CONTEXT_SIZE")  # tokens
    context_overlap_tokens: int = Field(200, env="CONTEXT_OVERLAP_TOKENS")
    
    # Error handling
    max_retries: int = Field(3, env="AGENT_MAX_RETRIES")
    retry_delay_seconds: int = Field(5, env="AGENT_RETRY_DELAY")
    
    # Specific agent settings
    news_discovery_interval: int = Field(1800, env="NEWS_DISCOVERY_INTERVAL")  # 30 minutes
    content_analysis_batch_size: int = Field(10, env="CONTENT_ANALYSIS_BATCH_SIZE")
    report_generation_schedule: str = Field("0 6 * * *", env="REPORT_GENERATION_SCHEDULE")  # 6 AM daily

# MCP Server Configuration
class MCPConfig(BaseSettings):
    """Model Context Protocol server configuration"""
    
    # Server settings
    rss_server_port: int = Field(8001, env="RSS_SERVER_PORT")
    social_server_port: int = Field(8002, env="SOCIAL_SERVER_PORT")
    analytics_server_port: int = Field(8003, env="ANALYTICS_SERVER_PORT")
    
    # Performance settings
    max_concurrent_connections: int = Field(100, env="MCP_MAX_CONNECTIONS")
    request_timeout_seconds: int = Field(30, env="MCP_REQUEST_TIMEOUT")