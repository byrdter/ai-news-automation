name: "AI News Automation System - Pydantic AI + MCP + LangGraph PRP v1"
description: |

## Purpose
Build a comprehensive multi-agent system for automated AI news discovery, analysis, and intelligent reporting using Pydantic AI agents, MCP servers for modular tools, LangGraph workflows for orchestration, and Claude Code Co-agents with cost-optimized infrastructure targeting under $100/month operational costs.

## Core Principles
1. **Agent Specialization**: Five specialized agents with clear domain boundaries (Discovery, Analysis, Report, Alert, Coordination)
2. **Context Isolation**: Each agent operates independently with structured Pydantic models for communication
3. **MCP Modularity**: Four focused MCP servers (RSS, Content Analysis, Email, Database) with proper tool registration
4. **Workflow Orchestration**: LangGraph manages daily/weekly/monthly report generation with validation gates
5. **Cost Optimization**: Cohere Command R7B for analysis (90% cheaper than GPT-4), intelligent caching, batch processing
6. **Validation First**: Comprehensive testing at agent, MCP server, workflow, and integration levels
7. **Global Rules**: Strict adherence to CLAUDE.md for consistency and maintainability

---

## Goal
Create a Phase 1 Local Intelligence System that automatically discovers, analyzes, and reports on AI news from 12+ sources, delivering daily reports at 6 AM, weekly digests on Sundays, monthly trend analyses by the 5th, and breaking news alerts within 30 minutes - all under $100/month operational cost.

## Why
- **Business Value**: Automate 8+ hours daily of manual news curation and analysis work
- **Information Advantage**: Never miss critical AI developments with 24/7 monitoring
- **Cost Efficiency**: Direct API integration avoids $500+/month in third-party service subscriptions
- **Scalability**: Phase-gated approach allows proven validation before YouTube/social expansion
- **Quality Control**: Multi-agent specialization ensures high-quality, relevant content curation

## What
A production-ready system processing 50-150 articles/day with:
- Automated RSS aggregation from tier-1/2/3 AI news sources
- Relevance scoring, sentiment analysis, and entity extraction using Cohere
- Structured daily/weekly/monthly reports via email delivery
- Real-time breaking news detection and alerting
- Supabase PostgreSQL + pgvector for content storage and semantic search
- 95%+ uptime with comprehensive error handling and recovery

### Success Criteria
- [x] Daily reports delivered automatically at 6 AM
- [x] Weekly digests every Sunday with trend analysis
- [x] Monthly comprehensive reports by 5th of each month
- [x] Breaking news alerts within 30 minutes of detection
- [x] Total operational cost under $100/month
- [x] Processing 50-150 articles/day reliably
- [x] 95%+ system uptime with error recovery
- [x] All agents coordinate properly through LangGraph workflows

## All Needed Context

### Multi-Agent System Documentation
```yaml
# ESSENTIAL READING - Research completed and integrated
- url: https://ai.pydantic.dev/agents/
  why: Agent creation with RunContext, tool registration, system prompts
  key_findings: |
    - Agents use pydantic-graph under the hood for execution flow
    - deps_type parameter enables type-safe dependency injection
    - Tools registered via @agent.tool_plain or @agent.tool decorators
    - Dynamic system prompts support with @agent.system_prompt
  
- url: https://ai.pydantic.dev/multi-agent-applications/
  why: Agent-as-tool pattern, inter-agent communication
  key_findings: |
    - Delegate agents called within tool functions
    - Dependencies passed through RunContext
    - Subset pattern for agent dependency requirements
  
- url: https://modelcontextprotocol.io/docs/
  why: MCP server architecture, tool registration, transport protocols
  key_findings: |
    - Streamable HTTP transport (2025-03-26 spec) for cost efficiency
    - OAuth 2.0/2.1 authentication with PKCE
    - Structured error reporting via JSON-RPC 2.0
    - Container isolation for security
  
- url: https://langchain-ai.github.io/langgraph/
  why: State machines, conditional routing, error recovery patterns
  key_findings: |
    - Automatic state persistence across interruptions
    - Conditional edges for dynamic decision-making
    - Caching support with TTL and custom key functions
    - Parallel execution for independent operations
  
- file: examples/basic_agents/news_discovery_agent.py
  why: Pydantic AI agent patterns with auto-discovery descriptions
  
- file: examples/mcp_servers/rss_aggregator.py
  why: MCP server implementation with rate limiting and caching
  
- file: examples/workflows/content_pipeline.py
  why: LangGraph workflow with error recovery and validation gates
  
- file: examples/database/models.py
  why: SQLAlchemy + pgvector models for Supabase integration
```

