---
title: Ralph Loop
description: Autonomous TDD development loop with Claude Code
version: 1.0.0
status: dev
created: 2026-01-19
---

Autonomous development loop that executes stories from prd.json using Test-Driven Development with Claude Code.

## Prerequisites

Ralph Loop requires the following system dependencies:

- **Bash** - Shell interpreter (pre-installed on Linux/macOS)
- **Claude Code CLI** - `claude` command ([installation guide](https://github.com/anthropics/claude-code))
- **jq** - JSON processor
  - Linux: `apt-get install jq` or `yum install jq`
  - macOS: `brew install jq`
  - Verify: `jq --version`
- **git** - Version control (required for worktrees)
- **make** - Build automation tool

Run `make ralph_init_loop` to validate all prerequisites are installed.

## Quick Start

```bash
make ralph [ITERATIONS=25]           # Single loop (isolated via worktree)
make ralph N_WT=5 ITERATIONS=25         # 5 parallel loops
```

## How It Works

```text
parallel_ralph.sh (orchestrator - always used, even N_WT=1)
  ├─> creates N_WT git worktrees (isolated environments)
  ├─> runs ralph.sh in each worktree (background jobs)
  │   └─> ralph.sh (worker):
  │       ├─> reads prd.json (incomplete stories)
  │       ├─> builds prompt from templates/prompt.md + story details
  │       ├─> invokes: claude -p --dangerously-skip-permissions
  │       │   └─> Agent follows TDD workflow:
  │       │       ├─ RED: write failing tests → commit [RED]
  │       │       ├─ GREEN: implement code → commit [GREEN]
  │       │       └─ REFACTOR: clean up → commit [REFACTOR]
  │       ├─> verifies TDD commits ([RED] and [GREEN] markers)
  │       ├─> runs: make validate
  │       │   ├─ If pass: mark story complete
  │       │   └─ If fail: invoke fix loop (max 3 attempts)
  │       ├─> generates docs (README.md, example.py)
  │       ├─> commits state: prd.json, progress.txt, docs
  │       └─> repeats until no incomplete stories or max iterations
  ├─> waits for all worktrees to complete
  ├─> N_WT=1: merges result (no scoring overhead)
  ├─> N_WT>1: scores all, merges best result
  └─> cleans up worktrees
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
├── parallel_ralph.sh     # Orchestrator: worktree management, scoring, merging
├── ralph.sh              # Worker: TDD loop execution (runs inside worktrees)
├── init.sh              # Environment initialization
├── archive.sh           # Archive current run state
├── abort.sh             # Terminate running loops
├── clean.sh             # Clean Ralph state (worktrees + local)
└── lib/
    ├── config.sh        # Centralized configuration
    ├── colors.sh        # Logging utilities
    ├── validate_json.sh # JSON validation utilities
    └── generate_app_docs.sh  # README/example generation
```

## Script Usage

- `init.sh` - Initialize environment (first time setup)
- `archive.sh` - Archive completed run before new iteration
- `abort.sh` - Emergency stop (kills loops + cleans worktrees)
- `clean.sh` - Reset to clean state (removes worktrees + local state)

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

## Execution Modes

**All execution uses git worktrees** (even N_WT=1) for safety and isolation.

```bash
# Single loop (N_WT=1, default)
make ralph [ITERATIONS=25]      # Isolated in worktree, no scoring overhead

# Parallel loops (N_WT>1)
make ralph N_WT=5 ITERATIONS=25    # 5 worktrees, scores results, merges best

# Monitoring
make ralph_status               # Progress summary with timestamp
make ralph_watch                # Live tail all logs
make ralph_log WT=2             # View specific worktree

# Control
make ralph_abort                # Abort all loops + cleanup
make ralph_clean                # Clean worktrees + local state (requires double confirmation)
```

**Safety Features:**

- `ralph_clean` requires double confirmation:
  1. Type `'yes'` to confirm
  2. Type `'YES'` (uppercase) to proceed
- Shows what will be deleted before asking for confirmation
- Cannot be undone - use with caution

**Scoring:**

(N_WT>1 only): `(stories × 100) + test_count + validation_bonus`

**Config:**

`RALPH_PARALLEL_*` variables in `scripts/ralph/lib/config.sh`

## Execution Flow Details

```text
make ralph [N_WT=1] [ITERATIONS=25]
  └─> parallel_ralph.sh
       ├─> creates N_WT worktrees
       ├─> for each worktree: ralph.sh (background) →
       │    └─> while stories incomplete:
       │         ├─ get_next_story() → story_id
       │         ├─ execute_story() → claude -p (TDD workflow)
       │         ├─ check_tdd_commits() → verify [RED]/[GREEN]
       │         ├─ run_quality_checks() → make validate
       │         │   └─ if fail: fix_validation_errors() (3 attempts)
       │         ├─ if pass: update_story_status() → prd.json
       │         ├─ commit_story_state() → git commit
       │         └─ repeat
       ├─> wait for all worktrees
       ├─> if N_WT=1: merge worktree 1
       ├─> if N_WT>1: score all, merge best
       └─> cleanup worktrees
```

## Troubleshooting

- **No commits made**: Agent didn't follow TDD workflow, story retries
- **TDD verification failed**: Missing [RED] or [GREEN] markers, story retries
- **Quality checks failed**: Fix loop invoked (3 attempts), then marked FAIL
- **Max iterations reached**: Loop stops, check progress.txt for failures

## TODO

### High Priority (High ROI)

- **Claude Judge for Parallel Runs**: LLM-as-Judge functionality to enhance simple scoring `(stories × 100) + test_count` with AI-based evaluation. Claude evaluates code quality, design, test coverage across worktrees. Can recommend "winner" or "cherry-pick" best modules from each worktree into hybrid codebase. Add `templates/judge.md` prompt and `lib/judge.sh`.
- **Directory Consolidation**: Consolidate `scripts/ralph/` and `docs/ralph/` into single `ralph/` root directory for cleaner ownership. Structure: `ralph/{scripts,templates,state,docs}`. Add symlinks for backward compatibility.
- **Clean up intermediate files**: Remove `*_green.py`, `*_red.py`, `*_stub` after story completion
- **E2E tests**: Add end-to-end test coverage for full application paths

### Medium Priority

- **Smart Story Distribution**: Analyze dependency graph, run independent stories in parallel by spinning up a new worktree
- **Memory/Lessons Learned**: Simple `AGENT_LEARNINGS.md` mechanism
- **Bi-directional Communication**: `AGENT_REQUESTS.md` for human-agent communication
- **Auto-resolve Conflicts**: Programmatic merge conflict resolution
- **Plugin Integration**: Ralph commands as Claude Code skills on marketplace
- **Packaging for pypi and npm**: Provide as packages for python and node
- **Vibe Kanban UI Exploration**: Evaluate [Vibe Kanban](https://github.com/BloopAI/vibe-kanban) (9.4k stars, Apache 2.0) as visual UI layer. Provides Kanban board for parallel agents, git worktree isolation, built-in diff review. Install: `npx vibe-kanban`. Compatible with Claude Code.

### Low Priority (Future Exploration)

- **Real-time Dashboard**: Live monitoring UI for parallel worktrees
- **JSON Status API Output** (Team/Enterprise quick win): Add `ralph --status --json` for structured output. Foundation for dashboards, CI/CD hooks, monitoring. Enables Grafana, Datadog, custom UIs.
- **Slack/Teams Notifications** (Team/Enterprise quick win): Post completion/failure alerts to team channels. Hook into `parallel_ralph.sh` completion. Example: "Ralph completed STORY-005 ✅" → `#dev-alerts`.
- **Rippletide Eval Integration**: Add hallucination detection for generated docs/comments using [Rippletide Eval CLI](https://docs.rippletide.com). Scores agent outputs 1-4, flags unsupported claims.
- **Conductor.build Integration** (macOS only): Evaluate [Conductor](https://conductor.build) for visual parallel agent orchestration. Uses same git worktree pattern as Ralph. Main value: visual dashboard, code review UI. Consider if team uses macOS; otherwise Vibe Kanban (cross-platform, open source) covers similar needs.
- **Omnara.com Integration**: Mobile/voice interface for Claude Code. Available SDKs (no custom HTTP layer needed):
  - **Python SDK**: `pip install omnara` - log events, request user input programmatically
  - **NPM CLI**: `@omnara/cli` - CLI wrapper
  - **n8n nodes**: `n8n-nodes-omnara` - workflow automation with "Human in the Loop" node
  - **New platform**: `curl -fsSL https://omnara.com/install/install.sh | bash` (built on Claude Agent SDK)
  - **Devcontainer note**: No explicit devcontainer/remote container support. Designed for local machine agents. Workaround: run Omnara inside the container, mount `.claude` folder for persistence.
  - Potential use: push notifications on Ralph completion, mobile approval for cherry-pick decisions, remote status monitoring. See [GitHub](https://github.com/omnara-ai/omnara), [PyPI](https://pypi.org/project/omnara/).
