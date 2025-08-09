#!/usr/bin/env python3
"""
Quick RSS Test Script

One-command test to verify RSS fetching is working end-to-end.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

async def quick_test():
    """Run a quick end-to-end test of RSS fetching."""
    console.print(Panel.fit(
        "[bold cyan]AI News Automation System - RSS Quick Test[/bold cyan]",
        border_style="cyan"
    ))
    
    tests_passed = 0
    total_tests = 4
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Test 1: Import test
        task1 = progress.add_task("Testing imports...", total=None)
        try:
            from mcp_servers.rss_aggregator import fetch_rss_feed, FeedFetchRequest
            from config.settings import get_settings
            from database.models import NewsSource, Article
            
            progress.update(task1, description="✅ Imports successful")
            tests_passed += 1
        except Exception as e:
            progress.update(task1, description=f"❌ Import failed: {e}")
        
        await asyncio.sleep(0.5)
        
        # Test 2: Settings test
        task2 = progress.add_task("Testing configuration...", total=None)
        try:
            settings = get_settings()
            if hasattr(settings, 'database') and settings.database.host:
                progress.update(task2, description="✅ Configuration loaded")
                tests_passed += 1
            else:
                progress.update(task2, description="❌ Configuration incomplete")
        except Exception as e:
            progress.update(task2, description=f"❌ Configuration failed: {e}")
        
        await asyncio.sleep(0.5)
        
        # Test 3: RSS fetch test
        task3 = progress.add_task("Testing RSS fetch...", total=None)
        try:
            # Test with a reliable RSS feed
            request = FeedFetchRequest(
                feed_url="https://huggingface.co/blog/feed.xml",
                max_articles=5,
                timeout=15
            )
            
            result = await fetch_rss_feed(request)
            
            if result.error:
                progress.update(task3, description=f"❌ RSS fetch failed: {result.error}")
            elif len(result.articles) > 0:
                progress.update(task3, description=f"✅ RSS fetch successful ({len(result.articles)} articles)")
                tests_passed += 1
            else:
                progress.update(task3, description="❌ RSS fetch returned no articles")
                
        except Exception as e:
            progress.update(task3, description=f"❌ RSS fetch error: {e}")
        
        await asyncio.sleep(0.5)
        
        # Test 4: Database connection test
        task4 = progress.add_task("Testing database connection...", total=None)
        try:
            from scripts.populate_articles import ArticlePopulator
            populator = ArticlePopulator()
            
            if populator.setup_database():
                progress.update(task4, description="✅ Database connection successful")
                tests_passed += 1
            else:
                progress.update(task4, description="❌ Database connection failed")
        except Exception as e:
            progress.update(task4, description=f"❌ Database error: {e}")
    
    # Results summary
    console.print("\n")
    
    if tests_passed == total_tests:
        panel_content = f"""
[green]🎉 All systems operational![/green]

✅ All {total_tests} tests passed
✅ RSS fetching system is ready
✅ Database connection working
✅ Configuration loaded successfully

[bold]Ready to fetch real articles![/bold]

Next steps:
1. Initialize sources: [cyan]python scripts/initialize_sources.py --init[/cyan]
2. Fetch articles: [cyan]python scripts/populate_articles.py --max-sources 3[/cyan]
3. Check results: [cyan]python scripts/cli_integration.py rss status[/cyan]
        """
        console.print(Panel(panel_content.strip(), title="Test Results", border_style="green"))
        
    elif tests_passed >= 2:
        panel_content = f"""
[yellow]⚠️ Partial functionality[/yellow]

✅ {tests_passed}/{total_tests} tests passed
⚠️  Some components need attention

The RSS system may work with some limitations.
Check the test output above for specific issues.

You can try running:
[cyan]python scripts/test_rss_fetch.py[/cyan]
        """
        console.print(Panel(panel_content.strip(), title="Test Results", border_style="yellow"))
        
    else:
        panel_content = f"""
[red]❌ System needs setup[/red]

❌ {tests_passed}/{total_tests} tests passed
❌ RSS system is not ready

Please check:
1. Virtual environment activated
2. Dependencies installed: [cyan]pip install -r requirements.txt[/cyan]
3. .env file configured with database settings
4. Running from project root directory

Refer to SETUP_RSS.md for detailed setup instructions.
        """
        console.print(Panel(panel_content.strip(), title="Test Results", border_style="red"))
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)