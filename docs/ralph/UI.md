# Ralph Loop + Vibe Kanban Integration

## Overview

Ralph Loop can push task status to Vibe Kanban via
REST API for real-time visual monitoring.
This is a **uni-directional read-only integration** - Vibe Kanban displays
Ralph's state without controlling it.

## Architecture

```text
Ralph Loop (Orchestrator)
  ├─> Manages worktrees (../ralph-wt-*)
  ├─> Runs Claude Code agents
  ├─> Enforces TDD workflow
  └─> REST API
              └─> Web UI Display
```

**Key Points:**

- Ralph remains the orchestrator (creates worktrees, runs agents)
- Vibe Kanban is DISPLAY ONLY (shows status, doesn't launch agents)
- Integration via REST API: `create_task`, `update_task`
- Uni-directional: Ralph → Vibe Kanban (read-only monitoring)

## Quick Start

### Real Ralph Integration

```bash
# Terminal 1: Start Vibe Kanban
make vibe_start          # Starts on port 5173

# Terminal 2: Run Ralph (auto-syncs in real-time)
make ralph_run N_WT=3

# Stop when done
make vibe_stop_all
```

Ralph will:

1. Auto-detect Vibe Kanban on configured port (default: 5173)
2. Create tasks from prd.json (all start as "todo")
3. Update status in real-time:
   - Story starts → "inprogress"
   - Story passes → "done"
   - Story fails → "todo"
4. Works across all parallel worktrees simultaneously

## Configuration

### Port Configuration

Default port: **5173** (configured in `scripts/ralph/lib/config.sh`)

**To change port:**

```bash
# Set in config.sh
RALPH_VIBE_PORT=8080

# Or override at runtime
RALPH_VIBE_PORT=8080 make vibe_start
RALPH_VIBE_PORT=8080 make ralph_run
```

Ralph auto-detects Vibe Kanban at the configured port and syncs automatically.

## REST API Integration

Ralph uses Vibe Kanban REST API endpoints:

### GET /api/projects

Get project list to find Ralph project ID.

```bash
curl -s http://127.0.0.1:5173/api/projects | jq -r '.data[0].id'
```

### POST /api/tasks

Create task for each story from prd.json.

```bash
curl -X POST http://127.0.0.1:5173/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project-uuid",
    "title": "[run_id] [WT1] STORY-001: Title",
    "description": "Story description\n\nAcceptance Criteria:\n
- Criterion 1\n- Criterion 2",
    "status": "todo"
  }'
```

### PUT /api/tasks/:id

Update task status during execution.

```bash
curl -X PUT http://127.0.0.1:5173/api/tasks/{task-uuid} \
  -H "Content-Type: application/json" \
  -d '{"status": "inprogress"}'
```

## Status Lifecycle

| Status | When | Description |
| --- | --- | --- |
| `todo` | Initial, or failed | Story not started or returned to queue |
| `inprogress` | Story execution starts | Claude Code working on story |
| `inreview` | Quality checks running | Tests and validation in progress |
| `done` | Story passes | All acceptance criteria met |
| `cancelled` | MAX_ITERATIONS reached | Story incomplete after max attempts |

**Source**: `scripts/ralph/lib/vibe.sh` (kanban_init, kanban_update)

## Vibe Kanban Data Storage

Vibe Kanban stores all data locally in `~/.vibe/`:

```text
~/.vibe/
├── vibe.db              # SQLite database (projects, tasks, attempts)
├── profiles.json        # Agent configurations (custom overrides)
├── images/              # Uploaded task images/screenshots
└── logs/                # Execution logs
```

**Key Files:**

- `vibe.db` - All project and task state
- `profiles.json` - Custom agent configurations (GUI: Settings → Agents)

## Project Configuration

### Auto-Generated Project Config

Ralph initialization creates `.vibe-kanban/project.json` from template:

```bash
make ralph_init_loop
# or
./scripts/ralph/init.sh
```

Template location: `docs/ralph/templates/vibe-project.json.template`

**Variables populated:**

- `{{PROJECT_NAME}}` - From git repo or directory name
- `{{GIT_REPO_PATH}}` - Current directory (.)
- `{{WORKTREE_PREFIX}}` - From `RALPH_PARALLEL_WORKTREE_PREFIX`
- `{{PRD_PATH}}` - From `RALPH_PRD_JSON`
- `{{PROGRESS_PATH}}` - From `RALPH_PROGRESS_FILE`

## Sources

- [Vibe Kanban GitHub](https://github.com/BloopAI/vibe-kanban)