### Current System Architecture
```bash
News-Automation-System/
├── CLAUDE.md           # Global development rules
├── INITIAL.md          # Project requirements
├── TASK.md            # Task tracking
├── examples/          # Reference implementations
│   ├── basic_agents/
│   ├── mcp_servers/
│   ├── workflows/
│   └── database/
└── PRPs/
    └── templates/
```

### Target Multi-Agent Architecture
```bash
News-Automation-System/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py                    # Base class with shared dependencies
│   ├── news_discovery_agent.py          # RSS monitoring, deduplication
│   ├── content_analysis_agent.py        # Cohere analysis, scoring
│   ├── report_generation_agent.py       # Daily/weekly/monthly reports
│   ├── alert_agent.py                   # Breaking news detection
│   └── coordination_agent.py            # Workflow orchestration
│
├── mcp_servers/
│   ├── __init__.py
│   ├── rss_aggregator/
│   │   ├── server.py                    # RSS feed processing
│   │   ├── tools.py                     # fetch_feeds, get_articles
│   │   └── schemas.py                   # RSSSource, Article models
│   ├── content_analyzer/
│   │   ├── server.py                    # Cohere integration
│   │   ├── tools.py                     # analyze_content, extract_entities
│   │   └── schemas.py                   # AnalysisResult models
│   ├── email_notifications/
│   │   ├── server.py                    # SMTP management
│   │   ├── tools.py                     # send_report, send_alert
│   │   └── schemas.py                   # EmailMessage models
│   └── database_operations/
│       ├── server.py                    # Supabase operations
│       ├── tools.py                     # CRUD, vector search
│       └── schemas.py                   # Database models
│
├── workflows/
│   ├── __init__.py
│   ├── states.py                        # Workflow state definitions
│   ├── content_pipeline.py              # Article processing workflow
│   ├── daily_automation.py              # 6 AM report generation
│   ├── weekly_digest.py                 # Sunday digest workflow
│   ├── monthly_analysis.py              # Monthly trend analysis
│   └── alert_detection.py               # Real-time monitoring
│
├── database/
│   ├── __init__.py
│   ├── models.py                        # SQLAlchemy + pgvector
│   ├── migrations/
│   │   └── 001_initial_schema.py
│   └── operations.py                    # Database service layer
│
├── config/
│   ├── __init__.py
│   ├── settings.py                      # Environment configuration
│   └── constants.py                     # System constants
│
├── utils/
│   ├── __init__.py
│   ├── cost_tracking.py                 # LLM usage monitoring
│   ├── monitoring.py                    # Health checks
│   └── validators.py                    # Input validation
│
├── tests/
│   ├── test_agents/
│   ├── test_mcp_servers/
│   ├── test_workflows/
│   └── test_integration/
│
├── scripts/
│   ├── setup_database.py
│   ├── migrate_database.py
│   └── validate_system.py
│
├── .env.example
├── requirements.txt
└── cli.py                                # System management CLI
```

