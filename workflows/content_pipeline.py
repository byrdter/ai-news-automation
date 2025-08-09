"""
Content Processing Pipeline using LangGraph.

Multi-step workflow for processing news articles from RSS feeds
through analysis, categorization, and report generation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from uuid import uuid4

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from agents.news_discovery.models import NewsDiscoveryRequest, NewsDiscoveryResponse
from agents.content_analysis.models import AnalysisRequest, AnalysisResponse
from agents.report_generation.models import ReportGenerationRequest, ReportGenerationResponse
from agents.alert.models import AlertRequest, AlertResponse
from agents.coordination.models import Task, TaskStatus, TaskType, TaskPriority
from utils.cost_tracking import CostTracker, ServiceType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentPipelineState(TypedDict):
    """State for content processing pipeline."""
    # Input parameters
    max_articles: int
    report_type: str
    recipients: List[str]
    
    # Processing state
    current_step: str
    step_count: int
    total_steps: int
    
    # Data flowing through pipeline
    discovered_articles: List[Dict[str, Any]]
    analyzed_articles: List[Dict[str, Any]]
    generated_alerts: List[Dict[str, Any]]
    generated_reports: List[Dict[str, Any]]
    
    # Error handling
    errors: Annotated[List[str], add_messages]
    warnings: Annotated[List[str], add_messages]
    
    # Metrics
    processing_start_time: datetime
    step_start_times: Dict[str, datetime]
    step_durations: Dict[str, float]
    total_cost: float
    articles_processed: int
    alerts_generated: int
    reports_generated: int
    
    # Quality gates
    quality_checks_passed: bool
    min_quality_threshold: float
    min_relevance_threshold: float
    
    # Recovery state
    retry_count: int
    max_retries: int
    recovery_strategies: List[str]


class ContentPipelineConfig(BaseModel):
    """Configuration for content pipeline workflow."""
    max_articles: int = Field(default=100, ge=1, le=500)
    report_type: str = Field(default="daily", pattern="^(daily|weekly|monthly|breaking)$")
    recipients: List[str] = Field(default_factory=list)
    
    # Quality thresholds
    min_quality_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    min_relevance_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Processing limits
    max_cost_per_run: float = Field(default=2.0, ge=0.1, le=10.0)
    timeout_minutes: int = Field(default=30, ge=5, le=120)
    
    # Error handling
    max_retries: int = Field(default=3, ge=0, le=10)
    enable_fallback_strategies: bool = Field(default=True)
    
    # Alert settings
    enable_alerts: bool = Field(default=True)
    alert_priority_threshold: str = Field(default="medium")
    
    # Report settings
    enable_reports: bool = Field(default=True)
    report_formats: List[str] = Field(default=["html", "email"])


class ContentPipelineWorkflow:
    """LangGraph workflow for content processing pipeline."""
    
    def __init__(self, config: ContentPipelineConfig):
        """Initialize workflow with configuration."""
        self.config = config
        self.cost_tracker = CostTracker()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        
        # Create graph
        workflow = StateGraph(ContentPipelineState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_pipeline)
        workflow.add_node("discover_news", self._discover_news)
        workflow.add_node("quality_gate_1", self._quality_gate_discovery)
        workflow.add_node("analyze_content", self._analyze_content)
        workflow.add_node("quality_gate_2", self._quality_gate_analysis)
        workflow.add_node("evaluate_alerts", self._evaluate_alerts)
        workflow.add_node("generate_reports", self._generate_reports)
        workflow.add_node("quality_gate_3", self._quality_gate_final)
        workflow.add_node("finalize_pipeline", self._finalize_pipeline)
        workflow.add_node("handle_error", self._handle_error)
        workflow.add_node("recovery", self._recovery_strategy)
        
        # Add edges
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "discover_news")
        workflow.add_edge("discover_news", "quality_gate_1")
        
        # Quality gate 1 routing
        workflow.add_conditional_edges(
            "quality_gate_1",
            self._route_after_discovery,
            {
                "continue": "analyze_content",
                "retry": "discover_news",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("analyze_content", "quality_gate_2")
        
        # Quality gate 2 routing
        workflow.add_conditional_edges(
            "quality_gate_2",
            self._route_after_analysis,
            {
                "continue": "evaluate_alerts",
                "retry": "analyze_content",
                "error": "handle_error"
            }
        )
        
        # Parallel alert and report generation
        workflow.add_edge("evaluate_alerts", "generate_reports")
        workflow.add_edge("generate_reports", "quality_gate_3")
        
        # Quality gate 3 routing
        workflow.add_conditional_edges(
            "quality_gate_3",
            self._route_final,
            {
                "success": "finalize_pipeline",
                "retry": "generate_reports",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("finalize_pipeline", END)
        
        # Error handling
        workflow.add_conditional_edges(
            "handle_error",
            self._route_error_handling,
            {
                "retry": "recovery",
                "fail": END
            }
        )
        
        workflow.add_conditional_edges(
            "recovery",
            self._route_recovery,
            {
                "discover": "discover_news",
                "analyze": "analyze_content", 
                "reports": "generate_reports",
                "fail": END
            }
        )
        
        return workflow.compile()
    
    async def _initialize_pipeline(self, state: ContentPipelineState) -> ContentPipelineState:
        """Initialize pipeline state."""
        logger.info("Initializing content processing pipeline")
        
        current_time = datetime.utcnow()
        
        # Update state
        state.update({
            "current_step": "initialize",
            "step_count": 1,
            "total_steps": 7,
            "processing_start_time": current_time,
            "step_start_times": {"initialize": current_time},
            "step_durations": {},
            "total_cost": 0.0,
            "articles_processed": 0,
            "alerts_generated": 0,
            "reports_generated": 0,
            "quality_checks_passed": False,
            "retry_count": 0,
            "max_retries": self.config.max_retries,
            "recovery_strategies": [],
            "errors": [],
            "warnings": [],
            "discovered_articles": [],
            "analyzed_articles": [],
            "generated_alerts": [],
            "generated_reports": []
        })
        
        return state
    
    async def _discover_news(self, state: ContentPipelineState) -> ContentPipelineState:
        """Discover news articles from RSS feeds."""
        logger.info("Discovering news articles")
        
        step_start = datetime.utcnow()
        state["step_start_times"]["discover_news"] = step_start
        state["current_step"] = "discover_news"
        state["step_count"] = 2
        
        try:
            # Import and use news discovery service
            from agents.news_discovery.agent import get_news_discovery_service
            
            # Create request
            discovery_request = NewsDiscoveryRequest(
                max_articles=state["max_articles"],
                min_relevance_score=self.config.min_relevance_threshold,
                include_breaking_news=self.config.enable_alerts,
                deduplicate_articles=True
            )
            
            # Execute discovery
            discovery_service = get_news_discovery_service()
            response = await discovery_service.discover_news(discovery_request)
            
            if response.success:
                state["discovered_articles"] = [
                    {
                        "id": str(article.article_id),
                        "title": article.title,
                        "content": article.content,
                        "url": article.url,
                        "source": article.source,
                        "published_date": article.published_date,
                        "relevance_score": article.relevance_score
                    }
                    for article in response.articles
                ]
                
                state["articles_processed"] = len(state["discovered_articles"])
                state["total_cost"] += response.processing_cost
                
                logger.info(f"Discovered {len(state['discovered_articles'])} articles")
                
            else:
                error_msg = f"News discovery failed: {response.error_message}"
                state["errors"].append(error_msg)
                logger.error(error_msg)
        
        except Exception as e:
            error_msg = f"News discovery error: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
        
        # Record step duration
        step_duration = (datetime.utcnow() - step_start).total_seconds()
        state["step_durations"]["discover_news"] = step_duration
        
        return state
    
    async def _quality_gate_discovery(self, state: ContentPipelineState) -> ContentPipelineState:
        """Quality gate after news discovery."""
        logger.info("Quality gate: Discovery validation")
        
        state["current_step"] = "quality_gate_1"
        
        # Check article count
        article_count = len(state["discovered_articles"])
        min_articles = max(1, self.config.max_articles // 10)  # At least 10% of target
        
        if article_count < min_articles:
            warning_msg = f"Low article count: {article_count} < {min_articles}"
            state["warnings"].append(warning_msg)
            logger.warning(warning_msg)
        
        # Check average relevance
        if state["discovered_articles"]:
            avg_relevance = sum(
                article["relevance_score"] for article in state["discovered_articles"]
            ) / len(state["discovered_articles"])
            
            if avg_relevance < self.config.min_relevance_threshold:
                warning_msg = f"Low average relevance: {avg_relevance:.2f} < {self.config.min_relevance_threshold}"
                state["warnings"].append(warning_msg)
                logger.warning(warning_msg)
        
        # Check cost
        if state["total_cost"] > self.config.max_cost_per_run * 0.3:  # 30% of budget
            warning_msg = f"High discovery cost: ${state['total_cost']:.3f}"
            state["warnings"].append(warning_msg)
            logger.warning(warning_msg)
        
        return state
    
    async def _analyze_content(self, state: ContentPipelineState) -> ContentPipelineState:
        """Analyze discovered articles."""
        logger.info("Analyzing article content")
        
        step_start = datetime.utcnow()
        state["step_start_times"]["analyze_content"] = step_start
        state["current_step"] = "analyze_content"
        state["step_count"] = 4
        
        try:
            from agents.content_analysis.agent import get_content_analysis_service
            
            analyzed_articles = []
            analysis_service = get_content_analysis_service()
            
            # Process articles in batches
            batch_size = 10
            articles = state["discovered_articles"]
            
            for i in range(0, len(articles), batch_size):
                batch = articles[i:i + batch_size]
                
                for article in batch:
                    try:
                        # Create analysis request
                        analysis_request = AnalysisRequest(
                            article_id=article["id"],
                            title=article["title"],
                            content=article["content"],
                            url=article["url"],
                            source=article["source"],
                            published_date=article["published_date"]
                        )
                        
                        # Analyze article
                        analysis_response = await analysis_service.analyze_content(analysis_request)
                        
                        if analysis_response.success:
                            analyzed_article = {
                                **article,
                                "analysis": {
                                    "quality_score": analysis_response.analysis.quality_score,
                                    "sentiment_score": analysis_response.analysis.sentiment_score,
                                    "impact_score": analysis_response.analysis.impact_score,
                                    "entities": analysis_response.analysis.entities,
                                    "topics": analysis_response.analysis.topics,
                                    "summary": analysis_response.analysis.summary
                                }
                            }
                            analyzed_articles.append(analyzed_article)
                            state["total_cost"] += analysis_response.processing_cost
                        
                        else:
                            warning_msg = f"Analysis failed for article {article['id']}: {analysis_response.error_message}"
                            state["warnings"].append(warning_msg)
                            logger.warning(warning_msg)
                    
                    except Exception as e:
                        error_msg = f"Article analysis error {article['id']}: {str(e)}"
                        state["warnings"].append(error_msg)
                        logger.warning(error_msg)
                
                # Brief pause between batches to avoid rate limits
                if i + batch_size < len(articles):
                    await asyncio.sleep(1)
            
            state["analyzed_articles"] = analyzed_articles
            logger.info(f"Analyzed {len(analyzed_articles)} articles")
        
        except Exception as e:
            error_msg = f"Content analysis error: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
        
        # Record step duration
        step_duration = (datetime.utcnow() - step_start).total_seconds()
        state["step_durations"]["analyze_content"] = step_duration
        
        return state
    
    async def _quality_gate_analysis(self, state: ContentPipelineState) -> ContentPipelineState:
        """Quality gate after content analysis."""
        logger.info("Quality gate: Analysis validation")
        
        state["current_step"] = "quality_gate_2"
        
        analyzed_count = len(state["analyzed_articles"])
        discovered_count = len(state["discovered_articles"])
        
        # Check analysis success rate
        if discovered_count > 0:
            success_rate = analyzed_count / discovered_count
            if success_rate < 0.8:  # 80% minimum success rate
                warning_msg = f"Low analysis success rate: {success_rate:.1%}"
                state["warnings"].append(warning_msg)
                logger.warning(warning_msg)
        
        # Check quality scores
        if state["analyzed_articles"]:
            quality_scores = [
                article["analysis"]["quality_score"] 
                for article in state["analyzed_articles"]
            ]
            avg_quality = sum(quality_scores) / len(quality_scores)
            
            if avg_quality < self.config.min_quality_threshold:
                warning_msg = f"Low average quality: {avg_quality:.2f} < {self.config.min_quality_threshold}"
                state["warnings"].append(warning_msg)
                logger.warning(warning_msg)
        
        return state
    
    async def _evaluate_alerts(self, state: ContentPipelineState) -> ContentPipelineState:
        """Evaluate articles for alerts."""
        if not self.config.enable_alerts:
            logger.info("Alert evaluation disabled")
            state["current_step"] = "evaluate_alerts"
            state["step_count"] = 5
            return state
        
        logger.info("Evaluating articles for alerts")
        
        step_start = datetime.utcnow()
        state["step_start_times"]["evaluate_alerts"] = step_start
        state["current_step"] = "evaluate_alerts"
        state["step_count"] = 5
        
        try:
            from agents.alert.agent import get_alert_service
            
            alert_service = get_alert_service()
            generated_alerts = []
            
            # Evaluate high-impact articles for alerts
            high_impact_articles = [
                article for article in state["analyzed_articles"]
                if article["analysis"]["impact_score"] > 0.7 or
                   article["relevance_score"] > 0.8
            ]
            
            for article in high_impact_articles[:10]:  # Limit alert evaluations
                try:
                    # Create alert request
                    alert_request = AlertRequest(
                        article_id=article["id"],
                        article_content=article["content"],
                        article_url=article["url"],
                        source_name=article["source"],
                        published_at=article["published_date"],
                        relevance_score=article["relevance_score"],
                        quality_score=article["analysis"]["quality_score"],
                        sentiment_score=article["analysis"]["sentiment_score"],
                        entities=article["analysis"]["entities"],
                        topics=article["analysis"]["topics"]
                    )
                    
                    # Evaluate alert
                    alert_response = await alert_service.evaluate_alert(alert_request)
                    
                    if alert_response.success and alert_response.alert_generated:
                        alert_data = {
                            "article_id": article["id"],
                            "alert_id": str(alert_response.alert.alert_id),
                            "alert_type": alert_response.alert.alert_type.value,
                            "priority": alert_response.alert.priority.value,
                            "headline": alert_response.alert.content.headline,
                            "summary": alert_response.alert.content.summary
                        }
                        generated_alerts.append(alert_data)
                        state["total_cost"] += alert_response.evaluation_cost
                
                except Exception as e:
                    warning_msg = f"Alert evaluation error {article['id']}: {str(e)}"
                    state["warnings"].append(warning_msg)
                    logger.warning(warning_msg)
            
            state["generated_alerts"] = generated_alerts
            state["alerts_generated"] = len(generated_alerts)
            
            logger.info(f"Generated {len(generated_alerts)} alerts")
        
        except Exception as e:
            error_msg = f"Alert evaluation error: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
        
        # Record step duration
        step_duration = (datetime.utcnow() - step_start).total_seconds()
        state["step_durations"]["evaluate_alerts"] = step_duration
        
        return state
    
    async def _generate_reports(self, state: ContentPipelineState) -> ContentPipelineState:
        """Generate reports from analyzed content."""
        if not self.config.enable_reports:
            logger.info("Report generation disabled")
            state["current_step"] = "generate_reports"
            state["step_count"] = 6
            return state
        
        logger.info("Generating reports")
        
        step_start = datetime.utcnow()
        state["step_start_times"]["generate_reports"] = step_start
        state["current_step"] = "generate_reports"
        state["step_count"] = 6
        
        try:
            from agents.report_generation.agent import get_report_generation_service
            from agents.report_generation.models import ReportType, ReportFormat
            
            report_service = get_report_generation_service()
            
            # Determine report period
            current_time = datetime.utcnow()
            if state["report_type"] == "daily":
                period_start = current_time - timedelta(days=1)
                report_type = ReportType.DAILY
            elif state["report_type"] == "weekly":
                period_start = current_time - timedelta(days=7)
                report_type = ReportType.WEEKLY
            else:
                period_start = current_time - timedelta(days=1)
                report_type = ReportType.DAILY
            
            # Create report generation request
            report_request = ReportGenerationRequest(
                report_type=report_type,
                period_start=period_start,
                period_end=current_time,
                recipients=state["recipients"],
                output_formats=[ReportFormat(fmt) for fmt in self.config.report_formats],
                send_immediately=bool(state["recipients"]),
                min_relevance_score=self.config.min_relevance_threshold,
                min_quality_score=self.config.min_quality_threshold
            )
            
            # Generate report
            report_response = await report_service.generate_report(report_request)
            
            if report_response.success:
                report_data = {
                    "report_id": str(report_response.report.metadata.report_id),
                    "title": report_response.report.metadata.title,
                    "type": report_response.report.metadata.report_type.value,
                    "articles_included": report_response.articles_processed,
                    "sections_generated": report_response.sections_generated,
                    "completeness_score": report_response.completeness_score,
                    "html_content": report_response.report.html_content[:1000] if report_response.report.html_content else None,
                    "delivery_scheduled": report_response.delivery_scheduled
                }
                
                state["generated_reports"].append(report_data)
                state["reports_generated"] = 1
                state["total_cost"] += report_response.generation_cost
                
                logger.info(f"Generated report: {report_data['title']}")
            else:
                error_msg = f"Report generation failed: {report_response.error_message}"
                state["errors"].append(error_msg)
                logger.error(error_msg)
        
        except Exception as e:
            error_msg = f"Report generation error: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
        
        # Record step duration
        step_duration = (datetime.utcnow() - step_start).total_seconds()
        state["step_durations"]["generate_reports"] = step_duration
        
        return state
    
    async def _quality_gate_final(self, state: ContentPipelineState) -> ContentPipelineState:
        """Final quality gate before completion."""
        logger.info("Quality gate: Final validation")
        
        state["current_step"] = "quality_gate_3"
        
        # Check if we have minimum required outputs
        has_articles = len(state["analyzed_articles"]) > 0
        has_reports = len(state["generated_reports"]) > 0 if self.config.enable_reports else True
        
        # Check cost constraints
        within_budget = state["total_cost"] <= self.config.max_cost_per_run
        
        # Check error count
        error_count = len(state["errors"])
        warning_count = len(state["warnings"])
        
        # Determine if pipeline succeeded
        success_criteria = [
            has_articles,
            has_reports,
            within_budget,
            error_count == 0
        ]
        
        state["quality_checks_passed"] = all(success_criteria)
        
        if not state["quality_checks_passed"]:
            logger.warning(f"Quality checks failed: articles={has_articles}, reports={has_reports}, budget=${state['total_cost']:.2f}, errors={error_count}")
        
        return state
    
    async def _finalize_pipeline(self, state: ContentPipelineState) -> ContentPipelineState:
        """Finalize pipeline execution."""
        logger.info("Finalizing content processing pipeline")
        
        total_duration = (datetime.utcnow() - state["processing_start_time"]).total_seconds()
        state["step_durations"]["total"] = total_duration
        
        # Log final metrics
        logger.info(f"Pipeline completed in {total_duration:.1f}s")
        logger.info(f"Articles processed: {state['articles_processed']}")
        logger.info(f"Alerts generated: {state['alerts_generated']}")
        logger.info(f"Reports generated: {state['reports_generated']}")
        logger.info(f"Total cost: ${state['total_cost']:.3f}")
        logger.info(f"Errors: {len(state['errors'])}")
        logger.info(f"Warnings: {len(state['warnings'])}")
        
        # Track costs
        self.cost_tracker.track_operation(
            operation="content_pipeline",
            service=ServiceType.SYSTEM,
            model="langgraph-workflow",
            processing_time=total_duration,
            cost_usd=state["total_cost"]
        )
        
        state["current_step"] = "completed"
        
        return state
    
    # Routing functions
    def _route_after_discovery(self, state: ContentPipelineState) -> str:
        """Route after discovery quality gate."""
        if state["errors"]:
            return "error"
        
        article_count = len(state["discovered_articles"])
        min_articles = max(1, self.config.max_articles // 20)  # At least 5% of target
        
        if article_count < min_articles and state["retry_count"] < state["max_retries"]:
            return "retry"
        
        return "continue"
    
    def _route_after_analysis(self, state: ContentPipelineState) -> str:
        """Route after analysis quality gate."""
        if state["errors"]:
            return "error"
        
        analyzed_count = len(state["analyzed_articles"])
        min_analyzed = max(1, len(state["discovered_articles"]) // 2)  # At least 50% analyzed
        
        if analyzed_count < min_analyzed and state["retry_count"] < state["max_retries"]:
            return "retry"
        
        return "continue"
    
    def _route_final(self, state: ContentPipelineState) -> str:
        """Route after final quality gate."""
        if state["errors"]:
            return "error"
        
        if not state["quality_checks_passed"] and state["retry_count"] < state["max_retries"]:
            return "retry"
        
        return "success"
    
    def _route_error_handling(self, state: ContentPipelineState) -> str:
        """Route error handling."""
        if state["retry_count"] < state["max_retries"]:
            return "retry"
        return "fail"
    
    def _route_recovery(self, state: ContentPipelineState) -> str:
        """Route recovery strategy."""
        if "discovery" in state["recovery_strategies"]:
            return "discover"
        elif "analysis" in state["recovery_strategies"]:
            return "analyze"
        elif "reports" in state["recovery_strategies"]:
            return "reports"
        return "fail"
    
    async def _handle_error(self, state: ContentPipelineState) -> ContentPipelineState:
        """Handle errors and determine recovery strategy."""
        logger.warning("Handling pipeline errors")
        
        state["current_step"] = "handle_error"
        state["retry_count"] += 1
        
        # Determine recovery strategies based on where we failed
        if state["current_step"] in ["discover_news", "quality_gate_1"]:
            state["recovery_strategies"] = ["discovery"]
        elif state["current_step"] in ["analyze_content", "quality_gate_2"]:
            state["recovery_strategies"] = ["analysis"]
        elif state["current_step"] in ["generate_reports", "quality_gate_3"]:
            state["recovery_strategies"] = ["reports"]
        
        return state
    
    async def _recovery_strategy(self, state: ContentPipelineState) -> ContentPipelineState:
        """Execute recovery strategy."""
        logger.info(f"Executing recovery strategy: {state['recovery_strategies']}")
        
        state["current_step"] = "recovery"
        
        # Clear some errors to allow retry
        if len(state["errors"]) > 0:
            state["errors"] = state["errors"][-3:]  # Keep only last 3 errors
        
        return state
    
    async def execute_pipeline(self, **kwargs) -> Dict[str, Any]:
        """Execute the complete content processing pipeline."""
        logger.info("Starting content processing pipeline execution")
        
        # Initialize state with configuration and input parameters
        initial_state = ContentPipelineState(
            max_articles=kwargs.get("max_articles", self.config.max_articles),
            report_type=kwargs.get("report_type", self.config.report_type),
            recipients=kwargs.get("recipients", self.config.recipients),
            current_step="",
            step_count=0,
            total_steps=7,
            discovered_articles=[],
            analyzed_articles=[],
            generated_alerts=[],
            generated_reports=[],
            errors=[],
            warnings=[],
            processing_start_time=datetime.utcnow(),
            step_start_times={},
            step_durations={},
            total_cost=0.0,
            articles_processed=0,
            alerts_generated=0,
            reports_generated=0,
            quality_checks_passed=False,
            min_quality_threshold=self.config.min_quality_threshold,
            min_relevance_threshold=self.config.min_relevance_threshold,
            retry_count=0,
            max_retries=self.config.max_retries,
            recovery_strategies=[]
        )
        
        try:
            # Execute workflow
            result = await self.graph.ainvoke(initial_state)
            
            # Extract final results
            return {
                "success": result["quality_checks_passed"],
                "articles_processed": result["articles_processed"],
                "alerts_generated": result["alerts_generated"],
                "reports_generated": result["reports_generated"],
                "total_cost": result["total_cost"],
                "processing_time": result["step_durations"].get("total", 0),
                "errors": result["errors"],
                "warnings": result["warnings"],
                "discovered_articles": result["discovered_articles"],
                "analyzed_articles": result["analyzed_articles"],
                "generated_alerts": result["generated_alerts"],
                "generated_reports": result["generated_reports"]
            }
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "articles_processed": 0,
                "alerts_generated": 0,
                "reports_generated": 0,
                "total_cost": 0.0,
                "processing_time": 0
            }


# Factory functions
def create_daily_pipeline_config(**overrides) -> ContentPipelineConfig:
    """Create configuration for daily content pipeline."""
    return ContentPipelineConfig(
        max_articles=100,
        report_type="daily",
        min_quality_threshold=0.6,
        min_relevance_threshold=0.7,
        max_cost_per_run=1.5,
        timeout_minutes=20,
        enable_alerts=True,
        enable_reports=True,
        **overrides
    )


def create_breaking_pipeline_config(**overrides) -> ContentPipelineConfig:
    """Create configuration for breaking news pipeline."""
    return ContentPipelineConfig(
        max_articles=20,
        report_type="breaking",
        min_quality_threshold=0.7,
        min_relevance_threshold=0.8,
        max_cost_per_run=0.5,
        timeout_minutes=10,
        enable_alerts=True,
        enable_reports=False,
        alert_priority_threshold="high",
        **overrides
    )


async def execute_daily_content_pipeline(**kwargs) -> Dict[str, Any]:
    """Execute daily content processing pipeline."""
    config = create_daily_pipeline_config()
    workflow = ContentPipelineWorkflow(config)
    return await workflow.execute_pipeline(**kwargs)


async def execute_breaking_news_pipeline(**kwargs) -> Dict[str, Any]:
    """Execute breaking news processing pipeline."""
    config = create_breaking_pipeline_config()
    workflow = ContentPipelineWorkflow(config)
    return await workflow.execute_pipeline(**kwargs)


# Export main components
__all__ = [
    "ContentPipelineWorkflow",
    "ContentPipelineConfig",
    "ContentPipelineState", 
    "create_daily_pipeline_config",
    "create_breaking_pipeline_config",
    "execute_daily_content_pipeline",
    "execute_breaking_news_pipeline"
]