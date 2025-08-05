name: "Pydantic AI + MCP + LangChain PRP Template v1"
description: |

## Purpose
Template optimized for building multi-agent systems using Pydantic AI, MCP servers, LangChain/LangGraph workflows, and Claude Code Co-agents with comprehensive context and validation capabilities.

## Core Principles
1. **Agent Specialization**: Each agent has clear domain expertise and boundaries
2. **Context Isolation**: Agents operate independently with structured communication
3. **MCP Modularity**: Tools are organized in focused, reusable MCP servers
4. **Workflow Orchestration**: LangGraph manages complex multi-step processes
5. **Cost Optimization**: Efficient LLM usage and resource management
6. **Validation First**: Comprehensive testing at every integration point
7. **Global Rules**: Follow all rules in CLAUDE.md for consistency

---

## Goal
[Multi-agent system to be built - specify agent roles, coordination patterns, and end-user value]

## Why
- [Business value and automation benefits]
- [Integration with existing systems and workflows]
- [Problems solved through agent specialization and coordination]

## What
[User-visible behavior, agent interactions, and technical architecture]

### Success Criteria
- [ ] [Agent coordination and communication working reliably]
- [ ] [MCP tools accessible and performing correctly]
- [ ] [Workflows executing with proper state management]
- [ ] [Cost targets met for LLM usage and infrastructure]
- [ ] [End-to-end system validation passing]

## All Needed Context

### Multi-Agent System Documentation
```yaml
# ESSENTIAL READING - Include in context window
- url: https://ai.pydantic.dev/agents/
  why: Agent creation patterns, dependency injection, tool registration
  
- url: https://ai.pydantic.dev/multi-agent-applications/
  why: Multi-agent coordination, agent-as-tool patterns
  
- url: https://modelcontextprotocol.io/docs/
  why: MCP server development, tool implementation patterns
  
- url: https://langchain-ai.github.io/langgraph/
  why: Workflow orchestration, state management, error recovery
  
- file: examples/agents/
  why: Agent architecture patterns and communication protocols
  
- file: examples/mcp_servers/
  why: MCP server structure, tool registration, error handling
  
- file: examples/workflows/
  why: LangGraph patterns, state persistence, validation gates
```

### Current System Architecture
```bash
# Run `tree` to see current structure
[Current codebase tree here]
```

### Target Multi-Agent Architecture
```bash
# Desired structure with new components
agents/
├── __init__.py
├── base_agent.py              # Base agent class with dependencies
├── [specific_agent_1].py      # Specialized agent implementation
├── [specific_agent_2].py      # Another specialized agent
└── coordination_agent.py     # Master orchestration agent

mcp_servers/
├── __init__.py
├── [domain_server_1]/         # MCP server for specific domain
│   ├── server.py             # MCP server implementation
│   ├── tools.py              # Tool definitions
│   └── schemas.py            # Data validation schemas
└── [domain_server_2]/        # Another domain-specific MCP server

workflows/
├── __init__.py
├── base_workflow.py          # Base workflow patterns
├── [specific_workflow].py    # LangGraph workflow implementation
└── states.py                 # Workflow state definitions
```

### Technology Stack Gotchas
```python
# CRITICAL: Pydantic AI requires async throughout - no sync in async context
# CRITICAL: MCP servers need proper tool registration with type hints
# CRITICAL: LangGraph workflows require explicit state management
# CRITICAL: Agent auto-discovery depends on precise, unique descriptions
# CRITICAL: Database connections must use dependency injection patterns
# CRITICAL: Cost tracking essential for multi-agent LLM usage
# CRITICAL: Environment variables must be validated at startup
```

## Implementation Blueprint

### Agent Architecture Design
```python
# Define agent responsibilities and boundaries
class SpecializedAgent(Agent):
    """
    AGENT DESCRIPTION: [Precise, unique description for auto-discovery]
    Domain: [Specific expertise area]
    Tools: [MCP tools this agent can access]
    Dependencies: [Database, APIs, other agents]
    """
    
    # Dependencies injection pattern
    def __init__(self, deps: AgentDependencies):
        self.deps = deps
        super().__init__(
            model='gpt-4',  # or specified model
            system_prompt=SPECIALIZED_PROMPT,
            tools=[...],  # MCP tools for this agent
        )
```

### MCP Server Implementation Strategy
```python
# MCP server with proper tool registration
from mcp.server import Server
from mcp.types import Tool

@server.tool("tool_name")
async def specialized_tool(
    argument: str,
    context: Optional[dict] = None
) -> ToolResult:
    """
    Tool description for agent discovery
    Args: Clear parameter descriptions
    Returns: Structured result with error handling
    """
    # Tool implementation with validation
    # Error handling and logging
    # Rate limiting considerations
```

### LangGraph Workflow Patterns
```python
# Workflow with state management and error recovery
from langgraph import StateGraph
from typing_extensions import TypedDict

class WorkflowState(TypedDict):
    # State schema definition
    input_data: str
    agent_results: dict
    current_step: str
    error_state: Optional[str]

def create_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Node definitions with error handling
    workflow.add_node("agent_1", agent_1_step)
    workflow.add_node("agent_2", agent_2_step)
    
    # Conditional routing with validation
    workflow.add_conditional_edges(
        "agent_1",
        should_continue,
        {"continue": "agent_2", "end": END}
    )
    
    return workflow.compile()
```

