#!/bin/bash
#
# Parallel Ralph Loop - Orchestrator for parallel execution
#
# Usage: ./scripts/ralph/parallel_ralph.sh [N_WT] [MAX_ITERATIONS]
#        make ralph N_WT=2 ITERATIONS=10
#
# Environment variables:
#   USE_LOCK=true (default) - Lock worktrees to prevent pruning
#   USE_NO_TRACK=true (default) - Create local-only branches
#   LOCK_REASON="..." - Custom lock reason message
#   WORKTREE_QUIET=false (default) - Suppress worktree output
#   MERGE_VERIFY_SIGNATURES=false (default) - Verify GPG signatures
#   MERGE_LOG=true (default) - Include commit descriptions in merge
#
# Examples:
#   make ralph N_WT=3 ITERATIONS=25
#   USE_LOCK=false make ralph N_WT=1
#   MERGE_VERIFY_SIGNATURES=true make ralph N_WT=2
#
# This script orchestrates parallel Ralph loop execution by:
# 1. Creating N_WT git worktrees (default=1, max=10)
# 2. Running ralph.sh in each worktree SIMULTANEOUSLY (background jobs)
# 3. Waiting for all to complete and scoring results
# 4. Merging the best result back to original branch
# 5. Cleaning up worktrees and branches
#
# Architecture:
# - N_WT=1: Single worktree isolation (security)
# - N_WT>1: True parallel execution via bash background jobs
# - Worktrees default to --lock (prevents pruning) and --no-track (local branches)
#   Both flags configurable via USE_LOCK and USE_NO_TRACK env vars
# - Best result selected by scoring algorithm
# - Merge via --no-ff --no-commit (dry-run test, then commit)
#
# Worktree Naming:
# - N_WT=1: ${PREFIX}-${RUN_ID}        (e.g., ../agenteval-ralph-wt-a3f5e2)
# - N_WT>1: ${PREFIX}-${RUN_ID}-${NUM} (e.g., ../agenteval-ralph-wt-b9c4d1-1)
# - PREFIX: Dynamic, defaults to ../${SRC_PACKAGE_DIR}-ralph-wt (configurable)
# - RUN_ID: Unique 6-char alphanumeric ID generated per run
# - NUM: Worktree index (1 to N_WT)
# - Purpose: Distinguish different Ralph runs, prevent collisions
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/colors.sh"
source "$SCRIPT_DIR/lib/config.sh"
source "$SCRIPT_DIR/lib/validate_json.sh"

# Configuration (import from config.sh with CLI/env overrides)
# Note: N_WT and MAX_ITERATIONS are parsed in main() to avoid conflicts with subcommands
WORKTREE_PREFIX="$RALPH_PARALLEL_WORKTREE_PREFIX"
BRANCH_PREFIX="$RALPH_PARALLEL_BRANCH_PREFIX"

# System limit for parallel worktrees (validated in main)
MAX_WORKTREES=10

# Worktree flags (inherited from config.sh with env override support)
USE_LOCK="$RALPH_PARALLEL_USE_LOCK"
USE_NO_TRACK="$RALPH_PARALLEL_USE_NO_TRACK"
LOCK_REASON="$RALPH_PARALLEL_LOCK_REASON"
WORKTREE_QUIET="$RALPH_PARALLEL_WORKTREE_QUIET"

# Merge flags (inherited from config.sh with env override support)
MERGE_VERIFY_SIGNATURES="$RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES"
MERGE_LOG="$RALPH_PARALLEL_MERGE_LOG"

# PID tracking
declare -a WORKTREE_PIDS=()
declare -a WORKTREE_EXIT_CODES=()

# Generate unique 6-char alphanumeric run ID
generate_run_id() {
    # Use timestamp + random for uniqueness
    local timestamp=$(date +%s%N)
    echo "${timestamp}" | md5sum | cut -c1-6
}

