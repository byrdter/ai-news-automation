# AI News Automation System - Architecture & Planning

## 🎯 Project Overview

The AI News Automation System is a multi-agent, context-engineered platform designed to automate news discovery, analysis, and distribution. Built with Pydantic AI, MCP servers, and LangGraph workflows, it provides intelligent content curation and reporting while maintaining strict cost optimization.

## 🏗️ Architecture Overview

### Core Technologies
- **Agent Framework**: Pydantic AI for multi-agent coordination
- **Tool Integration**: MCP (Model Context Protocol) servers
- **Workflow Engine**: LangGraph for complex state management  
- **Database**: Supabase PostgreSQL with pgvector for semantic search
- **LLM Provider**: Cohere Command R7B (cost-optimized)
- **Deployment**: Railway/Fly.io with automated CI/CD

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordination Agent                        │
│              (Orchestrates all other agents)                 │
└─────────────────────────────────────────────────────────────┘
                              │
      ┌───────────────────────┴───────────────────────┐
      │                                               │
┌─────▼──────┐  ┌──────────────┐  ┌─────────────┐  ┌▼──────────┐
│  Discovery │  │   Analysis   │  │  Generation │  │   Alert   │
│   Agent    │──►    Agent     │──►    Agent    │  │   Agent   │
└─────┬──────┘  └──────┬───────┘  └──────┬──────┘  └─────┬─────┘
      │                │                  │                │
┌─────▼──────┐  ┌──────▼───────┐  ┌──────▼──────┐  ┌─────▼─────┐
│    RSS     │  │   Content    │  │    Email    │  │  Breaking │
│ Aggregator │  │   Analyzer   │  │ Notifier   │  │   News    │
│ MCP Server │  │  MCP Server  │  │ MCP Server │  │MCP Server │
└────────────┘  └──────────────┘  └─────────────┘  └───────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Supabase DB     │
                    │  (PostgreSQL +    │
                    │     pgvector)     │
                    └───────────────────┘
```

## 🤖 Agent Design Patterns

### Agent Structure
Each agent follows a consistent structure:
```
agents/
├── <agent_name>/
│   ├── agent.py       # Core agent logic & system prompts
│   ├── tools.py       # MCP tool integrations
│   ├── models.py      # Pydantic data models
│   └── workflows.py   # LangGraph workflow definitions
```

### Agent Communication Protocol
- **Structured Data**: All inter-agent communication uses Pydantic models
- **Event-Driven**: Agents emit and respond to typed events
- **State Isolation**: Each agent maintains its own state context
- **Error Propagation**: Failures cascade with detailed context

## 🔄 Development Phases

### Phase 1: Local Intelligence System (Current)
**Goal**: Automated news curation and daily reporting
- RSS aggregation from 12+ sources
- Content analysis and categorization
- Daily, weekly, and monthly reports
- Breaking news alerts
- Target: <$100/month operational cost

### Phase 2: YouTube Content Generation (Future)
**Goal**: Automated video script creation
- Long-form and short-form scripts
- SEO optimization
- Thumbnail generation
- Publishing automation

### Phase 3: Social Media Distribution (Future)
**Goal**: Multi-platform content distribution
- Platform-specific content adaptation
- Direct API integration
- Cross-platform analytics

## 📁 Project Structure

```
News-Automation-System/
├── agents/                    # Pydantic AI agents
│   ├── news_discovery/       # RSS feed aggregation
│   ├── content_analysis/     # Article analysis
│   ├── report_generation/    # Report creation
│   ├── alert/                # Breaking news detection
│   └── coordination/         # Multi-agent orchestration
├── mcp_servers/              # MCP tool servers
│   ├── rss_aggregator.py     # RSS feed processing
│   ├── content_analyzer.py   # Text analysis tools
│   ├── email_notifications.py # Email delivery
│   └── breaking_news.py      # Real-time alerts
├── workflows/                # LangGraph workflows
│   ├── content_pipeline.py   # Processing pipeline
│   ├── daily_automation.py   # Scheduled tasks
│   └── alert_workflow.py     # Alert processing
├── database/                 # Database layer
│   ├── models.py            # SQLModel definitions
│   ├── operations.py        # CRUD operations
│   └── migrations/          # Schema migrations
├── config/                  # Configuration
│   ├── settings.py          # Environment settings
│   ├── sources.json         # RSS feed sources
│   └── prompts.yaml         # Agent prompts
├── utils/                   # Shared utilities
│   ├── cost_tracking.py     # API cost monitoring
│   ├── monitoring.py        # System health
│   └── validators.py        # Data validation
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
├── scripts/                # Utility scripts
│   ├── setup_database.py   # DB initialization
│   └── migrate_database.py # Schema migrations
├── cli.py                  # CLI interface
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── CLAUDE.md              # AI assistant instructions
├── PLANNING.md            # This file
└── TASK.md               # Task tracking

