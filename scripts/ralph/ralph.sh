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
# 7. Generating application documentation (README.md, example.py)
#
# TDD Workflow Enforcement:
# - Agent must make separate commits for RED (tests) and GREEN (implementation)
# - Script verifies at least 2 commits were made during execution
# - Checks for [RED] and [GREEN] markers in commit messages
#
# Commit Architecture:
# - Agent commits (prompt.md): tests [RED], implementation [GREEN], refactoring [REFACTOR]
# - Script commits (commit_story_state): prd.json, progress.txt, README.md, example.py
# - Both required: Agent commits prove TDD compliance, script commits track progress
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/generate_app_docs.sh"

# Configuration
MAX_ITERATIONS=${1:-10}
# Maximum attempts to fix validation errors
MAX_FIX_ATTEMPTS=3
PRD_JSON="docs/ralph/prd.json"
PROGRESS_FILE="docs/ralph/progress.txt"
PROMPT_FILE="docs/ralph/templates/prompt.md"
BRANCH_PREFIX="ralph/story-"

# Model Configuration
DEFAULT_MODEL="sonnet"    # Model for complex stories
SIMPLE_MODEL="haiku"      # Model for simple tasks
FIX_MODEL="haiku"         # Model for validation fixes
# Patterns that trigger SIMPLE_MODEL (case-insensitive grep -E regex)
SIMPLE_PATTERNS="fix|typo|update.*doc|small.*change|minor|format|style|cleanup|remove.*unused"
DOCS_PATTERNS="^(docs|documentation|readme|comment)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Smart model selection router - classify story complexity
# Returns model based on configuration (DEFAULT_MODEL or SIMPLE_MODEL)
classify_story() {
    local title="$1"
    local description="$2"
    local combined="$title $description"

    # Use SIMPLE_MODEL for simple tasks
    if echo "$combined" | grep -qiE "$SIMPLE_PATTERNS"; then
        echo "$SIMPLE_MODEL"
        return 0
    fi

    # Use SIMPLE_MODEL for documentation-only changes
    if echo "$combined" | grep -qiE "$DOCS_PATTERNS"; then
        echo "$SIMPLE_MODEL"
        return 0
    fi

    # Use DEFAULT_MODEL for everything else (new features, refactoring, tests)
    echo "$DEFAULT_MODEL"
}

# Validate environment
validate_environment() {
    log_info "Validating environment..."

    if [ ! -f "$PRD_JSON" ]; then
        log_error "prd.json not found at $PRD_JSON"
        log_info "Run 'claude -p /generate-prd-json-from-md' or 'make ralph_init_loop'"
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

    # Git state check - prevents conflicts
    if ! git diff --quiet 2>/dev/null || ! git diff --staged --quiet 2>/dev/null; then
        log_warn "Uncommitted changes detected - consider committing first"
    fi

    # Branch protection - prevents accidents on main/master
    current_branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
    if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
        log_error "Running on protected branch: $current_branch"
        log_info "Create a feature branch: git checkout -b feat/your-feature"
        exit 1
    fi

    log_info "Environment validated successfully"
}

# Get next story with resolved dependencies (execute deps first)
get_next_story() {
    # Get all incomplete stories
    local incomplete=$(jq -r '.stories[] | select(.passes == false) | .id' "$PRD_JSON")

    for story_id in $incomplete; do
        # Check if all dependencies are complete
        local deps=$(jq -r --arg id "$story_id" \
            '.stories[] | select(.id == $id) | .depends_on // [] | .[]' \
            "$PRD_JSON" 2>/dev/null)

        local deps_met=true
        for dep in $deps; do
            local dep_passes=$(jq -r --arg id "$dep" \
                '.stories[] | select(.id == $id) | .passes' "$PRD_JSON")
            if [ "$dep_passes" != "true" ]; then
                deps_met=false
                break
            fi
        done

        # Return first story with all deps satisfied
        if [ "$deps_met" = "true" ]; then
            echo "$story_id"
            return 0
        fi
    done

    # No story with satisfied deps found
    echo ""
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

    # Smart model selection based on story complexity
    local model=$(classify_story "$title" "$description")
    log_info "Using model: $model (based on story complexity)"

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

    # Execute via Claude Code with selected model
    log_info "Running Claude Code with story context..."
    if cat "$iteration_prompt" | claude -p --model "$model" --dangerously-skip-permissions 2>&1 | tee "/tmp/ralph_execute_${story_id}.log"; then
        log_info "Execution log saved: /tmp/ralph_execute_${story_id}.log"
        rm "$iteration_prompt"
        return 0
    else
        log_error "Execution failed, log saved: /tmp/ralph_execute_${story_id}.log"
        rm "$iteration_prompt"
        return 1
    fi
}