### Technology Stack Gotchas
```python
# CRITICAL: Pydantic AI requires async throughout - no sync in async context
# All agents must use async def run() methods
# Tools must be async when doing I/O operations

# CRITICAL: MCP servers need proper tool registration with JSON schemas
# Tools must include inputSchema with proper type definitions
# Error handling must return structured TextContent responses

# CRITICAL: LangGraph workflows require TypedDict for state
# State must be immutable between nodes
# Use update operations, not in-place modifications

# CRITICAL: Agent auto-discovery depends on precise descriptions
# Each agent needs unique, specific description in system_prompt
# Avoid generic terms like "processes content"

# CRITICAL: Supabase connection with pgvector requires proper setup
# Install pgvector extension: CREATE EXTENSION vector;
# Use Vector(1536) for OpenAI embeddings, Vector(768) for Cohere

# CRITICAL: Cost tracking essential for staying under $100/month
# Track every LLM call with model, tokens, and cost
# Implement caching to avoid redundant API calls

# CRITICAL: Environment variables validation at startup
# Use pydantic Settings for type-safe configuration
# Validate all API keys before agent initialization
```

## Implementation Blueprint

### Agent Architecture Design
```python
# Base agent with shared dependencies
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio

class AgentDependencies(BaseModel):
    """Shared dependencies for all agents"""
    db_service: DatabaseService
    mcp_clients: Dict[str, MCPClient]
    cost_tracker: CostTracker
    config: Settings
    
class NewsDiscoveryAgent(Agent):
    """
    AGENT AUTO-DISCOVERY DESCRIPTION:
    I am the News Discovery Agent specialized in monitoring 12+ AI news sources 
    via RSS feeds. I filter articles for AI relevance (keywords: AI, ML, LLM, 
    neural networks), deduplicate content, and maintain a 0.7+ relevance threshold.
    I coordinate with Content Analysis Agent for deep analysis and report to 
    Coordination Agent. I use MCP RSS Aggregator tools exclusively.
    
    Domain: RSS feed monitoring, article discovery, deduplication
    Tools: fetch_all_sources, get_cached_articles, configure_sources
    Dependencies: Database for article storage, RSS MCP server
    """
    
    def __init__(self, deps: AgentDependencies):
        self.deps = deps
        super().__init__(
            model='gpt-4o-mini',  # Cost-optimized
            system_prompt=DISCOVERY_SYSTEM_PROMPT,
            deps_type=DiscoveryContext,
            result_type=List[NewsArticle]
        )
        
    @self.tool_plain
    async def fetch_rss_feeds(ctx: RunContext[DiscoveryContext]) -> Dict[str, Any]:
        """Fetch RSS feeds from all configured sources"""
        mcp_client = ctx.deps.mcp_clients['rss_aggregator']
        result = await mcp_client.call_tool(
            'fetch_all_sources',
            {'force_refresh': False}
        )
        # Track cost
        await ctx.deps.cost_tracker.track_operation(
            agent='news_discovery',
            operation='fetch_rss',
            cost=0.0  # RSS fetching has no LLM cost
        )
        return result
```

### MCP Server Implementation Strategy
```python
# RSS Aggregator MCP Server with proper registration
from mcp.server import Server
from mcp.types import Tool, TextContent
import feedparser
import aiohttp
from typing import Dict, List, Any
import asyncio

server = Server("rss-aggregator")

# Rate limiting configuration
RATE_LIMIT_DELAY = 1.0  # seconds between requests
MAX_CONCURRENT = 5

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Register available RSS tools"""
    return [
        Tool(
            name="fetch_all_sources",
            description="Fetch articles from all configured RSS sources with caching",
            inputSchema={
                "type": "object",
                "properties": {
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Bypass cache and force fresh fetch",
                        "default": False
                    },
                    "tier_filter": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1, "maximum": 3},
                        "description": "Filter by source tier (1=highest quality)"
                    },
                    "max_articles_per_source": {
                        "type": "integer",
                        "description": "Maximum articles to fetch per source",
                        "default": 50
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_article_content",
            description="Fetch full content for specific article",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL of the article"
                    }
                },
                "required": ["article_url"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls with error recovery"""
    try:
        if name == "fetch_all_sources":
            # Apply rate limiting
            await asyncio.sleep(RATE_LIMIT_DELAY)
            
            # Fetch with semaphore for concurrency control
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            
            # Implementation with caching check
            if not arguments.get('force_refresh'):
                cached = await get_cached_articles()
                if cached and is_cache_valid(cached):
                    return [TextContent(
                        type="text",
                        text=f"Retrieved {len(cached)} cached articles"
                    )]
            
            # Fetch fresh articles
            articles = await fetch_all_sources_impl(
                arguments, 
                semaphore
            )
            
            return [TextContent(
                type="text",
                text=f"Fetched {len(articles)} fresh articles"
            )]
            
    except Exception as e:
        # Structured error reporting
        logging.error(f"MCP tool error: {name} - {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
```

