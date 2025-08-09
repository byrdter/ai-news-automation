#!/bin/bash
# Simple AI News Automation Daemon Starter

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [ -d "$SCRIPT_DIR/venv_linux" ]; then
    source "$SCRIPT_DIR/venv_linux/bin/activate"
    echo "✅ Activated virtual environment: venv_linux"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "✅ Activated virtual environment: venv"
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Check for daemon type
DAEMON_TYPE="${1:-simple}"

echo "🚀 Starting AI News Automation Daemon ($DAEMON_TYPE mode)..."

if [ "$DAEMON_TYPE" = "simple" ]; then
    python "$SCRIPT_DIR/daemon_simple.py"
elif [ "$DAEMON_TYPE" = "full" ]; then
    python "$SCRIPT_DIR/daemon.py"
else
    echo "❌ Unknown daemon type: $DAEMON_TYPE"
    echo "Usage: $0 [simple|full]"
    exit 1
fi