"""
Alert Agent using Pydantic AI.

Detects breaking news, evaluates urgency, and manages alert notifications
with intelligent filtering and delivery optimization.
"""

import asyncio
import time
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Set
import logging
from collections import defaultdict, Counter

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from config.settings import get_settings
from .models import (
    AlertRequest, AlertResponse, Alert, AlertContent, AlertTrigger,
    AlertType, AlertPriority, AlertStatus, AlertConfiguration,
    AlertRecipient, DeliveryChannel, AlertMetrics
)
from mcp_servers.email_notifications import TemplateEmailRequest, send_templated_email
from utils.cost_tracking import CostTracker, ServiceType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertEvaluationDeps(BaseModel):
    """Dependencies for Alert Agent."""
    cost_tracker: CostTracker
    settings: Any
    alert_config: AlertConfiguration
    recent_alerts: List[Alert]


class AlertEvaluation(BaseModel):
    """AI evaluation of alert worthiness."""
    is_alert_worthy: bool = Field(..., description="Whether this deserves an alert")
    alert_type: AlertType = Field(..., description="Type of alert")
    priority: AlertPriority = Field(..., description="Alert priority level")
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="Urgency score")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Potential impact score")
    
    # Content generation
    headline: str = Field(..., max_length=150, description="Alert headline")
    summary: str = Field(..., max_length=500, description="Alert summary")
    impact_analysis: str = Field(..., max_length=300, description="Why this matters")
    key_points: List[str] = Field(..., max_items=5, description="Key takeaways")
    
    # Classification reasoning
    evaluation_reasoning: str = Field(..., description="Detailed reasoning for alert decision")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in evaluation")
    human_review_recommended: bool = Field(default=False, description="Whether human review is recommended")
    
    # Trigger identification
    trigger_keywords: List[str] = Field(default_factory=list, description="Keywords that triggered alert")
    trigger_entities: List[str] = Field(default_factory=list, description="Entities that triggered alert")
    market_implications: List[str] = Field(default_factory=list, description="Market or industry implications")


# Create Alert Agent
alert_agent = Agent(
    'openai:gpt-5-mini',
    deps_type=AlertEvaluationDeps,
    result_type=AlertEvaluation,
    system_prompt="""You are an AI Alert Agent specialized in detecting breaking news and urgent developments in AI and technology.

Your role is to evaluate articles and determine whether they warrant immediate alerts to AI industry professionals.

ALERT CRITERIA:

CRITICAL PRIORITY (Immediate notification required):
- Major AI breakthroughs or scientific discoveries
- Significant regulatory changes affecting AI industry
- Large-scale funding rounds (>$100M) or major acquisitions
- Safety incidents or security breaches with wide impact
- Key personnel changes at major AI companies (CEO, CTO, etc.)
- Product launches with industry-changing potential

HIGH PRIORITY (Within 1-2 hours):
- Important research paper releases from top institutions
- Significant product announcements from major companies
- Notable funding rounds ($10M-$100M) 
- Important partnerships or collaborations
- Regulatory proposals or policy discussions
- Notable AI model releases or updates

MEDIUM PRIORITY (Within 6 hours):
- Industry analysis with significant insights
- Conference announcements or major speaking events
- Standard product updates with meaningful impact
- Research findings with commercial applications
- Market analysis with actionable insights

LOW PRIORITY (Daily digest appropriate):
- General news coverage of AI topics
- Educational content or tutorials
- Minor product updates or bug fixes
- Opinion pieces without new information
- Routine business updates

EVALUATION FACTORS:

Urgency Assessment (0.0-1.0):
- Time sensitivity of the information
- Competitive advantage of early knowledge
- Speed at which situation is developing
- Whether delays in awareness could cause missed opportunities

Impact Assessment (0.0-1.0):
- Number of people/companies affected
- Magnitude of change or disruption
- Strategic importance for AI professionals
- Long-term implications for the industry

Content Quality:
- Credibility of source and author
- Factual accuracy and verification
- Depth of information and analysis
- Uniqueness compared to other coverage

ALERT CONTENT REQUIREMENTS:

Headlines:
- Clear, specific, and action-oriented
- Include key entity names when relevant
- Avoid vague terms like "major" or "significant" without context
- Lead with the most important information

Summaries:
- Answer who, what, when, where, why in first 2 sentences
- Include specific numbers, dates, and names
- Highlight immediate implications
- Maintain objective, professional tone

Impact Analysis:
- Explain why this matters to AI professionals
- Identify who is most affected
- Note potential business or technical implications
- Connect to broader industry trends when relevant

Key Points:
- Prioritize actionable information
- Include concrete details and data points
- Focus on facts that drive decision-making
- Limit to most essential information

REJECTION CRITERIA:
- Duplicate or substantially similar to recent alerts (6-hour window)
- Speculation without credible sources
- Opinion pieces without new factual information
- Content that's already widely known
- Articles focused on non-AI technology without clear AI connection
- Marketing content disguised as news

Always provide clear reasoning for your alert decision and assign appropriate confidence scores. When in doubt about priority, err on the side of caution but don't suppress genuinely important alerts."""
)


