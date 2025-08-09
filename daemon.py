#!/usr/bin/env python3
"""
AI News Automation System - Main Daemon Process

Continuously runs RSS fetching, content analysis, and report generation.
Built with APScheduler for robust scheduling and monitoring.
"""

import asyncio
import logging
import signal
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Third-party imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich import box
import psutil

# Project imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from utils.cost_tracking import CostTracker, ServiceType
from agents.content_analysis.agent import get_content_analysis_service
from mcp_servers.rss_aggregator import fetch_all_sources, BatchFetchRequest
from database.models import Article, NewsSource
from daemon_database import DaemonDatabase

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()


@dataclass
class DaemonStats:
    """Daemon performance statistics."""
    started_at: datetime
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    articles_fetched: int = 0
    articles_analyzed: int = 0
    total_cost_usd: float = 0.0
    last_rss_fetch: Optional[datetime] = None
    last_analysis: Optional[datetime] = None
    last_error: Optional[str] = None
    current_memory_mb: float = 0.0
    current_cpu_percent: float = 0.0


class NewsAutomationDaemon:
    """Main automation daemon for the AI News System."""

    def __init__(self):
        """Initialize the automation daemon."""
        self.settings = get_settings()
        self.cost_tracker = CostTracker()
        self.content_service = get_content_analysis_service()
        self.scheduler = AsyncIOScheduler()
        self.shutdown_event = asyncio.Event()
        
        # Performance tracking
        self.stats = DaemonStats(started_at=datetime.utcnow())
        self.process = psutil.Process()
        
        # Job control
        self.running_jobs: Dict[str, bool] = {}
        
        console.print("🤖 AI News Automation Daemon initialized", style="green")
        logger.info("Daemon initialized successfully")

    async def setup_jobs(self) -> None:
        """Setup scheduled jobs for the daemon."""
        
        # RSS Fetching Job - Every hour by default
        self.scheduler.add_job(
            self.rss_fetch_job,
            trigger=IntervalTrigger(seconds=self.settings.rss_fetch_interval),
            id="rss_fetch",
            name="RSS Article Fetching",
            max_instances=1,
            misfire_grace_time=300  # 5 minutes grace
        )
        
        # Content Analysis Job - Process unanalyzed articles every 10 minutes
        self.scheduler.add_job(
            self.content_analysis_job,
            trigger=IntervalTrigger(minutes=10),
            id="content_analysis",
            name="Content Analysis",
            max_instances=1,
            misfire_grace_time=600  # 10 minutes grace
        )
        
        # Daily Report Job
        daily_time = self.settings.daily_report_time.split(':')
        self.scheduler.add_job(
            self.daily_report_job,
            trigger=CronTrigger(hour=int(daily_time[0]), minute=int(daily_time[1])),
            id="daily_report",
            name="Daily Report Generation",
            max_instances=1
        )
        
        # Health Check Job - Every 5 minutes
        self.scheduler.add_job(
            self.health_check_job,
            trigger=IntervalTrigger(seconds=self.settings.health_check_interval),
            id="health_check",
            name="System Health Check",
            max_instances=1
        )
        
        # Cost Monitoring Job - Every 30 minutes
        self.scheduler.add_job(
            self.cost_monitoring_job,
            trigger=IntervalTrigger(minutes=30),
            id="cost_monitoring",
            name="Cost Monitoring",
            max_instances=1
        )
        
        # Add event listeners
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        logger.info("All scheduled jobs configured successfully")

    async def rss_fetch_job(self) -> None:
        """Fetch articles from RSS sources."""
        if self.running_jobs.get("rss_fetch", False):
            logger.warning("RSS fetch job already running, skipping...")
            return
            
        self.running_jobs["rss_fetch"] = True
        
        try:
            console.print("🔍 Starting RSS fetch cycle...", style="cyan")
            start_time = time.time()
            
            # Fetch articles using existing RSS system
            batch_request = BatchFetchRequest(
                max_articles_per_source=self.settings.rss_max_articles_per_source,
                rate_limit_delay=self.settings.rss_rate_limit_delay,
                max_concurrent=self.settings.rss_max_concurrent,
                timeout=self.settings.rss_timeout
            )
            
            result = await fetch_all_sources(batch_request)
            
            if hasattr(result, 'all_articles'):
                articles = result.all_articles
                console.print(f"✅ Fetched {len(articles)} articles", style="green")
                
                # Save to database using DaemonDatabase
                save_results = await DaemonDatabase.save_rss_articles(articles)
                
                # Update stats
                self.stats.articles_fetched += len(articles)
                self.stats.last_rss_fetch = datetime.utcnow()
                
                processing_time = time.time() - start_time
                console.print(f"📊 RSS cycle completed: {save_results['saved']} saved, {save_results['skipped']} skipped, {processing_time:.1f}s", style="green")
                
                if save_results['unmapped'] > 0:
                    console.print(f"⚠️  {save_results['unmapped']} articles from unmapped sources", style="yellow")
                
            else:
                console.print("❌ RSS fetch returned no articles", style="red")
                
        except Exception as e:
            logger.error(f"RSS fetch job failed: {e}")
            self.stats.last_error = str(e)
            console.print(f"❌ RSS fetch failed: {e}", style="red")
            
        finally:
            self.running_jobs["rss_fetch"] = False

    async def content_analysis_job(self) -> None:
        """Analyze unanalyzed articles."""
        if self.running_jobs.get("content_analysis", False):
            logger.warning("Content analysis job already running, skipping...")
            return
            
        self.running_jobs["content_analysis"] = True
        
        try:
            console.print("🧠 Starting content analysis cycle...", style="cyan")
            start_time = time.time()
            
            # Get unanalyzed articles from database
            unanalyzed = await DaemonDatabase.get_unanalyzed_articles(limit=self.settings.batch_size)
            
            if not unanalyzed:
                console.print("ℹ️  No unanalyzed articles found", style="yellow")
                return
                
            console.print(f"📝 Analyzing {len(unanalyzed)} articles", style="cyan")
            
            analyzed_count = 0
            for article in unanalyzed:
                try:
                    # Use content analysis service
                    from agents.content_analysis.models import AnalysisRequest, ContentType
                    
                    # Prepare content for analysis
                    content_text = article.content or article.summary or article.title
                    if not content_text or len(content_text.strip()) < 10:
                        console.print(f"⚠️  Skipping article {article.id}: insufficient content", style="yellow")
                        continue
                    
                    request = AnalysisRequest(
                        content=content_text,
                        content_type=ContentType.NEWS_ARTICLE,
                        content_id=str(article.id),
                        extract_entities=True,
                        identify_topics=True
                    )
                    
                    analysis_response = await self.content_service.analyze_content(request)
                    
                    if analysis_response.success:
                        # Update article with analysis results
                        success = await DaemonDatabase.update_article_analysis(article.id, analysis_response.analysis)
                        if success:
                            analyzed_count += 1
                            # Track costs
                            self.stats.total_cost_usd += analysis_response.analysis_cost
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze article {article.id}: {e}")
            
            self.stats.articles_analyzed += analyzed_count
            self.stats.last_analysis = datetime.utcnow()
            
            processing_time = time.time() - start_time
            console.print(f"✅ Analysis cycle completed: {analyzed_count}/{len(unanalyzed)} articles, {processing_time:.1f}s", style="green")
            
        except Exception as e:
            logger.error(f"Content analysis job failed: {e}")
            self.stats.last_error = str(e)
            console.print(f"❌ Content analysis failed: {e}", style="red")
            
        finally:
            self.running_jobs["content_analysis"] = False

    async def daily_report_job(self) -> None:
        """Generate and send daily report."""
        try:
            console.print("📊 Generating daily report...", style="cyan")
            
            # Get articles from last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_articles = await DaemonDatabase.get_articles_since(yesterday)
            top_articles = await DaemonDatabase.get_top_articles_by_relevance(yesterday, limit=10)
            
            if not recent_articles:
                console.print("ℹ️  No articles found for daily report", style="yellow")
                return
            
            # Generate comprehensive report
            report = await self.generate_daily_report(recent_articles, top_articles)
            
            # Save report to file
            report_file = f"reports/daily_report_{datetime.utcnow().strftime('%Y%m%d')}.md"
            Path(report_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            console.print(f"✅ Daily report generated: {report_file}", style="green")
            logger.info(f"Daily report generated with {len(recent_articles)} articles, {len(top_articles)} top articles")
            
        except Exception as e:
            logger.error(f"Daily report job failed: {e}")
            console.print(f"❌ Daily report failed: {e}", style="red")

    async def health_check_job(self) -> None:
        """Perform system health checks."""
        try:
            # Update system metrics
            self.stats.current_memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.stats.current_cpu_percent = self.process.cpu_percent()
            
            # Check database connection
            db_healthy = await DaemonDatabase.check_database_health()
            
            # Get database stats for monitoring
            db_stats = await DaemonDatabase.get_database_stats()
            
            # Check API quotas
            cost_healthy = self.stats.total_cost_usd < self.settings.daily_cost_limit
            
            # Check for stuck jobs
            stuck_jobs = [job_id for job_id, running in self.running_jobs.items() if running]
            
            # Check breaking news
            breaking_news = await DaemonDatabase.get_breaking_news(self.settings.alert_urgency_threshold)
            if breaking_news:
                console.print(f"🚨 {len(breaking_news)} breaking news articles detected!", style="red bold")
                for article in breaking_news[:3]:  # Show top 3
                    console.print(f"   • {article.title[:80]}...", style="red")
            
            if not db_healthy or not cost_healthy or stuck_jobs:
                warning_msg = []
                if not db_healthy:
                    warning_msg.append("Database connection issues")
                if not cost_healthy:
                    warning_msg.append(f"Cost limit exceeded: ${self.stats.total_cost_usd:.2f}")
                if stuck_jobs:
                    warning_msg.append(f"Stuck jobs: {stuck_jobs}")
                    
                logger.warning(f"Health check warnings: {'; '.join(warning_msg)}")
                console.print(f"⚠️  Health warnings: {'; '.join(warning_msg)}", style="yellow")
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")

    async def cost_monitoring_job(self) -> None:
        """Monitor and report cost usage."""
        try:
            daily_cost = self.stats.total_cost_usd
            daily_limit = self.settings.daily_cost_limit
            
            if daily_cost > daily_limit * self.settings.cost_alert_threshold:
                console.print(f"💰 Cost alert: ${daily_cost:.2f} of ${daily_limit:.2f} daily limit", style="yellow")
                logger.warning(f"Daily cost approaching limit: ${daily_cost:.2f}")
            
            # Reset daily stats if needed (simplified - in production use proper date tracking)
            if datetime.utcnow().hour == 0:  # Reset at midnight
                self.stats.total_cost_usd = 0.0
                
        except Exception as e:
            logger.error(f"Cost monitoring failed: {e}")

    def job_listener(self, event) -> None:
        """Handle job execution events."""
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
            self.stats.failed_cycles += 1
        else:
            self.stats.successful_cycles += 1
        
        self.stats.total_cycles += 1

    async def generate_daily_report(self, articles: List[Article], top_articles: List[Article]) -> str:
        """Generate a comprehensive daily report from articles."""
        now = datetime.utcnow()
        
        # Calculate statistics
        analyzed_articles = [a for a in articles if a.is_analyzed]
        avg_relevance = sum(a.relevance_score for a in analyzed_articles) / max(len(analyzed_articles), 1) if analyzed_articles else 0
        avg_quality = sum(a.quality_score for a in analyzed_articles) / max(len(analyzed_articles), 1) if analyzed_articles else 0
        
        # Count by category
        categories = {}
        for article in analyzed_articles:
            if article.primary_category:
                categories[article.primary_category] = categories.get(article.primary_category, 0) + 1
        
        # Generate report
        report = f"""# 🤖 AI News Daily Report - {now.strftime('%Y-%m-%d')}

Generated at: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC

## 📊 Summary Statistics
- **Total Articles**: {len(articles)}
- **Analyzed Articles**: {len(analyzed_articles)}
- **Analysis Completion**: {(len(analyzed_articles)/max(len(articles),1)*100):.1f}%
- **Average Relevance Score**: {avg_relevance:.2f}
- **Average Quality Score**: {avg_quality:.2f}

## 📂 Content Categories
"""
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{category}**: {count} articles\n"
        
        report += "\n## 🏆 Top Articles by Relevance\n\n"
        
        for i, article in enumerate(top_articles, 1):
            source_name = article.source.name if hasattr(article, 'source') and article.source else 'Unknown'
            report += f"### {i}. {article.title}\n"
            report += f"- **Source**: {source_name}\n"
            report += f"- **Published**: {article.published_at.strftime('%Y-%m-%d %H:%M')}\n"
            report += f"- **Relevance**: {article.relevance_score:.2f}\n"
            report += f"- **Quality**: {article.quality_score:.2f}\n"
            if hasattr(article, 'url') and article.url:
                report += f"- **URL**: {article.url}\n"
            if article.summary:
                report += f"- **Summary**: {article.summary[:200]}...\n"
            report += "\n"
        
        report += "\n## 📈 All Recent Articles\n\n"
        
        for i, article in enumerate(sorted(articles, key=lambda x: x.published_at, reverse=True)[:20], 1):
            source_name = article.source.name if hasattr(article, 'source') and article.source else 'Unknown'
            relevance = f" (Relevance: {article.relevance_score:.2f})" if article.is_analyzed else ""
            report += f"{i}. **{article.title}**{relevance}\n"
            report += f"   - Source: {source_name} | Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}\n"
            if hasattr(article, 'url') and article.url:
                report += f"   - URL: {article.url}\n"
            report += "\n"
        
        report += "\n---\n*Report generated by AI News Automation Daemon*\n"
        
        return report

    def display_status(self) -> None:
        """Display current daemon status."""
        
        # Create status table
        table = Table(title="🤖 AI News Automation Daemon Status", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Runtime stats
        runtime = datetime.utcnow() - self.stats.started_at
        table.add_row("Runtime", f"{runtime.days}d {runtime.seconds//3600}h {(runtime.seconds%3600)//60}m")
        table.add_row("Total Cycles", str(self.stats.total_cycles))
        table.add_row("Success Rate", f"{(self.stats.successful_cycles/max(self.stats.total_cycles,1)*100):.1f}%")
        
        # Performance stats
        table.add_row("Articles Fetched", str(self.stats.articles_fetched))
        table.add_row("Articles Analyzed", str(self.stats.articles_analyzed))
        table.add_row("Daily Cost", f"${self.stats.total_cost_usd:.2f}")
        
        # System stats
        table.add_row("Memory Usage", f"{self.stats.current_memory_mb:.1f} MB")
        table.add_row("CPU Usage", f"{self.stats.current_cpu_percent:.1f}%")
        
        # Last operations
        last_rss = self.stats.last_rss_fetch.strftime("%H:%M:%S") if self.stats.last_rss_fetch else "Never"
        last_analysis = self.stats.last_analysis.strftime("%H:%M:%S") if self.stats.last_analysis else "Never"
        
        table.add_row("Last RSS Fetch", last_rss)
        table.add_row("Last Analysis", last_analysis)
        
        if self.stats.last_error:
            table.add_row("Last Error", self.stats.last_error[:50] + "..." if len(self.stats.last_error) > 50 else self.stats.last_error)
        
        console.print(table)

    async def shutdown(self) -> None:
        """Graceful shutdown of the daemon."""
        console.print("🛑 Shutting down daemon...", style="yellow")
        
        # Stop scheduler
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            
        # Wait for running jobs to complete (with timeout)
        timeout = 30
        while any(self.running_jobs.values()) and timeout > 0:
            await asyncio.sleep(1)
            timeout -= 1
        
        console.print("✅ Daemon shutdown complete", style="green")
        logger.info("Daemon shutdown completed")

    async def run(self) -> None:
        """Main daemon run loop."""
        try:
            console.print("🚀 Starting AI News Automation Daemon", style="bold green")
            
            # Setup signal handlers
            for sig in [signal.SIGINT, signal.SIGTERM]:
                signal.signal(sig, lambda s, f: asyncio.create_task(self.handle_signal(s)))
            
            # Setup jobs and start scheduler
            await self.setup_jobs()
            self.scheduler.start()
            
            console.print("⚡ Daemon started successfully! Press Ctrl+C to stop.", style="green")
            logger.info("Daemon started and running")
            
            # Status display loop
            while not self.shutdown_event.is_set():
                try:
                    # Update and display status every 30 seconds
                    self.display_status()
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=30.0)
                except asyncio.TimeoutError:
                    continue  # Normal timeout, continue status updates
                    
        except Exception as e:
            logger.error(f"Daemon run failed: {e}")
            console.print(f"❌ Daemon failed: {e}", style="red")
            raise
        finally:
            await self.shutdown()

    async def handle_signal(self, signum) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_event.set()


async def main():
    """Main entry point."""
    daemon = NewsAutomationDaemon()
    
    try:
        await daemon.run()
    except KeyboardInterrupt:
        console.print("🛑 Received interrupt signal", style="yellow")
    except Exception as e:
        console.print(f"❌ Daemon error: {e}", style="red")
        logger.error(f"Daemon error: {e}")
        traceback.print_exc()
    finally:
        console.print("👋 Daemon stopped", style="blue")


if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)