# Helper: Get worktree path for given index, run ID, and total count
get_worktree_path() {
    local wt_num="$1"
    local run_id="${2:-}"
    local n_wt="${3:-}"

    if [ -n "$run_id" ]; then
        # If N_WT=1, omit the worktree number (cleaner, less confusing)
        if [ "$n_wt" = "1" ]; then
            echo "${WORKTREE_PREFIX}-${run_id}"
        else
            echo "${WORKTREE_PREFIX}-${run_id}-${wt_num}"
        fi
    else
        # For utility functions scanning existing worktrees
        # Match both patterns: with and without number suffix
        echo "${WORKTREE_PREFIX}-*"
    fi
}

# Helper: Get branch name for given index
get_branch_name() {
    echo "${BRANCH_PREFIX}-${1}"
}

# Helper: Find all worktrees for a given index (across all run IDs)
find_worktree_by_index() {
    local wt_num="$1"

    # For index 1, check both patterns: with number (N_WT>1) and without (N_WT=1)
    if [ "$wt_num" = "1" ]; then
        # Try pattern without number first (N_WT=1 case)
        local wt=$(compgen -G "${WORKTREE_PREFIX}-*" 2>/dev/null | grep -v -- "-[0-9]$" | head -1)
        if [ -n "$wt" ]; then
            echo "$wt"
            return
        fi
    fi

    # Standard pattern with number (N_WT>1 case, or fallback for index 1)
    compgen -G "${WORKTREE_PREFIX}-*-${wt_num}" 2>/dev/null | head -1
}

# Create worktree with optimized flags
create_worktree() {
    local i="$1"
    local run_id="$2"
    local n_wt="$3"
    local worktree_path=$(get_worktree_path "$i" "$run_id" "$n_wt")
    local branch_name=$(get_branch_name "$i")

    log_info "Creating worktree $i at $worktree_path..."

    # Build worktree command with optional flags (defaults: both enabled)
    local wt_flags=()

    # --no-track: Creates local-only branch (no remote tracking = cleaner, no push conflicts)
    [ "$USE_NO_TRACK" = "true" ] && wt_flags+=(--no-track)

    # --lock: Prevents 'git worktree prune' from removing active worktrees during long runs
    if [ "$USE_LOCK" = "true" ]; then
        wt_flags+=(--lock --reason "$LOCK_REASON")
    fi

    # --quiet: Suppress feedback messages
    [ "$WORKTREE_QUIET" = "true" ] && wt_flags+=(--quiet)

    git worktree add "${wt_flags[@]}" -b "$branch_name" "$worktree_path" HEAD

    log_info "Worktree $i created $([ "$USE_LOCK" = "true" ] && echo "and locked" || echo "")"
}

# Initialize worktree state (reset prd.json, fresh progress.txt)
init_worktree_state() {
    local i="$1"
    local run_id="$2"
    local n_wt="$3"
    local worktree_path=$(get_worktree_path "$i" "$run_id" "$n_wt")

    log_info "Initializing state for worktree $i..."

    # Reset prd.json to original state (all stories incomplete)
    if [ -f "$RALPH_PRD_JSON" ]; then
        # Reset all passes to false and clear completed_at
        jq '(.stories[] | .passes) = false | (.stories[] | .completed_at) = null' \
            "$RALPH_PRD_JSON" > "$worktree_path/$RALPH_PRD_JSON"
    fi

    # Create fresh progress.txt
    mkdir -p "$worktree_path/$RALPH_DOCS_DIR"
    cat > "$worktree_path/$RALPH_PROGRESS_FILE" <<EOF
# Ralph Loop Progress - Worktree $i
Started: $(date)

EOF

    log_info "Worktree $i state initialized"
}

# Start parallel ralph.sh execution
start_parallel() {
    local i="$1"
    local run_id="$2"
    local n_wt="$3"
    local worktree_path=$(get_worktree_path "$i" "$run_id" "$n_wt")
    local log_file="$worktree_path/ralph.log"

    log_info "Starting ralph.sh in worktree $i (background)..."

    (
        cd "$worktree_path"
        ./scripts/ralph/ralph.sh "$MAX_ITERATIONS" > "$log_file" 2>&1
    ) &

    WORKTREE_PIDS[$i]=$!
    log_info "Worktree $i running (PID: ${WORKTREE_PIDS[$i]})"
}