# Run quality checks
run_quality_checks() {
    local error_log="${1:-/tmp/ralph_validate.log}"
    log_info "Running quality checks (make validate)..."

    if make validate 2>&1 | tee "$error_log"; then
        log_info "Quality checks passed"
        return 0
    else
        log_error "Quality checks failed"
        cat "$error_log"
        return 1
    fi
}

# Fix validation errors by re-invoking agent with error details
fix_validation_errors() {
    local story_id="$1"
    local details="$2"
    local error_log="$3"
    local max_attempts="$4"

    log_info "Attempting to fix validation errors (max $max_attempts attempts)..."

    local title=$(echo "$details" | cut -d'|' -f1)
    local description=$(echo "$details" | cut -d'|' -f2)

    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        log_info "Fix attempt $attempt/$max_attempts"

        # Use FIX_MODEL for fixes (usually simpler than initial implementation)
        local model="$FIX_MODEL"
        log_info "Using model: $model (validation fix)"

        # Reuse main prompt with story details + validation errors
        local fix_prompt=$(mktemp)
        cat "$PROMPT_FILE" > "$fix_prompt"
        {
            echo ""
            echo "## Current Story"
            echo "**ID**: $story_id"
            echo "**Title**: $title"
            echo "**Description**: $description"
            echo ""
            echo "## VALIDATION ERRORS TO FIX"
            echo ""
            echo "The story implementation has validation errors. Fix them:"
            echo ""
            echo '```'
            cat "$error_log"
            echo '```'
            echo ""
            echo "Fix all errors and run \`make validate\` to verify."
        } >> "$fix_prompt"

        # Execute fix via Claude Code with haiku model
        if cat "$fix_prompt" | claude -p --model "$model" --dangerously-skip-permissions 2>&1 | tee "/tmp/ralph_fix_${story_id}_${attempt}.log"; then
            log_info "Fix attempt log saved: /tmp/ralph_fix_${story_id}_${attempt}.log"
            rm "$fix_prompt"

            # Use quick validation (no coverage) for intermediate attempts to save time, full validation on last attempt
            local retry_log="/tmp/ralph_validate_fix_${attempt}.log"
            if [ $attempt -lt $max_attempts ]; then
                log_info "Running quick validation (attempt $attempt/$max_attempts)..."
                if make validate_quick 2>&1 | tee "$retry_log"; then
                    # Quick validation passed, run full validation to confirm
                    if run_quality_checks "$retry_log"; then
                        log_info "Full validation passed after fix attempt $attempt"
                        return 0
                    fi
                else
                    log_warn "Quick validation still failing after fix attempt $attempt"
                    error_log="$retry_log"  # Use new errors for next attempt
                fi
            else
                # Last attempt - run full validation directly
                log_info "Running full validation (final attempt)..."
                if run_quality_checks "$retry_log"; then
                    log_info "Validation passed after fix attempt $attempt"
                    return 0
                else
                    log_warn "Validation still failing after fix attempt $attempt"
                    error_log="$retry_log"  # Use new errors for next attempt
                fi
            fi
        else
            log_error "Fix execution failed, log saved: /tmp/ralph_fix_${story_id}_${attempt}.log"
            rm "$fix_prompt"
            return 1
        fi

        attempt=$((attempt + 1))
    done

    log_error "Failed to fix validation errors after $max_attempts attempts"
    return 1
}

