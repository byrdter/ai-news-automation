#!/usr/bin/env python3
"""
CLI Integration for RSS Article Management

Adds real RSS article fetching to the existing CLI interface.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich import box

from scripts.populate_articles import ArticlePopulator
from scripts.initialize_sources import initialize_sources, show_database_sources
from scripts.test_rss_fetch import test_all_feeds

console = Console()


@click.group()
def rss():
    """RSS and article management commands."""
    pass


@rss.command()
def test_feeds():
    """Test RSS feed connectivity."""
    console.print("[bold cyan]Testing RSS Feed Connectivity[/bold cyan]\n")
    
    async def run_test():
        results = await test_all_feeds()
        
        # Create results table
        table = Table(title="RSS Feed Test Results", box=box.ROUNDED)
        table.add_column("Feed Name", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Articles", justify="right")
        table.add_column("Fetch Time", justify="right")
        
        for result in results:
            status = "✅ Working" if result['success'] else "❌ Failed"
            articles = str(result.get('articles_count', 0))
            fetch_time = f"{result.get('fetch_time', 0):.2f}s" if result.get('fetch_time') else "N/A"
            
            table.add_row(
                result['name'][:30],
                status,
                articles,
                fetch_time
            )
        
        console.print(table)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        total_articles = sum(r.get('articles_count', 0) for r in results)
        
        if successful > 0:
            console.print(f"\n[green]✅ {successful}/{len(results)} feeds working successfully[/green]")
            console.print(f"[green]Total articles available: {total_articles}[/green]")
        else:
            console.print(f"\n[red]❌ No feeds are working properly[/red]")
    
    asyncio.run(run_test())


@rss.command()
def init_sources():
    """Initialize RSS sources in database from config."""
    console.print("[bold cyan]Initializing RSS Sources[/bold cyan]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Loading sources configuration...", total=None)
        
        success = initialize_sources()
        
        if success:
            progress.update(task, description="✅ Sources initialized successfully!")
            console.print("\n[green]RSS sources have been initialized in the database[/green]")
        else:
            progress.update(task, description="❌ Source initialization failed!")
            console.print("\n[red]Failed to initialize RSS sources[/red]")


@rss.command()
def show_sources():
    """Show current RSS sources in database."""
    show_database_sources()


@rss.command()
@click.option("--max-sources", "-m", default=None, type=int, help="Maximum number of sources to process")
@click.option("--test-run", "-t", is_flag=True, help="Test run without saving to database")
def fetch_articles(max_sources, test_run):
    """Fetch articles from RSS sources and populate database."""
    console.print("[bold cyan]Fetching Articles from RSS Sources[/bold cyan]\n")
    
    if test_run:
        console.print("[yellow]⚠️  Test run mode - articles will not be saved to database[/yellow]\n")
    
    async def run_fetch():
        populator = ArticlePopulator()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                
                if test_run:
                    # Just test connectivity
                    task = progress.add_task("Testing RSS feeds...", total=100)
                    results = await test_all_feeds()
                    progress.update(task, completed=100)
                    
                    # Show results
                    table = Table(title="RSS Test Results")
                    table.add_column("Source")
                    table.add_column("Status")
                    table.add_column("Articles")
                    
                    for result in results:
                        status = "✅" if result['success'] else "❌"
                        articles = str(result.get('articles_count', 0))
                        table.add_row(result['name'], status, articles)
                    
                    console.print(table)
                else:
                    # Real article population
                    task = progress.add_task("Fetching and saving articles...", total=100)
                    
                    result = await populator.populate_articles(max_sources=max_sources)
                    
                    progress.update(task, completed=100)
                    
                    if result['success']:
                        # Success summary
                        panel_content = f"""
[green]✅ Article population completed successfully![/green]

📊 **Statistics:**
• Sources processed: {result['sources_processed']}
• Sources successful: {result['sources_successful']}
• New articles saved: {result['new_articles_saved']}
• Duplicate articles skipped: {result['duplicate_articles_skipped']}
• Total articles fetched: {result['total_articles_fetched']}

