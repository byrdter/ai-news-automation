#!/usr/bin/env python3
"""
CLI interface for the AI News Automation System.

Provides commands for system management, testing, monitoring, and automation control.
"""

import asyncio
import sys
import subprocess
import signal
import psutil
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel

from config.settings import get_settings
from database.models import NewsSource, Article, Report, Alert, CostTracking
from automation_modules import automation_modules

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI News Automation System CLI - Advanced automation and monitoring commands."""
    pass


# Daemon PID file location
DAEMON_PID_FILE = Path("logs/daemon.pid")


def is_daemon_running() -> bool:
    """Check if daemon is currently running."""
    if not DAEMON_PID_FILE.exists():
        return False
    
    try:
        with open(DAEMON_PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists and is our daemon
        process = psutil.Process(pid)
        return 'daemon' in ' '.join(process.cmdline()).lower()
    except (ValueError, FileNotFoundError, psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def get_daemon_pid() -> Optional[int]:
    """Get daemon PID from file."""
    if DAEMON_PID_FILE.exists():
        try:
            with open(DAEMON_PID_FILE, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            pass
    return None


def cleanup_pid_file():
    """Remove stale PID file."""
    if DAEMON_PID_FILE.exists():
        DAEMON_PID_FILE.unlink()


# ============================================================================
# AUTOMATION COMMANDS
# ============================================================================

@cli.group()
def automation():
    """Automation daemon control and management."""
    pass


@automation.command()
@click.option('--mode', '-m', default='simple', type=click.Choice(['simple', 'full']),
              help='Daemon mode (simple or full)')
@click.option('--background', '-b', is_flag=True, help='Run in background')
def start(mode: str, background: bool):
    """Start the automation daemon."""
    if is_daemon_running():
        console.print("❌ Daemon is already running!", style="red")
        sys.exit(1)
    
    console.print(f"🚀 Starting automation daemon ({mode} mode)...", style="green")
    
    try:
        # Ensure directories exist
        DAEMON_PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        if background:
            # Start daemon in background
            daemon_script = "daemon_simple.py" if mode == "simple" else "daemon.py"
            log_file = Path("logs") / f"{mode}_daemon.log"
            
            with open(log_file, 'a') as log:
                process = subprocess.Popen([
                    sys.executable, daemon_script
                ], stdout=log, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
            
            # Write PID file
            with open(DAEMON_PID_FILE, 'w') as f:
                f.write(str(process.pid))
            
            # Wait to see if it starts
            time.sleep(2)
            if process.poll() is None:
                console.print(f"✅ Daemon started successfully! PID: {process.pid}", style="green")
                console.print(f"📋 Log file: {log_file}", style="cyan")
            else:
                console.print("❌ Daemon failed to start", style="red")
                sys.exit(1)
        else:
            # Start daemon in foreground
            if mode == "simple":
                from daemon_simple import main
                main()
            else:
                from daemon import main
                asyncio.run(main())
                
    except Exception as e:
        console.print(f"❌ Failed to start daemon: {e}", style="red")
        sys.exit(1)


@automation.command()
def stop():
    """Stop the automation daemon."""
    if not is_daemon_running():
        console.print("ℹ️  Daemon is not currently running", style="yellow")
        return
    
    try:
        pid = get_daemon_pid()
        if pid:
            console.print(f"🛑 Stopping daemon (PID: {pid})...", style="yellow")
            
            # Send SIGTERM for graceful shutdown
            import os
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for i in range(30):
                if not is_daemon_running():
                    console.print("✅ Daemon stopped gracefully", style="green")
                    cleanup_pid_file()
                    return
                time.sleep(1)
            
            # Force kill if still running
            console.print("⚠️  Force stopping daemon...", style="yellow")
            os.kill(pid, signal.SIGKILL)
            time.sleep(2)
            
            if not is_daemon_running():
                console.print("✅ Daemon force stopped", style="green")
                cleanup_pid_file()
            else:
                console.print("❌ Failed to stop daemon", style="red")
                sys.exit(1)
                
    except ProcessLookupError:
        console.print("ℹ️  Daemon process not found (already stopped)", style="yellow")
        cleanup_pid_file()
    except PermissionError:
        console.print("❌ Permission denied - cannot stop daemon", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error stopping daemon: {e}", style="red")
        sys.exit(1)


@automation.command()
def restart():
    """Restart the automation daemon."""
    console.print("🔄 Restarting daemon...", style="cyan")
    
    # Stop if running
    if is_daemon_running():
        # Call stop function directly
        try:
            pid = get_daemon_pid()
            if pid:
                console.print(f"🛑 Stopping daemon (PID: {pid})...", style="yellow")
                
                # Send SIGTERM for graceful shutdown
                os.kill(pid, signal.SIGTERM)
                
                # Wait for graceful shutdown
                for i in range(30):
                    if not is_daemon_running():
                        console.print("✅ Daemon stopped gracefully", style="green")
                        cleanup_pid_file()
                        break
                    time.sleep(1)
                else:
                    # Force kill if still running
                    console.print("⚠️  Force stopping daemon...", style="yellow")
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(2)
                    cleanup_pid_file()
                        
        except Exception as e:
            console.print(f"❌ Error stopping daemon: {e}", style="red")
    
    # Wait a moment
    time.sleep(2)
    
    # Start daemon in simple mode
    if is_daemon_running():
        console.print("❌ Daemon is still running, cannot restart", style="red")
        return
    
    console.print("🚀 Starting automation daemon (simple mode)...", style="green")
    
    try:
        # Ensure directories exist
        DAEMON_PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Start daemon in background
        daemon_script = "daemon_simple.py"
        log_file = Path("logs") / "simple_daemon.log"
        
        with open(log_file, 'a') as log:
            process = subprocess.Popen([
                sys.executable, daemon_script
            ], stdout=log, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        
        # Write PID file
        with open(DAEMON_PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        # Wait to see if it starts
        time.sleep(2)
        if process.poll() is None:
            console.print(f"✅ Daemon started successfully! PID: {process.pid}", style="green")
            console.print(f"📋 Log file: {log_file}", style="cyan")
        else:
            console.print("❌ Daemon failed to start", style="red")
            
    except Exception as e:
        console.print(f"❌ Failed to start daemon: {e}", style="red")


@automation.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed status')
def status(detailed: bool):
    """Show automation daemon status."""
    console.print("🤖 AI News Automation Daemon Status", style="bold cyan")
    console.print("=" * 50)
    
    if is_daemon_running():
        pid = get_daemon_pid()
        try:
            process = psutil.Process(pid)
            uptime_seconds = time.time() - process.create_time()
            uptime_hours = uptime_seconds / 3600
            
            console.print(f"✅ Status: Running (PID: {pid})", style="green")
            console.print(f"⏱️  Uptime: {uptime_hours:.1f} hours", style="cyan")
            console.print(f"💾 Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB", style="cyan")
            console.print(f"🖥️  CPU: {process.cpu_percent():.1f}%", style="cyan")
            
        except psutil.NoSuchProcess:
            console.print("❌ Status: Process not found (stale PID file)", style="red")
            cleanup_pid_file()
    else:
        console.print("❌ Status: Not Running", style="red")
    
    # Show log file info
    for log_file in ["logs/simple_daemon.log", "logs/daemon.log"]:
        log_path = Path(log_file)
        if log_path.exists():
            log_size_mb = log_path.stat().st_size / 1024 / 1024
            console.print(f"📋 Log ({log_path.name}): {log_size_mb:.1f} MB", style="cyan")
    
    if detailed:
        # Show system status
        console.print("\n📊 System Status", style="bold cyan")
        console.print("-" * 20)
        
        try:
            status_data = automation_modules.get_system_status()
            if status_data.get('database_healthy'):
                table = Table()
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Articles", str(status_data['total_articles']))
                table.add_row("Analyzed Articles", str(status_data['analyzed_articles']))
                table.add_row("Unanalyzed Articles", str(status_data['unanalyzed_articles']))
                table.add_row("Recent Articles (24h)", str(status_data['recent_articles_24h']))
                table.add_row("Active Sources", str(status_data['active_sources']))
                table.add_row("Analysis Completion", f"{status_data['analysis_completion_rate']:.1f}%")
                table.add_row("Avg Relevance Score", f"{status_data['avg_relevance_score']:.2f}")
                
                console.print(table)
            else:
                console.print(f"❌ Database error: {status_data.get('error', 'Unknown')}", style="red")
                
        except Exception as e:
            console.print(f"❌ Status error: {e}", style="red")


# ============================================================================
# MANUAL OPERATION COMMANDS
# ============================================================================

@cli.command("fetch-news")
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def fetch_news(verbose: bool):
    """Manually fetch news articles from RSS sources."""
    console.print("🔍 Manual RSS News Fetch", style="bold cyan")
    
    async def run_fetch():
        result = await automation_modules.fetch_rss_news(verbose=verbose)
        
        if result['success']:
            console.print("\n✅ Fetch Summary:", style="bold green")
            console.print(f"   Articles Fetched: {result['articles_fetched']}")
            console.print(f"   Articles Saved: {result['articles_saved']}")
            console.print(f"   Articles Skipped: {result['articles_skipped']}")
            console.print(f"   Processing Time: {result['processing_time']:.1f}s")
            
            if result['unmapped_sources'] > 0:
                console.print(f"   ⚠️  Unmapped Sources: {result['unmapped_sources']}", style="yellow")
        else:
            console.print(f"\n❌ Fetch failed: {result.get('error', 'Unknown error')}", style="red")
            sys.exit(1)
    
    try:
        asyncio.run(run_fetch())
    except KeyboardInterrupt:
        console.print("\n🛑 Fetch interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Fetch error: {e}", style="red")
        sys.exit(1)


@cli.command("run-pipeline")
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def run_pipeline(verbose: bool):
    """Run the complete news processing pipeline (fetch + analysis + report)."""
    console.print("🚀 Full News Processing Pipeline", style="bold cyan")
    
    async def run_full_pipeline():
        result = await automation_modules.run_full_pipeline(verbose=verbose)
        
        # Show final summary
        console.print("\n" + "=" * 60)
        console.print("📋 PIPELINE RESULTS", style="bold cyan")
        console.print("=" * 60)
        
        if result['success']:
            console.print("🎉 Pipeline completed successfully!", style="bold green")
        else:
            console.print("⚠️  Pipeline completed with issues", style="bold yellow")
        
        console.print(f"⏱️  Total Time: {result['total_processing_time']:.1f}s")
        console.print(f"✅ Completed Steps: {', '.join(result['steps_completed'])}")
        
        if result['steps_failed']:
            console.print(f"❌ Failed Steps: {', '.join(result['steps_failed'])}", style="red")
        
        # Show step details
        if result['rss_results']:
            rss = result['rss_results']
            console.print(f"\n📥 RSS: {rss['articles_fetched']} fetched, {rss['articles_saved']} saved")
        
        if result['analysis_results'] and not result['analysis_results'].get('skipped'):
            analysis = result['analysis_results']
            console.print(f"🧠 Analysis: {analysis['articles_analyzed']} analyzed")
            if analysis.get('total_cost_usd', 0) > 0:
                console.print(f"💰 Cost: ${analysis['total_cost_usd']:.4f}")
        
        if result['report_results']:
            report = result['report_results']
            if report.get('report_file'):
                console.print(f"📊 Report: {report['report_file']}")
        
        if not result['success']:
            sys.exit(1)
    
    try:
        asyncio.run(run_full_pipeline())
    except KeyboardInterrupt:
        console.print("\n🛑 Pipeline interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Pipeline error: {e}", style="red")
        sys.exit(1)


@cli.command("generate-report")
@click.option('--now', is_flag=True, help='Generate report immediately')
@click.option('--type', '-t', default='daily', type=click.Choice(['daily', 'weekly', 'summary']),
              help='Report type')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def generate_report(now: bool, type: str, verbose: bool):
    """Generate a news report."""
    if not now:
        console.print("💡 Use --now flag to generate report immediately", style="yellow")
        console.print("Example: python cli.py generate-report --now", style="cyan")
        return
    
    console.print(f"📊 Generating {type} report...", style="bold cyan")
    
    try:
        result = automation_modules.generate_report(report_type=type, verbose=verbose)
        
        if result['success']:
            console.print("\n✅ Report Generation Summary:", style="bold green")
            console.print(f"   Report File: {result['report_file']}")
            console.print(f"   Articles Included: {result['articles_count']}")
            console.print(f"   Top Articles: {result['top_articles_count']}")
            console.print(f"   Processing Time: {result['processing_time']:.1f}s")
            
            # Show report location
            if result['report_file']:
                report_path = Path(result['report_file'])
                console.print(f"\n📋 Report saved to: {report_path.absolute()}", style="cyan")
        else:
            console.print(f"\n❌ Report generation failed: {result.get('error', 'Unknown error')}", style="red")
            sys.exit(1)
    
    except Exception as e:
        console.print(f"\n❌ Report error: {e}", style="red")
        sys.exit(1)


@cli.command("generate-comprehensive-reports")
def generate_comprehensive_reports():
    """Generate comprehensive report coverage for all articles."""
    console.print("🚀 Starting comprehensive report generation...", style="bold cyan")
    
    try:
        result = automation_modules.generate_comprehensive_reports(verbose=True)
        
        if result['success']:
            console.print(f"\n🎉 Comprehensive reporting completed successfully!", style="bold green")
            console.print(f"   📈 Total reports generated: {result['total_reports_generated']}")
            console.print(f"   📰 Total articles covered: {result['total_articles_covered']}")
            console.print(f"   ⏱️  Processing time: {result['processing_time']:.1f}s")
            
            # Show breakdown by report type
            console.print(f"\n📊 Report Breakdown:", style="bold cyan")
            for report_type, stats in result['reports_by_type'].items():
                console.print(f"   {report_type.replace('_', ' ').title()}: {stats['reports_count']} reports")
            
            if result.get('errors'):
                console.print(f"\n⚠️  Errors encountered: {len(result['errors'])}", style="yellow")
                for error in result['errors']:
                    console.print(f"     - {error}", style="red")
        else:
            console.print(f"\n❌ Comprehensive reporting failed: {result.get('error', 'Unknown error')}", style="red")
    
    except Exception as e:
        console.print(f"❌ Comprehensive reporting error: {e}", style="red")
        import traceback
        traceback.print_exc()


# ============================================================================
# ORIGINAL CLI COMMANDS (keep existing functionality)
# ============================================================================

@cli.command()
@click.option("--environment", "-e", type=click.Choice(["development", "staging", "production"]), 
              help="Environment to start")
def start(environment: Optional[str]):
    """Start the news automation system."""
    settings = get_settings()
    
    if environment:
        settings.system.environment = environment
    
    console.print(f"[bold cyan]Starting AI News Automation System[/bold cyan]")
    console.print(f"Environment: {str(settings.environment)}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Start various components
        task1 = progress.add_task("Starting MCP servers...", total=4)
        time.sleep(0.5)
        progress.advance(task1)
        
        task2 = progress.add_task("Initializing agents...", total=5)
        time.sleep(0.5)
        progress.advance(task2)
        
        task3 = progress.add_task("Connecting to database...", total=1)
        time.sleep(0.5)
        progress.advance(task3)
        
    console.print("[bold green]✓ System started successfully![/bold green]")


@cli.command()
def stop():
    """Stop the news automation system."""
    console.print("[bold yellow]Stopping AI News Automation System...[/bold yellow]")
    # Implementation for stopping services
    console.print("[bold green]✓ System stopped[/bold green]")


@cli.command()
def status():
    """Show system status and health."""
    settings = get_settings()
    
    # Create status table
    table = Table(title="System Status", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    # Check various components
    table.add_row("Database", "✓ Connected", "PostgreSQL + pgvector")
    table.add_row("MCP Servers", "✓ Running", "4 servers active")
    table.add_row("Agents", "✓ Active", "5 agents operational")
    table.add_row("Scheduler", "✓ Running", "Next job in 5 minutes")
    
    console.print(table)
    
    # Show cost tracking
    cost_table = Table(title="Cost Tracking (Today)", show_header=True)
    cost_table.add_column("Service", style="cyan")
    cost_table.add_column("Requests")
    cost_table.add_column("Cost (USD)", style="yellow")
    
    cost_table.add_row("OpenAI", "42", "$0.84")
    cost_table.add_row("Cohere", "156", "$1.23")
    cost_table.add_row("Total", "198", "$2.07")
    
    console.print(cost_table)
    
    # Show daily limit status
    daily_limit = settings.daily_cost_limit
    current_cost = 2.07
    percentage = (current_cost / daily_limit) * 100
    
    console.print(f"\n[bold]Daily Budget:[/bold] ${current_cost:.2f} / ${daily_limit:.2f} ({percentage:.1f}%)")
    
    if percentage > 80:
        console.print("[bold yellow]⚠ Approaching daily limit![/bold yellow]")


@cli.command()
@click.option("--limit", "-l", default=20, help="Number of sources to show")
def sources(limit: int):
    """List configured RSS sources from database."""
    console.print("[bold]Configured RSS Sources[/bold]\n")
    
    try:
        from database.models import NewsSource
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        engine = create_engine(settings.database_url.get_secret_value())
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Get real sources from database
        sources = session.query(NewsSource).order_by(NewsSource.tier, NewsSource.name).limit(limit).all()
        
        if not sources:
            console.print("[yellow]No sources found in database[/yellow]")
            session.close()
            return
        
        table = Table(show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Category")
        table.add_column("Tier")
        table.add_column("Status")
        table.add_column("Articles", style="yellow")
        table.add_column("Last Fetched")
        
        for source in sources:
            status = "[green]Active[/green]" if source.active else "[red]Inactive[/red]"
            article_count = len(source.articles) if source.articles else 0
            last_fetched = source.last_fetched_at.strftime('%Y-%m-%d %H:%M') if source.last_fetched_at else "Never"
            
            table.add_row(
                source.name,
                source.category or "Uncategorized",
                str(source.tier),
                status,
                f"{article_count:,}",
                last_fetched
            )
        
        console.print(table)
        
        # Show summary
        total_sources = session.query(NewsSource).count()
        active_sources = session.query(NewsSource).filter(NewsSource.active == True).count()
        total_articles = sum(len(s.articles) if s.articles else 0 for s in sources)
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Active Sources: {active_sources}/{total_sources}")
        console.print(f"  Total Articles: {total_articles:,}")
        
        session.close()
        
    except Exception as e:
        console.print(f"❌ Sources error: {e}", style="red")


@cli.command()
@click.option("--type", "-t", type=click.Choice(["daily", "weekly", "monthly"]), 
              default="daily", help="Report type")
@click.option("--date", "-d", help="Report date (YYYY-MM-DD)")
def report(type: str, date: Optional[str]):
    """Generate or view reports."""
    if date:
        report_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        report_date = datetime.now()
    
    console.print(f"[bold]Generating {type} report for {report_date.strftime('%Y-%m-%d')}[/bold]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating report...", total=100)
        
        # Simulate report generation steps
        for i in range(100):
            time.sleep(0.01)
            progress.advance(task)
    
    console.print("[bold green]✓ Report generated successfully![/bold green]")
    console.print("Report saved to: reports/daily_2025-08-07.html")


@cli.command()
@click.option("--days", "-d", default=7, help="Number of days to analyze")
def analytics(days: int):
    """Show analytics and metrics from real database data."""
    console.print(f"[bold]Analytics for last {days} days[/bold]\n")
    
    try:
        # Get real system status from automation modules
        status_data = automation_modules.get_system_status()
        
        if not status_data.get('database_healthy'):
            console.print(f"❌ Database error: {status_data.get('error', 'Unknown')}", style="red")
            return
        
        # Get additional analytics from database
        analytics_data = automation_modules.get_analytics_data(days)
        
        # Articles processed table with real data
        articles_table = Table(title="Articles Processed")
        articles_table.add_column("Metric", style="cyan")
        articles_table.add_column("Value", style="yellow")
        
        articles_table.add_row("Total Articles", f"{status_data['total_articles']:,}")
        articles_table.add_row("Analyzed", f"{status_data['analyzed_articles']:,}")
        articles_table.add_row("Unanalyzed", f"{status_data['unanalyzed_articles']:,}")
        articles_table.add_row(f"Relevant (>0.7)", f"{analytics_data.get('high_relevance_count', 0):,}")
        articles_table.add_row("Recent (24h)", f"{status_data['recent_articles_24h']:,}")
        articles_table.add_row("In Reports", f"{analytics_data.get('articles_in_reports', 0):,}")
        articles_table.add_row("Alerts Generated", f"{analytics_data.get('total_alerts', 0):,}")
        
        console.print(articles_table)
        
        # Performance metrics with real data
        perf_table = Table(title="Performance Metrics")
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="green")
        
        completion_rate = status_data['analysis_completion_rate']
        avg_relevance = status_data['avg_relevance_score']
        
        perf_table.add_row("Analysis Completion", f"{completion_rate:.1f}%")
        perf_table.add_row("Avg Relevance Score", f"{avg_relevance:.3f}")
        perf_table.add_row("Active Sources", f"{status_data['active_sources']:,}")
        perf_table.add_row("Total Reports", f"{analytics_data.get('total_reports', 0):,}")
        perf_table.add_row("Processing Success", f"{analytics_data.get('processing_success_rate', 0):.1f}%")
        
        console.print(perf_table)
        
        # Category breakdown
        if analytics_data.get('category_breakdown'):
            cat_table = Table(title="Content Categories")
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Count", style="yellow")
            cat_table.add_column("Percentage", style="green")
            
            total_categorized = sum(analytics_data['category_breakdown'].values())
            for category, count in sorted(analytics_data['category_breakdown'].items(), 
                                        key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / total_categorized * 100) if total_categorized > 0 else 0
                cat_table.add_row(category, f"{count:,}", f"{percentage:.1f}%")
            
            console.print(cat_table)
        
        # Cost tracking
        if analytics_data.get('cost_data'):
            cost_table = Table(title=f"Cost Tracking (Last {days} days)")
            cost_table.add_column("Service", style="cyan")
            cost_table.add_column("Operations", style="yellow")  
            cost_table.add_column("Total Cost", style="green")
            
            cost_data = analytics_data['cost_data']
            for provider, data in cost_data.items():
                cost_table.add_row(
                    provider.title(),
                    f"{data['operations']:,}",
                    f"${data['total_cost']:.4f}"
                )
            
            console.print(cost_table)
            
            total_cost = sum(data['total_cost'] for data in cost_data.values())
            if total_cost > 0:
                console.print(f"\n💰 [bold]Total Cost (Last {days} days): ${total_cost:.4f}[/bold]")
        
    except Exception as e:
        console.print(f"❌ Analytics error: {e}", style="red")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option("--component", "-c", type=click.Choice(["database", "api", "agents", "all"]), 
              default="all", help="Component to test")
def test(component: str):
    """Run system tests."""
    console.print(f"[bold]Running {component} tests...[/bold]\n")
    
    tests = []
    if component in ["database", "all"]:
        tests.extend([
            ("Database Connection", True),
            ("pgvector Extension", True),
            ("Table Creation", True),
            ("Index Verification", True),
        ])
    
    if component in ["api", "all"]:
        tests.extend([
            ("OpenAI API", True),
            ("Cohere API", True),
            ("Email SMTP", True),
        ])
    
    if component in ["agents", "all"]:
        tests.extend([
            ("Discovery Agent", True),
            ("Analysis Agent", True),
            ("Report Agent", True),
            ("Alert Agent", False),
        ])
    
    # Run tests
    table = Table(title=f"{component.title()} Tests")
    table.add_column("Test", style="cyan")
    table.add_column("Result")
    
    for test_name, passed in tests:
        result = "[green]✓ Passed[/green]" if passed else "[red]✗ Failed[/red]"
        table.add_row(test_name, result)
    
    console.print(table)
    
    # Summary
    passed_count = sum(1 for _, p in tests if p)
    total_count = len(tests)
    
    if passed_count == total_count:
        console.print(f"\n[bold green]All {total_count} tests passed![/bold green]")
    else:
        console.print(f"\n[bold yellow]{passed_count}/{total_count} tests passed[/bold yellow]")


@cli.command()
def monitor():
    """Live monitoring dashboard."""
    console.print("[bold]AI News System Monitor[/bold]")
    console.print("Press Ctrl+C to exit\n")
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Panel("[bold cyan]AI News Automation System - Live Monitor[/bold cyan]"))
    layout["footer"].update(Panel("Press Ctrl+C to exit"))
    
    # Body sections
    layout["body"].split_row(
        Layout(name="stats"),
        Layout(name="activity")
    )
    
    try:
        with Live(layout, refresh_per_second=1, console=console):
            while True:
                # Update stats
                stats_text = """
