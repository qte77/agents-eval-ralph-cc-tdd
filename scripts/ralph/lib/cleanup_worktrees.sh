#!/bin/bash
# Cleanup all Ralph worktrees and branches
# Can be sourced or called directly

# Get script directory for sourcing dependencies
_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source dependencies if not already loaded
if ! command -v log_info &> /dev/null; then
    source "$_LIB_DIR/colors.sh"
fi

if [ -z "${RALPH_PARALLEL_WORKTREE_PREFIX:-}" ]; then
    source "$_LIB_DIR/config.sh"
fi

cleanup_worktrees() {
    log_info "Cleaning up worktrees..."

    # Find all ralph worktrees and clean them
    local worktree_list=$(git worktree list | grep "$RALPH_PARALLEL_WORKTREE_PREFIX" || true)

    if [ -z "$worktree_list" ]; then
        log_info "No worktrees found to clean"
        return 0
    fi

    echo "$worktree_list" | awk '{print $1}' | while read worktree_path; do
        # Extract worktree number from path
        local wt_num=$(basename "$worktree_path" | sed "s#${RALPH_PARALLEL_WORKTREE_PREFIX}-##")
        local branch_name="${RALPH_PARALLEL_BRANCH_PREFIX}-${wt_num}"

        log_info "Removing worktree $wt_num at $worktree_path..."
        git worktree unlock "$worktree_path" 2>/dev/null || true
        git worktree remove "$worktree_path" --force 2>/dev/null || true
        git branch -D "$branch_name" 2>/dev/null || true
    done

    log_info "Cleanup completed"
}

# If called directly (not sourced), run cleanup
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    cleanup_worktrees
fi