# Wait for all worktrees and monitor completion
wait_and_monitor() {
    log_info "Waiting for all $N_WT worktrees to complete..."

    for i in $(seq 1 $N_WT); do
        local pid=${WORKTREE_PIDS[$i]}
        log_info "Waiting for worktree $i (PID: $pid)..."

        if wait "$pid"; then
            WORKTREE_EXIT_CODES[$i]=0
            log_info "Worktree $i completed successfully"
        else
            WORKTREE_EXIT_CODES[$i]=$?
            log_warn "Worktree $i exited with code: ${WORKTREE_EXIT_CODES[$i]}"
        fi
    done

    log_info "All worktrees completed"
}

# Score worktree results
score_worktree() {
    local i="$1"
    local run_id="$2"
    local n_wt="$3"
    local worktree_path=$(get_worktree_path "$i" "$run_id" "$n_wt")
    local prd_json="$worktree_path/$RALPH_PRD_JSON"

    if [ ! -f "$prd_json" ]; then
        echo 0
        return
    fi

    # Scoring: (stories_passed * 100) + test_count + (validation_pass ? 50 : 0)
    local stories_passed=$(jq '[.stories[] | select(.passes == true)] | length' "$prd_json" 2>/dev/null || echo 0)

    # Count test files in worktree
    local test_count=$(find "$worktree_path" -name "test_*.py" -type f 2>/dev/null | wc -l)

    # Check if last validation passed (exit code 0)
    local validation_bonus=0
    if [ "${WORKTREE_EXIT_CODES[$i]}" -eq 0 ]; then
        validation_bonus=50
    fi

    local score=$((stories_passed * 100 + test_count + validation_bonus))
    echo "$score"
}

# Select best worktree
select_best() {
    local run_id="$1"
    local n_wt="$2"
    log_info "Scoring all worktrees..."

    local best_wt=1
    local best_score=$(score_worktree 1 "$run_id" "$n_wt")

    for i in $(seq 2 $n_wt); do
        local score=$(score_worktree $i "$run_id" "$n_wt")
        log_info "Worktree $i score: $score (best: $best_score)"

        if [ "$score" -gt "$best_score" ]; then
            best_wt=$i
            best_score=$score
        fi
    done

    log_info "Best worktree: $best_wt (score: $best_score)"
    echo "$best_wt"
}

# Merge best worktree back to original branch
merge_best() {
    local best_wt="$1"
    local n_wt="$2"
    local run_id="$3"
    local branch_name="${BRANCH_PREFIX}-${best_wt}"

    log_info "Merging best result from worktree $best_wt..."

    # Build merge command with configurable flags
    local merge_flags="--no-ff --no-commit"

    # --verify-signatures: Verify GPG signatures (security)
    [ "$MERGE_VERIFY_SIGNATURES" = "true" ] && merge_flags="$merge_flags --verify-signatures"

    # --log: Include commit descriptions in merge commit
    [ "$MERGE_LOG" = "true" ] && merge_flags="$merge_flags --log"

    # Test merge (dry-run with --no-commit)
    if git merge $merge_flags "$branch_name" 2>/dev/null; then
        log_info "Merge succeeded - committing..."

        # Get story completion stats for commit message
        local worktree_path=$(get_worktree_path "$best_wt" "$run_id" "$n_wt")
        local prd_json="$worktree_path/$RALPH_PRD_JSON"
        local stories_passed=0
        local total_stories=0

        if [ -f "$prd_json" ]; then
            stories_passed=$(jq '[.stories[] | select(.passes == true)] | length' "$prd_json" 2>/dev/null || echo 0)
            total_stories=$(jq '.stories | length' "$prd_json" 2>/dev/null || echo 0)
        fi

        # Generate commit message based on N_WT
        local commit_msg
        if [ "$n_wt" -eq 1 ]; then
            # Single worktree - simpler message
            commit_msg="feat: complete Ralph loop ($stories_passed/$total_stories stories) [run:$run_id]"
        else
            # Parallel worktrees - mention which one was selected
            commit_msg="feat: merge best Ralph result from worktree $best_wt ($stories_passed/$total_stories stories) [run:$run_id]"
        fi

        git commit -m "$commit_msg

Co-Authored-By: Claude <noreply@anthropic.com>"

        log_info "Merge completed successfully"
        return 0
    else
        # Conflicts detected
        git merge --abort 2>/dev/null || true

        log_error "Merge conflicts detected!"
        log_info "Best worktree: ${WORKTREE_PREFIX}-${best_wt}/"
        log_info "Manual merge required: git merge --no-ff $branch_name"
        return 1
    fi
}

