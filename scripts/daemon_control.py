#!/usr/bin/env python3
"""
AI News Automation Daemon Control Script

Provides commands to start, stop, status, and manage the daemon process.
"""

import argparse
import asyncio
import os
import signal
import sys
import time
import psutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from daemon_database import DaemonDatabase

console = Console()

# Daemon process management
DAEMON_PID_FILE = project_root / "logs" / "daemon.pid"
DAEMON_LOG_FILE = project_root / "logs" / "daemon.log"


class DaemonController:
    """Controller for managing the AI News Automation Daemon."""

    @staticmethod
    def start_daemon(background: bool = True) -> bool:
        """
        Start the daemon process.
        
        Args:
            background: If True, run as background process
            
        Returns:
            True if started successfully, False otherwise
        """
        # Check if daemon is already running
        if DaemonController.is_daemon_running():
            console.print("❌ Daemon is already running!", style="red")
            return False
        
        console.print("🚀 Starting AI News Automation Daemon...", style="green")
        
        try:
            # Ensure directories exist
            DAEMON_PID_FILE.parent.mkdir(parents=True, exist_ok=True)
            DAEMON_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            if background:
                # Start daemon in background
                import subprocess
                
                daemon_script = project_root / "daemon.py"
                process = subprocess.Popen([
                    sys.executable, str(daemon_script)
                ], stdout=open(DAEMON_LOG_FILE, 'a'), 
                   stderr=subprocess.STDOUT,
                   preexec_fn=os.setsid)
                
                # Write PID file
                with open(DAEMON_PID_FILE, 'w') as f:
                    f.write(str(process.pid))
                
                # Wait a moment to see if it starts successfully
                time.sleep(2)
                
                if process.poll() is None:  # Still running
                    console.print(f"✅ Daemon started successfully! PID: {process.pid}", style="green")
                    console.print(f"📋 Log file: {DAEMON_LOG_FILE}", style="cyan")
                    return True
                else:
                    console.print("❌ Daemon failed to start", style="red")
                    return False
            else:
                # Start daemon in foreground
                from daemon import main
                asyncio.run(main())
                return True
                
        except Exception as e:
            console.print(f"❌ Failed to start daemon: {e}", style="red")
            return False

    @staticmethod
    def stop_daemon() -> bool:
        """
        Stop the daemon process.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not DaemonController.is_daemon_running():
            console.print("ℹ️  Daemon is not currently running", style="yellow")
            return True
        
        try:
            pid = DaemonController.get_daemon_pid()
            if pid:
                console.print(f"🛑 Stopping daemon (PID: {pid})...", style="yellow")
                
                # Send SIGTERM for graceful shutdown
                os.kill(pid, signal.SIGTERM)
                
                # Wait for graceful shutdown
                for i in range(30):  # 30 seconds timeout
                    if not DaemonController.is_daemon_running():
                        console.print("✅ Daemon stopped gracefully", style="green")
                        DaemonController.cleanup_pid_file()
                        return True
                    time.sleep(1)
                
                # Force kill if still running
                console.print("⚠️  Force stopping daemon...", style="yellow")
                os.kill(pid, signal.SIGKILL)
                time.sleep(2)
                
                if not DaemonController.is_daemon_running():
                    console.print("✅ Daemon force stopped", style="green")
                    DaemonController.cleanup_pid_file()
                    return True
                else:
                    console.print("❌ Failed to stop daemon", style="red")
                    return False
            
        except ProcessLookupError:
            console.print("ℹ️  Daemon process not found (already stopped)", style="yellow")
            DaemonController.cleanup_pid_file()
            return True
        except PermissionError:
            console.print("❌ Permission denied - cannot stop daemon", style="red")
            return False
        except Exception as e:
            console.print(f"❌ Error stopping daemon: {e}", style="red")
            return False

    @staticmethod
    def restart_daemon() -> bool:
        """
        Restart the daemon process.
        
        Returns:
            True if restarted successfully, False otherwise
        """
        console.print("🔄 Restarting daemon...", style="cyan")
        
        # Stop daemon if running
        if DaemonController.is_daemon_running():
            if not DaemonController.stop_daemon():
                return False
        
        # Wait a moment
        time.sleep(2)
        
        # Start daemon
        return DaemonController.start_daemon()

    @staticmethod
    def get_daemon_status() -> dict:
        """
        Get daemon status information.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'running': False,
            'pid': None,
            'uptime': None,
            'cpu_percent': None,
            'memory_mb': None,
            'log_size_mb': None
        }
        
        if DaemonController.is_daemon_running():
            pid = DaemonController.get_daemon_pid()
            if pid:
                try:
                    process = psutil.Process(pid)
                    status['running'] = True
                    status['pid'] = pid
                    status['uptime'] = time.time() - process.create_time()
                    status['cpu_percent'] = process.cpu_percent()
                    status['memory_mb'] = process.memory_info().rss / 1024 / 1024
                except psutil.NoSuchProcess:
                    status['running'] = False
        
        # Log file size
        if DAEMON_LOG_FILE.exists():
            status['log_size_mb'] = DAEMON_LOG_FILE.stat().st_size / 1024 / 1024
        
        return status

    @staticmethod
    async def get_database_status() -> dict:
        """Get database status information."""
        try:
            return await DaemonDatabase.get_database_stats()
        except Exception as e:
            console.print(f"❌ Failed to get database status: {e}", style="red")
            return {}

    @staticmethod
    def display_status():
        """Display comprehensive daemon status."""
        console.print("🤖 AI News Automation Daemon Status", style="bold cyan")
        console.print("=" * 50)
        
        # Daemon process status
        status = DaemonController.get_daemon_status()
        
        if status['running']:
            uptime_hours = status['uptime'] / 3600 if status['uptime'] else 0
            console.print(f"✅ Status: Running (PID: {status['pid']})", style="green")
            console.print(f"⏱️  Uptime: {uptime_hours:.1f} hours", style="cyan")
            console.print(f"💾 Memory: {status['memory_mb']:.1f} MB", style="cyan")
            console.print(f"🖥️  CPU: {status['cpu_percent']:.1f}%", style="cyan")
        else:
            console.print("❌ Status: Not Running", style="red")
        
        # Log file info
        if status['log_size_mb']:
            console.print(f"📋 Log Size: {status['log_size_mb']:.1f} MB", style="cyan")
        
        console.print()

    @staticmethod
    async def display_detailed_status():
        """Display detailed status including database information."""
        DaemonController.display_status()
        
        # Database status
        console.print("📊 Database Status", style="bold cyan")
        console.print("-" * 20)
        
        try:
            db_stats = await DaemonController.get_database_status()
            
            if db_stats:
                table = Table(box=box.SIMPLE)
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Articles", str(db_stats.get('total_articles', 0)))
                table.add_row("Analyzed Articles", str(db_stats.get('analyzed_articles', 0)))
                table.add_row("Unanalyzed Articles", str(db_stats.get('unanalyzed_articles', 0)))
                table.add_row("Recent Articles (24h)", str(db_stats.get('recent_articles_24h', 0)))
                table.add_row("Active Sources", str(db_stats.get('active_sources', 0)))
                table.add_row("Analysis Completion", f"{db_stats.get('analysis_completion_rate', 0):.1f}%")
                table.add_row("Avg Relevance Score", f"{db_stats.get('avg_relevance_score', 0):.2f}")
                
                console.print(table)
            else:
                console.print("❌ Unable to retrieve database statistics", style="red")
                
        except Exception as e:
            console.print(f"❌ Database status error: {e}", style="red")

    @staticmethod
    def show_logs(lines: int = 50):
        """Show recent daemon log entries."""
        if not DAEMON_LOG_FILE.exists():
            console.print("❌ Log file not found", style="red")
            return
        
        console.print(f"📋 Recent Daemon Logs (Last {lines} lines)", style="bold cyan")
        console.print("=" * 50)
        
        try:
            # Read last N lines
            with open(DAEMON_LOG_FILE, 'r') as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
            for line in recent_lines:
                line = line.strip()
                if 'ERROR' in line:
                    console.print(line, style="red")
                elif 'WARNING' in line:
                    console.print(line, style="yellow")
                elif 'INFO' in line:
                    console.print(line, style="cyan")
                else:
                    console.print(line)
                    
        except Exception as e:
            console.print(f"❌ Error reading log file: {e}", style="red")

    @staticmethod
    def is_daemon_running() -> bool:
        """Check if daemon is currently running."""
        pid = DaemonController.get_daemon_pid()
        if pid:
            try:
                # Check if process exists and is our daemon
                process = psutil.Process(pid)
                return 'daemon.py' in ' '.join(process.cmdline())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False
        return False

    @staticmethod
    def get_daemon_pid() -> int:
        """Get daemon PID from PID file."""
        if DAEMON_PID_FILE.exists():
            try:
                with open(DAEMON_PID_FILE, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, FileNotFoundError):
                pass
        return None

    @staticmethod
    def cleanup_pid_file():
        """Remove stale PID file."""
        if DAEMON_PID_FILE.exists():
            DAEMON_PID_FILE.unlink()


