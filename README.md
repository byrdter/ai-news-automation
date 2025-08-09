# AI News Automation System

A modern web-based AI news automation platform featuring intelligent content discovery, analysis, and visualization through an intuitive dashboard interface.

> **Transforms CLI-based news intelligence into an accessible, professional web application.**

## 🌐 Live Dashboard

Access your AI-powered news intelligence through a modern, responsive web interface:

- **Real-time Metrics**: System performance, processing costs, and content quality scores
- **Article Browser**: 152+ analyzed articles with advanced search and filtering
- **Analytics Dashboard**: Interactive charts showing trends, costs, and source performance  
- **Report System**: 121+ generated reports with export capabilities
- **Mobile-Responsive**: Full functionality across all device sizes

## 🚀 Quick Start

```bash
# 1. Clone this repository
git clone <repository-url>
cd ai-news-automation

# 2. Start the web dashboard
cd frontend
npm install
npm run dev

# 3. Access the dashboard
open http://localhost:3000

# 4. View real data
# Dashboard connects to existing Supabase database
# 152+ articles and 121+ reports ready to explore

# 5. Backend processing (optional)
pip install -r requirements.txt
python daemon.py start
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

A modern web-based AI news automation platform that transforms raw news data into actionable intelligence through an intuitive dashboard interface. Built with Next.js, TypeScript, and Supabase, it provides instant access to comprehensive news analysis and reporting.

### 🎯 Core Features

#### Web Dashboard Interface
- **Modern UI**: Next.js 15 with shadcn/ui components and Tailwind CSS
- **Real-time Data**: Live metrics showing system performance and processing costs
- **Responsive Design**: Full mobile optimization with touch-friendly interface
- **Professional Charts**: Interactive visualizations using Recharts

#### Intelligence Processing
- **152+ Articles Analyzed**: AI-powered content analysis with relevance scoring
- **121+ Reports Generated**: Daily, weekly, and monthly intelligence briefings  
- **13 Active News Sources**: Tier 1-3 sources with 94.7% processing success rate
- **$0.565 Total Cost**: Efficient processing at $0.0037 per article

#### Advanced Search & Analytics
- **Dual Search Modes**: Text search and semantic search using AI embeddings
- **Advanced Filtering**: By source, category, relevance score, and date range
- **Performance Metrics**: Cost tracking, processing rates, and quality scores
- **Export Capabilities**: PDF and CSV export for all reports and data

### 🏗️ Technical Architecture

#### Frontend Stack
- **Next.js 15**: App Router with Server Components and TypeScript
- **React Query**: Data fetching, caching, and synchronization
- **Supabase Integration**: Real-time database with PostgreSQL + pgvector
- **Component System**: shadcn/ui with custom theming and accessibility

#### Backend Services
- **API Routes**: RESTful endpoints for articles, search, and analytics
- **Database Layer**: Comprehensive schema with relationships and indexing
- **Processing Pipeline**: Automated news discovery, analysis, and reporting
- **Cost Optimization**: Direct API integration with intelligent caching

### 🚀 Why This Platform?

1. **Immediate Value**: Access 152+ analyzed articles and 121+ reports instantly
2. **Professional Interface**: Transform CLI tools into accessible web applications  
3. **Real-time Intelligence**: Live metrics and performance monitoring
4. **Mobile-Ready**: Full functionality across all devices and screen sizes
5. **Cost-Effective**: $0.565 total processing cost with transparent tracking

## Project Structure

```
ai-news-automation/
├── frontend/                        # Next.js 15 Web Dashboard
│   ├── app/                         # App Router pages
│   │   ├── (dashboard)/             # Dashboard layout group
│   │   │   ├── page.tsx             # Main dashboard with metrics
│   │   │   ├── articles/            # Article browser and search
│   │   │   ├── reports/             # Generated reports and exports
│   │   │   ├── analytics/           # Charts and performance metrics
│   │   │   ├── sources/             # News source management
│   │   │   └── settings/            # System configuration
│   │   └── api/                     # Next.js API routes
│   │       ├── articles/            # Article API endpoints
│   │       ├── analytics/           # Metrics and performance data
│   │       └── search/              # Search functionality
│   ├── components/                  # React Components
│   │   ├── ui/                      # shadcn/ui base components
│   │   ├── layout/                  # Navigation and layout components
│   │   ├── dashboard/               # Dashboard-specific components
│   │   ├── articles/                # Article display and interaction
│   │   └── analytics/               # Chart and visualization components
│   ├── lib/                         # Frontend utilities
│   │   ├── supabase.ts             # Database client configuration
│   │   ├── utils.ts                # Shared utility functions
│   │   └── types.ts                # TypeScript type definitions
│   └── types/                       # Database and API types
│       └── database.ts             # Complete database schema types
├── database/                        # Database Schema and Operations
│   ├── models.py                   # Supabase table definitions (595 lines)
│   ├── migrations/                 # Database schema migrations
│   └── operations.py               # CRUD operations and queries
├── agents/                          # Pydantic AI Processing Agents
│   ├── news_discovery_agent.py     # RSS feed monitoring and fetching
│   ├── content_analysis_agent.py   # AI-powered relevance scoring
│   ├── report_generation_agent.py  # Automated report creation
│   └── coordination_agent.py       # Multi-agent workflow orchestration
├── mcp_servers/                     # MCP Tool Server Implementations
│   ├── rss_aggregator/             # RSS feed processing and validation
│   ├── content_analyzer/           # AI analysis and scoring
│   └── database_operations/        # Supabase integration tools
├── workflows/                       # LangGraph Processing Workflows
│   ├── daily_processing.py         # Daily news aggregation and analysis
│   ├── weekly_digest.py            # Weekly report generation
│   └── content_creation.py         # Multi-format content generation
├── utils/                          # Shared Processing Utilities
│   ├── cost_tracking.py           # API usage and cost monitoring
│   ├── content_processing.py      # Text analysis and processing
│   └── database_helpers.py        # Database operation utilities
├── config/                         # System Configuration
│   ├── settings.py                 # Environment-based settings
│   └── supabase_config.py         # Database connection configuration
├── scripts/                        # Automation and Setup Scripts
│   ├── setup_database.py          # Database initialization
│   ├── import_articles.py         # Data import utilities
│   └── generate_reports.py        # Report generation scripts
├── data/                           # Processed Data and Exports
│   ├── articles/                   # Processed article cache
│   └── reports/                    # Generated report files
├── reports/                        # System Generated Reports
│   ├── daily/                      # Daily intelligence briefings
│   ├── weekly/                     # Weekly trend analysis
│   └── monthly/                    # Monthly comprehensive reports
├── daemon.py                       # Background processing daemon
├── cli.py                          # Command-line interface
├── requirements.txt                # Python dependencies
├── CLAUDE.md                       # AI development guidelines
├── PLANNING.md                     # System architecture documentation
└── README.md                       # Project overview and setup
```

## System Status

### 🎉 Current Implementation - Production Ready
**Objective**: Modern web dashboard for AI news intelligence

**✅ Completed Components**:
- **Web Dashboard**: Next.js 15 with responsive design and mobile optimization
- **Real-time Metrics**: 8 key performance indicators with live data updates
- **Article Browser**: 152+ articles with infinite scroll, search, and filtering
- **Analytics Dashboard**: Interactive charts showing costs, trends, and performance
- **API Integration**: Complete REST API with Supabase database connectivity
- **Search System**: Dual-mode text and semantic search functionality

**📊 Live Metrics** (as of latest data):
- ✅ **152 Articles** analyzed with AI-powered relevance scoring
- ✅ **121 Reports** generated across daily, weekly, monthly formats  
- ✅ **$0.565 Total Cost** achieving $0.0037 per article efficiency
- ✅ **13 Active Sources** with 94.7% processing success rate
- ✅ **83.2% Average Quality** content relevance scoring

### 🚀 Deployment Options

#### Option 1: Local Development
```bash
cd frontend
npm install && npm run dev
# Access at http://localhost:3000
```

#### Option 2: Production Deployment
```bash
cd frontend
npm run build && npm start
# Ready for Vercel, Netlify, or any Node.js hosting
```

### 🔮 Future Enhancements

#### Phase 2A: Advanced Features (Next)
- **Real-time Updates**: Supabase subscriptions for live data
- **Enhanced Reports**: PDF/CSV export with custom formatting
- **Semantic Search**: Full pgvector integration for meaning-based search
- **User Authentication**: Multi-user support with role-based access

#### Phase 2B: Content Creation Engine
- **Report Automation**: Scheduled report generation and email delivery
- **Content Templates**: Customizable report formats and branding
- **API Expansion**: Extended endpoints for external integrations
- **Performance Optimization**: Advanced caching and query optimization

#### Phase 2C: Intelligence Platform
- **Custom Dashboards**: User-configurable metrics and visualizations
- **Advanced Analytics**: Trend prediction and anomaly detection
- **Integration APIs**: Webhook support for external systems
- **Enterprise Features**: Team collaboration and custom data sources

## Technology Stack

### 🌐 Frontend Architecture
- **Next.js 15**: App Router with Server Components and React 18
- **TypeScript**: Strict mode with comprehensive type coverage
- **UI Framework**: shadcn/ui components with Tailwind CSS theming
- **State Management**: TanStack Query for server state and caching
- **Charts**: Recharts for interactive data visualizations
- **Mobile-First**: Responsive design with touch-friendly interfaces

### 🗄️ Database & Backend
- **Supabase**: PostgreSQL with real-time subscriptions and Row Level Security  
- **pgvector**: Vector embeddings for semantic search capabilities
- **API Routes**: Next.js API endpoints with TypeScript validation
- **Data Processing**: Python agents for news analysis and report generation
- **Cost Tracking**: Comprehensive API usage monitoring and optimization

### 🔄 Processing Pipeline  
- **Multi-Agent System**: Specialized Pydantic AI agents for different tasks
- **MCP Servers**: Modular tool servers for RSS, analysis, and database operations
- **LangGraph Workflows**: State management for complex processing chains
- **Real-time Updates**: Supabase subscriptions for live data synchronization

### 📊 Performance Features
- **Caching Strategy**: React Query with stale-while-revalidate patterns
- **Code Splitting**: Lazy loading and dynamic imports for optimal bundles
- **Image Optimization**: Next.js automatic image optimization and resizing
- **Database Indexing**: Optimized queries with proper indexing and relationships

### 🚀 Deployment Stack
- **Hosting**: Vercel-optimized with automatic deployments and edge functions
- **CDN**: Global content delivery with automatic caching
- **SSL**: Automatic HTTPS with certificate management
- **Monitoring**: Built-in analytics and performance monitoring

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