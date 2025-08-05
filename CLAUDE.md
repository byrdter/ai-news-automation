### 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.
- **Follow the phased development approach** - never implement features from future phases until current phase is validated and complete.

### 🤖 Pydantic AI Agent Development
- **Agent Structure**: Each Pydantic AI agent should have clear separation:
  - `agent.py` - Main agent definition with system prompts and dependencies
  - `tools.py` - MCP tool integrations and agent-specific functions
  - `models.py` - Pydantic data models for agent inputs/outputs
  - `workflows.py` - LangGraph workflow definitions for complex state management
- **Agent Descriptions**: Write precise, unique descriptions for each agent to enable Claude Code co-agent auto-discovery
- **Context Isolation**: Each agent operates in isolated context - never share state directly between agents
- **Tool Access Control**: Grant each agent only the MCP tools it specifically needs
- **Dependencies**: Use Pydantic AI dependency injection patterns for API keys, database connections, and shared resources
- **Agent Communication**: Use structured data models for inter-agent communication, never pass raw strings

### 🔗 MCP Server Development
- **Modular Design**: Each MCP server should handle one specific domain or capability
- **Tool Registration**: Always use proper MCP tool registration with clear descriptions and type hints
- **Error Handling**: Implement comprehensive error handling with fallback mechanisms
- **Rate Limiting**: Include rate limiting and retry logic for all external API calls
- **Configuration**: Use environment variables for all API keys and configuration - never hardcode secrets
- **Tool Descriptions**: Write clear, specific tool descriptions that enable accurate agent auto-discovery

### 🌊 LangGraph Workflow Management
- **State Management**: Use LangGraph for complex multi-step workflows with conditional branching
- **Error Recovery**: Implement error recovery and alternative pathways in workflows
- **Validation Gates**: Include validation checkpoints at each workflow stage
- **Monitoring**: Add logging and monitoring at each workflow node for debugging
- **Resource Management**: Ensure proper cleanup of resources in workflow error cases
- **State Persistence**: Implement proper state persistence for long-running workflows

### 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility:
  - `agents/` - Pydantic AI agent implementations
  - `mcp_servers/` - MCP server implementations for tools
  - `workflows/` - LangGraph workflow definitions
  - `database/` - Database models and operations
  - `utils/` - Shared utility functions
  - `config/` - Configuration and settings management
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_dotenv()** for environment variables.

### 💾 Database & Storage Guidelines
- **Database Models**: Use SQLModel or SQLAlchemy with proper relationships and constraints
- **Migrations**: Always create migration scripts for schema changes
- **Vector Storage**: Use appropriate vector database for semantic search when needed (pgvector, Qdrant, Chroma, etc.)
- **Connection Management**: Use connection pooling and proper session management
- **Data Validation**: Validate all data with Pydantic models before database operations
- **Transaction Management**: Use proper transaction boundaries for data consistency

### 💰 Cost Optimization Principles
- **Direct API Integration**: Prefer direct API calls over third-party services when possible
- **Efficient LLM Usage**: Choose appropriate model size and capability for each task
- **Caching Strategies**: Implement intelligent caching to reduce redundant API calls and processing
- **Resource Monitoring**: Track and log API usage and costs for optimization opportunities
- **Batch Processing**: Use batch operations where possible to reduce API call overhead

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
- **Include at least**:
  - 1 test for expected use
  - 1 edge case
  - 1 failure case
  - Integration tests for agent workflows
  - MCP server tool testing
  - Database operation testing
- **Mock External APIs**: Use proper mocking for all external API calls in tests
- **Test Agent Interactions**: Test agent communication and workflow coordination

### ✅ Task Completion & Phase Management
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- **Add new sub-tasks or TODOs** discovered during development to `TASK.md` under a "Discovered During Work" section.
- **Phase Validation**: Never proceed to next phase until current phase meets all success criteria
- **Rollback Planning**: Document rollback procedures for each major feature
- **Performance Monitoring**: Track system performance metrics for each phase

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation** - validate all inputs and outputs.
- **Use `FastAPI` for APIs** when building REST endpoints.
- **Write docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```
- **Async/Await**: Use async patterns throughout for better performance with I/O operations.

### 🎯 Context Engineering Principles
- **Comprehensive Upfront Context**: Provide extensive context in agent system prompts and tool descriptions
- **Agent Specialization**: Each agent should have deep domain expertise in its specific area
- **Clear Communication Protocols**: Define how agents pass information and coordinate workflows
- **Validation at Every Step**: Include validation checkpoints in all workflows and processes
- **Example-Driven Development**: Use concrete examples in agent prompts and documentation
- **Error Context**: Provide detailed error context for debugging and recovery

### 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- **When writing complex logic**, add an inline `# Reason:` comment explaining the why, not just the what.
- **Document Agent Interactions**: Clearly document how agents communicate and coordinate
- **API Documentation**: Document all MCP tools and their expected inputs/outputs
- **Workflow Documentation**: Document LangGraph workflows with state transition diagrams

### 🔄 Multi-Agent Coordination
- **Agent Auto-Discovery**: Write precise agent descriptions that enable Claude Code co-agent auto-discovery
- **State Management**: Use proper state management between agents and workflow steps
- **Error Propagation**: Implement proper error handling and propagation between agents
- **Resource Sharing**: Use dependency injection for shared resources (databases, API clients, etc.)
- **Agent Lifecycle**: Properly manage agent initialization, execution, and cleanup

### 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.
- **Validate AI-Generated Content**: Always implement validation for content generated by LLMs.
- **Cost Awareness**: Always consider cost implications of API calls and processing decisions.
- **Security First**: Never expose API keys, implement proper authentication, validate all inputs.

### 🔍 Monitoring & Observability
- **Comprehensive Logging**: Log all agent activities, API calls, and system events
- **Performance Metrics**: Track processing times, success rates, and resource usage
- **Cost Tracking**: Monitor and log API usage and associated costs where applicable
- **Health Checks**: Implement system health monitoring with automated alerts
- **Error Tracking**: Implement proper error tracking and alerting systems