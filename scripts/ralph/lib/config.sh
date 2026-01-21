#!/bin/bash
# Ralph Loop - Shared configuration
# Source this file in Ralph scripts: source "$SCRIPT_DIR/lib/config.sh"
#
# Configuration categories (44 variables total):
#   - Directory paths (10 vars: lines 13-21)
#   - State files (3 vars: lines 24-26)
#   - Templates (2 vars: lines 29-30)
#   - Logging (5 vars: lines 33-37)
#   - Archive configuration (3 vars: lines 40-42)
#   - Source package (2 vars: lines 45-46)
#   - Execution parameters (4 vars: lines 49-52)
#   - Git branch prefixes (2 vars: lines 55-56)
#   - Model configuration (5 vars: lines 59-65)
#   - Parallel execution (8 vars: lines 68-75)
#
# Override hierarchy (highest to lowest priority):
#   1. CLI arguments (e.g., ./ralph.sh 25)
#   2. Environment variables (e.g., VALIDATION_TIMEOUT=500)
#   3. Config defaults (this file)
#
# Usage examples:
#   - Override iterations: ./ralph.sh 50
#   - Override timeout: VALIDATION_TIMEOUT=600 ./ralph.sh
#   - Override parallel N: make ralph_parallel N=5

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
RALPH_LOOP_LOG_SUBDIR="ralph_logs"
RALPH_LOOP_LOG_DIR="$RALPH_LOG_DIR/$RALPH_LOOP_LOG_SUBDIR"
RALPH_MAX_LOG_FILES=20

# Archive configuration
ARCHIVE_BASE_DIR="src_archive"
ARCHIVE_PREFIX="agentseval_ralph_run"
ARCHIVE_SRC_SUBDIR="$SRC_BASE_DIR"

# Source package configuration
SRC_PACKAGE_DIR="agenteval"
SRC_DIR="$SRC_BASE_DIR/$SRC_PACKAGE_DIR"

# Ralph Loop execution parameters
RALPH_MAX_ITERATIONS=10
RALPH_MAX_FIX_ATTEMPTS=3
RALPH_VALIDATION_TIMEOUT=300
RALPH_FIX_TIMEOUT=600

# Git branch prefixes
RALPH_STORY_BRANCH_PREFIX="ralph/story-"
RALPH_PARALLEL_BRANCH_PREFIX="ralph/parallel"

# Model configuration (AI routing)
RALPH_DEFAULT_MODEL="sonnet"
RALPH_SIMPLE_MODEL="haiku"
RALPH_FIX_MODEL="haiku"
RALPH_SIMPLE_PATTERNS="fix|typo|update.*doc|small.*change|minor|format|style|cleanup|remove.*unused"
RALPH_DOCS_PATTERNS="^(docs|documentation|readme|comment)"

# Parallel Ralph Loop configuration
RALPH_PARALLEL_N=1
RALPH_PARALLEL_WORKTREE_PREFIX="../agents-eval-ralph-wt"  # Relative path to avoid conflicts with main repo
RALPH_PARALLEL_USE_LOCK=${RALPH_PARALLEL_USE_LOCK:-true}
RALPH_PARALLEL_USE_NO_TRACK=${RALPH_PARALLEL_USE_NO_TRACK:-true}
RALPH_PARALLEL_LOCK_REASON=${RALPH_PARALLEL_LOCK_REASON:-"Parallel Ralph Loop execution"}
RALPH_PARALLEL_WORKTREE_QUIET=${RALPH_PARALLEL_WORKTREE_QUIET:-false}
RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES=${RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES:-false}
RALPH_PARALLEL_MERGE_LOG=${RALPH_PARALLEL_MERGE_LOG:-true}
