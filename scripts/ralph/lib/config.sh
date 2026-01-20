#!/bin/bash
# Ralph Loop - Shared configuration
# Source this file in Ralph scripts: source "$SCRIPT_DIR/lib/config.sh"

# Directory paths
RALPH_DOCS_DIR="docs/ralph"
RALPH_TEMPLATES_DIR="$RALPH_DOCS_DIR/templates"
SRC_BASE_DIR="src"
TESTS_BASE_DIR="tests"
DOCS_BASE_DIR="docs"

# State files
RALPH_PRD_JSON="$RALPH_DOCS_DIR/prd.json"
RALPH_PROGRESS_FILE="$RALPH_DOCS_DIR/progress.txt"
RALPH_PROMPT_FILE="$RALPH_TEMPLATES_DIR/prompt.md"

# Templates
RALPH_PROGRESS_TEMPLATE="$RALPH_TEMPLATES_DIR/progress.txt.template"
RALPH_PRD_TEMPLATE="$RALPH_TEMPLATES_DIR/prd.json.template"

# Logging
RALPH_LOG_DIR="/tmp"
RALPH_LOG_PATTERN="ralph_*.log"

# Archive configuration
ARCHIVE_BASE_DIR="src_archive"
ARCHIVE_PREFIX="agentseval_ralph_run"
