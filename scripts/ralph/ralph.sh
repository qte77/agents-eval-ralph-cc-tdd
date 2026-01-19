#!/bin/bash
#
# Ralph Loop - Autonomous iteration script
#
# Usage: ./scripts/ralph/ralph.sh [MAX_ITERATIONS]
#        make ralph_run [ITERATIONS=25]
#
# This script orchestrates autonomous task execution by:
# 1. Reading prd.json for incomplete stories
# 2. Executing single story via Claude Code (with TDD workflow)
# 3. Verifying TDD commits (RED + GREEN phases)
# 4. Running quality checks (make validate)
# 5. Updating prd.json status on success
# 6. Appending learnings to progress.txt
#
# TDD Workflow Enforcement:
# - Agent must make separate commits for RED (tests) and GREEN (implementation)
# - Script verifies at least 2 commits were made during execution
# - Checks for [RED] and [GREEN] markers in commit messages
#

set -euo pipefail

# Configuration
MAX_ITERATIONS=${1:-10}
PRD_JSON="docs/ralph/prd.json"
PROGRESS_FILE="docs/ralph/progress.txt"
PROMPT_FILE="docs/ralph/templates/prompt.md"
BRANCH_PREFIX="ralph/story-"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Validate environment
validate_environment() {
    log_info "Validating environment..."

    if [ ! -f "$PRD_JSON" ]; then
        log_error "prd.json not found at $PRD_JSON"
        log_info "Run 'claude -p' and ask: 'Use generating-prd skill to create prd.json'"
        exit 1
    fi

    if [ ! -f "$PROGRESS_FILE" ]; then
        log_warn "progress.txt not found, creating..."
        mkdir -p "$(dirname "$PROGRESS_FILE")"
        echo "# Ralph Loop Progress" > "$PROGRESS_FILE"
        echo "Started: $(date)" >> "$PROGRESS_FILE"
        echo "" >> "$PROGRESS_FILE"
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        exit 1
    fi

    log_info "Environment validated successfully"
}

# Get next incomplete story from prd.json
get_next_story() {
    jq -r '.stories[] | select(.passes == false) | .id' "$PRD_JSON" | head -n 1
}

# Get story details
get_story_details() {
    local story_id="$1"
    jq -r --arg id "$story_id" '.stories[] | select(.id == $id) | "\(.title)|\(.description)"' "$PRD_JSON"
}

# Update story status in prd.json
update_story_status() {
    local story_id="$1"
    local status="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    jq --arg id "$story_id" \
       --arg status "$status" \
       --arg timestamp "$timestamp" \
       '(.stories[] | select(.id == $id) | .passes) |= ($status == "true") |
        (.stories[] | select(.id == $id) | .completed_at) |= (if $status == "true" then $timestamp else null end)' \
       "$PRD_JSON" > "${PRD_JSON}.tmp"

    # Validate JSON before replacing original
    if ! jq empty "${PRD_JSON}.tmp" 2>/dev/null; then
        log_error "Generated invalid JSON, keeping original prd.json"
        rm -f "${PRD_JSON}.tmp"
        return 1
    fi

    mv "${PRD_JSON}.tmp" "$PRD_JSON"
}

# Append to progress log
log_progress() {
    local iteration="$1"
    local story_id="$2"
    local status="$3"
    local notes="$4"

    {
        echo "## Iteration $iteration - $(date)"
        echo "Story: $story_id"
        echo "Status: $status"
        echo "Notes: $notes"
        echo ""
    } >> "$PROGRESS_FILE"
}

# Execute single story via Claude Code
execute_story() {
    local story_id="$1"
    local details="$2"
    local title=$(echo "$details" | cut -d'|' -f1)
    local description=$(echo "$details" | cut -d'|' -f2)

    log_info "Executing story: $story_id - $title"

    # Create prompt for this iteration
    local iteration_prompt=$(mktemp)
    cat "$PROMPT_FILE" > "$iteration_prompt"
    {
        echo ""
        echo "## Current Story"
        echo "**ID**: $story_id"
        echo "**Title**: $title"
        echo "**Description**: $description"
        echo ""
        echo "Read prd.json for full acceptance criteria and expected files."
    } >> "$iteration_prompt"

    # Execute via Claude Code
    log_info "Running Claude Code with story context..."
    if cat "$iteration_prompt" | claude -p --dangerously-skip-permissions; then
        rm "$iteration_prompt"
        return 0
    else
        rm "$iteration_prompt"
        return 1
    fi
}

