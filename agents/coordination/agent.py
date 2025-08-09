"""
Coordination Agent using Pydantic AI.

Orchestrates multi-agent workflows, manages task scheduling, and monitors
system health for the AI News Automation System.
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID, uuid4
from collections import defaultdict, deque
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from config.settings import get_settings
from .models import (
    CoordinationRequest, CoordinationResponse, Task, TaskStatus, TaskType,
    TaskPriority, AgentInfo, AgentStatus, WorkflowTemplate, TaskDependency,
    TaskResource, SystemMetrics, SystemHealth, HealthCheckResult,
    StandardWorkflowTemplates
)
from agents.news_discovery.agent import get_news_discovery_service
from agents.content_analysis.agent import get_content_analysis_service
from agents.report_generation.agent import get_report_generation_service
from agents.alert.agent import get_alert_service
from utils.cost_tracking import CostTracker, ServiceType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoordinationDeps(BaseModel):
    """Dependencies for Coordination Agent."""
    cost_tracker: CostTracker
    settings: Any
    active_agents: Dict[str, AgentInfo]
    system_metrics: SystemMetrics


class TaskCoordinationPlan(BaseModel):
    """AI-generated plan for task coordination."""
    execution_strategy: str = Field(..., description="Overall execution strategy")
    task_sequence: List[UUID] = Field(..., description="Optimal task execution order")
    resource_allocation: Dict[str, str] = Field(..., description="Agent assignments")
    estimated_duration_minutes: int = Field(..., ge=1, description="Total estimated duration")
    critical_path: List[UUID] = Field(..., description="Critical path task IDs")
    
    # Risk assessment
    risk_factors: List[str] = Field(default_factory=list, description="Identified risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation")
    success_probability: float = Field(..., ge=0.0, le=1.0, description="Success probability")
    
    # Monitoring
    checkpoints: List[str] = Field(..., description="Progress checkpoints")
    fallback_plans: List[str] = Field(default_factory=list, description="Fallback strategies")
    escalation_triggers: List[str] = Field(default_factory=list, description="When to escalate")


# Create Coordination Agent
coordination_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=CoordinationDeps,
    result_type=TaskCoordinationPlan,
    system_prompt="""You are an AI Coordination Agent responsible for orchestrating multi-agent workflows in an AI News Automation System.

Your role is to:
1. Analyze incoming task requests and determine optimal execution strategies
2. Assign tasks to appropriate agents based on capabilities and current load
3. Sequence tasks to minimize dependencies and maximize parallel execution
4. Monitor system resources and agent health
5. Implement fallback strategies when tasks fail
6. Optimize for cost, speed, and reliability

AGENT CAPABILITIES:

News Discovery Agent:
- RSS feed processing and article collection
- Content deduplication and relevance scoring
- Best for: Daily news collection, breaking news monitoring
- Resource usage: Medium CPU, High I/O, Low cost
- Typical duration: 5-15 minutes for full discovery

Content Analysis Agent:
- Article analysis using Cohere API
- Entity extraction and sentiment analysis
- Best for: Batch content processing, quality assessment
- Resource usage: Low CPU, API-heavy, Medium cost
- Typical duration: 2-5 minutes per batch of 10 articles

Report Generation Agent:
- Multi-format report creation (HTML, Markdown, Text)
- AI-powered summaries and trend analysis
- Best for: Daily/weekly/monthly reports, executive summaries
- Resource usage: Medium CPU, API-heavy, Medium cost
- Typical duration: 3-8 minutes depending on complexity

Alert Agent:
- Breaking news detection and notification
- Priority-based alert filtering
- Best for: Real-time alerts, urgent notifications
- Resource usage: Low CPU, Low I/O, Low cost
- Typical duration: 30-60 seconds per evaluation

COORDINATION STRATEGIES:

Parallel Execution:
- Execute independent tasks simultaneously when resources allow
- Batch similar operations to optimize API usage
- Use agent availability to maximize throughput

Sequential Dependencies:
- Ensure prerequisite tasks complete before dependent tasks start
- Build in buffer time for dependency resolution
- Monitor dependency chains for bottlenecks

