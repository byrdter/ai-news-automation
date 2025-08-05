# Create PRP for Pydantic AI + MCP + LangChain Architecture

## Feature file: $ARGUMENTS

Generate a complete PRP for multi-agent system implementation using Pydantic AI, MCP servers, LangChain/LangGraph workflows, and Claude Code Co-agents. Ensure comprehensive context for self-validation and iterative refinement. Read the feature file first to understand the multi-agent system requirements, agent specializations, tool integrations, and workflow orchestration needs.

The AI agent only gets the context you provide in the PRP and training data. Research findings must be included or referenced in the PRP since the Agent has web search capabilities for documentation and examples.

## Research Process

1. **Codebase Analysis**
   - Search for existing agent patterns and MCP server implementations
   - Identify workflow patterns and agent coordination examples
   - Note existing conventions for agent communication and tool registration
   - Check test patterns for agent validation and MCP server testing
   - Review database models and dependency injection patterns

2. **Architecture Research**
   - **Pydantic AI Documentation**: Agent creation, tool registration, dependency injection
   - **MCP Server Patterns**: Tool development, server architecture, client integration
   - **LangGraph Workflows**: State management, conditional flows, error recovery
   - **Claude Code Co-agents**: Agent descriptions, auto-discovery, context isolation
   - **Multi-agent Coordination**: Inter-agent communication, shared state management

3. **External Research**
   - Multi-agent system design patterns and best practices
   - MCP server development and deployment strategies
   - LangChain/LangGraph workflow implementation examples
   - Agent orchestration and coordination patterns
   - Cost optimization strategies for LLM-heavy applications

4. **Technology Stack Documentation**
   - Pydantic AI: https://ai.pydantic.dev/ (agents, tools, dependencies)
   - MCP Protocol: https://modelcontextprotocol.io/docs (server development)
   - LangGraph: https://langchain-ai.github.io/langgraph/ (workflows, state)
   - Database integration patterns (PostgreSQL, Supabase, vector stores)

5. **User Clarification** (if needed)
   - Agent specialization requirements and boundaries
   - MCP tool requirements and integration patterns
   - Workflow complexity and state management needs
   - Database and storage architecture decisions

## PRP Generation

Using PRPs/templates/pydantic_ai_base.md as template:

### Critical Context to Include
- **Agent Architecture**: Multi-agent patterns, specialization strategies
- **MCP Development**: Server patterns, tool registration, error handling
- **Workflow Design**: LangGraph patterns, state management, validation gates
- **Co-agent Coordination**: Auto-discovery descriptions, context isolation
- **Technology Integration**: Database patterns, API integrations, cost optimization

### Implementation Blueprint
- Agent-by-agent implementation approach
- MCP server development and testing strategy
- Workflow orchestration and error recovery
- Database schema and migration strategy
- Testing strategy for multi-agent systems

### Multi-Agent System Considerations
- Agent responsibility boundaries and communication protocols
- Shared vs isolated context management
- Tool access control and permission patterns
- Workflow coordination and handoff points
- Performance and cost optimization across agents

*** CRITICAL: RESEARCH PYDANTIC AI + MCP + LANGGRAPH DOCUMENTATION BEFORE WRITING PRP ***

*** ULTRATHINK ABOUT MULTI-AGENT ARCHITECTURE AND COORDINATION PATTERNS ***

## Output
Save as: `PRPs/pydantic-ai-{feature-name}.md`

## Quality Checklist for Multi-Agent Systems
- [ ] All agent responsibilities clearly defined
- [ ] MCP server architecture validated
- [ ] LangGraph workflows properly designed
- [ ] Agent coordination patterns established
- [ ] Database and state management planned
- [ ] Cost optimization strategies included
- [ ] Testing approach covers agent interactions
- [ ] Deployment strategy addresses all components

Score the PRP on a scale of 1-10 (confidence level for one-pass multi-agent implementation)

Remember: Multi-agent systems require exceptional context engineering for reliable implementation.