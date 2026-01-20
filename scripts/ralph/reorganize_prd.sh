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

# Configuration
SRC_DIR="src/agenteval"
TESTS_DIR="tests"
DOCS_DIR="docs"
RALPH_DIR="docs/ralph"
ARCHIVE_BASE="src_archive"
ARCHIVE_PREFIX="agentseval_ralph_run"
DOC_FILES=("PRD.md" "UserStory.md")
STATE_FILES=("prd.json" "progress.txt")
LOG_DIR="/tmp"
LOG_PATTERN="ralph_*.log"

# Auto-detect next run number based on existing archives
NEXT_RUN=$(ls -d "$ARCHIVE_BASE/${ARCHIVE_PREFIX}"* 2>/dev/null | wc -l)
NEXT_RUN=$((NEXT_RUN + 1))

# Create archive directory following existing pattern
ARCHIVE_DIR="$ARCHIVE_BASE/${ARCHIVE_PREFIX}${NEXT_RUN}"
log_info "Creating archive: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/$DOCS_DIR"

# Archive source and tests
for dir in "$SRC_DIR" "$TESTS_DIR"; do
    [ ! -d "$dir" ] && continue
    if [ "$dir" = "$SRC_DIR" ]; then
        mv "$dir"/* "$ARCHIVE_DIR/" 2>/dev/null && rmdir "$dir"
    else
        mv "$dir" "$ARCHIVE_DIR/"
    fi
    log_info "Archived $dir/"
done

# Copy docs to archive (keep originals)
for doc in "${DOC_FILES[@]}"; do
    if [ -f "$DOCS_DIR/$doc" ]; then
        cp "$DOCS_DIR/$doc" "$ARCHIVE_DIR/$DOCS_DIR/$doc"
        log_info "Archived $DOCS_DIR/$doc"
    fi
done

# Archive ralph directory (copy templates, move state files)
if [ -d "$RALPH_DIR" ]; then
    mkdir -p "$ARCHIVE_DIR/$RALPH_DIR"
    # Copy all files first
    cp -r "$RALPH_DIR"/* "$ARCHIVE_DIR/$RALPH_DIR/" 2>/dev/null || true
    # Remove only state files from source
    for file in "${STATE_FILES[@]}"; do
        rm -f "$RALPH_DIR/$file"
    done
    log_info "Archived $RALPH_DIR/"
fi

# Handle ralph logs
if [ "$ARCHIVE_LOGS" = true ]; then
    mkdir -p "$ARCHIVE_DIR/logs"
    mv "$LOG_DIR/$LOG_PATTERN" "$ARCHIVE_DIR/logs/" 2>/dev/null && log_info "Archived logs/" || true
else
    log_info "Cleaning up ralph logs..."
    rm -f "$LOG_DIR/$LOG_PATTERN"
fi

log_info "Reorganization complete!"
echo ""
log_info "Archived to: $ARCHIVE_DIR"
echo ""
log_info "Next step: Create a new $DOCS_DIR/PRD.md, then run 'make ralph_init_loop'"
