"""
AI News Automation System - Configuration Settings
Location: config/settings.py

Type-safe configuration using Pydantic Settings with environment-based configuration.
Validates all API keys, database connections, and system settings at startup.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum

from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, field_validator
from pydantic import HttpUrl, EmailStr, ValidationError

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Settings(BaseSettings):
    """
    Application settings with type validation and environment-based configuration
    """
    
    # ============================================================================
    # ENVIRONMENT CONFIGURATION
    # ============================================================================
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    
    # ============================================================================
    # DATABASE CONFIGURATION (Supabase)
    # ============================================================================
    supabase_url: HttpUrl = Field(..., description="Supabase project URL")
    supabase_key: SecretStr = Field(..., description="Supabase anon key")
    supabase_service_key: SecretStr = Field(..., description="Supabase service role key")
    database_url: SecretStr = Field(..., description="PostgreSQL connection URL")
    
    # Database connection pool settings
    db_pool_size: int = Field(default=10, ge=1, le=50)
    db_max_overflow: int = Field(default=20, ge=0, le=100)
    db_pool_timeout: int = Field(default=30, ge=5, le=300)
    db_pool_recycle: int = Field(default=3600, ge=300, le=7200)
    
    # ============================================================================
    # AI MODEL CONFIGURATION
    # ============================================================================
    # OpenAI for Pydantic AI agents
    openai_api_key: SecretStr = Field(..., description="OpenAI API key")
    openai_organization: Optional[str] = Field(default=None)
    
    # Cohere for content analysis (cost-optimized)
    cohere_api_key: SecretStr = Field(..., description="Cohere API key")
    cohere_model: str = Field(default="command-r7b-12-2024")
    
    # Model configurations per agent
    discovery_agent_model: str = Field(default="gpt-4o-mini")
    analysis_agent_model: str = Field(default="command-r7b-12-2024")
    report_agent_model: str = Field(default="gpt-4o-mini")
    alert_agent_model: str = Field(default="gpt-4o-mini")
    coordination_agent_model: str = Field(default="gpt-4o-mini")
    
    # ============================================================================
    # EMAIL CONFIGURATION (SMTP)
    # ============================================================================
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: EmailStr = Field(..., description="SMTP username")
    smtp_password: SecretStr = Field(..., description="SMTP password")
    smtp_use_tls: bool = Field(default=True)
    
    # Email settings
    email_from: EmailStr = Field(..., description="Sender email address")
    email_to: EmailStr = Field(..., description="Default recipient email")
    email_reply_to: Optional[EmailStr] = Field(default=None)
    
    # ============================================================================
    # NEWS SOURCE CONFIGURATION
    # ============================================================================
    rss_fetch_interval: int = Field(default=3600, ge=300, le=86400, description="RSS fetch interval in seconds")
    rss_max_articles_per_source: int = Field(default=50, ge=1, le=200)
    rss_rate_limit_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    rss_max_concurrent: int = Field(default=5, ge=1, le=20)
    rss_timeout: int = Field(default=30, ge=5, le=120)
    
    # Content filtering
    relevance_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    ai_keywords: List[str] = Field(default=[
        "AI", "artificial intelligence", "machine learning", "LLM", 
        "neural networks", "GPT", "Claude", "deep learning", "ChatGPT",
        "generative AI", "transformer", "NLP", "computer vision"
    ])
    
    # ============================================================================
    # SYSTEM CONFIGURATION
    # ============================================================================
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_file: str = Field(default="logs/ai_news_system.log")
    log_max_size: int = Field(default=10485760, description="10MB max log file size")
    log_backup_count: int = Field(default=5)
    
    # Cost tracking and limits (critical for $100/month budget)
    monthly_budget_usd: float = Field(default=100.0, gt=0.0)
    daily_budget_usd: float = Field(default=3.33, gt=0.0)
    cost_alert_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Processing limits
    max_articles_per_day: int = Field(default=150, ge=1, le=1000)
    batch_size: int = Field(default=10, ge=1, le=50)
    cache_ttl: int = Field(default=3600, ge=300, le=86400)
    
    # ============================================================================
    # AGENT CONFIGURATION
    # ============================================================================
    # Timeouts (seconds)
    agent_timeout: int = Field(default=300, ge=30, le=1800)
    mcp_tool_timeout: int = Field(default=60, ge=10, le=300)
    workflow_timeout: int = Field(default=1800, ge=300, le=7200)
    
    # Retry settings
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    exponential_backoff: bool = Field(default=True)
    
    # ============================================================================
    # WORKFLOW CONFIGURATION
    # ============================================================================
    # Report generation schedules
    daily_report_time: str = Field(default="06:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    weekly_report_day: str = Field(default="sunday")
    monthly_report_date: int = Field(default=5, ge=1, le=28)
    
    # Alert settings
    alert_urgency_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    alert_throttle_minutes: int = Field(default=30, ge=5, le=240)
    max_alerts_per_hour: int = Field(default=5, ge=1, le=20)
    
    # ============================================================================
    # MONITORING & HEALTH CHECKS
    # ============================================================================
    health_check_interval: int = Field(default=300, ge=60, le=3600)
    metrics_retention_days: int = Field(default=30, ge=1, le=365)
    performance_alert_threshold: float = Field(default=5.0, ge=1.0, le=30.0)
    
    # Resource monitoring
    cpu_alert_threshold: float = Field(default=80.0, ge=50.0, le=95.0)
    memory_alert_threshold: float = Field(default=85.0, ge=50.0, le=95.0)
    disk_alert_threshold: float = Field(default=90.0, ge=70.0, le=95.0)
    
    # ============================================================================
    # MCP SERVER CONFIGURATION
    # ============================================================================
    mcp_rss_server_port: int = Field(default=3001, ge=3000, le=9999)
    mcp_content_server_port: int = Field(default=3002, ge=3000, le=9999)
    mcp_email_server_port: int = Field(default=3003, ge=3000, le=9999)
    mcp_database_server_port: int = Field(default=3004, ge=3000, le=9999)
    
    # MCP server settings
    mcp_server_timeout: int = Field(default=30, ge=5, le=120)
    mcp_max_connections: int = Field(default=10, ge=1, le=50)
    
    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    # API rate limiting
    api_rate_limit_per_minute: int = Field(default=60, ge=10, le=1000)
    api_burst_limit: int = Field(default=10, ge=1, le=100)
    
    # Content validation
    max_content_length: int = Field(default=50000, ge=1000, le=200000)
    allowed_domains: List[str] = Field(default=[
        "openai.com", "google.com", "mit.edu", "stanford.edu", "berkeley.edu",
        "techcrunch.com", "venturebeat.com", "nvidia.com", "anthropic.com"
    ])
    
    # Security headers and validation
    validate_ssl_certs: bool = Field(default=True)
    user_agent: str = Field(default="AI-News-Automation/1.0")
    
    # ============================================================================
    # DEVELOPMENT SETTINGS
    # ============================================================================
    # Development-only settings
    dev_skip_authentication: bool = Field(default=False)
    dev_mock_external_apis: bool = Field(default=False)
    dev_enable_debug_logging: bool = Field(default=False)
    
    # Test data settings
    test_rss_feeds: int = Field(default=3, ge=1, le=10)
    test_articles_count: int = Field(default=5, ge=1, le=50)
    test_email_recipient: Optional[EmailStr] = Field(default=None)
    
    # ============================================================================
    # DERIVED PROPERTIES
    # ============================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def project_root(self) -> Path:
        """Get project root directory"""
        return Path(__file__).parent.parent
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory path"""
        return self.project_root / "logs"
    
    @property
    def daily_cost_limit(self) -> float:
        """Get daily cost limit with alert threshold"""
        return self.daily_budget_usd * self.cost_alert_threshold
    
    # ============================================================================
    # VALIDATORS
    # ============================================================================
    @field_validator('environment', mode='before')
    def validate_environment(cls, v):
        """Validate environment setting"""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @field_validator('log_level', mode='before') 
    def validate_log_level(cls, v):
        """Validate log level setting"""
        if isinstance(v, str):
            return LogLevel(v.upper())
        return v
    
    @field_validator('ai_keywords')
    def validate_ai_keywords(cls, v):
        """Ensure AI keywords are not empty"""
        if not v or len(v) < 3:
            raise ValueError("At least 3 AI keywords must be specified")
        return [keyword.lower().strip() for keyword in v]
    
    @field_validator('weekly_report_day')
    def validate_weekly_report_day(cls, v):
        """Validate weekly report day"""
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if v.lower() not in valid_days:
            raise ValueError(f"Weekly report day must be one of: {valid_days}")
        return v.lower()
    
    @field_validator('allowed_domains')
    def validate_allowed_domains(cls, v):
        """Validate allowed domains list"""
        if not v:
            raise ValueError("At least one allowed domain must be specified")
        return [domain.lower().strip() for domain in v]
    
    @field_validator('*', mode='before')
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if v == '':
            return None
        return v
    
    # ============================================================================
    # CONFIGURATION VALIDATION
    # ============================================================================
    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate that all required API keys are present and potentially valid
        Returns dict of validation results
        """
        validations = {}
        
        # OpenAI API key validation
        openai_key = self.openai_api_key.get_secret_value()
        validations['openai'] = openai_key.startswith('sk-') and len(openai_key) > 20
        
        # Cohere API key validation  
        cohere_key = self.cohere_api_key.get_secret_value()
        validations['cohere'] = len(cohere_key) > 10  # Basic length check
        
        # Database URL validation
        db_url = self.database_url.get_secret_value()
        validations['database'] = db_url.startswith('postgresql://') or db_url.startswith('postgres://')
        
        # Supabase keys validation
        supabase_key = self.supabase_key.get_secret_value()
        validations['supabase'] = len(supabase_key) > 50  # Supabase keys are long
        
        return validations
    
    def validate_budget_consistency(self) -> bool:
        """Validate that budget settings are consistent"""
        monthly_daily_equivalent = self.monthly_budget_usd / 30
        return abs(self.daily_budget_usd - monthly_daily_equivalent) < 0.5
    
    def create_log_directory(self) -> None:
        """Create logs directory if it doesn't exist"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ============================================================================
    # PYDANTIC CONFIGURATION
    # ============================================================================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        use_enum_values = True
        validate_assignment = True
        
        # Field aliases for environment variables
        fields = {
            "supabase_url": {"env": "SUPABASE_URL"},
            "supabase_key": {"env": "SUPABASE_KEY"}, 
            "supabase_service_key": {"env": "SUPABASE_SERVICE_KEY"},
            "database_url": {"env": "DATABASE_URL"},
            "openai_api_key": {"env": "OPENAI_API_KEY"},
            "cohere_api_key": {"env": "COHERE_API_KEY"},
            "smtp_username": {"env": "SMTP_USERNAME"},
            "smtp_password": {"env": "SMTP_PASSWORD"},
            "email_from": {"env": "EMAIL_FROM"},
            "email_to": {"env": "EMAIL_TO"},
        }

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern)
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            
            # Validate configuration on first load
            api_validations = _settings.validate_api_keys()
            invalid_keys = [key for key, valid in api_validations.items() if not valid]
            
            if invalid_keys:
                print(f"⚠️  Warning: Invalid API keys detected: {invalid_keys}")
                if _settings.environment == Environment.PRODUCTION:
                    raise ValueError(f"Invalid API keys in production: {invalid_keys}")
            
            # Validate budget consistency
            if not _settings.validate_budget_consistency():
                print("⚠️  Warning: Daily and monthly budget settings are inconsistent")
            
            # Create log directory
            _settings.create_log_directory()
            
            print(f"✅ Configuration loaded successfully for {_settings.environment} environment")
            
        except ValidationError as e:
            print(f"❌ Configuration validation failed: {e}")
            raise
        except Exception as e:
            print(f"❌ Configuration loading failed: {e}")
            raise
    
    return _settings

def reload_settings() -> Settings:
    """
    Reload settings (useful for testing or configuration changes)
    """
    global _settings
    _settings = None
    return get_settings()

# Helper functions for common configuration access
def get_database_url() -> str:
    """Get database URL"""
    return get_settings().database_url.get_secret_value()

def get_openai_api_key() -> str:
    """Get OpenAI API key"""
    return get_settings().openai_api_key.get_secret_value()

def get_cohere_api_key() -> str:
    """Get Cohere API key"""
    return get_settings().cohere_api_key.get_secret_value()

def is_development() -> bool:
    """Check if running in development mode"""
    return get_settings().is_development

def is_production() -> bool:
    """Check if running in production mode"""
    return get_settings().is_production