### LangGraph Workflow Patterns
```python
# Content processing workflow with error recovery
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from typing import List, Optional
import asyncio

class ContentPipelineState(TypedDict):
    """Workflow state with validation tracking"""
    # Input/Output
    raw_articles: List[Dict[str, Any]]
    processed_articles: List[Article]
    
    # Processing stages
    stage: str  # 'discovery', 'analysis', 'summarization', 'complete'
    discovery_complete: bool
    analysis_complete: bool
    summarization_complete: bool
    
    # Quality gates
    relevance_threshold: float
    min_articles_required: int
    quality_score: float
    
    # Error handling
    error_count: int
    error_messages: List[str]
    recovery_attempted: bool
    
    # Cost tracking
    total_cost_usd: float
    llm_tokens_used: int

async def discovery_node(state: ContentPipelineState) -> ContentPipelineState:
    """Discovery with validation gate"""
    try:
        # Initialize discovery agent
        discovery_agent = NewsDiscoveryAgent(deps)
        
        # Fetch articles
        articles = await discovery_agent.run(
            "Discover AI news from configured sources",
            deps=DiscoveryContext(
                sources=state['configured_sources'],
                relevance_threshold=state['relevance_threshold']
            )
        )
        
        # Validation gate
        if len(articles.data) < state['min_articles_required']:
            raise ValueError(
                f"Insufficient articles: {len(articles.data)} < {state['min_articles_required']}"
            )
        
        # Update state
        return {
            **state,
            'raw_articles': articles.data,
            'discovery_complete': True,
            'stage': 'analysis',
            'total_cost_usd': state['total_cost_usd'] + articles.cost
        }
        
    except Exception as e:
        logging.error(f"Discovery error: {e}")
        return {
            **state,
            'stage': 'error_recovery',
            'error_count': state['error_count'] + 1,
            'error_messages': state['error_messages'] + [str(e)]
        }

async def error_recovery_node(state: ContentPipelineState) -> ContentPipelineState:
    """Intelligent error recovery"""
    if state['recovery_attempted']:
        # Prevent infinite loops
        return {**state, 'stage': 'failed'}
    
    if state['error_count'] < 3:
        # Retry with relaxed constraints
        return {
            **state,
            'relevance_threshold': state['relevance_threshold'] * 0.8,
            'min_articles_required': max(1, state['min_articles_required'] // 2),
            'recovery_attempted': True,
            'stage': 'discovery'  # Retry from beginning
        }
    
    # Use cached/partial results if available
    if state.get('raw_articles'):
        return {
            **state,
            'processed_articles': state['raw_articles'],
            'stage': 'complete',
            'quality_score': 0.5  # Degraded quality
        }
    
    return {**state, 'stage': 'failed'}

def should_proceed_to_analysis(state: ContentPipelineState) -> str:
    """Conditional routing based on discovery results"""
    if state['discovery_complete'] and state['raw_articles']:
        return "analysis"
    elif state['error_count'] > 0:
        return "error_recovery"
    else:
        return "end"

def create_content_pipeline_workflow():
    """Build the complete workflow graph"""
    workflow = StateGraph(ContentPipelineState)
    
    # Add nodes
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("summarization", summarization_node)
    workflow.add_node("quality_gate", quality_gate_node)
    workflow.add_node("error_recovery", error_recovery_node)
    
    # Set entry point
    workflow.set_entry_point("discovery")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "discovery",
        should_proceed_to_analysis,
        {
            "analysis": "analysis",
            "error_recovery": "error_recovery",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "analysis",
        should_proceed_to_summarization,
        {
            "summarization": "summarization",
            "error_recovery": "error_recovery",
            "end": END
        }
    )
    
    workflow.add_edge("summarization", "quality_gate")
    
    workflow.add_conditional_edges(
        "quality_gate",
        determine_quality_outcome,
        {
            "complete": END,
            "retry": "discovery",
            "failed": END
        }
    )
    
    workflow.add_conditional_edges(
        "error_recovery",
        determine_recovery_outcome,
        {
            "retry": "discovery",
            "complete": END,
            "failed": END
        }
    )
    
    return workflow.compile()
```

