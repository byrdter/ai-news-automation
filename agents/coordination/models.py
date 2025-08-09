"""
Data models for the Coordination Agent.

Defines structures for multi-agent orchestration, task scheduling,
and system health monitoring.
"""

from typing import List, Optional, Dict, Any, Union, Set
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
import json


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """Types of tasks that can be coordinated."""
    NEWS_DISCOVERY = "news_discovery"
    CONTENT_ANALYSIS = "content_analysis"
    REPORT_GENERATION = "report_generation"
    ALERT_EVALUATION = "alert_evaluation"
    EMAIL_DELIVERY = "email_delivery"
    SYSTEM_MAINTENANCE = "system_maintenance"
    DATA_CLEANUP = "data_cleanup"
    COST_ANALYSIS = "cost_analysis"
    HEALTH_CHECK = "health_check"


class AgentStatus(str, Enum):
    """Agent operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SystemHealth(str, Enum):
    """Overall system health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


class TaskDependency(BaseModel):
    """Dependency relationship between tasks."""
    task_id: UUID = Field(..., description="ID of the dependent task")
    dependency_type: str = Field(default="completion", description="Type of dependency")
    required_status: TaskStatus = Field(default=TaskStatus.COMPLETED)
    timeout_minutes: int = Field(default=60, ge=1, le=1440)


class TaskResource(BaseModel):
    """Resource requirements for task execution."""
    agent_type: str = Field(..., description="Required agent type")
    estimated_duration_seconds: int = Field(..., ge=1, description="Estimated execution time")
    max_memory_mb: int = Field(default=512, ge=64, le=4096)
    max_cpu_percent: int = Field(default=50, ge=1, le=100)
    requires_internet: bool = Field(default=True)
    api_calls_estimated: int = Field(default=1, ge=0)
    estimated_cost_usd: float = Field(default=0.01, ge=0.0)


