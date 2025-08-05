# AI News Automation System

A comprehensive multi-agent AI system for automated news discovery, analysis, and content creation using Pydantic AI, MCP servers, LangGraph workflows, and Claude Code co-agents.

> **Context Engineering is 10x better than prompt engineering and 100x better than vibe coding.**

## 🚀 Quick Start

```bash
# 1. Clone this repository
git clone <repository-url>
cd ai-news-automation

# 2. Set up your environment
cp .env.example .env
# Edit .env with your API keys and configuration

# 3. Set up Supabase database
# Follow setup instructions in docs/SETUP.md

# 4. Install dependencies (venv already configured)
pip install -r requirements.txt

# 5. Start with Phase 1 - Local Intelligence
# In Claude Code, run:
/execute-prp PRPs/phase1-local-intelligence.md

# 6. Test the system
python cli.py
```

## 📚 Table of Contents

- [What is This System?](#what-is-this-system)
- [Project Structure](#project-structure)
- [Phased Development Approach](#phased-development-approach)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Phase Implementation](#phase-implementation)
- [Cost Optimization](#cost-optimization)
- [Best Practices](#best-practices)

## What is This System?

This AI news automation system represents a paradigm shift from manual content creation to fully automated, intelligent news processing and content generation. Built using context engineering principles and Claude Code co-agents, it evolves through three main phases:

### Phase 1: Local Intelligence System
- **Automated News Discovery**: Monitor 12+ free AI news sources
- **Intelligent Analysis**: Relevance scoring, trend detection, entity extraction
- **Structured Reporting**: Daily reports, weekly digests, monthly trend analysis
- **Real-Time Alerts**: Breaking news notifications to dedicated email

### Phase 2: Content Creation Engine  
- **YouTube Integration**: Automated script generation for long-form videos and Shorts
- **Multi-Format Content**: Platform-optimized content creation
- **Engagement Optimization**: SEO-friendly titles, thumbnails, and descriptions

### Phase 3: Multi-Platform Distribution
- **Social Media Automation**: Twitter, LinkedIn, Instagram content creation
- **Cross-Platform Consistency**: Unified brand voice with platform-specific optimization
- **Performance Analytics**: Comprehensive engagement tracking and optimization

### Why This Architecture Matters

1. **Modular Agent Design**: Each Pydantic AI agent specializes in specific domains
2. **Cost-Effective**: Direct API integration eliminates subscription costs
3. **Context Engineering**: Comprehensive upfront context prevents AI failures
4. **Scalable**: MCP servers enable easy capability expansion
5. **Validated**: Each phase must prove functional before progression

## Project Structure

```
ai-news-automation/
├── frontend/                        # Next.js Frontend (Phase 3+)
│   ├── src/app/                     # App Router pages and API routes
│   ├── src/components/              # React components
│   └── src/lib/                     # Frontend utilities and API clients
├── backend/                         # Python Backend API Service
│   ├── app/                         # FastAPI application
│   └── api/                         # REST API endpoints
├── agents/                          # Pydantic AI Agents
│   ├── news_discovery_agent.py     # RSS aggregation and source monitoring
│   ├── content_analysis_agent.py   # Relevance scoring and trend detection
│   ├── report_generation_agent.py  # Daily/weekly/monthly reports
│   ├── alert_agent.py              # Breaking news notifications
│   └── coordination_agent.py       # Workflow orchestration
├── mcp_servers/                     # MCP Server Implementations
│   ├── rss_aggregator/             # RSS feed processing server
│   ├── content_analyzer/           # AI-powered content analysis
│   ├── email_notifications/        # SMTP email server
│   └── database_operations/        # Supabase integration server
├── workflows/                       # LangGraph Workflow Definitions
│   ├── daily_processing.py         # Daily news processing workflow
│   ├── weekly_digest.py            # Weekly report generation
│   ├── breaking_news.py            # Real-time alert workflow
│   └── content_creation.py         # Multi-platform content generation
├── database/                        # Database Models and Operations
│   ├── models.py                   # Supabase table definitions
│   ├── migrations/                 # Database schema migrations
│   └── operations.py               # CRUD operations
├── utils/                          # Shared Utilities
│   ├── cost_tracking.py           # API usage and cost monitoring
│   ├── content_processing.py      # Text processing utilities
│   └── monitoring.py              # System health monitoring
├── config/                         # Configuration Management
│   ├── settings.py                 # Environment-based configuration
│   └── agents_config.py           # Agent-specific settings
├── .claude/                        # Claude Code Configuration
│   ├── commands/                   # Custom Claude Code commands
│   │   ├── generate-prp.md         # PRP generation from INITIAL.md
│   │   ├── execute-prp.md          # PRP implementation command
│   │   ├── setup-phase.md          # Phase initialization
│   │   └── run-workflow.md         # Workflow execution
│   └── settings.local.json         # Claude Code permissions
├── PRPs/                           # Product Requirements Prompts
│   ├── templates/                  # PRP base templates
│   │   └── ai-news-base.md         # AI news automation PRP template
│   └── generated/                  # Auto-generated PRPs from INITIAL.md
├── docs/                           # Project Documentation
│   ├── SETUP.md                    # Detailed setup instructions
│   ├── AGENTS.md                   # Agent architecture documentation
│   ├── WORKFLOWS.md                # LangGraph workflow documentation
│   └── API.md                      # API documentation
├── tests/                          # Test Suite
│   ├── test_agents/                # Agent testing
│   ├── test_workflows/             # Workflow testing
│   └── test_integration/           # Integration testing
├── CLAUDE.md                       # Global rules for AI assistant
├── PLANNING.md                     # Project architecture and constraints
├── TASK.md                         # Task tracking and completion
└── INITIAL.md                      # Feature requirements (this phase)
```

## Phased Development Approach

### Phase 1: Foundation (Current) - 2-3 weeks
**Objective**: Local intelligence system with comprehensive news monitoring

**Key Components**:
- News Discovery Agent with RSS aggregation
- Content Analysis Agent with relevance scoring
- Report Generation Agent for daily/weekly/monthly outputs
- Alert Agent for breaking news notifications
- Supabase integration for data storage

**Success Criteria**:
- [ ] Daily reports delivered at 6 AM
- [ ] Weekly digests every Sunday
- [ ] Monthly trend analysis by 5th of each month
- [ ] Breaking news alerts within 30 minutes
- [ ] Cost under $100/month

### Phase 2: Content Creation - 2-3 weeks after Phase 1
**Objective**: YouTube script generation and video content creation

**Key Components**:
- Script Generation Agent for long-form and short-form content
- Video Creation coordination
- YouTube API integration
- Content optimization for engagement

### Phase 3: Multi-Platform Distribution - 1-2 weeks per platform
**Objective**: Social media content creation and distribution

**Key Components**:
- Platform-specific content adaptation
- Direct API integration (Twitter, LinkedIn, Instagram)
- Cross-platform coordination
- Performance analytics

## Technology Stack

### Core Architecture
- **Backend**: Python with Pydantic AI multi-agent system
- **Workflow Engine**: LangGraph for complex state management
- **Tool Integration**: MCP servers for modular capabilities
- **Database**: Supabase PostgreSQL + pgvector for vector storage
- **Frontend**: Next.js with TypeScript (Phase 3+)
- **Development**: Claude Code with custom co-agents

### Agent Communication
- **Context Isolation**: Each agent operates independently
- **Auto-Discovery**: Agent descriptions enable automatic routing
- **Tool Access Control**: Agents receive only necessary MCP tools
- **Dependency Injection**: Shared resources through Pydantic AI patterns

### Cost Optimization
- **Direct API Integration**: No third-party subscription services
- **Efficient LLM Usage**: Cohere Command R7B for analysis, premium models for generation
- **Self-Hosted Infrastructure**: Railway.app/Fly.io free tiers
- **Smart Caching**: Reduce redundant API calls and processing

## Getting Started

### Prerequisites
- Python 3.9+ with venv configured
- Claude Code access
- Supabase account (free tier)
- API keys for content analysis (Cohere recommended)

### Installation

1. **Environment Setup**
   ```bash
   # Clone and navigate to project
   git clone <repository-url>
   cd ai-news-automation
   
   # Copy environment template
   cp .env.example .env
   ```

2. **Configure Environment Variables**
   ```bash
   # Edit .env with your credentials
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   COHERE_API_KEY=your_cohere_api_key
   SMTP_SERVER=your_smtp_server
   ALERT_EMAIL=your_alert_email@domain.com
   ```

3. **Database Setup**
   ```bash
   # Initialize Supabase tables
   python scripts/setup_database.py
   
   # Run initial migrations
   python scripts/migrate_database.py
   ```

4. **Claude Code Setup**
   ```bash
   # Ensure .claude/commands/ directory exists with required commands
   # generate-prp.md should be included for PRP generation
   # execute-prp.md should be included for PRP implementation
   
   # Test Claude Code command availability
   # In Claude Code:
   /generate-prp --help
   ```

### First Run

```bash
# Start the coordination agent for testing
python cli.py

# In Claude Code, generate the comprehensive PRP blueprint
/generate-prp INITIAL.md

# Review and validate the generated PRP in PRPs/ folder
# Edit if needed, then execute the implementation
/execute-prp PRPs/ai-news-automation-phase1.md
```

**Important**: The PRP generation step creates a comprehensive implementation blueprint by combining:
- Your INITIAL.md requirements
- CLAUDE.md global rules  
- Examples from examples/ folder
- Documentation research
- PRP templates from PRPs/templates/

Always validate the generated PRP before executing to ensure it matches your requirements.

## Phase Implementation

### Phase 1 Implementation Steps

**Step 0: PRP Generation and Validation**
```bash
# Generate comprehensive implementation blueprint
/generate-prp INITIAL.md

# Review generated PRP in PRPs/generated/ folder
# Validate requirements, architecture, and implementation plan
# Edit PRP if needed before execution
```

1. **Week 1: Core Infrastructure**
   - Set up Supabase database with content schemas
   - Implement News Discovery Agent with RSS processing
   - Create Content Analysis Agent with Cohere integration
   - Basic content storage and retrieval workflows

2. **Week 2: Intelligence and Reporting**
   - Implement trend detection algorithms
   - Build Report Generation Agent with email templates
   - Create breaking news detection and alert system
   - Set up LangGraph workflows for daily processing

3. **Week 3: Testing and Optimization**
   - End-to-end testing of report generation
   - Optimize content analysis for cost and accuracy
   - Fine-tune breaking news detection criteria
   - Performance monitoring and cost tracking

### Validation Gates

Each phase includes automated validation:
- **Unit Tests**: All agent functions and MCP tools
- **Integration Tests**: Workflow execution and data flow
- **Cost Validation**: Monthly expense tracking under thresholds
- **Performance Tests**: Response times and system reliability

## Cost Optimization

### Phase 1 Target Costs
- **Supabase**: $0/month (free tier)
- **Cohere API**: $25-40/month (content analysis)
- **Hosting**: $0-30/month (free tier services)
- **Email**: $0-10/month (basic SMTP)
- **Total**: Under $100/month

### Cost Monitoring
- Real-time API usage tracking
- Daily cost reports with projections
- Automated alerts for budget thresholds
- Monthly optimization reviews

## Best Practices

### Context Engineering Workflow
- **PRP Generation First**: Always generate PRP from INITIAL.md before implementation
- **Validation Required**: Review and validate generated PRPs before execution  
- **Iterative Refinement**: Edit PRPs based on implementation learnings
- **Documentation Integration**: Include comprehensive documentation references in PRPs

### Agent Development
- Comprehensive agent descriptions for auto-discovery
- Detailed system prompts with domain expertise
- Structured data models for inter-agent communication
- Validation checkpoints at every workflow stage

### Agent Development
- Single responsibility per agent
- Clear dependency injection patterns
- Comprehensive error handling and recovery
- Detailed logging for debugging and monitoring

### Workflow Management
- State persistence for long-running processes
- Error recovery and alternative pathways
- Resource cleanup and proper shutdown
- Performance monitoring at each node

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase Documentation](https://supabase.com/docs)
- [Context Engineering Best Practices](https://github.com/coleam00/Context-Engineering-Intro)

## Contributing

This project follows context engineering principles. Before contributing:

1. Read `CLAUDE.md` for development guidelines
2. Check `TASK.md` for current priorities
3. Review `PLANNING.md` for architecture constraints
4. Ensure phase validation before expansion

## License

[Your License Here]