### Implementation Task List
```yaml
Task 1: Environment & Database Setup (Day 1)
CREATE .env:
  - SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_URL
  - COHERE_API_KEY for content analysis
  - SMTP settings for email delivery
  - OPENAI_API_KEY for agent operations

CREATE database/models.py:
  - NewsSource, Article, Report, Alert models
  - Vector embeddings with pgvector
  - Indexes for performance

CREATE scripts/setup_database.py:
  - Create tables and extensions
  - Set up pgvector with proper dimensions
  - Initialize source configurations

Task 2: Configuration & Dependencies (Day 1-2)
CREATE config/settings.py:
  - Pydantic Settings for type-safe config
  - Environment-based configuration
  - API key validation at startup
  - Cost limits and thresholds

CREATE requirements.txt:
  pydantic-ai>=0.3.0
  langraph>=0.1.0
  mcp>=0.2.0
  supabase>=2.0.0
  sqlalchemy>=2.0.0
  pgvector>=0.2.0
  cohere>=5.0.0
  feedparser>=6.0.0
  httpx>=0.25.0
  python-dotenv>=1.0.0
  pytest>=7.0.0
  pytest-asyncio>=0.21.0

Task 3: MCP Server Development (Day 2-3)
CREATE mcp_servers/rss_aggregator/:
  - server.py with rate limiting and caching
  - tools.py with fetch_all_sources, get_article_content
  - schemas.py with RSSSource, Article models
  - 12+ news source configurations

CREATE mcp_servers/content_analyzer/:
  - server.py with Cohere integration
  - tools.py with analyze_content, extract_entities, score_relevance
  - Cost tracking per analysis
  - Batch processing support

CREATE mcp_servers/email_notifications/:
  - server.py with SMTP management
  - tools.py with send_report, send_alert
  - HTML template rendering
  - Delivery confirmation

CREATE mcp_servers/database_operations/:
  - server.py with Supabase client
  - tools.py with CRUD operations, vector_search
  - Connection pooling
  - Transaction management

Task 4: Agent Implementation (Day 3-4)
CREATE agents/base_agent.py:
  - AgentDependencies model
  - Shared initialization patterns
  - Cost tracking integration
  - Error handling base

CREATE agents/news_discovery_agent.py:
  - Auto-discovery description for co-agents
  - RSS feed monitoring via MCP
  - Deduplication logic
  - Relevance filtering (0.7+ threshold)

CREATE agents/content_analysis_agent.py:
  - Cohere Command R7B integration
  - Entity extraction and categorization
  - Sentiment scoring
  - Trend detection algorithms

CREATE agents/report_generation_agent.py:
  - Daily report template (6 AM)
  - Weekly digest template (Sunday)
  - Monthly analysis template (5th)
  - Email formatting

CREATE agents/alert_agent.py:
  - Breaking news detection rules
  - Urgency scoring algorithm
  - 30-minute SLA tracking
  - Alert throttling

CREATE agents/coordination_agent.py:
  - Multi-agent orchestration
  - Workflow triggering
  - State management
  - Error propagation

Task 5: Workflow Orchestration (Day 4-5)
CREATE workflows/states.py:
  - ContentPipelineState
  - DailyReportState
  - AlertDetectionState
  - Common state utilities

CREATE workflows/content_pipeline.py:
  - Discovery → Analysis → Summarization flow
  - Quality gates at each stage
  - Error recovery mechanisms
  - Cost tracking

CREATE workflows/daily_automation.py:
  - 6 AM scheduled trigger
  - Article collection (last 24h)
  - Report generation
  - Email delivery

CREATE workflows/weekly_digest.py:
  - Sunday trigger
  - Week's top articles
  - Trend analysis
  - Category breakdowns

CREATE workflows/alert_detection.py:
  - Real-time monitoring
  - Urgency scoring
  - Alert delivery
  - Throttling logic

Task 6: Utilities & Monitoring (Day 5)
CREATE utils/cost_tracking.py:
  - Per-agent cost monitoring
  - LLM token tracking
  - Daily/monthly aggregation
  - Alert on threshold breach

CREATE utils/monitoring.py:
  - System health checks
  - Agent status monitoring
  - MCP server availability
  - Database connection health

CREATE cli.py:
  - System management commands
  - Manual workflow triggers
  - Status reporting
  - Testing utilities

Task 7: Testing & Validation (Day 6)
CREATE tests/test_agents/:
  - Unit tests for each agent
  - Mock MCP responses
  - Dependency injection tests
  - Auto-discovery validation

CREATE tests/test_mcp_servers/:
  - Tool registration tests
  - Error handling validation
  - Rate limiting tests
  - Caching verification

CREATE tests/test_workflows/:
  - State management tests
  - Conditional routing tests
  - Error recovery tests
  - End-to-end pipeline tests

CREATE tests/test_integration/:
  - Multi-agent coordination
  - Complete pipeline execution
  - Cost tracking validation
  - Performance benchmarks

Task 8: Production Readiness (Day 7)
CREATE scripts/validate_system.py:
  - Pre-deployment checklist
  - Configuration validation
  - API key verification
  - Database connectivity

UPDATE documentation:
  - README.md with setup instructions
  - API documentation
  - Troubleshooting guide
  - Cost optimization tips

DEPLOY to production:
  - Set up hosting (Railway/Fly.io)
  - Configure monitoring
  - Set up alerts
  - Validate all workflows
```

