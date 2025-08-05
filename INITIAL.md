# AI News Automation System - Phase 1: Local Intelligence

## FEATURE:

Build a comprehensive Pydantic AI multi-agent system for automated AI news discovery, analysis, and intelligent reporting. This system uses Claude Code co-agents principles with MCP servers, LangGraph workflows, and Supabase database integration.

**Phase 1 Scope (Local Intelligence System)**:
- **News Discovery Agent**: Aggregate content from 12+ free AI news sources using RSS feeds and basic APIs
- **Content Analysis Agent**: Perform relevance scoring, sentiment analysis, trend detection, and entity extraction using cost-effective LLMs (Cohere Command R7B)
- **Report Generation Agent**: Create structured daily reports (6 AM delivery), weekly digests (Sunday), and monthly trend analyses (5th of each month)
- **Alert Agent**: Monitor for breaking news with real-time email notifications to dedicated email address
- **Coordination Agent**: Orchestrate workflows between specialized agents using LangGraph state management

**Key Technical Requirements**:
- Each agent operates in isolated context to prevent pollution
- MCP servers provide modular tool access (RSS aggregation, email notifications, database operations, content analysis)
- Supabase PostgreSQL with pgvector for content storage and semantic search
- LangGraph workflows for complex multi-step processing with validation gates
- Agent auto-discovery through precise description writing
- Direct API integration to minimize recurring costs (no Buffer, Hootsuite, etc.)
- Cost target: Under $100/month for Phase 1 operations

**Content Sources (Tier 1 & 2 Free Sources)**:
- MIT AI News, Google AI Research, OpenAI Blog, Berkeley BAIR
- TechCrunch AI, VentureBeat AI, Stanford HAI, NVIDIA AI Blog
- MarkTechPost, Unite.AI, Analytics Vidhya, Axios AI
- Expected volume: 50-150 articles/day (1,500-4,500/month)

**Outputs**:
- Daily curated reports with key developments and analysis
- Weekly comprehensive digests with trend insights
- Monthly deep-dive trend analysis showing emerging patterns
- Real-time breaking news alerts (within 30 minutes of detection)

## EXAMPLES:

Use the examples in the `examples/` folder to understand best practices for multi-agent systems:

- `examples/agent/` - Study all files to understand Pydantic AI agent creation patterns, dependency injection, tool registration, and multi-provider support
- `examples/mcp_servers/` - Reference modular MCP server implementations for RSS aggregation, API integration, and database operations
- `examples/workflows/` - Examine LangGraph workflow patterns for state management, error recovery, and validation gates
- `examples/database/` - Review Supabase integration patterns, schema design, and vector storage implementation
- `examples/cli.py` - Template for agent coordination and user interaction patterns

Focus on the agent-as-tool pattern where specialized agents can invoke other agents as tools, similar to how the research agent delegates email tasks to an email agent in the examples.

Don't copy these examples directly as they are for a different project, but use them as inspiration for:
- Agent architecture and communication patterns
- MCP server tool registration and error handling
- LangGraph workflow design with conditional branching
- Database integration and vector storage patterns
- Cost optimization through efficient API usage

## DOCUMENTATION:

Reference these resources during development:

**Core Framework Documentation**:
- Pydantic AI: https://ai.pydantic.dev/ (focus on agents, tools, and dependencies)
- LangGraph: https://langchain-ai.github.io/langgraph/ (workflow management and state persistence)
- MCP Servers: https://modelcontextprotocol.io/docs (tool integration patterns)
- Supabase: https://supabase.com/docs (PostgreSQL, pgvector, real-time subscriptions)

**API Integration Documentation**:
- Cohere API: https://docs.cohere.com/ (for cost-effective content analysis)
- RSS Specification: https://www.rss-specifications.com/ (for feed parsing)
- SMTP Configuration: Email server setup and authentication patterns

**AI News Sources (for understanding content patterns)**:
- MIT AI News: https://news.mit.edu/topic/artificial-intelligence2
- Google AI Research: https://research.google/blog/
- OpenAI Blog: https://openai.com/blog/
- Berkeley BAIR: https://bair.berkeley.edu/blog/
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence/

**Context Engineering Resources**:
- Context Engineering Template: https://github.com/coleam00/Context-Engineering-Intro
- PRP Framework: For comprehensive context provision to AI assistants

## OTHER CONSIDERATIONS:

**Critical Implementation Requirements**:

- **Environment Variables**: Use python_dotenv and load_dotenv() for all configuration. Store API keys, database credentials, and email settings in .env file, never hardcode secrets.

- **Cost Optimization First**: Always use direct API integration. Never implement third-party services like Buffer, Hootsuite, or Blog2Social. Use Cohere Command R7B for content analysis (90% cheaper than GPT-4). Implement intelligent caching to reduce API calls.

- **Phase Validation**: Never proceed to Phase 2 (YouTube integration) until Phase 1 meets all success criteria. Each phase must prove functional and cost-effective before expansion.

- **Agent Auto-Discovery**: Write extremely precise, unique agent descriptions. These determine when Claude Code co-agents are automatically invoked. Avoid generic descriptions like "processes content" - use specific domain descriptions like "analyzes AI news for relevance scoring and trend detection."

- **Context Isolation**: Each Pydantic AI agent must operate in isolated context. Never share state directly between agents - use structured Pydantic models for all inter-agent communication.

- **MCP Server Modularity**: Each MCP server should handle exactly one domain (RSS aggregation, email notifications, database operations, content analysis). Include comprehensive error handling, rate limiting, and retry logic for all external API calls.

- **Database Schema Design**: Design Supabase tables for articles, analysis results, reports, and alerts. Use pgvector for semantic search and content similarity. Implement proper indexing for time-based queries and content retrieval.

- **LangGraph Workflows**: Use LangGraph for any multi-step processes (daily report generation, breaking news detection, trend analysis). Include validation gates, error recovery, and state persistence for long-running workflows.

- **Breaking News Detection**: Implement configurable urgency thresholds. Major product launches from tier-1 companies, significant funding (>$50M), regulatory developments, and research breakthroughs should trigger alerts. Include throttling to prevent alert spam.

- **Testing Strategy**: Create comprehensive tests for each agent, MCP server, and workflow. Include unit tests for individual functions, integration tests for agent communication, and end-to-end tests for complete workflows.

- **Monitoring and Logging**: Log all agent activities, API calls, costs, and system events. Implement health checks and automated alerting for system failures or cost threshold violations.

**Common AI Coding Assistant Gotchas**:
- Always validate API responses before processing - news APIs can return unexpected formats
- Implement proper error handling for network failures and rate limiting
- Use async/await patterns throughout for I/O operations
- Never assume RSS feed structures are consistent - implement defensive parsing
- Include proper cleanup for database connections and external resources
- Test agent communication thoroughly - inter-agent failures are hard to debug
- Validate all Pydantic models before database operations to prevent data corruption

**System Architecture Constraints**:
- Follow the full-stack project structure as defined in `ai_news_project_structure.md`
- Use the generic CLAUDE.md guidelines for all development
- Implement comprehensive logging for debugging and cost tracking
- Design for horizontal scaling in later phases
- Maintain backward compatibility as system evolves through phases