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
├── parallel_ralph.sh     # Parallel execution via git worktrees
├── init.sh              # Environment initialization
├── reorganize_prd.sh    # Archive current PRD state
├── abort.sh             # Terminate running loops
└── lib/
    ├── config.sh        # Centralized configuration
    ├── colors.sh        # Logging utilities
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

Centralized in `scripts/ralph/lib/config.sh`:

**Execution:**

- `RALPH_MAX_ITERATIONS=10` - Loop iterations
- `RALPH_MAX_FIX_ATTEMPTS=3` - Fix attempts
- `RALPH_VALIDATION_TIMEOUT=300` - Validation timeout (5 min)
- `RALPH_FIX_TIMEOUT=600` - Fix timeout (10 min)

**Models:**

- `RALPH_DEFAULT_MODEL="sonnet"` - Complex stories
- `RALPH_SIMPLE_MODEL="haiku"` - Simple tasks
- `RALPH_FIX_MODEL="haiku"` - Fix attempts

**Override hierarchy:**

1. CLI: `./ralph.sh 50`
2. Env: `VALIDATION_TIMEOUT=600 ./ralph.sh`
3. Config: `scripts/ralph/lib/config.sh`

See `config.sh` header for complete list.

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

## Parallel Execution

Run multiple loops simultaneously via git worktrees:

```bash
make ralph_parallel N=5 ITERATIONS=25  # 5 parallel loops
make ralph_parallel_status             # Monitor progress
make ralph_parallel_watch              # Live tail all logs
```

**How it works:**

1. Creates N isolated git worktrees
2. Runs ralph.sh in each simultaneously
3. Scores: `(stories × 100) + tests + validation_bonus`
4. Merges best result to main branch
5. Cleans up worktrees

**Config:** `RALPH_PARALLEL_*` variables in `config.sh`

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

- **Clean up intermediate files**: Remove `*_green.py`, `*_red.py`, `*_stub` after story completion
- **E2E tests**: Add end-to-end test coverage for full application paths
- **Smart Story Distribution**: Analyze dependency graph, distribute independent stories across worktrees
- **Memory/Lessons Learned**: Simple `AGENT_LEARNINGS.md` mechanism
- **Bi-directional Communication**: `AGENT_REQUESTS.md` for human-agent communication
- **Real-time Dashboard**: Live monitoring UI for parallel worktrees
- **Auto-resolve Conflicts**: Programmatic merge conflict resolution
- **Plugin Integration**: Ralph commands as Claude Code skills
