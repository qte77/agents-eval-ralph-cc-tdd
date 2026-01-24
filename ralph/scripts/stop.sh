#!/bin/bash
# Stops all running Ralph loops (keeps worktrees and data)
set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/stop_ralph_processes.sh"

# Execute stop
stop_ralph_processes
