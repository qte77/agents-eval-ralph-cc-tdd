#!/bin/bash
# Script to reorganize PRD files for ralph-loop
set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source libraries
source "$SCRIPT_DIR/lib/colors.sh"

# Usage info
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [new_prd_file]

Archives current PRD and ralph state, optionally activates a new PRD.

Arguments:
  new_prd_file    (Optional) Path to new PRD file to activate

Options:
  -h              Show this help message

Examples:
  $0                              # Archive only
  $0 docs/PRD-Benchmarking.md     # Archive and activate new PRD
EOF
    exit 1
}

# Parse options
while getopts "h" opt; do
    case $opt in
        h) usage ;;
        *) usage ;;
    esac
done
shift $((OPTIND-1))

# NEW_PRD is optional
NEW_PRD="${1:-}"

# Validate new PRD exists if provided
if [ -n "$NEW_PRD" ] && [ ! -f "$NEW_PRD" ]; then
    log_error "File not found: $NEW_PRD"
    exit 1
fi

# Auto-detect next run number based on existing archives
NEXT_RUN=$(ls -d src_archive/agentseval_ralph_run* 2>/dev/null | wc -l)
NEXT_RUN=$((NEXT_RUN + 1))

# Create archive directory following existing pattern
ARCHIVE_DIR="src_archive/agentseval_ralph_run${NEXT_RUN}"
log_info "Creating archive: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/docs/ralph"

# Move src/agenteval contents to archive root (preserving structure)
if [ -d "src/agenteval" ]; then
    # Copy directory structure (not the agenteval dir itself) to archive root
    cp -r src/agenteval/* "$ARCHIVE_DIR/" 2>/dev/null || true
    rm -rf src/agenteval
    log_info "Archived src/agenteval -> $ARCHIVE_DIR/"
fi

# Copy tests/ to archive
if [ -d "tests" ]; then
    cp -r tests "$ARCHIVE_DIR/tests"
    log_info "Archived tests/"
fi

# Copy docs to archive
if [ -f "docs/PRD.md" ]; then
    cp docs/PRD.md "$ARCHIVE_DIR/docs/PRD.md"
    log_info "Archived docs/PRD.md"
fi
if [ -f "docs/UserStory.md" ]; then
    cp docs/UserStory.md "$ARCHIVE_DIR/docs/UserStory.md"
    log_info "Archived docs/UserStory.md"
fi

# Copy ralph state to archive
if [ -f "docs/ralph/prd.json" ]; then
    cp docs/ralph/prd.json "$ARCHIVE_DIR/docs/ralph/prd.json"
    log_info "Archived docs/ralph/prd.json"
fi
if [ -f "docs/ralph/progress.txt" ]; then
    cp docs/ralph/progress.txt "$ARCHIVE_DIR/docs/ralph/progress.txt"
    log_info "Archived docs/ralph/progress.txt"
fi

# Clean up old ralph state
rm -f docs/ralph/prd.json docs/ralph/progress.txt

# Clean up ralph logs from /tmp
log_info "Cleaning up ralph logs..."
rm -f /tmp/ralph_*.log

# Activate new PRD if provided
if [ -n "$NEW_PRD" ]; then
    log_info "Activating new PRD: $NEW_PRD -> docs/PRD.md"
    mv "$NEW_PRD" docs/PRD.md
    log_info "Reorganization complete!"
    echo ""
    log_info "Archived to: $ARCHIVE_DIR"
    echo ""
    log_info "Next step: Run 'make ralph_init_loop' to generate new prd.json"
else
    log_info "Reorganization complete (archive only)!"
    echo ""
    log_info "Archived to: $ARCHIVE_DIR"
    echo ""
    log_info "Next step: Create a new docs/PRD.md, then run 'make ralph_init_loop'"
fi
