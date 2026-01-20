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
Usage: $0 [OPTIONS] <new_prd_file>

Archives current PRD and ralph state, then activates a new PRD.

Arguments:
  new_prd_file    Path to new PRD file (relative to project root)

Options:
  -v VERSION      Archive version (default: auto-detected)
  -h              Show this help message

Examples:
  $0 docs/PRD-Benchmarking.md
  $0 -v 2 docs/PRD-Benchmarking.md

Auto-detection:
  Version is auto-detected by counting existing archives (v1, v2, v3, ...)
EOF
    exit 1
}

# Parse options
VERSION=""
while getopts "v:h" opt; do
    case $opt in
        v) VERSION="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done
shift $((OPTIND-1))

# Validate arguments
if [ $# -ne 1 ]; then
    log_error "Missing new PRD file argument"
    usage
fi

NEW_PRD="$1"

# Validate new PRD exists
if [ ! -f "$NEW_PRD" ]; then
    log_error "File not found: $NEW_PRD"
    exit 1
fi

# Auto-detect version if not provided
if [ -z "$VERSION" ]; then
    # Count existing PRD archives
    COUNT=$(find docs/archive -maxdepth 1 -name "PRD-v*.md" 2>/dev/null | wc -l)
    VERSION=$((COUNT + 1))
    log_info "Auto-detected version: v$VERSION"
fi

ARCHIVE_DIR="docs/archive/ralph-v${VERSION}"
PRD_ARCHIVE="docs/archive/PRD-v${VERSION}.md"

log_info "Creating archive directory: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR"

log_info "Archiving current PRD: $PRD_ARCHIVE"
if [ -f "docs/PRD.md" ]; then
    mv docs/PRD.md "$PRD_ARCHIVE"
else
    log_warn "No current PRD.md to archive"
fi

log_info "Archiving ralph state to: $ARCHIVE_DIR"
if [ -f "docs/ralph/prd.json" ]; then
    mv docs/ralph/prd.json "$ARCHIVE_DIR/prd.json"
fi
if [ -f "docs/ralph/progress.txt" ]; then
    mv docs/ralph/progress.txt "$ARCHIVE_DIR/progress.txt"
fi

# Archive src code from this run (matches ${APP_NAME}_ralph_run* pattern)
APP_NAME=$(grep -oP 'packages = \["src/\K[^"\]]+' pyproject.toml || echo "")
if [ -n "$APP_NAME" ]; then
    SRC_ARCHIVE_DIR="src_archive/ralph-v${VERSION}"
    if ls src/${APP_NAME}_ralph_run* 1>/dev/null 2>&1; then
        log_info "Archiving src code to: $SRC_ARCHIVE_DIR"
        mkdir -p "$SRC_ARCHIVE_DIR"
        mv src/${APP_NAME}_ralph_run* "$SRC_ARCHIVE_DIR/"
    fi
fi

# Clean up ralph logs from /tmp
log_info "Cleaning up ralph logs..."
rm -f /tmp/ralph_*.log

log_info "Activating new PRD: $NEW_PRD -> docs/PRD.md"
cp "$NEW_PRD" docs/PRD.md
rm "$NEW_PRD"

log_info "Reorganization complete!"
echo ""
log_info "Archived:"
echo "  - PRD: $PRD_ARCHIVE"
echo "  - Ralph state: $ARCHIVE_DIR"
echo ""
log_info "Next step: Run 'make ralph_init_loop' to generate new prd.json"