# Cleanup worktrees
cleanup_worktrees() {
    log_info "Cleaning up worktrees..."

    # Scan up to system max to find all existing worktrees
    # Works for both: trap calls from main() and direct 'clean' subcommand
    for i in $(seq 1 $MAX_WORKTREES); do
        local worktree_path=$(find_worktree_by_index "$i")
        [ -z "$worktree_path" ] && continue  # No worktree found for this index

        local branch_name=$(get_branch_name "$i")

        # Unlock worktree first (only if we locked it during creation)
        if [ "$USE_LOCK" = "true" ]; then
            log_info "Unlocking worktree $i..."
            git worktree unlock "$worktree_path" 2>/dev/null || true
        fi

        # Remove worktree
        log_info "Removing worktree $i..."
        git worktree remove "$worktree_path" --force 2>/dev/null || true

        # Delete branch
        log_info "Deleting branch $branch_name..."
        git branch -D "$branch_name" 2>/dev/null || true
    done

    log_info "Cleanup completed"
}

# Show status of all worktrees
show_all_status() {
    log_info "Parallel Ralph Status:"
    echo ""

    # Scan up to system max to find all existing worktrees
    # Subcommand must auto-detect since it doesn't know what N_WT was used
    local found_any=false
    for i in $(seq 1 $MAX_WORKTREES); do
        local worktree_path=$(find_worktree_by_index "$i")
        [ -z "$worktree_path" ] && continue
        found_any=true
        local prd_json="$worktree_path/$RALPH_PRD_JSON"
        local progress_file="$worktree_path/$RALPH_PROGRESS_FILE"

        echo "=== Worktree $i ==="

        if [ -f "$prd_json" ]; then
            local total=$(jq '.stories | length' "$prd_json" 2>/dev/null || echo 0)
            local passed=$(jq '[.stories[] | select(.passes == true)] | length' "$prd_json" 2>/dev/null || echo 0)
            echo "Stories: $passed/$total passed"
        fi

        if [ -f "$progress_file" ]; then
            local current_story=$(tail -10 "$progress_file" | grep "Story:" | tail -1 || echo "N/A")
            echo "Current: $current_story"
        fi

        # Check if still running
        if [ -n "${WORKTREE_PIDS[$i]:-}" ]; then
            if ps -p "${WORKTREE_PIDS[$i]}" > /dev/null 2>&1; then
                echo "Status: Running (PID: ${WORKTREE_PIDS[$i]})"
            else
                echo "Status: Completed"
            fi
        fi

        echo ""
    done

    if [ "$found_any" = false ]; then
        echo "No active Ralph worktrees found."
        echo "Hint: Run 'make ralph' to start a new loop"
    fi
}

# Watch all logs live
watch_all_logs() {
    log_info "Watching all parallel logs (Ctrl+C to exit)..."

    local log_files=""
    # Scan up to system max to find all log files
    for i in $(seq 1 $MAX_WORKTREES); do
        local worktree_path=$(find_worktree_by_index "$i")
        [ -z "$worktree_path" ] && continue

        local log_file="$worktree_path/ralph.log"
        if [ -f "$log_file" ]; then
            log_files="$log_files $log_file"
        fi
    done

    if [ -n "$log_files" ]; then
        tail -f $log_files
    else
        log_warn "No log files found yet"
    fi
}

