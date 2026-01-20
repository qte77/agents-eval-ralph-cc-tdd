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
Usage: $0 [OPTIONS]

Archives current PRD and ralph state.

Options:
  -h              Show this help message
  -l              Archive logs to logs/ (default: delete)

Examples:
  $0                              # Archive without logs
  $0 -l                           # Archive with logs
EOF
    exit 1
}

# Parse options
ARCHIVE_LOGS=false
while getopts "hl" opt; do
    case $opt in
        h) usage ;;
        l) ARCHIVE_LOGS=true ;;
        *) usage ;;
    esac
done
shift $((OPTIND-1))

# Auto-detect next run number based on existing archives
NEXT_RUN=$(ls -d src_archive/agentseval_ralph_run* 2>/dev/null | wc -l)
NEXT_RUN=$((NEXT_RUN + 1))

# Create archive directory following existing pattern
ARCHIVE_DIR="src_archive/agentseval_ralph_run${NEXT_RUN}"
log_info "Creating archive: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/docs/ralph"

# Archive source and tests
[ -d "src/agenteval" ] && mv src/agenteval/* "$ARCHIVE_DIR/" 2>/dev/null && rmdir src/agenteval && log_info "Archived src/agenteval -> $ARCHIVE_DIR/"
[ -d "tests" ] && mv tests "$ARCHIVE_DIR/tests" && log_info "Archived tests/"

# Copy docs to archive (keep originals)
for doc in PRD.md UserStory.md; do
    if [ -f "docs/$doc" ]; then
        cp "docs/$doc" "$ARCHIVE_DIR/docs/$doc"
        log_info "Archived docs/$doc"
    fi
done

# Move ralph state to archive
for file in prd.json progress.txt; do
    if [ -f "docs/ralph/$file" ]; then
        mv "docs/ralph/$file" "$ARCHIVE_DIR/docs/ralph/$file"
        log_info "Archived docs/ralph/$file"
    fi
done

# Handle ralph logs from /tmp
if [ "$ARCHIVE_LOGS" = true ]; then
    mkdir -p "$ARCHIVE_DIR/logs"
    mv /tmp/ralph_*.log "$ARCHIVE_DIR/logs/" 2>/dev/null && log_info "Archived logs/" || true
else
    log_info "Cleaning up ralph logs..."
    rm -f /tmp/ralph_*.log
fi

log_info "Reorganization complete!"
echo ""
log_info "Archived to: $ARCHIVE_DIR"
echo ""
log_info "Next step: Create a new docs/PRD.md, then run 'make ralph_init_loop'"