class AlertService:
    """Service for alert detection and management."""
    
    def __init__(self):
        """Initialize alert service."""
        self.settings = get_settings()
        self.cost_tracker = CostTracker()
        self.alert_config = AlertConfiguration()
        
        # Alert history for deduplication
        self.recent_alerts: List[Alert] = []
        self.alert_cache: Dict[str, Alert] = {}
        
        # Rate limiting
        self.hourly_alert_count = 0
        self.daily_alert_count = 0
        self.last_hour_reset = datetime.utcnow().hour
        self.last_day_reset = datetime.utcnow().date()
        
        # Performance metrics
        self.metrics = AlertMetrics(
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow()
        )
    
    async def evaluate_alert(self, request: AlertRequest) -> AlertResponse:
        """Evaluate whether an article should trigger an alert."""
        start_time = time.time()
        evaluation_cost = 0.0
        
        try:
            logger.info(f"Evaluating alert for article: {request.article_id}")
            
            # Check rate limits first
            if not self._check_rate_limits():
                return AlertResponse(
                    success=True,
                    alert_generated=False,
                    rejection_reason="Rate limit exceeded for alerts",
                    processing_time=time.time() - start_time
                )
            
            # Check for duplicates
            if request.check_duplicates:
                duplicate_alert = await self._check_duplicates(request)
                if duplicate_alert:
                    return AlertResponse(
                        success=True,
                        alert_generated=False,
                        rejection_reason=f"Duplicate of alert {duplicate_alert.alert_id}",
                        processing_time=time.time() - start_time
                    )
            
            # Initial filtering based on content quality
            if not self._passes_initial_filter(request):
                return AlertResponse(
                    success=True,
                    alert_generated=False,
                    rejection_reason="Article does not meet minimum quality thresholds",
                    processing_time=time.time() - start_time
                )
            
            # Detect triggers
            triggers = await self._detect_triggers(request)
            if not triggers:
                return AlertResponse(
                    success=True,
                    alert_generated=False,
                    rejection_reason="No alert triggers detected",
                    triggers_detected=[],
                    processing_time=time.time() - start_time
                )
            
            # Get AI evaluation
            evaluation = await self._get_ai_evaluation(request, triggers)
            evaluation_cost += 0.02  # Estimated cost for AI evaluation
            
            if not evaluation.is_alert_worthy:
                return AlertResponse(
                    success=True,
                    alert_generated=False,
                    rejection_reason=evaluation.evaluation_reasoning,
                    evaluation_score=evaluation.confidence_score,
                    triggers_detected=[t.trigger_type for t in triggers],
                    processing_time=time.time() - start_time,
                    evaluation_cost=evaluation_cost
                )
            
            # Create alert
            alert = await self._create_alert(request, evaluation, triggers)
            
            # Determine if human review is needed
            if self._requires_human_review(alert, evaluation):
                alert.human_review_required = True
                alert.status = AlertStatus.PENDING
                logger.info(f"Alert {alert.alert_id} queued for human review")
            else:
                alert.status = AlertStatus.APPROVED
                alert.approved_at = datetime.utcnow()
            
            # Store alert
            self.recent_alerts.append(alert)
            self.alert_cache[str(alert.alert_id)] = alert
            
            # Update counters
            self.hourly_alert_count += 1
            self.daily_alert_count += 1
            
            # Track costs
            self.cost_tracker.track_operation(
                operation="alert_evaluation",
                service=ServiceType.OPENAI,
                model="gpt-5-mini",
                input_tokens=len(request.article_content.split()) * 1.3,
                output_tokens=len(evaluation.headline.split()) * 10,
                cost_usd=evaluation_cost
            )
            
            processing_time = time.time() - start_time
            
            logger.info(f"Alert generated: {alert.alert_type.value} priority={alert.priority.value}")
            
            return AlertResponse(
                success=True,
                alert_generated=True,
                alert=alert,
                evaluation_score=evaluation.confidence_score,
                triggers_detected=[t.trigger_type for t in triggers],
                processing_time=processing_time,
                evaluation_cost=evaluation_cost,
                human_review_required=alert.human_review_required
            )
            
        except Exception as e:
            logger.error(f"Alert evaluation failed: {e}")
            
            return AlertResponse(
                success=False,
                alert_generated=False,
                rejection_reason=f"Evaluation failed: {str(e)}",
                processing_time=time.time() - start_time,
                evaluation_cost=evaluation_cost
            )
    
    def _check_rate_limits(self) -> bool:
        """Check if rate limits allow for new alerts."""
        current_time = datetime.utcnow()
        
        # Reset hourly counter if needed
        if current_time.hour != self.last_hour_reset:
            self.hourly_alert_count = 0
            self.last_hour_reset = current_time.hour
        
        # Reset daily counter if needed
        if current_time.date() != self.last_day_reset:
            self.daily_alert_count = 0
            self.last_day_reset = current_time.date()
        
        # Check limits
        if self.hourly_alert_count >= self.alert_config.max_alerts_per_hour_global:
            logger.warning(f"Hourly alert limit reached: {self.hourly_alert_count}")
            return False
        
        if self.daily_alert_count >= self.alert_config.max_alerts_per_day_global:
            logger.warning(f"Daily alert limit reached: {self.daily_alert_count}")
            return False
        
        return True
    
    async def _check_duplicates(self, request: AlertRequest) -> Optional[Alert]:
        """Check for duplicate alerts in recent history."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.alert_config.duplicate_window_hours)
        
        # Check against recent alerts
        for alert in self.recent_alerts:
            if alert.created_at < cutoff_time:
                continue  # Too old
            
            # Check URL match (exact duplicate)
            if alert.source_url == request.article_url:
                return alert
            
            # Check content similarity (fuzzy duplicate)
            if self._calculate_content_similarity(alert.content.summary, request.article_content[:500]) > self.alert_config.similar_content_threshold:
                return alert
        
        return None
    
    def _calculate_content_similarity(self, text1: str, text2: str) -> float:
        """Calculate content similarity between two texts."""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _passes_initial_filter(self, request: AlertRequest) -> bool:
        """Check if article passes initial quality filters."""
        # Minimum quality thresholds
        if request.relevance_score < 0.7:
            return False
        
        if request.quality_score < 0.6:
            return False
        
        # Content length check
        if len(request.article_content.split()) < 50:
            return False
        
        # Source credibility (basic check)
        low_credibility_indicators = ["blog", "personal", "opinion", "rumor"]
        if any(indicator in request.source_name.lower() for indicator in low_credibility_indicators):
            return False
        
        return True
    
    async def _detect_triggers(self, request: AlertRequest) -> List[AlertTrigger]:
        """Detect what triggered the potential alert."""
        triggers = []
        content_lower = request.article_content.lower()
        title_lower = (request.article_url.split('/')[-1] if '/' in request.article_url else '').lower()
        
        # Breaking news keywords
        breaking_matches = [kw for kw in self.alert_config.breaking_news_keywords if kw.lower() in content_lower]
        if breaking_matches:
            trigger = AlertTrigger(
                trigger_type="breaking_news_keywords",
                trigger_value=0.8,
                actual_value=len(breaking_matches) * 0.2,
                confidence=0.8,
                keywords_matched=breaking_matches,
                article_age_minutes=int((datetime.utcnow() - request.published_at).total_seconds() / 60)
            )
            triggers.append(trigger)
        
        # High-priority company mentions
        company_matches = [company for company in self.alert_config.high_priority_companies if company.lower() in content_lower]
        if company_matches:
            trigger = AlertTrigger(
                trigger_type="high_priority_companies",
                trigger_value=0.7,
                actual_value=len(company_matches) * 0.3,
                confidence=0.9,
                entities_detected=company_matches,
                article_age_minutes=int((datetime.utcnow() - request.published_at).total_seconds() / 60)
            )
            triggers.append(trigger)
        
        # Funding indicators
        funding_matches = [kw for kw in self.alert_config.funding_keywords if kw.lower() in content_lower]
        funding_amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:million|billion|M|B)', request.article_content)
        if funding_matches and funding_amounts:
            # Convert amounts to millions for comparison
            amounts = []
            for amount, unit in zip(funding_amounts, re.findall(r'(?:million|billion|M|B)', request.article_content)):
                value = float(amount)
                if unit.lower() in ['billion', 'b']:
                    value *= 1000
                amounts.append(value)
            
            max_amount = max(amounts) if amounts else 0
            if max_amount >= 10:  # $10M threshold
                trigger = AlertTrigger(
                    trigger_type="funding_announcement",
                    trigger_value=10.0,  # $10M threshold
                    actual_value=max_amount,
                    confidence=0.85,
                    keywords_matched=funding_matches,
                    market_indicators={"funding_amount_millions": max_amount},
                    article_age_minutes=int((datetime.utcnow() - request.published_at).total_seconds() / 60)
                )
                triggers.append(trigger)
        
        # Research breakthrough indicators
        research_matches = [kw for kw in self.alert_config.research_keywords if kw.lower() in content_lower]
        if research_matches and any(entity in content_lower for entity in ['arxiv', 'nature', 'science', 'research', 'paper']):
            trigger = AlertTrigger(
                trigger_type="research_breakthrough",
                trigger_value=0.7,
                actual_value=len(research_matches) * 0.3,
                confidence=0.75,
                keywords_matched=research_matches,
                article_age_minutes=int((datetime.utcnow() - request.published_at).total_seconds() / 60)
            )
            triggers.append(trigger)
        
        # Product launch indicators
        product_matches = [kw for kw in self.alert_config.product_keywords if kw.lower() in content_lower]
        if product_matches and company_matches:
            trigger = AlertTrigger(
                trigger_type="product_launch",
                trigger_value=0.6,
                actual_value=(len(product_matches) + len(company_matches)) * 0.2,
                confidence=0.8,
                keywords_matched=product_matches,
                entities_detected=company_matches,
                article_age_minutes=int((datetime.utcnow() - request.published_at).total_seconds() / 60)
            )
            triggers.append(trigger)
        
        # Sentiment-based triggers (very positive or negative)
        if abs(request.sentiment_score) > 0.7:
            sentiment_type = "very_positive" if request.sentiment_score > 0.7 else "very_negative"
            trigger = AlertTrigger(
                trigger_type=f"extreme_sentiment_{sentiment_type}",
                trigger_value=0.7,
                actual_value=abs(request.sentiment_score),
                confidence=0.6,
                sentiment_indicators={"sentiment_score": request.sentiment_score},
                article_age_minutes=int((datetime.utcnow() - request.published_at).total_seconds() / 60)
            )
            triggers.append(trigger)
        
        return triggers
    
    async def _get_ai_evaluation(self, request: AlertRequest, triggers: List[AlertTrigger]) -> AlertEvaluation:
        """Get comprehensive AI evaluation of the article."""
        
        # Prepare context
        trigger_context = "\n".join([
            f"- {trigger.trigger_type}: confidence={trigger.confidence:.2f}, keywords={trigger.keywords_matched}"
            for trigger in triggers
        ])
        
        evaluation_prompt = f"""