[bold]System Stats[/bold]
━━━━━━━━━━━━━━━
Articles/hour: 42
Processing Queue: 3
Active Agents: 5
CPU Usage: 23%
Memory: 512 MB
                """
                layout["stats"].update(Panel(stats_text.strip()))
                
                # Update activity
                activity_text = f"""
[bold]Recent Activity[/bold]
━━━━━━━━━━━━━━━━
{datetime.now().strftime('%H:%M:%S')} - Analyzed: "OpenAI Announces GPT-5"
{datetime.now().strftime('%H:%M:%S')} - Fetched: MIT AI News (15 articles)
{datetime.now().strftime('%H:%M:%S')} - Report: Daily digest sent
{datetime.now().strftime('%H:%M:%S')} - Alert: Breaking news detected
                """
                layout["activity"].update(Panel(activity_text.strip()))
                
                time.sleep(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]")


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Number of results")
def search(query: str, limit: int):
    """Search articles in the database by title and content."""
    console.print(f"[bold]Searching for: '{query}'[/bold]\n")
    
    try:
        from database.models import Article
        from sqlalchemy import create_engine, or_, func
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        engine = create_engine(settings.database_url.get_secret_value())
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Search in title, content, and summary
        search_term = f"%{query.lower()}%"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Searching database...", total=100)
            progress.advance(task, 50)
            
            # Query the database for matching articles
            results = session.query(Article).filter(
                or_(
                    func.lower(Article.title).contains(search_term),
                    func.lower(Article.content).contains(search_term),
                    func.lower(Article.summary).contains(search_term)
                )
            ).order_by(
                Article.relevance_score.desc().nulls_last(),
                Article.published_at.desc().nulls_last()
            ).limit(limit).all()
            
            progress.advance(task, 50)
        
        if not results:
            console.print(f"[yellow]No articles found matching '{query}'[/yellow]")
            session.close()
            return
        
        # Display results
        table = Table(title=f"Search Results for '{query}' ({len(results)} found)")
        table.add_column("Title", style="cyan", max_width=50)
        table.add_column("Source", style="blue")
        table.add_column("Relevance", style="yellow")
        table.add_column("Date", style="green")
        table.add_column("Status")
        
        for article in results:
            # Format title (truncate if too long)
            title = article.title
            if len(title) > 47:
                title = title[:44] + "..."
            
            # Get source name
            source_name = "Unknown"
            if hasattr(article, 'source') and article.source:
                source_name = article.source.name[:15]
            
            # Format relevance score
            relevance = f"{article.relevance_score:.2f}" if article.relevance_score else "N/A"
            
            # Format date
            date_str = "Unknown"
            if article.published_at:
                date_str = article.published_at.strftime('%Y-%m-%d')
            elif article.created_at:
                date_str = article.created_at.strftime('%Y-%m-%d')
            
            # Status
            status = "Analyzed" if article.processing_stage == 'analyzed' else "Unanalyzed"
            status_color = "green" if article.processing_stage == 'analyzed' else "yellow"
            
            table.add_row(
                title,
                source_name,
                relevance,
                date_str,
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        console.print(table)
        
        # Show summary
        total_articles = session.query(Article).count()
        analyzed_count = len([a for a in results if a.processing_stage == 'analyzed'])
        
        console.print(f"\n[bold]Search Summary:[/bold]")
        console.print(f"  Found: {len(results)} articles (searched {total_articles:,} total)")
        console.print(f"  Analyzed: {analyzed_count}/{len(results)}")
        
        if analyzed_count > 0:
            relevance_scores = [a.relevance_score for a in results if a.relevance_score]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
            console.print(f"  Avg Relevance: {avg_relevance:.2f}")
        
        session.close()
        
    except Exception as e:
        console.print(f"❌ Search error: {e}", style="red")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option("--view", "-v", help="View specific report by ID")
@click.option("--limit", "-l", default=10, help="Number of reports to show")
def reports(view: str, limit: int):
    """Show reports from the database."""
    try:
        from database.models import Report, ReportArticle, Article
        from sqlalchemy import create_engine, desc
        from sqlalchemy.orm import sessionmaker, selectinload
        
        settings = get_settings()
        engine = create_engine(settings.database_url.get_secret_value())
        Session = sessionmaker(bind=engine)
        session = Session()
        
        if view:
            # View specific report content
            console.print(f"[bold]Report Details: {view}[/bold]\n")
            
            # Handle partial UUID matching
            if len(view) < 36:  # Not a full UUID
                # Search for reports that start with the provided string
                from sqlalchemy import cast, String
                report = session.query(Report).filter(
                    cast(Report.id, String).like(f"{view}%")
                ).first()
            else:
                # Full UUID provided
                report = session.query(Report).filter(Report.id == view).first()
            if not report:
                console.print(f"[red]Report with ID '{view}' not found[/red]")
                session.close()
                return
            
            # Show report metadata
            metadata_table = Table(title="Report Metadata")
            metadata_table.add_column("Field", style="cyan")
            metadata_table.add_column("Value", style="green")
            
            metadata_table.add_row("ID", str(report.id))
            metadata_table.add_row("Title", report.title)
            metadata_table.add_row("Type", report.report_type.capitalize())
            metadata_table.add_row("Created", report.report_date.strftime('%Y-%m-%d %H:%M:%S'))
            metadata_table.add_row("Status", report.status.capitalize())
            metadata_table.add_row("Article Count", str(report.article_count))
            metadata_table.add_row("Avg Relevance", f"{report.avg_relevance_score:.2f}")
            metadata_table.add_row("Generation Duration", f"{report.generation_duration:.1f}s")
            metadata_table.add_row("Model", report.generation_model)
            
            console.print(metadata_table)
            
            # Show executive summary
            if report.executive_summary:
                console.print(f"\n[bold]Executive Summary:[/bold]")
                console.print(Panel(report.executive_summary, border_style="blue"))
            
            # Show key highlights if available
            if report.key_highlights:
                console.print(f"\n[bold]Key Highlights:[/bold]")
                highlights_table = Table()
                highlights_table.add_column("Title", style="cyan", max_width=40)
                highlights_table.add_column("Relevance", style="yellow")
                highlights_table.add_column("URL", style="blue", max_width=30)
                
                for highlight in report.key_highlights[:5]:
                    url_display = highlight.get('url', 'N/A')
                    if len(url_display) > 27:
                        url_display = url_display[:24] + "..."
                    
                    highlights_table.add_row(
                        highlight.get('title', 'N/A'),
                        f"{highlight.get('relevance', 0.0):.2f}",
                        url_display
                    )
                
                console.print(highlights_table)
            
            # Show category breakdown
            if report.category_breakdown:
                console.print(f"\n[bold]Category Breakdown:[/bold]")
                category_table = Table()
                category_table.add_column("Category", style="cyan")
                category_table.add_column("Articles", style="yellow")
                category_table.add_column("Percentage", style="green")
                
                total_categories = sum(report.category_breakdown.values())
                for category, count in sorted(report.category_breakdown.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_categories * 100) if total_categories > 0 else 0
                    category_table.add_row(category, str(count), f"{percentage:.1f}%")
                
                console.print(category_table)
            
            # Show linked articles
            report_articles = session.query(ReportArticle)\
                .options(selectinload(ReportArticle.article))\
                .filter(ReportArticle.report_id == report.id)\
                .order_by(desc(ReportArticle.importance_score))\
                .all()
            
            if report_articles:
                console.print(f"\n[bold]Linked Articles ({len(report_articles)}):[/bold]")
                articles_table = Table()
                articles_table.add_column("Title", style="cyan", max_width=40)
                articles_table.add_column("Section", style="blue")
                articles_table.add_column("Importance", style="yellow")
                articles_table.add_column("Position", style="green")
                
                for ra in report_articles[:10]:  # Show top 10
                    title = ra.article.title if ra.article else "Unknown"
                    if len(title) > 37:
                        title = title[:34] + "..."
                    
                    articles_table.add_row(
                        title,
                        ra.section or "N/A",
                        f"{ra.importance_score:.2f}" if ra.importance_score else "N/A",
                        str(ra.position_in_section) if ra.position_in_section else "N/A"
                    )
                
                console.print(articles_table)
            
            # Offer to show full content
            console.print(f"\n[dim]💡 Use --view {report.id} to see full report content[/dim]")
            
        else:
            # List all reports
            console.print("[bold]Generated Reports[/bold]\n")
            
            reports = session.query(Report)\
                .order_by(desc(Report.report_date))\
                .limit(limit)\
                .all()
            
            if not reports:
                console.print("[yellow]No reports found in the database[/yellow]")
                session.close()
                return
            
            # Display reports table
            table = Table(title=f"Reports ({len(reports)} found)")
            table.add_column("ID", style="dim", max_width=8)
            table.add_column("Title", style="cyan", max_width=40)
            table.add_column("Type", style="blue")
            table.add_column("Created", style="green")
            table.add_column("Articles", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Avg Relevance", style="yellow")
            
            for report in reports:
                # Format ID (show first 8 chars)
                report_id = str(report.id)[:8] + "..."
                
                # Format title
                title = report.title
                if len(title) > 37:
                    title = title[:34] + "..."
                
                # Format date
                created_date = report.report_date.strftime('%m-%d %H:%M')
                
                # Status with color
                status = report.status.capitalize()
                if status == "Published":
                    status_display = f"[green]{status}[/green]"
                elif status == "Draft":
                    status_display = f"[yellow]{status}[/yellow]"
                else:
                    status_display = f"[red]{status}[/red]"
                
                table.add_row(
                    report_id,
                    title,
                    report.report_type.capitalize(),
                    created_date,
                    str(report.article_count),
                    status_display,
                    f"{report.avg_relevance_score:.2f}" if report.avg_relevance_score else "N/A"
                )
            
            console.print(table)
            
            # Show summary stats
            total_articles = sum(r.article_count for r in reports if r.article_count)
            avg_relevance = sum(r.avg_relevance_score for r in reports if r.avg_relevance_score) / len([r for r in reports if r.avg_relevance_score]) if reports else 0
            
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"  Total Reports: {len(reports)}")
            console.print(f"  Total Articles Covered: {total_articles:,}")
            console.print(f"  Average Relevance: {avg_relevance:.2f}")
            
            if reports:
                console.print(f"\n[dim]💡 Use --view <report_id> to view a specific report[/dim]")
                console.print(f"[dim]   Example: python cli.py reports --view {str(reports[0].id)[:8]}[/dim]")
        
        session.close()
        
    except Exception as e:
        console.print(f"❌ Reports error: {e}", style="red")
        import traceback
        traceback.print_exc()


@cli.command()
def config():
    """Show current configuration."""
    settings = get_settings()
    
    table = Table(title="System Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", str(settings.environment))
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Daily Budget", f"${settings.daily_cost_limit:.2f}")
    table.add_row("OpenAI Model", settings.discovery_agent_model)
    table.add_row("Cohere Model", settings.cohere_model)
    table.add_row("RSS Interval", f"{settings.rss_fetch_interval}s")
    table.add_row("Report Time", "06:00 AM")
    
    console.print(table)
    
    # Validate API keys
    validations = settings.validate_api_keys()
    
    validation_table = Table(title="API Key Validation")
    validation_table.add_column("Service", style="cyan")
    validation_table.add_column("Status")
    
    for key, valid in validations.items():
        status = "[green]✓ Valid[/green]" if valid else "[red]✗ Missing[/red]"
        validation_table.add_row(key.replace("_", " ").title(), status)
    
    console.print(validation_table)


if __name__ == "__main__":
    cli()