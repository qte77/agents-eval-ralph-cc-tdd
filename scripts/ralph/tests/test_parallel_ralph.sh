#!/bin/bash
#
# E2E Test: Parallel Ralph Orchestration
#
# Basic smoke tests for parallel_ralph.sh functionality
#
# Usage: Run from project root: bash scripts/ralph/tests/test_parallel_ralph.sh
#

set -euo pipefail

# Ensure we're running from project root
if [ ! -f "Makefile" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

echo "Starting Parallel Ralph E2E Tests"
echo "=================================="

TEST_COUNT=0
PASS_COUNT=0

# Test 1: Script exists and is executable
echo ""
echo "=== Test 1: Script Validation ==="
TEST_COUNT=$((TEST_COUNT + 1))

if [ -x "scripts/ralph/parallel_ralph.sh" ]; then
    echo "✓ parallel_ralph.sh exists and is executable"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ parallel_ralph.sh not found or not executable"
fi

# Test 2: Script has required functions
echo ""
echo "=== Test 2: Function Definitions ==="
TEST_COUNT=$((TEST_COUNT + 1))

required_functions="create_worktree init_worktree_state start_parallel wait_and_monitor score_worktree select_best merge_best cleanup_worktrees"
all_found=true

for func in $required_functions; do
    if grep -q "^${func}()" scripts/ralph/parallel_ralph.sh; then
        echo "  ✓ Function '$func' defined"
    else
        echo "  ✗ Function '$func' not found"
        all_found=false
    fi
done

if [ "$all_found" = true ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "✓ All required functions defined"
else
    echo "✗ Some functions missing"
fi

# Test 3: Makefile targets exist
echo ""
echo "=== Test 3: Makefile Integration ==="
TEST_COUNT=$((TEST_COUNT + 1))

required_targets="ralph_parallel ralph_parallel_abort ralph_parallel_clean ralph_parallel_status ralph_parallel_watch ralph_parallel_log"
all_found=true

for target in $required_targets; do
    if grep -q "^${target}:" Makefile; then
        echo "  ✓ Target '$target' defined"
    else
        echo "  ✗ Target '$target' not found"
        all_found=false
    fi
done

if [ "$all_found" = true ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "✓ All Makefile targets defined"
else
    echo "✗ Some targets missing"
fi

# Test 4: Git worktree flags are configurable with safe defaults
echo ""
echo "=== Test 4: Git Worktree Flag Configuration ==="
TEST_COUNT=$((TEST_COUNT + 1))

# Check that USE_LOCK and USE_NO_TRACK default to true
if grep -q 'USE_LOCK=${USE_LOCK:-true}' scripts/ralph/parallel_ralph.sh && \
   grep -q 'USE_NO_TRACK=${USE_NO_TRACK:-true}' scripts/ralph/parallel_ralph.sh; then
    echo "✓ Worktree flags configurable with safe defaults (USE_LOCK=true, USE_NO_TRACK=true)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ Worktree flag defaults not configured properly"
fi

# Test 5: Merge strategy uses --no-ff --no-commit
echo ""
echo "=== Test 5: Merge Strategy Validation ==="
TEST_COUNT=$((TEST_COUNT + 1))

# Check that merge_flags variable includes --no-ff --no-commit
if grep -q 'merge_flags="--no-ff --no-commit"' scripts/ralph/parallel_ralph.sh && \
   grep -q 'git merge $merge_flags' scripts/ralph/parallel_ralph.sh; then
    echo "✓ Merge uses correct flags (--no-ff --no-commit) with configurable options"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ Merge missing correct flags"
fi

# Test 6: Scoring algorithm present
echo ""
echo "=== Test 6: Scoring Algorithm ==="
TEST_COUNT=$((TEST_COUNT + 1))

if grep -q "score_worktree()" scripts/ralph/parallel_ralph.sh; then
    # Check for scoring components: stories, tests, validation bonus
    if grep -A 20 "score_worktree()" scripts/ralph/parallel_ralph.sh | grep -q "stories_passed.*100"; then
        echo "✓ Scoring algorithm includes story weight (*100)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "✗ Scoring algorithm incomplete"
    fi
else
    echo "✗ Scoring function not found"
fi

# Test 7: Cleanup and unlock present
echo ""
echo "=== Test 7: Cleanup Procedures ==="
TEST_COUNT=$((TEST_COUNT + 1))

cleanup_found=true
if ! grep -q "git worktree unlock" scripts/ralph/parallel_ralph.sh; then
    echo "  ✗ Worktree unlock missing"
    cleanup_found=false
fi
if ! grep -q "git worktree remove" scripts/ralph/parallel_ralph.sh; then
    echo "  ✗ Worktree remove missing"
    cleanup_found=false
fi
if ! grep -q "git branch -D" scripts/ralph/parallel_ralph.sh; then
    echo "  ✗ Branch deletion missing"
    cleanup_found=false
fi

if [ "$cleanup_found" = true ]; then
    echo "✓ Cleanup procedures complete (unlock, remove, delete branch)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ Cleanup procedures incomplete"
fi

# Test 8: Monitoring functions present
echo ""
echo "=== Test 8: Monitoring Functions ==="
TEST_COUNT=$((TEST_COUNT + 1))

monitoring_found=true
for func in show_all_status watch_all_logs show_worktree_log; do
    if ! grep -q "${func}()" scripts/ralph/parallel_ralph.sh; then
        echo "  ✗ Function '$func' missing"
        monitoring_found=false
    fi
done

if [ "$monitoring_found" = true ]; then
    echo "✓ All monitoring functions present"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ Some monitoring functions missing"
fi

# Summary
echo ""
echo "=================================="
echo "Test Results: $PASS_COUNT/$TEST_COUNT passed"
echo "=================================="

if [ $PASS_COUNT -eq $TEST_COUNT ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