class Task(BaseModel):
    """Coordinated task with scheduling and dependency management."""
    task_id: UUID = Field(default_factory=uuid4)
    task_type: TaskType = Field(..., description="Type of task")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    
    # Task definition
    name: str = Field(..., description="Human-readable task name")
    description: str = Field(default="", description="Task description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    
    # Scheduling
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    scheduled_for: Optional[datetime] = Field(None, description="When to execute task")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    
    # Dependencies
    dependencies: List[TaskDependency] = Field(default_factory=list)
    blocks_tasks: List[UUID] = Field(default_factory=list, description="Tasks blocked by this task")
    
    # Resource requirements
    resource_requirements: TaskResource = Field(..., description="Resource needs")
    
    # Execution tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_retry_at: Optional[datetime] = None
    
    # Results and errors
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error if failed")
    execution_log: List[str] = Field(default_factory=list, description="Execution log entries")
    
    # Retry configuration
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_count: int = Field(default=0, ge=0)
    retry_delay_seconds: int = Field(default=60, ge=1, le=3600)
    exponential_backoff: bool = Field(default=True)
    
    # Performance metrics
    actual_duration_seconds: float = Field(default=0.0, ge=0.0)
    actual_cost_usd: float = Field(default=0.0, ge=0.0)
    memory_used_mb: int = Field(default=0, ge=0)
    cpu_used_percent: float = Field(default=0.0, ge=0.0)
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    
    @property
    def is_ready_to_run(self) -> bool:
        """Check if all dependencies are satisfied."""
        if self.status != TaskStatus.PENDING:
            return False
        
        # Check if scheduled time has arrived
        if self.scheduled_for and datetime.utcnow() < self.scheduled_for:
            return False
        
        # All dependencies must be satisfied
        return len(self.dependencies) == 0  # Simplified - would check actual dependency status
    
    @property
    def estimated_completion_time(self) -> Optional[datetime]:
        """Estimate when task will complete."""
        if self.status == TaskStatus.COMPLETED:
            return self.completed_at
        
        if self.status == TaskStatus.RUNNING and self.started_at:
            estimated_end = self.started_at + timedelta(seconds=self.resource_requirements.estimated_duration_seconds)
            return estimated_end
        
        if self.scheduled_for:
            return self.scheduled_for + timedelta(seconds=self.resource_requirements.estimated_duration_seconds)
        
        return None


class AgentInfo(BaseModel):
    """Information about an available agent."""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent")
    status: AgentStatus = Field(..., description="Current agent status")
    
    # Capabilities
    supported_task_types: List[TaskType] = Field(..., description="Task types this agent can handle")
    max_concurrent_tasks: int = Field(default=1, ge=1, le=10)
    current_task_count: int = Field(default=0, ge=0)
    
    # Performance metrics
    total_tasks_completed: int = Field(default=0, ge=0)
    total_tasks_failed: int = Field(default=0, ge=0)
    avg_execution_time_seconds: float = Field(default=0.0, ge=0.0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Resource usage
    current_memory_usage_mb: int = Field(default=0, ge=0)
    current_cpu_usage_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Health information
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    error_count_last_hour: int = Field(default=0, ge=0)
    last_error: Optional[str] = None
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return (
            self.status == AgentStatus.ONLINE and
            self.current_task_count < self.max_concurrent_tasks
        )
    
    @property
    def is_healthy(self) -> bool:
        """Check if agent is healthy."""
        heartbeat_age = datetime.utcnow() - self.last_heartbeat
        return (
            self.status in [AgentStatus.ONLINE, AgentStatus.BUSY] and
            heartbeat_age.total_seconds() < 300 and  # 5 minutes
            self.error_count_last_hour < 10
        )


class WorkflowTemplate(BaseModel):
    """Template for common task workflows."""
    template_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    version: str = Field(default="1.0")
    
    # Template structure
    task_templates: List[Dict[str, Any]] = Field(..., description="Task templates in order")
    default_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Scheduling defaults
    default_priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    estimated_total_duration_minutes: int = Field(..., ge=1)
    estimated_total_cost_usd: float = Field(..., ge=0.0)
    
    # Usage tracking
    usage_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    avg_completion_time_minutes: float = Field(default=0.0, ge=0.0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system")
    tags: List[str] = Field(default_factory=list)


class SystemMetrics(BaseModel):
    """Current system performance metrics."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Task metrics
    total_tasks_pending: int = Field(default=0, ge=0)
    total_tasks_running: int = Field(default=0, ge=0)
    total_tasks_completed_last_hour: int = Field(default=0, ge=0)
    total_tasks_failed_last_hour: int = Field(default=0, ge=0)
    
    # Agent metrics
    total_agents: int = Field(default=0, ge=0)
    agents_online: int = Field(default=0, ge=0)
    agents_busy: int = Field(default=0, ge=0)
    agents_error: int = Field(default=0, ge=0)
    
    # Resource usage
    total_memory_usage_mb: int = Field(default=0, ge=0)
    avg_cpu_usage_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Cost tracking
    hourly_cost_usd: float = Field(default=0.0, ge=0.0)
    daily_cost_usd: float = Field(default=0.0, ge=0.0)
    monthly_cost_projection_usd: float = Field(default=0.0, ge=0.0)
    
    # Queue health
    avg_queue_wait_time_seconds: float = Field(default=0.0, ge=0.0)
    max_queue_wait_time_seconds: float = Field(default=0.0, ge=0.0)
    
    # Error rates
    error_rate_last_hour: float = Field(default=0.0, ge=0.0, le=1.0)
    critical_errors_last_hour: int = Field(default=0, ge=0)
    
    @property
    def overall_health(self) -> SystemHealth:
        """Determine overall system health."""
        # Critical conditions
        if self.agents_online == 0:
            return SystemHealth.DOWN
        
        if self.error_rate_last_hour > 0.5 or self.critical_errors_last_hour > 10:
            return SystemHealth.CRITICAL
        
        # Warning conditions
        if (
            self.error_rate_last_hour > 0.1 or
            self.avg_queue_wait_time_seconds > 300 or  # 5 minutes
            self.avg_cpu_usage_percent > 80 or
            self.agents_error > self.agents_online * 0.2
        ):
            return SystemHealth.WARNING
        
        return SystemHealth.HEALTHY


class CoordinationRequest(BaseModel):
    """Request to coordinate a new task or workflow."""
    request_type: str = Field(..., pattern="^(single_task|workflow|scheduled_workflow)$")
    
    # Single task
    task: Optional[Task] = Field(None, description="Single task to coordinate")
    
    # Workflow
    workflow_template_id: Optional[UUID] = Field(None, description="Workflow template to use")
    workflow_parameters: Dict[str, Any] = Field(default_factory=dict, description="Workflow parameters")
    
    # Scheduling options
    immediate_execution: bool = Field(default=True, description="Execute immediately")
    schedule_time: Optional[datetime] = Field(None, description="Schedule for later")
    recurring: bool = Field(default=False, description="Is this a recurring task")
    recurrence_pattern: Optional[str] = Field(None, description="Cron-like recurrence pattern")
    
    # Priority and constraints
    priority_override: Optional[TaskPriority] = None
    max_execution_time_minutes: int = Field(default=60, ge=1, le=1440)
    max_cost_usd: float = Field(default=1.0, ge=0.001, le=10.0)
    
    # Notification preferences
    notify_on_completion: bool = Field(default=False)
    notify_on_failure: bool = Field(default=True)
    notification_recipients: List[str] = Field(default_factory=list)


class CoordinationResponse(BaseModel):
    """Response from coordination request."""
    success: bool
    message: str
    
    # Created tasks
    task_ids: List[UUID] = Field(default_factory=list, description="IDs of created tasks")
    workflow_id: Optional[UUID] = Field(None, description="Workflow ID if applicable")
    
    # Scheduling information
    scheduled_tasks: int = Field(default=0, description="Number of tasks scheduled")
    immediate_tasks: int = Field(default=0, description="Number of tasks started immediately")
    
    # Estimates
    estimated_completion_time: Optional[datetime] = None
    estimated_total_cost_usd: float = Field(default=0.0, ge=0.0)
    
    # Next steps
    next_task_id: Optional[UUID] = Field(None, description="Next task to execute")
    dependencies_pending: int = Field(default=0, description="Tasks waiting on dependencies")
    
    # Warnings
    warnings: List[str] = Field(default_factory=list, description="Any warnings about the request")


class HealthCheckResult(BaseModel):
    """Result of system health check."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_health: SystemHealth
    
    # Component health
    agents_health: Dict[str, AgentStatus] = Field(default_factory=dict)
    mcp_servers_health: Dict[str, bool] = Field(default_factory=dict)
    database_health: bool = Field(default=True)
    external_apis_health: Dict[str, bool] = Field(default_factory=dict)
    
    # Performance indicators
    system_metrics: SystemMetrics
    
    # Issues detected
    critical_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    
    # Recovery actions taken
    recovery_actions: List[str] = Field(default_factory=list)


# Predefined workflow templates
class StandardWorkflowTemplates:
    """Standard workflow templates for common operations."""
    
    DAILY_NEWS_PROCESSING = {
        "name": "Daily News Processing",
        "description": "Complete daily news discovery, analysis, and reporting",
        "task_templates": [
            {
                "task_type": "news_discovery",
                "name": "RSS Feed Discovery",
                "priority": "high",
                "estimated_duration_seconds": 600,
                "parameters": {"max_articles": 150}
            },
            {
                "task_type": "content_analysis",
                "name": "Content Analysis Batch",
                "priority": "high",
                "estimated_duration_seconds": 1800,
                "dependencies": ["news_discovery"],
                "parameters": {"batch_size": 10}
            },
            {
                "task_type": "report_generation",
                "name": "Daily Report Generation",
                "priority": "normal",
                "estimated_duration_seconds": 300,
                "dependencies": ["content_analysis"],
                "parameters": {"report_type": "daily"}
            },
            {
                "task_type": "email_delivery",
                "name": "Daily Report Delivery",
                "priority": "normal", 
                "estimated_duration_seconds": 60,
                "dependencies": ["report_generation"]
            }
        ]
    }
    
    BREAKING_NEWS_ALERT = {
        "name": "Breaking News Alert",
        "description": "Immediate alert processing for breaking news",
        "task_templates": [
            {
                "task_type": "alert_evaluation",
                "name": "Alert Evaluation",
                "priority": "critical",
                "estimated_duration_seconds": 30
            },
            {
                "task_type": "email_delivery",
                "name": "Alert Delivery",
                "priority": "critical",
                "estimated_duration_seconds": 15,
                "dependencies": ["alert_evaluation"]
            }
        ]
    }
    
    WEEKLY_MAINTENANCE = {
        "name": "Weekly System Maintenance",
        "description": "Weekly cleanup and maintenance tasks",
        "task_templates": [
            {
                "task_type": "data_cleanup",
                "name": "Database Cleanup",
                "priority": "low",
                "estimated_duration_seconds": 1800
            },
            {
                "task_type": "cost_analysis",
                "name": "Weekly Cost Analysis",
                "priority": "low",
                "estimated_duration_seconds": 300,
                "dependencies": ["data_cleanup"]
            },
            {
                "task_type": "health_check",
                "name": "System Health Assessment",
                "priority": "normal",
                "estimated_duration_seconds": 600
            }
        ]
    }


# Export all models
__all__ = [
    "TaskStatus",
    "TaskPriority",
    "TaskType",
    "AgentStatus",
    "SystemHealth",
    "TaskDependency",
    "TaskResource",
    "Task",
    "AgentInfo",
    "WorkflowTemplate",
    "SystemMetrics",
    "CoordinationRequest",
    "CoordinationResponse",
    "HealthCheckResult",
    "StandardWorkflowTemplates",
]