⏱️  **Performance:**
• Average fetch time: {sum(r.get('fetch_time', 0) for r in result['processing_results']) / len(result['processing_results']):.2f}s per source
                        """.strip()
                        
                        console.print(Panel(panel_content, title="Fetch Complete", border_style="green"))
                        
                        # Show per-source results
                        if result['processing_results']:
                            table = Table(title="Per-Source Results")
                            table.add_column("Source Name")
                            table.add_column("Status")
                            table.add_column("Articles Fetched")
                            table.add_column("Fetch Time")
                            
                            for r in result['processing_results']:
                                status = "✅" if r['success'] else "❌"
                                articles = str(r.get('articles_fetched', 0))
                                fetch_time = f"{r.get('fetch_time', 0):.2f}s" if 'fetch_time' in r else "N/A"
                                
                                table.add_row(r['source_name'][:25], status, articles, fetch_time)
                            
                            console.print(table)
                    else:
                        console.print(f"[red]❌ Article population failed: {result.get('error', 'Unknown error')}[/red]")
        
        finally:
            await populator.cleanup()
    
    asyncio.run(run_fetch())


@rss.command()
@click.option("--source-name", "-s", help="Test specific source by name")
def test_source(source_name):
    """Test fetching from a specific RSS source."""
    if not source_name:
        console.print("[red]Please specify a source name with --source-name[/red]")
        return
    
    console.print(f"[bold cyan]Testing RSS Source: {source_name}[/bold cyan]\n")
    
    populator = ArticlePopulator()
    
    try:
        populator.test_single_source(source_name)
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")


@rss.command()
def status():
    """Show RSS system status and statistics."""
    console.print("[bold cyan]RSS System Status[/bold cyan]\n")
    
    populator = ArticlePopulator()
    
    if not populator.setup_database():
        console.print("[red]❌ Database connection failed[/red]")
        return
    
    try:
        # Get database statistics
        from sqlalchemy import func
        
        with populator.Session() as session:
            # Source statistics
            total_sources = session.query(NewsSource).count()
            active_sources = session.query(NewsSource).filter(NewsSource.active == True).count()
            
            # Article statistics
            total_articles = session.query(Article).count()
            recent_articles = session.query(Article).filter(
                Article.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
            ).count()
            
            # Processing statistics
            processed_articles = session.query(Article).filter(Article.processed == True).count()
            pending_articles = total_articles - processed_articles
            
            # Top sources by article count
            top_sources = session.query(
                NewsSource.name,
                func.count(Article.id).label('article_count')
            ).join(Article).group_by(NewsSource.name).order_by(
                func.count(Article.id).desc()
            ).limit(5).all()
        
        # Status overview
        status_table = Table(title="System Status", box=box.ROUNDED)
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="green", justify="right")
        
        status_table.add_row("Total RSS Sources", str(total_sources))
        status_table.add_row("Active Sources", str(active_sources))
        status_table.add_row("Total Articles", str(total_articles))
        status_table.add_row("Articles Today", str(recent_articles))
        status_table.add_row("Processed Articles", str(processed_articles))
        status_table.add_row("Pending Processing", str(pending_articles))
        
        console.print(status_table)
        
        # Top sources
        if top_sources:
            console.print("\n")
            top_table = Table(title="Top Sources by Article Count", box=box.ROUNDED)
            top_table.add_column("Source Name", style="cyan")
            top_table.add_column("Article Count", justify="right")
            
            for name, count in top_sources:
                top_table.add_row(name, str(count))
            
            console.print(top_table)
    
    except Exception as e:
        console.print(f"[red]❌ Failed to get status: {e}[/red]")


# Add this to the main CLI
def add_rss_commands_to_cli(main_cli):
    """Add RSS commands to main CLI."""
    main_cli.add_command(rss)


if __name__ == "__main__":
    rss()