async def main():
    """Main entry point for daemon control."""
    parser = argparse.ArgumentParser(
        description="AI News Automation Daemon Control",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the daemon')
    start_parser.add_argument(
        '--foreground', '-f', action='store_true',
        help='Run in foreground (not as background process)'
    )
    
    # Stop command
    subparsers.add_parser('stop', help='Stop the daemon')
    
    # Restart command
    subparsers.add_parser('restart', help='Restart the daemon')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show daemon status')
    status_parser.add_argument(
        '--detailed', '-d', action='store_true',
        help='Show detailed status including database info'
    )
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show daemon logs')
    logs_parser.add_argument(
        '--lines', '-n', type=int, default=50,
        help='Number of log lines to show (default: 50)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'start':
        success = DaemonController.start_daemon(background=not args.foreground)
        sys.exit(0 if success else 1)
        
    elif args.command == 'stop':
        success = DaemonController.stop_daemon()
        sys.exit(0 if success else 1)
        
    elif args.command == 'restart':
        success = DaemonController.restart_daemon()
        sys.exit(0 if success else 1)
        
    elif args.command == 'status':
        if args.detailed:
            await DaemonController.display_detailed_status()
        else:
            DaemonController.display_status()
            
    elif args.command == 'logs':
        DaemonController.show_logs(args.lines)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)