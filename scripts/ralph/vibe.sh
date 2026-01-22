#!/bin/bash
# Vibe Kanban management script
# Usage: ./vibe.sh {start|stop_all|status|demo|cleanup}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/config.sh"

VIBE_PORT="${RALPH_VIBE_PORT:-5173}"
VIBE_URL="http://127.0.0.1:$VIBE_PORT"

# Start Vibe Kanban
vibe_start() {
    local port="${2:-$VIBE_PORT}"  # Use arg if provided, else config.sh default
    local url="http://127.0.0.1:$port"

    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Port $port is already in use"
        echo "View at: $url"
    else
        PORT="$port" npx vibe-kanban > /tmp/vibe-kanban-"$port".log 2>&1 &
        echo "Vibe Kanban started on port $port"
        echo "View at: $url"
    fi
}

# Stop all Vibe Kanban instances
vibe_stop_all() {
    pkill -f "vibe-kanban" 2>/dev/null && echo "All Vibe Kanban instances stopped" || echo "No Vibe Kanban instances running"
    return 0
}

# Check status of all instances
vibe_status() {
    local found_any=false
    for log in /tmp/vibe-kanban-*.log; do
        if [ -f "$log" ]; then
            local port=$(grep -oP 'Server running on http://127\.0\.0\.1:\K\d+' "$log" 2>/dev/null)
            if [ -n "$port" ]; then
                local pid=$(lsof -Pi :"$port" -sTCP:LISTEN -t 2>/dev/null)
                if [ -n "$pid" ]; then
                    if [ "$found_any" = "false" ]; then
                        echo "Vibe Kanban instances running:"
                        found_any=true
                    fi
                    echo "  - Port $port (PID: $pid) - http://127.0.0.1:$port"
                fi
            fi
        fi
    done
    if [ "$found_any" = "false" ]; then
        echo "Vibe Kanban is not running"
    fi
}

# Clean up all tasks
vibe_cleanup() {
    local project_id=$(curl -sf "$VIBE_URL/api/projects" | jq -r '.data[0].id')
    if [ -z "$project_id" ]; then
        echo "Error: No Vibe Kanban project found at $VIBE_URL"
        exit 1
    fi

    local tasks=$(curl -sf "$VIBE_URL/api/tasks?project_id=$project_id" | jq -r '.data[].id')
    if [ -z "$tasks" ]; then
        echo "No tasks to delete"
        exit 0
    fi

    echo "Deleting all tasks from project: $project_id"
    for task_id in $tasks; do
        curl -sf -X DELETE "$VIBE_URL/api/tasks/$task_id" >/dev/null
        echo "  Deleted task: $task_id"
    done

    echo "All tasks deleted"
}

# Main command dispatcher
case "${1:-}" in
    start)
        vibe_start "$@"
        ;;
    stop_all)
        vibe_stop_all
        ;;
    status)
        vibe_status
        ;;
    cleanup)
        vibe_cleanup
        ;;
    *)
        echo "Usage: $0 {start [PORT]|stop_all|status|cleanup}"
        exit 1
        ;;
esac
