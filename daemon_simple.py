#!/usr/bin/env python3
"""
Simple AI News Automation Daemon

A minimal version to test basic functionality.
"""

import time
import signal
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from scripts.rss_with_database_save import RSSWithDatabaseSaver

console = Console()

class SimpleAutomationDaemon:
    """Simple automation daemon for testing."""
    
    def __init__(self):
        self.settings = get_settings()
        self.running = True
        self.rss_fetcher = RSSWithDatabaseSaver()
        
        console.print("🤖 Simple AI News Automation Daemon initialized", style="green")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        console.print(f"\n🛑 Received signal {signum}, shutting down...", style="yellow")
        self.running = False

    async def run_rss_cycle(self):
        """Run one RSS fetch cycle."""
        try:
            console.print("🔍 Starting RSS fetch cycle...", style="cyan")
            
            # Setup database connection
            if not self.rss_fetcher.setup_database():
                console.print("❌ Failed to setup database", style="red")
                return False
            
            # Fetch articles
            success, articles = await self.rss_fetcher.fetch_articles_from_rss()
            
            if success and articles:
                console.print(f"✅ Fetched {len(articles)} articles", style="green")
                
                # Save to database
                save_stats = self.rss_fetcher.save_articles_to_database(articles)
                
                console.print(f"📊 Saved: {save_stats['saved']}, Skipped: {save_stats['skipped']}", style="green")
                return True
            else:
                console.print("❌ RSS fetch failed", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ RSS cycle error: {e}", style="red")
            return False

    def run(self):
        """Main daemon run loop."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        console.print("🚀 Simple Daemon Started!", style="bold green")
        console.print("⚡ Running RSS fetch every 10 minutes. Press Ctrl+C to stop.", style="green")
        
        last_fetch = 0
        fetch_interval = 600  # 10 minutes
        
        try:
            while self.running:
                current_time = time.time()
                
                # Check if it's time for RSS fetch
                if current_time - last_fetch >= fetch_interval:
                    import asyncio
                    success = asyncio.run(self.run_rss_cycle())
                    last_fetch = current_time
                    
                    if success:
                        console.print(f"✅ RSS cycle completed at {datetime.now().strftime('%H:%M:%S')}", style="green")
                    else:
                        console.print(f"❌ RSS cycle failed at {datetime.now().strftime('%H:%M:%S')}", style="red")
                
                # Status update every 30 seconds
                time.sleep(30)
                if self.running:
                    next_fetch = int((fetch_interval - (current_time - last_fetch)) / 60)
                    console.print(f"⏱️  Next fetch in ~{next_fetch} minutes", style="cyan")
                
        except KeyboardInterrupt:
            console.print("\n🛑 Interrupted by user", style="yellow")
        finally:
            console.print("👋 Simple daemon stopped", style="blue")

def main():
    """Main entry point."""
    daemon = SimpleAutomationDaemon()
    daemon.run()

if __name__ == "__main__":
    main()