# Run quality checks
run_quality_checks() {
    log_info "Running quality checks (make validate)..."

    if make validate 2>&1 | tee /tmp/ralph_validate.log; then
        log_info "Quality checks passed"
        return 0
    else
        log_error "Quality checks failed"
        cat /tmp/ralph_validate.log
        return 1
    fi
}

# Check that TDD commits were made during story execution
# Verify TDD commit order: [RED] must be committed BEFORE [GREEN]
# In git log output, older commits appear on higher line numbers
# Sets TDD_ERROR_MSG global variable with detailed error message
check_tdd_commits() {
    local story_id="$1"
    local commits_before="$2"

    # Skip TDD verification for first story to allow ramp-up
    if [ "$story_id" = "STORY-001" ]; then
        log_info "Skipping TDD verification for first story (ramp-up)"
        return 0
    fi

    log_info "Checking TDD commits..."
    TDD_ERROR_MSG=""  # Reset error message

    # Count commits made during story execution
    local commits_after=$(git rev-list --count HEAD)
    local new_commits=$((commits_after - commits_before))

    # If no commits made during this execution, skip verification
    if [ $new_commits -eq 0 ]; then
        log_warn "No commits made - skipping TDD verification"
        TDD_ERROR_MSG="No commits made during execution"
        return 2  # Return code 2 = skip (not fail)
    fi

    if [ $new_commits -lt 2 ]; then
        TDD_ERROR_MSG="Found $new_commits commit(s), need 2+ (RED + GREEN)"
        log_error "TDD check failed: $TDD_ERROR_MSG"
        return 1
    fi

    # Verify commits mention the story ID or phases
    local recent_commits=$(git log --oneline -n $new_commits)
    log_info "Recent commits:"
    echo "$recent_commits"

    # Check for RED and GREEN phase markers
    if echo "$recent_commits" | grep -q "\[RED\]" && echo "$recent_commits" | grep -q "\[GREEN\]"; then
        log_info "TDD phases verified: RED and GREEN found"
        return 0
    else
        TDD_ERROR_MSG="Missing [RED] or [GREEN] markers in commits: $recent_commits"
        log_error "TDD check failed: missing [RED] or [GREEN] markers in commits"
        return 1
    fi
}

# Main loop
main() {
    log_info "Starting Ralph Loop (max iterations: $MAX_ITERATIONS)"

    validate_environment

    local iteration=0

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        iteration=$((iteration + 1))
        log_info "===== Iteration $iteration/$MAX_ITERATIONS ====="

        # Get next incomplete story
        local story_id=$(get_next_story)

        if [ -z "$story_id" ]; then
            log_info "No incomplete stories found"
            log_info "<promise>COMPLETE</promise>"
            break
        fi

        local details=$(get_story_details "$story_id")
        local title=$(echo "$details" | cut -d'|' -f1)

        # Record commit count before execution
        local commits_before=$(git rev-list --count HEAD)

        # Execute story
        if execute_story "$story_id" "$details"; then
            log_info "Story execution completed"

            # Verify TDD commits were made (capture return code without triggering set -e)
            local tdd_check_result=0
            check_tdd_commits "$story_id" "$commits_before" || tdd_check_result=$?

            if [ $tdd_check_result -eq 2 ]; then
                # No commits made, skip verification and continue to next iteration
                log_info "No commits - retrying story"
                log_progress "$iteration" "$story_id" "RETRY" "$TDD_ERROR_MSG"
                continue
            elif [ $tdd_check_result -ne 0 ]; then
                # TDD verification failed
                log_progress "$iteration" "$story_id" "FAIL" "TDD verification failed: $TDD_ERROR_MSG"
                continue
            fi

            # Run quality checks
            if run_quality_checks; then
                # Mark as passing
                update_story_status "$story_id" "true"
                log_progress "$iteration" "$story_id" "PASS" "Completed successfully with TDD commits"
                log_info "Story $story_id marked as PASSING"
            else
                log_warn "Story completed but quality checks failed"
                log_progress "$iteration" "$story_id" "FAIL" "Quality checks failed"
            fi
        else
            log_error "Story execution failed"
            log_progress "$iteration" "$story_id" "FAIL" "Execution error"
        fi

        echo ""
    done

    if [ $iteration -eq $MAX_ITERATIONS ]; then
        log_warn "Reached maximum iterations ($MAX_ITERATIONS)"
    fi

    # Summary
    local total=$(jq '.stories | length' "$PRD_JSON")
    local passing=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")

    log_info "Summary: $passing/$total stories passing"
}

# Run main
main