Resource Management:
- Balance CPU, memory, and API usage across agents
- Implement rate limiting to stay within cost budgets
- Scale task complexity based on available resources

Error Handling:
- Implement retry logic with exponential backoff
- Prepare fallback strategies for each task type
- Escalate to human intervention when automated recovery fails

Cost Optimization:
- Batch API calls to reduce per-request overhead
- Use caching to avoid redundant processing
- Monitor and enforce daily/monthly budget limits

Quality Assurance:
- Include validation checkpoints in workflows
- Implement quality gates before task completion
- Monitor success rates and adjust strategies accordingly

TASK PRIORITIZATION:

CRITICAL (Complete within 5 minutes):
- Breaking news alerts
- System health emergencies
- Security incidents

HIGH (Complete within 30 minutes):
- Daily report generation and delivery
- Important content analysis batches
- Alert evaluations for high-priority content

NORMAL (Complete within 2 hours):
- Regular RSS feed processing
- Weekly report preparation
- Routine system maintenance

LOW (Complete within 24 hours):
- Monthly report generation
- Data cleanup and archival
- Performance optimization tasks

Always provide clear reasoning for task sequencing, resource allocation, and risk mitigation strategies. Consider system load, agent availability, and cost constraints when planning execution."""
)


class TaskScheduler:
    """Task scheduling and queue management."""
    
    def __init__(self):
        self.task_queue = deque()
        self.running_tasks: Dict[UUID, Task] = {}
        self.completed_tasks: Dict[UUID, Task] = {}
        self.failed_tasks: Dict[UUID, Task] = {}
        self.task_dependencies: Dict[UUID, Set[UUID]] = defaultdict(set)
        
    def add_task(self, task: Task):
        """Add task to queue."""
        self.task_queue.append(task)
        
        # Update dependency mapping
        for dep in task.dependencies:
            self.task_dependencies[task.task_id].add(dep.task_id)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to run."""
        ready_tasks = []
        
        for task in list(self.task_queue):
            if task.is_ready_to_run:
                # Check if all dependencies are satisfied
                dependencies = self.task_dependencies.get(task.task_id, set())
                dependencies_satisfied = all(
                    dep_id in self.completed_tasks for dep_id in dependencies
                )
                
                if dependencies_satisfied:
                    ready_tasks.append(task)
                    self.task_queue.remove(task)
        
        # Sort by priority and scheduled time
        ready_tasks.sort(key=lambda t: (
            t.priority.value,
            t.scheduled_for or datetime.utcnow()
        ))
        
        return ready_tasks
    
    def mark_task_running(self, task: Task):
        """Mark task as running."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.running_tasks[task.task_id] = task
    
    def mark_task_completed(self, task: Task, result: Dict[str, Any]):
        """Mark task as completed."""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = result
        task.actual_duration_seconds = (task.completed_at - task.started_at).total_seconds()
        
        if task.task_id in self.running_tasks:
            del self.running_tasks[task.task_id]
        
        self.completed_tasks[task.task_id] = task
    
    def mark_task_failed(self, task: Task, error_message: str):
        """Mark task as failed."""
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.utcnow()
        
        if task.task_id in self.running_tasks:
            del self.running_tasks[task.task_id]
        
        # Check if retry is needed
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            task.last_retry_at = datetime.utcnow()
            
            # Add back to queue with delay
            retry_delay = task.retry_delay_seconds
            if task.exponential_backoff:
                retry_delay *= (2 ** task.retry_count)
            
            task.scheduled_for = datetime.utcnow() + timedelta(seconds=retry_delay)
            self.task_queue.append(task)
        else:
            self.failed_tasks[task.task_id] = task


class CoordinationService:
    """Main coordination service for multi-agent orchestration."""
    
    def __init__(self):
        """Initialize coordination service."""
        self.settings = get_settings()
        self.cost_tracker = CostTracker()
        self.scheduler = TaskScheduler()
        
        # Agent registry
        self.active_agents: Dict[str, AgentInfo] = {}
        self.agent_services = {
            "news_discovery": get_news_discovery_service(),
            "content_analysis": get_content_analysis_service(),
            "report_generation": get_report_generation_service(),
            "alert": get_alert_service()
        }
        
        # System monitoring
        self.system_metrics = SystemMetrics()
        self.health_check_interval = 60  # seconds
        self.last_health_check = datetime.utcnow()
        
        # Workflow templates
        self.workflow_templates = self._load_workflow_templates()
        
        # Execution control
        self.max_concurrent_tasks = 5
        self.is_running = False
        
    def _load_workflow_templates(self) -> Dict[str, WorkflowTemplate]:
        """Load standard workflow templates."""
        templates = {}
        
        # Load standard templates from StandardWorkflowTemplates
        for template_name, template_data in [
            ("daily_processing", StandardWorkflowTemplates.DAILY_NEWS_PROCESSING),
            ("breaking_alert", StandardWorkflowTemplates.BREAKING_NEWS_ALERT),
            ("weekly_maintenance", StandardWorkflowTemplates.WEEKLY_MAINTENANCE)
        ]:
            template = WorkflowTemplate(
                name=template_data["name"],
                description=template_data["description"],
                task_templates=template_data["task_templates"],
                estimated_total_duration_minutes=sum(
                    t.get("estimated_duration_seconds", 300) for t in template_data["task_templates"]
                ) // 60,
                estimated_total_cost_usd=0.5  # Default estimate
            )
            templates[template_name] = template
        
        return templates
    
    async def coordinate_request(self, request: CoordinationRequest) -> CoordinationResponse:
        """Main coordination entry point."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing coordination request: {request.request_type}")
            
            # Update system metrics
            await self._update_system_metrics()
            
            # Process request based on type
            if request.request_type == "single_task":
                return await self._coordinate_single_task(request)
            elif request.request_type == "workflow":
                return await self._coordinate_workflow(request)
            elif request.request_type == "scheduled_workflow":
                return await self._coordinate_scheduled_workflow(request)
            else:
                return CoordinationResponse(
                    success=False,
                    message=f"Unknown request type: {request.request_type}"
                )
        
        except Exception as e:
            logger.error(f"Coordination failed: {e}")
            return CoordinationResponse(
                success=False,
                message=f"Coordination failed: {str(e)}"
            )
    
    async def _coordinate_single_task(self, request: CoordinationRequest) -> CoordinationResponse:
        """Coordinate a single task."""
        if not request.task:
            return CoordinationResponse(
                success=False,
                message="No task provided for single task coordination"
            )
        
        task = request.task
        
        # Apply priority override if specified
        if request.priority_override:
            task.priority = request.priority_override
        
        # Set scheduling
        if request.immediate_execution:
            task.scheduled_for = None
        elif request.schedule_time:
            task.scheduled_for = request.schedule_time
        
        # Add to scheduler
        self.scheduler.add_task(task)
        
        # Get AI coordination plan
        coordination_plan = await self._get_coordination_plan([task], request)
        
        return CoordinationResponse(
            success=True,
            message="Single task scheduled successfully",
            task_ids=[task.task_id],
            scheduled_tasks=1,
            immediate_tasks=1 if request.immediate_execution else 0,
            estimated_completion_time=task.estimated_completion_time,
            estimated_total_cost_usd=task.resource_requirements.estimated_cost_usd
        )
    
    async def _coordinate_workflow(self, request: CoordinationRequest) -> CoordinationResponse:
        """Coordinate a workflow from template."""
        if not request.workflow_template_id:
            return CoordinationResponse(
                success=False,
                message="No workflow template ID provided"
            )
        
        # Find template (simplified - in real implementation would lookup by ID)
        template_name = "daily_processing"  # Default for demonstration
        template = self.workflow_templates.get(template_name)
        
        if not template:
            return CoordinationResponse(
                success=False,
                message=f"Workflow template not found: {request.workflow_template_id}"
            )
        
        # Create tasks from template
        tasks = await self._create_tasks_from_template(template, request.workflow_parameters)
        
        # Add dependencies between tasks
        self._setup_task_dependencies(tasks)
        
        # Add all tasks to scheduler
        for task in tasks:
            self.scheduler.add_task(task)
        
        # Get AI coordination plan
        coordination_plan = await self._get_coordination_plan(tasks, request)
        
        return CoordinationResponse(
            success=True,
            message=f"Workflow '{template.name}' scheduled successfully",
            task_ids=[task.task_id for task in tasks],
            scheduled_tasks=len(tasks),
            immediate_tasks=len(tasks) if request.immediate_execution else 0,
            estimated_completion_time=datetime.utcnow() + timedelta(
                minutes=coordination_plan.estimated_duration_minutes
            ),
            estimated_total_cost_usd=sum(
                task.resource_requirements.estimated_cost_usd for task in tasks
            )
        )
    
    async def _coordinate_scheduled_workflow(self, request: CoordinationRequest) -> CoordinationResponse:
        """Coordinate a scheduled workflow."""
        # Similar to workflow but with scheduling logic
        response = await self._coordinate_workflow(request)
        
        if response.success and request.schedule_time:
            # Update all tasks with scheduled time
            for task_id in response.task_ids:
                task = self._find_task(task_id)
                if task:
                    task.scheduled_for = request.schedule_time
            
            response.message += f" (scheduled for {request.schedule_time})"
        
        return response
    
    async def _create_tasks_from_template(self, 
                                        template: WorkflowTemplate, 
                                        parameters: Dict[str, Any]) -> List[Task]:
        """Create tasks from workflow template."""
        tasks = []
        
        for i, task_template in enumerate(template.task_templates):
            task = Task(
                task_type=TaskType(task_template["task_type"]),
                name=task_template["name"],
                description=task_template.get("description", ""),
                priority=TaskPriority(task_template.get("priority", "normal")),
                parameters={**task_template.get("parameters", {}), **parameters},
                resource_requirements=TaskResource(
                    agent_type=task_template["task_type"],
                    estimated_duration_seconds=task_template.get("estimated_duration_seconds", 300),
                    estimated_cost_usd=task_template.get("estimated_cost_usd", 0.01)
                )
            )
            tasks.append(task)
        
        return tasks
    
    def _setup_task_dependencies(self, tasks: List[Task]):
        """Setup dependencies between workflow tasks."""
        # Create a simple sequential dependency chain
        for i in range(1, len(tasks)):
            dependency = TaskDependency(
                task_id=tasks[i-1].task_id,
                dependency_type="completion",
                required_status=TaskStatus.COMPLETED,
                timeout_minutes=30
            )
            tasks[i].dependencies.append(dependency)
    
    async def _get_coordination_plan(self, 
                                   tasks: List[Task], 
                                   request: CoordinationRequest) -> TaskCoordinationPlan:
        """Get AI-generated coordination plan."""
        
        # Prepare context for AI agent
        task_context = "\n".join([
            f"- {task.name} ({task.task_type.value}): Priority={task.priority.value}, "
            f"Duration={task.resource_requirements.estimated_duration_seconds}s, "
            f"Cost=${task.resource_requirements.estimated_cost_usd:.3f}"
            for task in tasks
        ])
        
        agent_context = "\n".join([
            f"- {agent_id}: Status={agent.status.value}, Load={agent.current_task_count}/{agent.max_concurrent_tasks}"
            for agent_id, agent in self.active_agents.items()
        ])
        
        coordination_prompt = f"""
Plan coordination for {len(tasks)} tasks:

TASKS TO COORDINATE:
{task_context}

AVAILABLE AGENTS:
{agent_context}

SYSTEM CONSTRAINTS:
- Max concurrent tasks: {self.max_concurrent_tasks}
- Current budget usage: ${self.cost_tracker.get_daily_cost():.2f}/day
- Request type: {request.request_type}
- Immediate execution: {request.immediate_execution}

Create an optimal execution plan considering dependencies, resource constraints, and cost optimization.
"""
        
        try:
            # Create dependencies
            deps = CoordinationDeps(
                cost_tracker=self.cost_tracker,
                settings=self.settings,
                active_agents=self.active_agents,
                system_metrics=self.system_metrics
            )
            
            # Run AI coordination
            result = await coordination_agent.run(coordination_prompt, deps=deps)
            return result.data
            
        except Exception as e:
            logger.warning(f"AI coordination failed, using fallback: {e}")
            return self._generate_fallback_plan(tasks)
    
    def _generate_fallback_plan(self, tasks: List[Task]) -> TaskCoordinationPlan:
        """Generate fallback coordination plan."""
        return TaskCoordinationPlan(
            execution_strategy="Sequential execution with basic prioritization",
            task_sequence=[task.task_id for task in sorted(tasks, key=lambda t: t.priority.value)],
            resource_allocation={
                str(task.task_id): task.resource_requirements.agent_type 
                for task in tasks
            },
            estimated_duration_minutes=sum(
                task.resource_requirements.estimated_duration_seconds for task in tasks
            ) // 60,
            critical_path=[task.task_id for task in tasks],
            success_probability=0.8,
            checkpoints=[f"Task {i+1} completion" for i in range(len(tasks))],
            risk_factors=["AI coordination unavailable", "Using fallback planning"],
            mitigation_strategies=["Monitor task progress closely", "Manual intervention if needed"]
        )
    
    async def _update_system_metrics(self):
        """Update current system metrics."""
        current_time = datetime.utcnow()
        
        # Update task counts
        self.system_metrics.total_tasks_pending = len(self.scheduler.task_queue)
        self.system_metrics.total_tasks_running = len(self.scheduler.running_tasks)
        
        # Update agent counts
        online_agents = sum(1 for agent in self.active_agents.values() if agent.status == AgentStatus.ONLINE)
        busy_agents = sum(1 for agent in self.active_agents.values() if agent.status == AgentStatus.BUSY)
        error_agents = sum(1 for agent in self.active_agents.values() if agent.status == AgentStatus.ERROR)
        
        self.system_metrics.total_agents = len(self.active_agents)
        self.system_metrics.agents_online = online_agents
        self.system_metrics.agents_busy = busy_agents
        self.system_metrics.agents_error = error_agents
        
        # Update cost metrics
        self.system_metrics.hourly_cost_usd = self.cost_tracker.get_hourly_cost()
        self.system_metrics.daily_cost_usd = self.cost_tracker.get_daily_cost()
        self.system_metrics.monthly_cost_projection_usd = self.cost_tracker.get_monthly_projection()
        
        self.system_metrics.timestamp = current_time
    
    def _find_task(self, task_id: UUID) -> Optional[Task]:
        """Find task by ID across all queues."""
        # Check running tasks
        if task_id in self.scheduler.running_tasks:
            return self.scheduler.running_tasks[task_id]
        
        # Check completed tasks
        if task_id in self.scheduler.completed_tasks:
            return self.scheduler.completed_tasks[task_id]
        
        # Check failed tasks
        if task_id in self.scheduler.failed_tasks:
            return self.scheduler.failed_tasks[task_id]
        
        # Check queue
        for task in self.scheduler.task_queue:
            if task.task_id == task_id:
                return task
        
        return None
    
    async def run_coordination_loop(self):
        """Main coordination loop."""
        logger.info("Starting coordination loop")
        self.is_running = True
        
        while self.is_running:
            try:
                # Get ready tasks
                ready_tasks = self.scheduler.get_ready_tasks()
                
                # Execute tasks up to concurrency limit
                current_running = len(self.scheduler.running_tasks)
                available_slots = max(0, self.max_concurrent_tasks - current_running)
                
                for task in ready_tasks[:available_slots]:
                    await self._execute_task(task)
                
                # Health check if needed
                if (datetime.utcnow() - self.last_health_check).total_seconds() > self.health_check_interval:
                    await self._perform_health_check()
                    self.last_health_check = datetime.utcnow()
                
                # Update system metrics
                await self._update_system_metrics()
                
                # Brief pause before next iteration
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Coordination loop error: {e}")
                await asyncio.sleep(10)  # Longer pause on error
    
    async def _execute_task(self, task: Task):
        """Execute a single task."""
        self.scheduler.mark_task_running(task)
        
        try:
            logger.info(f"Executing task: {task.name} ({task.task_type.value})")
            
            # Route to appropriate agent service
            result = await self._route_task_to_agent(task)
            
            if result.get("success", False):
                self.scheduler.mark_task_completed(task, result)
                logger.info(f"Task completed: {task.name}")
            else:
                error_msg = result.get("error", "Task execution failed")
                self.scheduler.mark_task_failed(task, error_msg)
                logger.warning(f"Task failed: {task.name} - {error_msg}")
        
        except Exception as e:
            self.scheduler.mark_task_failed(task, str(e))
            logger.error(f"Task execution error: {task.name} - {e}")
    
    async def _route_task_to_agent(self, task: Task) -> Dict[str, Any]:
        """Route task to appropriate agent service."""
        task_type = task.task_type
        
        try:
            if task_type == TaskType.NEWS_DISCOVERY:
                # Route to news discovery agent
                from agents.news_discovery.models import NewsDiscoveryRequest
                request = NewsDiscoveryRequest(**task.parameters)
                response = await self.agent_services["news_discovery"].discover_news(request)
                return {"success": response.success, "data": response}
            
            elif task_type == TaskType.CONTENT_ANALYSIS:
                # Route to content analysis agent
                from agents.content_analysis.models import AnalysisRequest
                request = AnalysisRequest(**task.parameters)
                response = await self.agent_services["content_analysis"].analyze_content(request)
                return {"success": response.success, "data": response}
            
            elif task_type == TaskType.REPORT_GENERATION:
                # Route to report generation agent
                from agents.report_generation.models import ReportGenerationRequest
                request = ReportGenerationRequest(**task.parameters)
                response = await self.agent_services["report_generation"].generate_report(request)
                return {"success": response.success, "data": response}
            
            elif task_type == TaskType.ALERT_EVALUATION:
                # Route to alert agent
                from agents.alert.models import AlertRequest
                request = AlertRequest(**task.parameters)
                response = await self.agent_services["alert"].evaluate_alert(request)
                return {"success": response.success, "data": response}
            
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        
        except Exception as e:
            return {"success": False, "error": f"Task routing failed: {str(e)}"}
    
    async def _perform_health_check(self) -> HealthCheckResult:
        """Perform comprehensive system health check."""
        health_result = HealthCheckResult(
            overall_health=SystemHealth.HEALTHY,
            system_metrics=self.system_metrics
        )
        
        # Check agent health
        for agent_id, agent in self.active_agents.items():
            health_result.agents_health[agent_id] = agent.status
            if not agent.is_healthy:
                health_result.warnings.append(f"Agent {agent_id} is unhealthy")
        
        # Check system resources
        if self.system_metrics.avg_cpu_usage_percent > 80:
            health_result.warnings.append("High CPU usage detected")
        
        if self.system_metrics.daily_cost_usd > 3.0:  # Daily budget threshold
            health_result.warnings.append("Daily cost budget approaching limit")
        
        # Check task queue health
        if self.system_metrics.total_tasks_pending > 50:
            health_result.warnings.append("High task queue backlog")
        
        # Determine overall health
        if len(health_result.critical_issues) > 0:
            health_result.overall_health = SystemHealth.CRITICAL
        elif len(health_result.warnings) > 3:
            health_result.overall_health = SystemHealth.WARNING
        
        return health_result
    
    def stop_coordination(self):
        """Stop the coordination loop."""
        logger.info("Stopping coordination loop")
        self.is_running = False


# Global service instance
_coordination_service: Optional[CoordinationService] = None


def get_coordination_service() -> CoordinationService:
    """Get global coordination service instance."""
    global _coordination_service
    if _coordination_service is None:
        _coordination_service = CoordinationService()
    return _coordination_service


# Main entry points
async def coordinate_request(request: CoordinationRequest) -> CoordinationResponse:
    """Coordinate a task or workflow request."""
    service = get_coordination_service()
    return await service.coordinate_request(request)


async def start_coordination_loop():
    """Start the main coordination loop."""
    service = get_coordination_service()
    await service.run_coordination_loop()


def stop_coordination():
    """Stop the coordination loop."""
    service = get_coordination_service()
    service.stop_coordination()


# Export main components
__all__ = [
    'coordination_agent',
    'CoordinationService',
    'TaskScheduler',
    'coordinate_request',
    'start_coordination_loop',
    'stop_coordination',
    'get_coordination_service'
]