# Show specific worktree log
show_worktree_log() {
    local wt_num="${1:-1}"
    local worktree_path=$(find_worktree_by_index "$wt_num")

    if [ -z "$worktree_path" ]; then
        log_error "No worktree found for index: $wt_num"
        exit 1
    fi

    local log_file="$worktree_path/ralph.log"
    if [ -f "$log_file" ]; then
        cat "$log_file"
    else
        log_error "Log file not found: $log_file"
        exit 1
    fi
}

# Abort all parallel loops
abort_parallel() {
    log_warn "Aborting all parallel loops..."

    # Scan up to system max to find all running worktrees
    for i in $(seq 1 $MAX_WORKTREES); do
        if [ -n "${WORKTREE_PIDS[$i]:-}" ]; then
            if ps -p "${WORKTREE_PIDS[$i]}" > /dev/null 2>&1; then
                log_info "Killing worktree $i (PID: ${WORKTREE_PIDS[$i]})..."
                kill -TERM "${WORKTREE_PIDS[$i]}" 2>/dev/null || true
            fi
        fi
    done

    # Wait briefly for graceful shutdown
    sleep 2

    # Force kill if still running
    for i in $(seq 1 $MAX_WORKTREES); do
        if [ -n "${WORKTREE_PIDS[$i]:-}" ]; then
            if ps -p "${WORKTREE_PIDS[$i]}" > /dev/null 2>&1; then
                log_warn "Force killing worktree $i..."
                kill -KILL "${WORKTREE_PIDS[$i]}" 2>/dev/null || true
            fi
        fi
    done

    cleanup_worktrees
    log_info "All loops aborted"
}

# Main orchestration
main() {
    # Parse CLI arguments (or use config defaults)
    local N_WT=${1:-$RALPH_PARALLEL_N_WT}  # CLI arg or config default (1-10)
    local MAX_ITERATIONS=${2:-$RALPH_MAX_ITERATIONS}  # CLI arg or config default

    # Validate N_WT
    if [ "$N_WT" -lt 1 ] || [ "$N_WT" -gt 10 ]; then
        log_error "N_WT must be between 1 and 10 (got: $N_WT)"
        exit 1
    fi

    # Generate unique run ID for this execution
    local RUN_ID=$(generate_run_id)
    log_info "Starting Parallel Ralph Loop (run_id=$RUN_ID, N_WT=$N_WT, iterations=$MAX_ITERATIONS)"

    # Validate environment
    if ! validate_prd_json "$RALPH_PRD_JSON"; then
        exit 1
    fi

    # Setup trap for cleanup on exit
    trap cleanup_worktrees EXIT

    # Create and initialize all worktrees
    for i in $(seq 1 $N_WT); do
        create_worktree "$i" "$RUN_ID" "$N_WT"
        init_worktree_state "$i" "$RUN_ID" "$N_WT"
    done

    # Start all ralph.sh instances in parallel
    for i in $(seq 1 $N_WT); do
        start_parallel "$i" "$RUN_ID" "$N_WT"
    done

    log_info "All $N_WT worktrees started in parallel"

    # Wait for completion
    wait_and_monitor

    # Select and merge best result
    local best_wt
    if [ "$N_WT" -eq 1 ]; then
        # N_WT=1: Skip scoring overhead, use the only worktree
        log_info "Single worktree mode - merging worktree 1..."
        best_wt=1
    else
        # N_WT>1: Score all and select best
        best_wt=$(select_best "$RUN_ID" "$N_WT")
    fi

    if merge_best "$best_wt" "$N_WT" "$RUN_ID"; then
        log_info "Success! Best result merged from worktree $best_wt"
    else
        log_error "Merge failed - manual intervention required"
        exit 1
    fi

    # Cleanup happens via trap
}

# Handle command-line actions
case "${1:-run}" in
    status)
        show_all_status
        ;;
    watch)
        watch_all_logs
        ;;
    log)
        show_worktree_log "${2:-1}"
        ;;
    abort)
        abort_parallel
        ;;
    clean)
        cleanup_worktrees
        ;;
    *)
        main "$1" "$2"
        ;;
esac
