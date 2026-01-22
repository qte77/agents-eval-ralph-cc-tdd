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

required_targets="ralph ralph_abort ralph_clean ralph_status ralph_watch ralph_get_log"
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

# Check that defaults are set in config.sh and sourced by parallel_ralph.sh
if grep -q 'RALPH_PARALLEL_USE_LOCK=${RALPH_PARALLEL_USE_LOCK:-true}' scripts/ralph/lib/config.sh && \
   grep -q 'RALPH_PARALLEL_USE_NO_TRACK=${RALPH_PARALLEL_USE_NO_TRACK:-true}' scripts/ralph/lib/config.sh && \
   grep -q 'source.*lib/config.sh' scripts/ralph/parallel_ralph.sh; then
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

# Test 9: JSON validation function exists and works
echo ""
echo "=== Test 9: JSON Validation ==="
TEST_COUNT=$((TEST_COUNT + 1))

# Test that validate_json.sh exists (executable bit may not be set until after commit)
if [ -f "scripts/ralph/lib/validate_json.sh" ]; then
    # Test with valid JSON
    echo '{"test": true}' > /tmp/test_valid.json
    if bash scripts/ralph/lib/validate_json.sh /tmp/test_valid.json > /dev/null 2>&1; then
        # Test with invalid JSON
        echo '{invalid}' > /tmp/test_invalid.json
        if ! bash scripts/ralph/lib/validate_json.sh /tmp/test_invalid.json > /dev/null 2>&1; then
            # Test with missing file
            if ! bash scripts/ralph/lib/validate_json.sh /tmp/nonexistent.json > /dev/null 2>&1; then
                echo "✓ validate_json.sh works correctly (valid, invalid, missing)"
                PASS_COUNT=$((PASS_COUNT + 1))
            else
                echo "✗ validate_json.sh doesn't detect missing files"
            fi
        else
            echo "✗ validate_json.sh doesn't detect invalid JSON"
        fi
    else
        echo "✗ validate_json.sh rejects valid JSON"
    fi
    rm -f /tmp/test_valid.json /tmp/test_invalid.json
else
    echo "✗ validate_json.sh missing or not executable"
fi

# Test 10: N_WT=1 optimization (skip scoring for single worktree)
echo ""
echo "=== Test 10: N_WT=1 Optimization ==="
TEST_COUNT=$((TEST_COUNT + 1))

# Check that N_WT=1 path skips scoring
if grep -q 'if \[ "$N_WT" -eq 1 \]' scripts/ralph/parallel_ralph.sh && \
   grep -A 5 'if \[ "$N_WT" -eq 1 \]' scripts/ralph/parallel_ralph.sh | grep -q 'best_wt=1'; then
    echo "✓ N_WT=1 optimization present (skips scoring)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "✗ N_WT=1 optimization missing"
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
