#!/bin/bash
# Ralph Loop - Shared configuration
# Source this file in Ralph scripts: source "$SCRIPT_DIR/lib/config.sh"
#
# Configuration categories (38 variables total):
#   - Directory paths (5 vars)
#   - Archive configuration (3 vars)
#   - Execution parameters (4 vars)
#   - Git branch prefixes (2 vars)
#   - Logging (5 vars)
#   - Model configuration (5 vars)
#   - Parallel execution (7 vars)
#   - Source package (2 vars)
#   - State files (3 vars)
#   - Templates (2 vars)
#
# Override hierarchy (highest to lowest priority):
#   1. CLI arguments (e.g., ./ralph.sh 25)
#   2. Environment variables (e.g., VALIDATION_TIMEOUT=500)
#   3. Config defaults (this file)
#
# Usage examples:
#   - Override iterations: ./ralph.sh 50
#   - Override timeout: VALIDATION_TIMEOUT=600 ./ralph.sh
#   - Override parallel N_WT: make ralph N_WT=5

# ==============================================================================
# Directory paths
# ==============================================================================
DOCS_BASE_DIR="docs"
RALPH_DOCS_DIR="docs/ralph"
RALPH_TEMPLATES_DIR="$RALPH_DOCS_DIR/templates"
SRC_BASE_DIR="src"
TESTS_BASE_DIR="tests"

# ==============================================================================
# Archive configuration
# ==============================================================================
ARCHIVE_BASE_DIR="src_archive"
ARCHIVE_PREFIX="agentseval_ralph_run"
ARCHIVE_SRC_SUBDIR="$SRC_BASE_DIR"

# ==============================================================================
# Execution parameters
# All values support environment variable override (e.g., RALPH_MAX_ITERATIONS=50 make ralph)
# ==============================================================================
RALPH_FIX_TIMEOUT=${RALPH_FIX_TIMEOUT:-600}  # Fix attempt timeout (10 min)
RALPH_MAX_FIX_ATTEMPTS=${RALPH_MAX_FIX_ATTEMPTS:-3}  # Max validation fix attempts
RALPH_MAX_ITERATIONS=${RALPH_MAX_ITERATIONS:-25}  # Default loop iterations
RALPH_VALIDATION_TIMEOUT=${RALPH_VALIDATION_TIMEOUT:-300}  # Validation timeout (5 min)

# ==============================================================================
# Git branch prefixes
# ==============================================================================
RALPH_PARALLEL_BRANCH_PREFIX="ralph/parallel"
RALPH_STORY_BRANCH_PREFIX="ralph/story-"

# ==============================================================================
# Logging
# ==============================================================================
RALPH_LOG_DIR="/tmp"
RALPH_LOG_PATTERN="ralph_*.log"
RALPH_LOOP_LOG_SUBDIR="ralph_logs"
RALPH_LOOP_LOG_DIR="$RALPH_LOG_DIR/$RALPH_LOOP_LOG_SUBDIR"
RALPH_MAX_LOG_FILES=20

# ==============================================================================
# Model configuration (AI routing)
# ==============================================================================
RALPH_DEFAULT_MODEL="sonnet"
RALPH_DOCS_PATTERNS="^(docs|documentation|readme|comment)"
RALPH_FIX_MODEL="haiku"
RALPH_SIMPLE_MODEL="haiku"
RALPH_SIMPLE_PATTERNS="fix|typo|update.*doc|small.*change|minor|format|style|cleanup|remove.*unused"

# ==============================================================================
# Parallel execution configuration
# ==============================================================================
RALPH_PARALLEL_LOCK_REASON=${RALPH_PARALLEL_LOCK_REASON:-"Parallel Ralph Loop execution"}
RALPH_PARALLEL_MERGE_LOG=${RALPH_PARALLEL_MERGE_LOG:-true}
RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES=${RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES:-false}
RALPH_PARALLEL_N_WT=1
RALPH_PARALLEL_USE_LOCK=${RALPH_PARALLEL_USE_LOCK:-true}
RALPH_PARALLEL_USE_NO_TRACK=${RALPH_PARALLEL_USE_NO_TRACK:-true}
RALPH_PARALLEL_WORKTREE_PREFIX="../agents-eval-ralph-wt"  # Relative path to avoid conflicts with main repo
RALPH_PARALLEL_WORKTREE_QUIET=${RALPH_PARALLEL_WORKTREE_QUIET:-false}

# ==============================================================================
# Source package configuration
# ==============================================================================
SRC_DIR="$SRC_BASE_DIR/$SRC_PACKAGE_DIR"
SRC_PACKAGE_DIR="agenteval"

# ==============================================================================
# State files
# ==============================================================================
RALPH_PRD_JSON="$RALPH_DOCS_DIR/prd.json"
RALPH_PROGRESS_FILE="$RALPH_DOCS_DIR/progress.txt"
RALPH_PROMPT_FILE="$RALPH_TEMPLATES_DIR/prompt.md"

# ==============================================================================
# Templates
# ==============================================================================
RALPH_PRD_TEMPLATE="$RALPH_TEMPLATES_DIR/prd.json.template"
RALPH_PROGRESS_TEMPLATE="$RALPH_TEMPLATES_DIR/progress.txt.template"