# Commit story state files after successful completion
commit_story_state() {
    local story_id="$1"
    local message="$2"

    # Generate/update application documentation
    local app_readme=$(generate_app_readme)
    local app_example=$(generate_app_example)

    # Commit state files (prd.json, progress.txt, README.md, example.py)
    log_info "Committing state files..."
    git add "$PRD_JSON" "$PROGRESS_FILE"
    [ -n "$app_readme" ] && git add "$app_readme"
    [ -n "$app_example" ] && git add "$app_example"

    if ! git commit -m "docs($story_id): $message

Co-Authored-By: Claude <noreply@anthropic.com>"; then
        log_warn "No state changes to commit"
        return 1
    fi

    # Push commits immediately after successful story completion
    log_info "Pushing commits to remote..."
    if git push; then
        log_info "Commits pushed successfully"
    else
        log_warn "Failed to push commits - will retry at end of loop"
    fi

    return 0
}

# Check that TDD commits were made during story execution
# Verify TDD commit order: [RED] must be committed BEFORE [GREEN]
# In git log output, older commits appear on higher line numbers
# Sets TDD_ERROR_MSG global variable with detailed error message
check_tdd_commits() {
    local story_id="$1"
    local commits_before="$2"

    # Skip TDD verification for first story being executed to allow ramp-up
    local completed_stories=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")
    if [ "$completed_stories" -eq 0 ]; then
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
            local validation_log="/tmp/ralph_validate_${story_id}.log"
            if run_quality_checks "$validation_log"; then
                # Mark as passing
                update_story_status "$story_id" "true"
                log_progress "$iteration" "$story_id" "PASS" "Completed successfully with TDD commits"
                log_info "Story $story_id marked as PASSING"

                # Commit state files with documentation
                commit_story_state "$story_id" "update state and documentation after completion"
            else
                log_warn "Story completed but quality checks failed - attempting fixes"

                # Attempt to fix validation errors
                if fix_validation_errors "$story_id" "$details" "$validation_log" "$MAX_FIX_ATTEMPTS"; then
                    # Mark as passing after successful fixes
                    update_story_status "$story_id" "true"
                    log_progress "$iteration" "$story_id" "PASS" "Completed after fixing validation errors"
                    log_info "Story $story_id marked as PASSING after fixes"

                    # Commit state files with documentation
                    commit_story_state "$story_id" "update state and documentation after fixing validation errors"
                else
                    log_error "Failed to fix validation errors"
                    log_progress "$iteration" "$story_id" "FAIL" "Quality checks failed after $MAX_FIX_ATTEMPTS fix attempts"
                fi
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

    # Commit any remaining uncommitted tracking files
    if ! git diff --quiet "$PRD_JSON" "$PROGRESS_FILE" 2>/dev/null; then
        log_info "Committing final tracking file changes..."
        git add "$PRD_JSON" "$PROGRESS_FILE"

        local total=$(jq '.stories | length' "$PRD_JSON")
        local passing=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")

        git commit -m "$(cat <<EOF
docs(ralph): update progress after loop completion

Summary: $passing/$total stories passing

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
    fi

    # Push all commits with retry (ensure changes are pushed before exit)
    log_info "Pushing all commits to remote..."
    local push_attempts=0
    local max_push_attempts=3
    while [ $push_attempts -lt $max_push_attempts ]; do
        push_attempts=$((push_attempts + 1))
        if git push; then
            log_info "All commits pushed successfully"
            break
        else
            if [ $push_attempts -lt $max_push_attempts ]; then
                log_warn "Push failed (attempt $push_attempts/$max_push_attempts), retrying in 5s..."
                sleep 5
            else
                log_error "Failed to push commits after $max_push_attempts attempts"
            fi
        fi
    done

    # Summary
    local total=$(jq '.stories | length' "$PRD_JSON")
    local passing=$(jq '[.stories[] | select(.passes == true)] | length' "$PRD_JSON")

    log_info "Summary: $passing/$total stories passing"
}

# Run main
main
