#!/bin/bash
# Claude-as-Judge evaluation library for parallel Ralph
# Uses LLM-based pairwise comparison to select best worktree

# Source dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/colors.sh"

# Evaluate worktrees using Claude-as-Judge
# Args: $1=run_id, $2=n_wt
# Outputs: winner worktree index (echoed)
# Returns: 0 on success, 1 if judge disabled/failed (caller should fall back to metrics)
judge_worktrees() {
    local run_id="$1"
    local n_wt="$2"

    # Check if enabled
    if [ "${RALPH_JUDGE_ENABLED:-false}" != "true" ]; then
        return 1
    fi

    # Check worktree count limit
    if [ "$n_wt" -gt "${RALPH_JUDGE_MAX_WT:-5}" ]; then
        log_warn "Too many worktrees ($n_wt > ${RALPH_JUDGE_MAX_WT:-5}) - falling back to metrics"
        return 1
    fi

    log_info "Running Claude-as-Judge evaluation for $n_wt worktrees..."

    # Build prompt from template
    local judge_prompt=$(mktemp)
    local judge_output=$(mktemp)

    if [ ! -f "$RALPH_JUDGE_TEMPLATE" ]; then
        log_error "Judge template not found: $RALPH_JUDGE_TEMPLATE"
        rm -f "$judge_prompt" "$judge_output"
        return 1
    fi

    cat "$RALPH_JUDGE_TEMPLATE" > "$judge_prompt"
    echo "" >> "$judge_prompt"

    # Append worktree data for each worktree
    for i in $(seq 1 $n_wt); do
        local worktree_path=$(get_worktree_path "$i" "$run_id" "$n_wt")
        local prd_json="$worktree_path/$RALPH_PRD_JSON"
        local log_file="$worktree_path/ralph.log"

        # Collect metrics (reuses extract_* functions from parallel_ralph.sh)
        local stories_passed=$(jq '[.stories[] | select(.passes == true)] | length' "$prd_json" 2>/dev/null || echo 0)
        local total_stories=$(jq '.stories | length' "$prd_json" 2>/dev/null || echo 0)
        local test_count=$(find "$worktree_path" -name "test_*.py" -type f 2>/dev/null | wc -l)
        local coverage=$(extract_coverage "$log_file" 2>/dev/null || echo 0)
        local ruff_violations=$(extract_ruff_violations "$log_file" 2>/dev/null || echo 0)
        local pyright_errors=$(extract_pyright_errors "$log_file" 2>/dev/null || echo 0)

        # Get diff summary (limited to avoid token explosion)
        local diff_summary=$(cd "$worktree_path" && git diff --stat HEAD~5 2>/dev/null | tail -20 || echo "No diff available")

        # Append to prompt
        cat <<EOF >> "$judge_prompt"

## Worktree $i

**Metrics:**
- stories_passed: $stories_passed/$total_stories
- test_count: $test_count
- coverage: ${coverage}%
- ruff_violations: $ruff_violations
- pyright_errors: $pyright_errors

**Diff summary:**
\`\`\`
$diff_summary
\`\`\`
EOF
    done

    # Invoke Claude with timeout
    local timeout_val="${RALPH_JUDGE_TIMEOUT:-120}"
    local model="${RALPH_JUDGE_MODEL:-sonnet}"

    if timeout "$timeout_val" bash -c \
        "cat \"$judge_prompt\" | claude -p --model \"$model\" --dangerously-skip-permissions" \
        > "$judge_output" 2>&1; then

        # Parse JSON response
        local winner=$(jq -r '.winner' "$judge_output" 2>/dev/null || \
                      grep -oP '"winner"\s*:\s*\K\d+' "$judge_output" 2>/dev/null | head -1)
        local reason=$(jq -r '.reason' "$judge_output" 2>/dev/null || echo "No reason provided")

        if [ -n "$winner" ] && [ "$winner" -ge 1 ] && [ "$winner" -le "$n_wt" ]; then
            log_info "Judge selected worktree $winner: $reason"
            rm -f "$judge_prompt" "$judge_output"
            echo "$winner"
            return 0
        else
            log_warn "Judge returned invalid winner ($winner) - falling back to metrics"
            rm -f "$judge_prompt" "$judge_output"
            return 1
        fi
    else
        log_warn "Judge evaluation timed out or failed - falling back to metrics"
        rm -f "$judge_prompt" "$judge_output"
        return 1
    fi
}
