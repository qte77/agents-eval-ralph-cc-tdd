#!/bin/bash
# Delete all tasks from Vibe Kanban project

set -euo pipefail

# Get script directory and source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/colors.sh"
source "$SCRIPT_DIR/lib/config.sh"
source "$SCRIPT_DIR/lib/vibe.sh"

log_info "Cleaning up all tasks from Vibe Kanban..."

# Get Vibe URL and project ID
VIBE_URL=$(get_vibe_url)
PROJECT_ID=$(get_project_id)
log_info "Project: $PROJECT_ID"

# Get all tasks
TASKS=$(curl -sf "$VIBE_URL/api/tasks?project_id=$PROJECT_ID" | jq -r '.data[].id')

if [ -z "$TASKS" ]; then
  log_info "No tasks to delete"
  exit 0
fi

# Delete each task
for task_id in $TASKS; do
  log_info "Deleting task: $task_id"
  curl -sf -X DELETE "$VIBE_URL/api/tasks/$task_id"
done

echo ""
log_success "All tasks deleted"
log_info "View at: $VIBE_URL"
