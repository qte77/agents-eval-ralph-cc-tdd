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
RALPH_LOOP_LOG_SUBDIR="ralph_logs"  # Subdirectory under RALPH_LOG_DIR for loop logs
RALPH_LOOP_LOG_DIR="$RALPH_LOG_DIR/$RALPH_LOOP_LOG_SUBDIR"  # Full path to loop logs
MAX_LOG_FILES=20  # Maximum number of validation logs to keep

# Archive configuration
ARCHIVE_BASE_DIR="src_archive"
ARCHIVE_PREFIX="agentseval_ralph_run"
ARCHIVE_SRC_SUBDIR="$SRC_BASE_DIR"  # Subdirectory within archive for source files

# Source package configuration
SRC_PACKAGE_DIR="agenteval"  # Package name under src/
SRC_DIR="$SRC_BASE_DIR/$SRC_PACKAGE_DIR"  # Full path to source package

# Ralph Loop execution parameters
RALPH_MAX_ITERATIONS=10  # Default max iterations per loop
MAX_FIX_ATTEMPTS=3  # Maximum attempts to fix validation errors
VALIDATION_TIMEOUT=${VALIDATION_TIMEOUT:-300}  # 5 minutes (allow env override)
FIX_TIMEOUT=${FIX_TIMEOUT:-600}  # 10 minutes (allow env override)

# Git branch prefixes
RALPH_STORY_BRANCH_PREFIX="ralph/story-"  # Branch prefix for story execution
RALPH_PARALLEL_BRANCH_PREFIX="ralph/parallel"  # Branch prefix for parallel worktrees

# Model configuration (AI routing)
RALPH_DEFAULT_MODEL="sonnet"  # Model for complex stories
RALPH_SIMPLE_MODEL="haiku"  # Model for simple tasks
RALPH_FIX_MODEL="haiku"  # Model for validation fixes

# Model selection patterns (case-insensitive grep -E regex)
RALPH_SIMPLE_PATTERNS="fix|typo|update.*doc|small.*change|minor|format|style|cleanup|remove.*unused"
RALPH_DOCS_PATTERNS="^(docs|documentation|readme|comment)"

# Parallel Ralph Loop configuration
RALPH_PARALLEL_N=1  # Default number of parallel worktrees (1=isolation, max=10)
RALPH_PARALLEL_WORKTREE_PREFIX="../agents-eval-ralph-wt"  # Path prefix for worktrees

# Parallel worktree flags (configurable but MANDATORY for safety)
RALPH_PARALLEL_USE_LOCK=${RALPH_PARALLEL_USE_LOCK:-true}  # Prevents pruning during execution
RALPH_PARALLEL_USE_NO_TRACK=${RALPH_PARALLEL_USE_NO_TRACK:-true}  # Local-only branches, no remote tracking
RALPH_PARALLEL_LOCK_REASON=${RALPH_PARALLEL_LOCK_REASON:-"Parallel Ralph Loop execution"}  # Lock reason message
RALPH_PARALLEL_WORKTREE_QUIET=${RALPH_PARALLEL_WORKTREE_QUIET:-false}  # Suppress worktree output

# Parallel merge flags (configurable for advanced use cases)
RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES=${RALPH_PARALLEL_MERGE_VERIFY_SIGNATURES:-false}  # Verify GPG signatures
RALPH_PARALLEL_MERGE_LOG=${RALPH_PARALLEL_MERGE_LOG:-true}  # Include commit descriptions in merge