### Implementation Task List
```yaml
Task 1: Core Infrastructure Setup
CREATE database/models.py:
  - Define all data models with proper relationships
  - Include vector storage considerations if needed
  - Add migration scripts for schema changes

CREATE config/settings.py:
  - Environment-based configuration with validation
  - API key management and rotation
  - Database connection pooling setup

Task 2: MCP Server Development  
CREATE mcp_servers/[domain]/server.py:
  - Implement MCP server with proper registration
  - Add comprehensive error handling and logging
  - Include rate limiting and retry logic

CREATE mcp_servers/[domain]/tools.py:
  - Define tools with clear descriptions for agent discovery
  - Implement proper input validation and output formatting
  - Add cost tracking for expensive operations

Task 3: Agent Implementation
CREATE agents/[specific_agent].py:
  - Implement agent with unique auto-discovery description
  - Add proper dependency injection for shared resources
  - Include tool access control and permission patterns

CREATE agents/coordination_agent.py:
  - Master orchestration agent for workflow management
  - Inter-agent communication and state coordination
  - Error propagation and recovery strategies

Task 4: Workflow Orchestration
CREATE workflows/[workflow_name].py:
  - LangGraph workflow with comprehensive state management
  - Error recovery and alternative pathway handling
  - Validation checkpoints at each workflow stage

Task 5: Integration and Testing
CREATE tests/test_agent_coordination.py:
  - Multi-agent interaction testing
  - MCP tool accessibility and functionality
  - Workflow state management and error recovery

Task 6: Monitoring and Optimization
CREATE utils/cost_tracking.py:
  - LLM usage monitoring across all agents
  - Performance metrics and optimization recommendations
  - Automated alerts for cost or performance thresholds
```

### Integration Points
```yaml
DATABASE:
  - migrations: "Add agent state and coordination tables"
  - indexes: "Optimize for agent communication patterns"
  - vector_storage: "Enable semantic search if required"
  
CONFIGURATION:
  - agents: "Agent-specific settings and model configurations"
  - mcp_servers: "MCP server registration and tool permissions"
  - workflows: "Workflow timeout and retry configurations"
  
MONITORING:
  - cost_tracking: "Multi-agent LLM usage and optimization"
  - performance: "Agent response times and workflow efficiency"
  - error_tracking: "Agent coordination and workflow failures"
```

## Validation Loop

### Level 1: Component Validation
```bash
# Individual component testing
pytest tests/test_agents/ -v           # Agent functionality
pytest tests/test_mcp_servers/ -v      # MCP tool registration and usage
pytest tests/test_workflows/ -v        # LangGraph state management
mypy agents/ mcp_servers/ workflows/   # Type checking across components
```

### Level 2: Integration Testing
```python
# Multi-agent coordination testing
async def test_agent_coordination():
    """Test agent communication and workflow handoffs"""
    coordination_agent = CoordinationAgent(deps)
    result = await coordination_agent.run("complex_multi_step_task")
    
    assert result.success
    assert len(result.agent_interactions) > 1
    assert all(step.status == "completed" for step in result.workflow_steps)

async def test_mcp_tool_accessibility():
    """Test MCP tools accessible across agents"""
    for agent in all_agents:
        tools = await agent.get_available_tools()
        assert len(tools) > 0
        # Test tool execution
        
async def test_workflow_error_recovery():
    """Test LangGraph error handling and recovery"""
    workflow = create_test_workflow()
    # Inject errors at various stages
    # Verify recovery mechanisms work
```

### Level 3: End-to-End System Testing
```bash
# Complete system validation
python cli.py --test-mode                    # CLI-based system testing
python scripts/validate_agent_coordination.py # Agent interaction testing
python scripts/test_cost_optimization.py     # Cost tracking validation

# Expected: All agents coordinate properly, workflows complete successfully
# If errors: Check agent logs and workflow state for debugging
```

## Final Validation Checklist
- [ ] All agents have unique, precise auto-discovery descriptions
- [ ] MCP servers register tools correctly and handle errors gracefully
- [ ] LangGraph workflows manage state properly with error recovery
- [ ] Agent coordination follows established communication protocols
- [ ] Database schemas support all agent and workflow requirements
- [ ] Cost tracking monitors LLM usage across all agents
- [ ] Environment variables are validated and properly injected
- [ ] Error handling covers agent failures and workflow interruptions
- [ ] Documentation covers setup, usage, and troubleshooting
- [ ] Performance meets requirements for response time and cost

---

## Multi-Agent System Anti-Patterns
- ❌ Don't create agents with overlapping responsibilities
- ❌ Don't use sync functions in async agent context
- ❌ Don't skip agent auto-discovery description validation
- ❌ Don't ignore MCP tool error handling and rate limiting
- ❌ Don't forget workflow state persistence and recovery
- ❌ Don't hardcode API keys or database credentials
- ❌ Don't skip cost monitoring for multi-agent LLM usage
- ❌ Don't trust agent outputs without validation gates

## Cost Optimization Strategies
- **Model Selection**: Use appropriate LLM size for each agent's complexity
- **Caching**: Implement intelligent caching for repeated operations
- **Batch Processing**: Group similar operations when possible
- **Tool Efficiency**: Optimize MCP tools for minimal LLM calls
- **Workflow Optimization**: Design workflows to minimize redundant agent calls

## Confidence Score: [1-10]
Rate confidence in one-pass implementation success based on:
- Complexity of agent coordination requirements
- Number of MCP servers and tools needed
- LangGraph workflow sophistication
- Database and integration complexity
- Team familiarity with technology stack