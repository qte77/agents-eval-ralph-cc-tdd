#!/bin/bash
# Vibe Kanban real-time integration via REST API

VIBE_URL=""
VIBE_PROJECT_ID=""

# Get Vibe Kanban URL from config
get_vibe_url() {
    echo "http://127.0.0.1:$RALPH_VIBE_PORT"
}

# Get project ID from Vibe Kanban
get_project_id() {
    local url=$(get_vibe_url)
    curl -sf "$url/api/projects" | jq -r '.data[0].id'
}

# Detect running Vibe Kanban instance on configured port
_detect_vibe() {
    local url=$(get_vibe_url)
    if curl -sf -m 1 "$url/api/projects" >/dev/null 2>&1; then
        VIBE_URL="$url"
        return 0
    fi
    return 1
}

# Initialize Kanban integration
kanban_init() {
    local run_id=$1

    # Try to detect Vibe Kanban
    if ! _detect_vibe; then
        return 0  # Silent fail - Vibe not running
    fi

    log_info "Vibe Kanban detected at $VIBE_URL"

    # Get project ID
    VIBE_PROJECT_ID=$(get_project_id)

    if [ -z "$VIBE_PROJECT_ID" ]; then
        log_warn "No Vibe Kanban project found"
        return 0
    fi

    log_info "Using Vibe project: $VIBE_PROJECT_ID"

    # Create tasks from prd.json
    > "$KANBAN_MAP"  # Initialize map file
    while IFS= read -r story; do
        local id=$(echo "$story" | jq -r '.id')
        local title=$(echo "$story" | jq -r '.title')
        local desc=$(echo "$story" | jq -r '.description // "No description"')

        local task_resp=$(curl -sf -X POST "$VIBE_URL/api/tasks" \
            -H "Content-Type: application/json" \
            -d '{
                "project_id": "'"$VIBE_PROJECT_ID"'",
                "title": "'"$id: $title"'",
                "description": "'"$desc"'",
                "status": "todo"
            }' 2>/dev/null)

        local task_id=$(echo "$task_resp" | jq -r '.data.id // empty')
        if [ -n "$task_id" ]; then
            echo "$id=$task_id" >> "$KANBAN_MAP"
            log_info "Created Vibe task: $id"
        fi
    done < <(jq -c '.stories[]' "$RALPH_PRD_JSON")

    log_info "Kanban sync active - created $(wc -l < "$KANBAN_MAP") tasks"
}

# Update task status
kanban_update() {
    local story_id=$1
    local status=$2

    # Check if Vibe Kanban was initialized
    [ -n "$VIBE_URL" ] && [ -f "$KANBAN_MAP" ] || return 0

    # Get task ID from map
    local task_id=$(grep "^$story_id=" "$KANBAN_MAP" 2>/dev/null | cut -d= -f2)
    [ -z "$task_id" ] && return 0

    # Update task
    curl -sf -X PUT "$VIBE_URL/api/tasks/$task_id" \
        -H "Content-Type: application/json" \
        -d '{
            "status": "'"$status"'"
        }' >/dev/null 2>&1
}