Evaluate this AI news article for alert worthiness:

ARTICLE INFO:
Title: {request.article_url.split('/')[-1] if '/' in request.article_url else 'N/A'}
Source: {request.source_name}
Author: {request.author or 'N/A'}
Published: {request.published_at.strftime('%Y-%m-%d %H:%M UTC')}
Age: {int((datetime.utcnow() - request.published_at).total_seconds() / 60)} minutes

ANALYSIS SCORES:
Relevance: {request.relevance_score:.2f}
Quality: {request.quality_score:.2f}
Sentiment: {request.sentiment_score:.2f}

ENTITIES: {', '.join(request.entities[:10]) if request.entities else 'None'}
TOPICS: {', '.join(request.topics[:5]) if request.topics else 'None'}

DETECTED TRIGGERS:
{trigger_context}

ARTICLE CONTENT (first 1000 chars):
{request.article_content[:1000]}...

Provide comprehensive evaluation including alert worthiness, priority, content generation, and reasoning.
"""
        
        try:
            # Create dependencies
            deps = AlertEvaluationDeps(
                cost_tracker=self.cost_tracker,
                settings=self.settings,
                alert_config=self.alert_config,
                recent_alerts=self.recent_alerts[-10:]  # Last 10 alerts for context
            )
            
            # Run AI evaluation
            result = await alert_agent.run(evaluation_prompt, deps=deps)
            return result.data
            
        except Exception as e:
            logger.warning(f"AI evaluation failed, using fallback: {e}")
            return self._fallback_evaluation(request, triggers)
    
    def _fallback_evaluation(self, request: AlertRequest, triggers: List[AlertTrigger]) -> AlertEvaluation:
        """Fallback evaluation when AI fails."""
        
        # Simple rule-based evaluation
        urgency_score = 0.0
        impact_score = 0.0
        alert_type = AlertType.BREAKING_NEWS
        priority = AlertPriority.LOW
        
        # Calculate scores based on triggers
        for trigger in triggers:
            urgency_score = max(urgency_score, trigger.confidence * 0.8)
            impact_score = max(impact_score, trigger.actual_value * 0.1)
            
            # Set alert type based on trigger
            if trigger.trigger_type == "funding_announcement":
                alert_type = AlertType.FUNDING_NEWS
            elif trigger.trigger_type == "research_breakthrough":
                alert_type = AlertType.RESEARCH_BREAKTHROUGH
            elif trigger.trigger_type == "product_launch":
                alert_type = AlertType.PRODUCT_LAUNCH
        
        # Determine priority
        overall_score = (urgency_score + impact_score) / 2
        if overall_score > 0.8:
            priority = AlertPriority.CRITICAL
        elif overall_score > 0.6:
            priority = AlertPriority.HIGH
        elif overall_score > 0.4:
            priority = AlertPriority.MEDIUM
        
        # Generate basic content
        headline = f"AI News: {request.source_name} Reports on {request.entities[0] if request.entities else 'AI Development'}"
        summary = f"New development reported by {request.source_name}. {request.article_content[:200]}..."
        
        return AlertEvaluation(
            is_alert_worthy=overall_score > 0.3,
            alert_type=alert_type,
            priority=priority,
            urgency_score=urgency_score,
            impact_score=impact_score,
            headline=headline[:150],
            summary=summary[:500],
            impact_analysis="This development may have significance for AI industry professionals.",
            key_points=[f"Report from {request.source_name}", "Details require further analysis"],
            evaluation_reasoning="Fallback rule-based evaluation due to AI evaluation failure",
            confidence_score=0.5,
            trigger_keywords=[kw for trigger in triggers for kw in trigger.keywords_matched],
            trigger_entities=request.entities[:5]
        )
    
    async def _create_alert(self, request: AlertRequest, evaluation: AlertEvaluation, triggers: List[AlertTrigger]) -> Alert:
        """Create complete alert from evaluation."""
        
        # Create alert content
        content = AlertContent(
            headline=evaluation.headline,
            summary=evaluation.summary,
            full_description=request.article_content[:2000],
            key_points=evaluation.key_points,
            impact_analysis=evaluation.impact_analysis,
            context=f"Published by {request.source_name}" + (f" by {request.author}" if request.author else "")
        )
        
        # Create alert
        alert = Alert(
            article_id=request.article_id,
            alert_type=evaluation.alert_type,
            priority=evaluation.priority,
            urgency_score=evaluation.urgency_score,
            impact_score=evaluation.impact_score,
            content=content,
            triggers=triggers,
            source_url=request.article_url,
            source_name=request.source_name,
            author=request.author,
            published_at=request.published_at,
            evaluation_reasoning=evaluation.evaluation_reasoning,
            confidence_score=evaluation.confidence_score,
            human_review_required=evaluation.human_review_recommended
        )
        
        return alert
    
    def _requires_human_review(self, alert: Alert, evaluation: AlertEvaluation) -> bool:
        """Determine if alert requires human review."""
        
        # Always review critical priority alerts
        if alert.priority == AlertPriority.CRITICAL:
            return True
        
        # Review if AI explicitly recommends it
        if evaluation.human_review_recommended:
            return True
        
        # Review if confidence is low
        if evaluation.confidence_score < 0.7:
            return True
        
        # Review if multiple conflicting triggers
        if len(alert.triggers) > 3:
            return True
        
        return False
    
    async def send_alert(self, alert: Alert, recipients: List[AlertRecipient]) -> Dict[str, Any]:
        """Send alert to specified recipients."""
        if alert.status != AlertStatus.APPROVED:
            return {
                "success": False,
                "error": f"Alert status is {alert.status.value}, not approved for sending"
            }
        
        successful_deliveries = 0
        failed_deliveries = 0
        delivery_errors = []
        
        for recipient in recipients:
            # Check if recipient wants this type of alert
            if alert.alert_type not in recipient.alert_types and recipient.alert_types:
                continue
            
            # Check priority filter
            priority_levels = {
                AlertPriority.LOW: 1,
                AlertPriority.MEDIUM: 2, 
                AlertPriority.HIGH: 3,
                AlertPriority.CRITICAL: 4
            }
            
            if priority_levels.get(alert.priority, 0) < priority_levels.get(recipient.priority_filter, 0):
                continue
            
            # Send via preferred channels
            for channel in recipient.preferred_channels:
                try:
                    if channel == DeliveryChannel.EMAIL and recipient.email:
                        success = await self._send_email_alert(alert, recipient)
                        if success:
                            successful_deliveries += 1
                        else:
                            failed_deliveries += 1
                            delivery_errors.append(f"Email delivery failed to {recipient.email}")
                    
                    # Add other channels as needed (SMS, Slack, etc.)
                    
                except Exception as e:
                    failed_deliveries += 1
                    delivery_errors.append(f"Delivery to {recipient.name} failed: {str(e)}")
        
        # Update alert status
        alert.successful_deliveries = successful_deliveries
        alert.failed_deliveries = failed_deliveries
        alert.delivery_errors = delivery_errors
        alert.sent_at = datetime.utcnow()
        
        if successful_deliveries > 0:
            alert.status = AlertStatus.DELIVERED
        elif failed_deliveries > 0:
            alert.status = AlertStatus.FAILED
        
        return {
            "success": successful_deliveries > 0,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "errors": delivery_errors
        }
    
    async def _send_email_alert(self, alert: Alert, recipient: AlertRecipient) -> bool:
        """Send alert via email."""
        try:
            # Determine urgency indicator
            urgency_indicator = ""
            if alert.priority == AlertPriority.CRITICAL:
                urgency_indicator = "🚨 URGENT: "
            elif alert.priority == AlertPriority.HIGH:
                urgency_indicator = "⚡ HIGH: "
            
            # Create email request
            email_request = TemplateEmailRequest(
                template_name="breaking_alert",
                to_addresses=[recipient.email],
                subject=f"{urgency_indicator}{alert.content.headline}",
                template_data={
                    "alert": alert,
                    "title": alert.content.headline,
                    "summary": alert.content.summary,
                    "source": alert.source_name,
                    "published_date": alert.published_at,
                    "url": alert.source_url,
                    "key_points": alert.content.key_points,
                    "impact_analysis": alert.content.impact_analysis,
                    "urgency_level": alert.priority.value,
                    "alert_time": datetime.utcnow()
                }
            )
            
            response = await send_templated_email(email_request)
            return response.success
            
        except Exception as e:
            logger.error(f"Email alert sending failed: {e}")
            return False


# Global service instance
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """Get global alert service instance."""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


# Main entry points
async def evaluate_alert(request: AlertRequest) -> AlertResponse:
    """Evaluate article for alert generation."""
    service = get_alert_service()
    return await service.evaluate_alert(request)


async def send_alert(alert: Alert, recipients: List[AlertRecipient]) -> Dict[str, Any]:
    """Send alert to recipients."""
    service = get_alert_service()
    return await service.send_alert(alert, recipients)


# Export main components
__all__ = [
    'alert_agent',
    'AlertService',
    'evaluate_alert',
    'send_alert',
    'get_alert_service'
]