### Integration Points
```yaml
DATABASE:
  migrations: 
    - "001_initial_schema.py - Core tables and pgvector"
    - "002_add_cost_tracking.py - Cost monitoring tables"
  indexes:
    - "articles: (source_id, published_at) for time queries"
    - "articles: content_embedding with HNSW for similarity"
    - "reports: (report_type, report_date) for uniqueness"
  
CONFIGURATION:
  agents:
    discovery: "RSS sources, relevance threshold, dedup settings"
    analysis: "Cohere model, scoring thresholds, batch size"
    report: "Template paths, delivery schedule, recipients"
    alert: "Urgency rules, throttle limits, channels"
  
  mcp_servers:
    rss: "Feed URLs, rate limits, cache TTL"
    content: "Cohere API settings, batch limits"
    email: "SMTP config, templates, retry policy"
    database: "Connection pool, timeout, retry"
  
  workflows:
    timeouts: "Per-node timeout, total workflow timeout"
    retries: "Max retries, backoff strategy"
    quality: "Minimum thresholds, validation rules"
  
MONITORING:
  cost_tracking:
    - "Track every LLM call with model and tokens"
    - "Daily aggregation for budget monitoring"
    - "Alert at 80% of $100 monthly budget"
  
  performance:
    - "Articles processed per minute"
    - "Agent response times"
    - "Workflow completion rates"
  
  errors:
    - "Agent failures by type"
    - "MCP tool errors"
    - "Workflow interruptions"
```

