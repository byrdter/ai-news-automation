#!/bin/bash
# AI News Automation Daemon Control Wrapper
# Simple shell script to control the daemon

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_CONTROL="$SCRIPT_DIR/scripts/daemon_control.py"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv_linux" ]; then
    source "$SCRIPT_DIR/venv_linux/bin/activate"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run daemon control with all arguments
python "$DAEMON_CONTROL" "$@"