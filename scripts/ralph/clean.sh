#!/bin/bash
# Cleans Ralph state (worktrees + local state files)
set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/colors.sh"
source "$SCRIPT_DIR/lib/config.sh"

log_warn "This will clean ALL Ralph state:"

# Check for worktrees
worktree_count=$(git worktree list | grep -c "$RALPH_PARALLEL_WORKTREE_PREFIX" || echo 0)
if [ "$worktree_count" -gt 0 ]; then
    echo "  - $worktree_count git worktree(s)"
fi

# Check for local state files
STATE_FILES=("$RALPH_DOCS_DIR/prd.json" "$RALPH_DOCS_DIR/progress.txt")
state_count=0
for file in "${STATE_FILES[@]}"; do
    if [ -f "$file" ]; then
        state_count=$((state_count + 1))
    fi
done

if [ "$state_count" -gt 0 ]; then
    echo "  - Local state files (prd.json, progress.txt)"
fi

# If nothing to clean
if [ "$worktree_count" -eq 0 ] && [ "$state_count" -eq 0 ]; then
    log_info "No Ralph state found to clean."
    exit 0
fi

# First confirmation
echo ""
log_warn "Are you sure? This action cannot be undone."
echo -n "Type 'yes' to confirm: "
read confirm1

if [ "$confirm1" != "yes" ]; then
    log_info "Cleanup cancelled."
    exit 0
fi

# Second confirmation
echo ""
log_warn "Final confirmation required."
echo -n "Type 'YES' (uppercase) to proceed: "
read confirm2

if [ "$confirm2" != "YES" ]; then
    log_info "Cleanup cancelled."
    exit 0
fi

echo ""
log_info "Proceeding with cleanup..."

# Clean worktrees
if [ "$worktree_count" -gt 0 ]; then
    log_info "Cleaning git worktrees..."

    # Find all ralph worktrees and clean them
    git worktree list | grep "$RALPH_PARALLEL_WORKTREE_PREFIX" | awk '{print $1}' | while read worktree_path; do
        # Extract worktree number from path
        wt_num=$(basename "$worktree_path" | sed "s#${RALPH_PARALLEL_WORKTREE_PREFIX}-##")
        branch_name="${RALPH_PARALLEL_BRANCH_PREFIX}-${wt_num}"

        log_info "  Removing worktree: $worktree_path"
        git worktree unlock "$worktree_path" 2>/dev/null || true
        git worktree remove "$worktree_path" --force 2>/dev/null || true
        git branch -D "$branch_name" 2>/dev/null || true
    done

    log_success "Worktrees cleaned"
fi

# Clean local state files
if [ "$state_count" -gt 0 ]; then
    echo ""
    log_warn "Remove Ralph state files (prd.json, progress.txt)?"
    echo -n "Type 'yes' to confirm: "
    read confirm_state

    if [ "$confirm_state" = "yes" ]; then
        log_info "Cleaning local state files..."
        for file in "${STATE_FILES[@]}"; do
            if [ -f "$file" ]; then
                rm -f "$file"
                log_info "  Removed: $file"
            fi
        done
        log_success "Local state cleaned"
    else
        log_info "Skipping state file cleanup"
    fi
fi

log_success "Clean complete!"