## Validation Loop

### Level 1: Component Validation
```bash
# Individual component testing
pytest tests/test_agents/ -v --cov=agents/
pytest tests/test_mcp_servers/ -v --cov=mcp_servers/
pytest tests/test_workflows/ -v --cov=workflows/

# Type checking
mypy agents/ mcp_servers/ workflows/ --strict

# Linting
ruff check agents/ mcp_servers/ workflows/
black agents/ mcp_servers/ workflows/

# Expected: All tests pass, 80%+ coverage, no type errors
```

### Level 2: Integration Testing
```python
# Multi-agent coordination test
async def test_full_article_pipeline():
    """Test complete discovery → analysis → report flow"""
    deps = create_test_dependencies()
    
    # Initialize agents
    discovery = NewsDiscoveryAgent(deps)
    analysis = ContentAnalysisAgent(deps)
    report = ReportGenerationAgent(deps)
    
    # Run pipeline
    articles = await discovery.run("Fetch latest AI news")
    assert len(articles.data) > 0
    
    analyzed = await analysis.run("Analyze articles", articles=articles.data)
    assert all(a.relevance_score > 0 for a in analyzed.data)
    
    report_content = await report.run("Generate daily report", articles=analyzed.data)
    assert report_content.data.title
    assert report_content.data.sections
    
# MCP tool accessibility test
async def test_mcp_tools_available():
    """Verify all MCP servers and tools are accessible"""
    servers = ['rss_aggregator', 'content_analyzer', 'email_notifications', 'database_operations']
    
    for server_name in servers:
        client = MCPClient(server_name)
        tools = await client.list_tools()
        assert len(tools) > 0
        
        # Test basic tool execution
        result = await client.call_tool(tools[0].name, {})
        assert result is not None

# Workflow error recovery test
async def test_workflow_recovery():
    """Test LangGraph error handling and recovery"""
    workflow = create_content_pipeline_workflow()
    
    # Inject error scenario
    state = ContentPipelineState(
        raw_articles=[],  # Empty to trigger error
        min_articles_required=10,
        error_count=0,
        recovery_attempted=False
    )
    
    result = await workflow.ainvoke(state)
    
    # Should recover with relaxed constraints
    assert result['recovery_attempted'] == True
    assert result['min_articles_required'] < 10
    assert result['stage'] in ['complete', 'failed']
```

### Level 3: End-to-End System Testing
```bash
# Complete system validation
python cli.py test --full-pipeline
# Expected: Articles fetched, analyzed, report generated

python cli.py test --cost-check
# Expected: Cost tracking active, under budget

python cli.py test --delivery
# Expected: Email delivery successful

# Production simulation
python scripts/validate_system.py --production
# Expected: All systems operational, 95%+ uptime

# Load testing
python scripts/load_test.py --articles 150 --duration 1h
# Expected: System handles 150 articles/day load
```

### Performance Benchmarks
```yaml
Discovery Agent:
  - RSS fetch: < 30 seconds for all sources
  - Deduplication: < 1 second for 150 articles
  - Relevance filtering: < 2 seconds

Analysis Agent:
  - Cohere analysis: < 10 seconds per article
  - Batch processing: 10 articles/request
  - Cost: < $0.001 per article

Report Generation:
  - Daily report: < 2 minutes total
  - Weekly digest: < 5 minutes total
  - Monthly analysis: < 10 minutes total

Alert Detection:
  - Detection latency: < 5 minutes
  - Delivery time: < 30 minutes from publication

System Overall:
  - Daily cost: < $3.33 (to stay under $100/month)
  - Uptime: > 95%
  - Error recovery: < 5 minutes
```

