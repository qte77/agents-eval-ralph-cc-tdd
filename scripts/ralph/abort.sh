#!/bin/bash
# Terminates all running Ralph loops and orphaned Claude processes
set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/colors.sh"

log_info "Aborting all running Ralph loops..."

# Find and kill Ralph processes
ralph_pids=$(ps aux | grep "scripts/ralph/ralph.sh" | grep -v grep | awk '{print $2}' || true)
if [ -n "$ralph_pids" ]; then
    log_info "Found Ralph processes: $ralph_pids"
    kill $ralph_pids 2>/dev/null || true
    sleep 1
    # Force kill if still running
    kill -9 $ralph_pids 2>/dev/null || true
    log_info "Ralph loops terminated"
else
    log_info "No running Ralph loops found"
fi

# Also kill any orphaned Claude processes spawned by Ralph
claude_pids=$(ps aux | grep "claude -p.*dangerously-skip-permissions" | grep -v grep | awk '{print $2}' || true)
if [ -n "$claude_pids" ]; then
    log_info "Cleaning up orphaned Claude processes: $claude_pids"
    kill $claude_pids 2>/dev/null || true
fi

# Clean up worktrees
bash "$SCRIPT_DIR/parallel_ralph.sh" abort 2>/dev/null || true

log_info "Abort complete"
