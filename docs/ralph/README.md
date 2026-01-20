---
title: Ralph Loop
description: Autonomous TDD development loop with Claude Code
version: 1.0.0
status: dev
created: 2026-01-19
---

Autonomous development loop that executes stories from prd.json using Test-Driven Development with Claude Code.

## Quick Start

```bash
make ralph_run [ITERATIONS=25]
# Or run directly
./scripts/ralph/ralph.sh [MAX_ITERATIONS]
```

## How It Works

```text
ralph.sh orchestrator
  ├─> reads prd.json (incomplete stories)
  ├─> builds prompt from templates/prompt.md + story details
  ├─> invokes: claude -p --dangerously-skip-permissions
  │   └─> Agent follows TDD workflow:
  │       ├─ RED: write failing tests → commit [RED]
  │       ├─ GREEN: implement code → commit [GREEN]
  │       └─ REFACTOR: clean up → commit [REFACTOR]
  ├─> verifies TDD commits ([RED] and [GREEN] markers)
  ├─> runs: make validate
  │   ├─ If pass: mark story complete
  │   └─ If fail: invoke fix loop (max 3 attempts)
  │       └─> builds prompt: templates/prompt.md + error output
  ├─> calls lib/generate_app_docs.sh
  │   ├─ generates src/*/README.md
  │   └─ generates src/*/example.py
  ├─> commits state: prd.json, progress.txt, docs
  └─> repeats until no incomplete stories or max iterations
```

## File Structure

```text
docs/ralph/
├── README.md              # This file
├── prd.json              # Story definitions and status
├── progress.txt          # Execution log
└── templates/
    └── prompt.md         # Agent instructions (TDD workflow)

scripts/ralph/
├── ralph.sh              # Main orchestrator (autonomous loop)
└── lib/
    └── generate_app_docs.sh  # README/example generation
```

## Commit Architecture

**Agent commits** (during story execution):

- `test(STORY-XXX): ... [RED]` - Failing tests
- `feat(STORY-XXX): ... [GREEN]` - Implementation
- `refactor(STORY-XXX): ... [REFACTOR]` - Cleanup

**Script commits** (after validation passes):

- `docs(STORY-XXX): update state and documentation` - State files

**Why both?** Agent commits prove TDD compliance. Script commits track progress.

## Validation & Fixes

1. **Initial validation**: `make validate` after story execution
2. **If fails**: Auto-retry loop (MAX_FIX_ATTEMPTS=3)
   - Re-invokes agent with error output
   - Re-runs `make validate`
   - Continues until pass or max attempts
3. **If passes**: Mark story complete, generate docs, commit state

## Configuration

In `ralph.sh`:

- `MAX_ITERATIONS=10` - Maximum loop iterations
- `MAX_FIX_ATTEMPTS=3` - Maximum validation fix attempts
- `PRD_JSON="docs/ralph/prd.json"` - Story definitions
- `PROGRESS_FILE="docs/ralph/progress.txt"` - Execution log
- `PROMPT_FILE="docs/ralph/templates/prompt.md"` - Agent instructions

### Model Selection

Ralph uses smart model routing to optimize cost/speed:

- `DEFAULT_MODEL="sonnet"` - Complex stories (features, refactoring)
- `SIMPLE_MODEL="haiku"` - Simple tasks
- `FIX_MODEL="haiku"` - Validation fix attempts
- `SIMPLE_PATTERNS` - Regex patterns that trigger simple model
- `DOCS_PATTERNS` - Regex patterns for documentation tasks

## Output Files

- `prd.json` - Updated with completion timestamps
- `progress.txt` - Iteration log (PASS/FAIL/RETRY status)
- `src/*/README.md` - Generated application documentation
- `src/*/example.py` - Generated usage example

## Quality Gates

All stories must pass:

- Code formatting (ruff)
- Type checking (pyright)
- All tests (pytest)

Via: `make validate`

## TDD Verification

Script enforces:

- Minimum 2 commits per story
- [RED] marker present (tests committed first)
- [GREEN] marker present (implementation committed second)
- Correct commit order (RED before GREEN)

Skipped for STORY-001 (ramp-up).

## Autonomous Operation

Runs without human approval:

- `--dangerously-skip-permissions` flag on all Claude invocations
- Auto-commits state files
- Auto-pushes to remote at completion
- No interactive prompts

## Execution Flow Details

```text
main()
  while stories incomplete:
    get_next_story() → story_id
    execute_story() → claude invocation
      └─> prompt.md + story details piped to claude -p
    check_tdd_commits() → verify [RED]/[GREEN]
    run_quality_checks() → make validate
      if fail:
        fix_validation_errors() → retry loop
          └─> prompt.md + error output piped to claude -p
    if pass:
      update_story_status() → prd.json
      commit_story_state() → git commit + push state files
  push all commits to remote
```

## Troubleshooting

- **No commits made**: Agent didn't follow TDD workflow, story retries
- **TDD verification failed**: Missing [RED] or [GREEN] markers, story retries
- **Quality checks failed**: Fix loop invoked (3 attempts), then marked FAIL
- **Max iterations reached**: Loop stops, check progress.txt for failures

## TODO

- **Parallel Story Execution**: Current story breakdown executes
  sequentially. Future optimization: implement parallel execution support in
  Ralph Loop for independent stories.
- **Memory for Lessons Learned**: Use simple mechanism with an
  `AGENT_LEARNINGS.md`
- **Bi-directional Communication**: Use simple `AGENT_REQUESTS.md` for
  session-spanning communication between humans and agents