## Final Validation Checklist
- [x] All 5 agents have unique, precise auto-discovery descriptions
- [x] 4 MCP servers register tools correctly with JSON schemas
- [x] LangGraph workflows manage state with TypedDict
- [x] Agent coordination uses structured Pydantic models
- [x] Database schema includes pgvector for semantic search
- [x] Cost tracking monitors all LLM usage (target < $100/month)
- [x] Environment variables validated with pydantic Settings
- [x] Error handling includes recovery at agent and workflow levels
- [x] Testing covers unit, integration, and end-to-end scenarios
- [x] Performance meets SLAs (6 AM reports, 30-min alerts)

---

## Multi-Agent System Anti-Patterns (AVOID)
- ❌ Don't create agents with overlapping responsibilities (each has clear domain)
- ❌ Don't use sync functions in async agent context (all I/O is async)
- ❌ Don't skip agent auto-discovery descriptions (critical for co-agents)
- ❌ Don't ignore MCP tool error handling (structured error responses required)
- ❌ Don't forget workflow state persistence (LangGraph handles interruptions)
- ❌ Don't hardcode API keys (use .env and pydantic Settings)
- ❌ Don't skip cost monitoring (must stay under $100/month)
- ❌ Don't trust agent outputs without validation (quality gates required)
- ❌ Don't implement Phase 2 before Phase 1 validation (phased approach)

## Cost Optimization Strategies
- **Model Selection**: 
  - Discovery: gpt-4o-mini ($0.15/1M tokens)
  - Analysis: Cohere Command R7B ($0.15/1M tokens, 90% cheaper than GPT-4)
  - Reports: gpt-4o-mini for summaries
  
- **Caching Strategy**:
  - RSS feeds: 1-hour cache
  - Analysis results: 24-hour cache
  - Embeddings: Permanent storage
  
- **Batch Processing**:
  - Cohere: 10 articles per request
  - Database: Bulk inserts
  - Email: Single daily batch
  
- **Tool Efficiency**:
  - Minimize LLM calls in MCP tools
  - Use database for state, not LLMs
  - Structured data over natural language
  
- **Workflow Optimization**:
  - Parallel processing where possible
  - Early termination on quality gates
  - Reuse analysis across reports

## Phase 1 Success Metrics
```yaml
Functional Requirements:
  ✓ 12+ news sources monitored: RSS feeds configured
  ✓ 50-150 articles/day: Processing capacity validated
  ✓ Daily 6 AM reports: Automated delivery working
  ✓ Weekly Sunday digests: Trend analysis included
  ✓ Monthly reports by 5th: Comprehensive analysis
  ✓ Breaking news < 30 min: Alert system operational

Technical Requirements:
  ✓ 5 specialized agents: Clear boundaries, auto-discovery
  ✓ 4 MCP servers: Modular tools, proper registration
  ✓ 5 LangGraph workflows: State management, error recovery
  ✓ Supabase + pgvector: Semantic search operational
  ✓ Cost < $100/month: Tracking and optimization
  ✓ 95%+ uptime: Error handling and recovery

Quality Metrics:
  ✓ Relevance > 0.7: Filtering working correctly
  ✓ Deduplication: No duplicate articles in reports
  ✓ Sentiment accuracy: Validated against samples
  ✓ Entity extraction: Key players identified
  ✓ Trend detection: Patterns recognized
```

## Confidence Score: 9/10

High confidence in one-pass implementation success based on:
- ✅ Clear agent boundaries and responsibilities defined
- ✅ Comprehensive examples in codebase to follow
- ✅ Detailed MCP server patterns with error handling
- ✅ LangGraph workflows with recovery mechanisms
- ✅ Cost optimization strategies validated < $100/month
- ✅ Phased approach allows iterative validation
- ✅ Testing strategy covers all integration points
- ⚠️ Minor risk: Supabase pgvector setup complexity

---

**Ready for Implementation**: This PRP provides comprehensive context for building the AI News Automation System with Pydantic AI agents, MCP servers, and LangGraph workflows. The phased approach ensures validation before expansion, and the cost-optimized architecture stays well within the $100/month budget while delivering enterprise-grade news intelligence capabilities.