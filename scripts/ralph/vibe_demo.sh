#!/bin/bash
# Create Ralph Loop example tasks in existing Vibe Kanban project

set -euo pipefail

# Get script directory and source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/colors.sh"
source "$SCRIPT_DIR/lib/config.sh"
source "$SCRIPT_DIR/lib/vibe.sh"

log_info "Creating Ralph Loop example tasks (N_WT=3)..."

# Get Vibe URL and project ID
VIBE_URL=$(get_vibe_url)
PROJECT_ID=$(get_project_id)
log_info "Using project: $PROJECT_ID"

# Helper function to create tasks
create_task() {
  local title="$1"
  local desc="$2"
  local status="$3"

  log_info "Creating task: $title ($status)"
  curl -sf -X POST "$VIBE_URL/api/tasks" \
    -H "Content-Type: application/json" \
    -d @- <<EOF
{
  "project_id": "$PROJECT_ID",
  "title": "$title",
  "description": "$desc",
  "status": "$status"
}
EOF
  echo
}

# Done tasks
create_task "STORY-007: Add health check endpoint" \
  "Create /health endpoint for monitoring. Completed with TDD commits: test [RED], feat [GREEN]" \
  "done"

create_task "STORY-006: Create API documentation" \
  "Generate OpenAPI/Swagger docs for all endpoints. Completed with TDD commits: test [RED], feat [GREEN], refactor [REFACTOR]" \
  "done"

# In progress (parallel worktrees)
create_task "STORY-001: Add user authentication" \
  "Implement JWT-based authentication. Worktree: ../ralph-wt-1, Branch: ralph/STORY-001-wt-1, Agent: Claude Sonnet 4.5, TDD Phase: RED" \
  "inprogress"

create_task "STORY-002: Create data validation layer" \
  "Add Pydantic models for validation. Worktree: ../ralph-wt-2, Branch: ralph/STORY-002-wt-2, Agent: Claude Haiku 4, TDD Phase: GREEN" \
  "inprogress"

create_task "STORY-003: Add database migrations" \
  "Create Alembic migrations. Worktree: ../ralph-wt-3, Branch: ralph/STORY-003-wt-3, Agent: Claude Sonnet 4.5, TDD Phase: REFACTOR" \
  "inprogress"

# Todo (waiting for worktree slot)
create_task "STORY-004: Implement password hashing" \
  "Add bcrypt hashing for secure password storage. Waiting for worktree slot" \
  "todo"

create_task "STORY-005: Add rate limiting middleware" \
  "Implement rate limiting to prevent API abuse. Waiting for worktree slot" \
  "todo"

echo ""
log_success "Example tasks created successfully"
echo ""
echo "Kanban Board State:"
echo "  Done: 2 tasks (STORY-006, STORY-007)"
echo "  In Progress: 3 tasks (STORY-001, STORY-002, STORY-003)"
echo "  Todo: 2 tasks (STORY-004, STORY-005)"
echo ""
log_info "View at: $VIBE_URL"