```

## 🧪 Testing Strategy

### Test Coverage Requirements
- **Unit Tests**: 80%+ coverage for all business logic
- **Integration Tests**: Agent communication and MCP tools
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Load and stress testing
- **Cost Tests**: API usage optimization validation

### Test Structure
```python
tests/
├── unit/
│   ├── test_agents/         # Agent logic tests
│   ├── test_mcp_servers/    # Tool tests
│   └── test_utils/          # Utility tests
├── integration/
│   ├── test_workflows/      # Workflow tests
│   └── test_database/       # DB integration
└── e2e/
    └── test_pipeline.py     # Full pipeline test
```

## 💰 Cost Optimization Strategy

### API Usage Optimization
- **Batch Processing**: Group API calls where possible
- **Intelligent Caching**: Cache analysis results for 24 hours
- **Model Selection**: Use smallest viable model for each task
- **Rate Limiting**: Prevent accidental cost overruns

### Cost Targets (Phase 1)
- RSS Processing: $0 (direct HTTP)
- Content Analysis: <$50/month (Cohere)
- Email Delivery: $0 (Gmail SMTP)
- Database: $0 (Supabase free tier)
- Hosting: <$20/month (Railway)
- **Total Target**: <$100/month

## 🔒 Security Considerations

### Credential Management
- All secrets in environment variables
- Never commit credentials to repository
- Use `.env` files for local development
- Production secrets in deployment platform

### Data Security
- Input validation on all external data
- SQL injection prevention via ORMs
- Rate limiting on all endpoints
- Audit logging for all operations

## 📊 Monitoring & Observability

### Key Metrics
- **Performance**: Processing time per article
- **Reliability**: System uptime percentage
- **Quality**: Report accuracy score
- **Cost**: Real-time API usage tracking
- **Volume**: Articles processed per day

### Alerting Thresholds
- Cost exceeds daily budget
- Processing queue backlog >1000
- Error rate >5% in 5 minutes
- No articles processed in 1 hour

## 🚀 Deployment Strategy

### Environment Progression
1. **Development**: Local with test data
2. **Staging**: Cloud with sample feeds
3. **Production**: Full automation with monitoring

### CI/CD Pipeline
- Automated testing on all commits
- Staging deployment on main branch
- Manual promotion to production
- Rollback capability within 5 minutes

## 📝 Development Guidelines

### Code Style
- Python 3.11+ with type hints
- PEP8 compliance via black formatter
- Google-style docstrings
- Async/await for I/O operations

### Commit Convention
```
type(scope): description

- feat: New feature
- fix: Bug fix
- docs: Documentation
- test: Testing
- refactor: Code restructuring
- perf: Performance improvement
```

### Pull Request Template
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Cost impact assessed
- [ ] Security review complete

## 🎯 Success Metrics

### Phase 1 Completion Criteria
- ✅ Daily reports at 6 AM automatically
- ✅ Weekly digests with trend analysis
- ✅ Monthly comprehensive reports
- ✅ Breaking news within 30 minutes
- ✅ <$100/month operational cost
- ✅ 95%+ system uptime

### Quality Benchmarks
- Report relevance: >90% accuracy
- Processing speed: <30s per article
- Email delivery: 99%+ success rate
- Alert latency: <5 minutes

## 🔄 Iteration Strategy

### Weekly Sprints
- Monday: Sprint planning & task assignment
- Tuesday-Thursday: Development & testing
- Friday: Integration & deployment
- Weekend: Monitoring & optimization

### Feedback Loops
- Daily system health checks
- Weekly cost analysis
- Bi-weekly user feedback review
- Monthly architecture review

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-07  
**Next Review**: End of Phase 1