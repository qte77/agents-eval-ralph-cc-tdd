# Ralph Loop + Vibe Kanban Integration

## Overview

Ralph Loop can push task status to Vibe Kanban via
**MCP (Model Context Protocol)** for real-time visual monitoring.
This is a **uni-directional read-only integration** - Vibe Kanban displays
Ralph's state without controlling it.

## Architecture

```text
Ralph Loop (Orchestrator)
  ├─> Manages worktrees (../ralph-wt-*)
  ├─> Runs Claude Code agents
  ├─> Enforces TDD workflow
  └─> MCP Client ──calls MCP tools──> Vibe Kanban MCP Server
                                           └─> Web UI Display
```

**Key Points:**

- Ralph remains the orchestrator (creates worktrees, runs agents)
- Vibe Kanban is DISPLAY ONLY (shows status, doesn't launch agents)
- Integration via MCP tools: `create_task`, `update_task`
- Uni-directional: Ralph → Vibe Kanban (read-only monitoring)

## Quick Start

### Option A: Try Example Tasks (Working Demo)

See what Ralph's parallel execution looks like:

```bash
# Terminal 1: Start Vibe Kanban
make vibe_start          # Starts on port 5173

# Terminal 2: Create example tasks
make vibe_demo

# Stop when done
make vibe_stop
```

**Custom Port:** Override via environment variable:

```bash
RALPH_VIBE_PORT=8080 make vibe_start
RALPH_VIBE_PORT=8080 make vibe_demo
```

Opens browser with a simulated Ralph run (N_WT=3):

- **Done**: 2 completed stories with TDD commits
- **In Progress**: 3 active stories (simulates 3 parallel worktrees)
  - Each shows: worktree path, branch name, agent, TDD phase
- **Todo**: 2 pending stories waiting for worktree slots

**What you'll see:**

- STORY-001: Authentication (wt-1, RED phase)
- STORY-002: Validation layer (wt-2, GREEN phase)
- STORY-003: Migrations (wt-3, REFACTOR phase)

### Option B: Real Ralph Integration (Working Now!)

```bash
# Terminal 1: Start Vibe Kanban
make vibe_start          # Starts on port 5173

# Terminal 2: Run Ralph (auto-syncs in real-time)
make ralph_run N_WT=3

# Stop when done
make vibe_stop
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

| Endpoint | Purpose | When |
| --- | --- | --- |
| `GET /api/projects` | Find Ralph project | On startup |
| `POST /api/tasks` | Create task for each story | On init |
| `PUT /api/tasks/:id` | Update status (todo/inprogress/done) | Story state changes |

## Status Mapping

| Ralph State | Vibe Kanban Status |
| --- | --- |
| Story starts | `inprogress` |
| Story passes | `done` |
| Story fails | `todo` |

## Implementation Status

### ✅ REST API Integration (Complete)

Implemented in `scripts/ralph/lib/vibe.sh`:

- `_detect_vibe()` - Auto-detect Vibe Kanban on configured port
- `kanban_init()` - Create tasks from prd.json
- `kanban_update()` - Update task status in real-time

**Integration points:**

- `parallel_ralph.sh:641` - Initialize on startup
- `ralph.sh:243` - Update to "inprogress" when story starts
- `ralph.sh:532,545` - Update to "done" when story passes
- `ralph.sh:522,552,558` - Update to "todo" when story fails

### 🔮 Phase 2: MCP Protocol (Future Enhancement)

Alternative implementation using Model Context Protocol for more robust
communication. Would replace REST API calls with MCP tool invocations.

## Benefits

✅ **Zero config** - Auto-detects Vibe Kanban on any port
✅ **Uni-directional** - Ralph controls, Vibe displays
✅ **Silent fail** - Works perfectly without Vibe Kanban running
✅ **Real-time** - Status updates appear immediately
✅ **TDD preserved** - Ralph's quality gates unchanged
✅ **Parallel safe** - All N worktrees update simultaneously
✅ **Non-invasive** - Single line: `source kanban.sh`

## Alternative: Simple Monitor Script

If you don't want MCP integration, use this simple monitor:

```bash
#!/bin/bash
# watch_ralph.sh
watch -n 2 '
echo "=== Ralph Progress ==="
tail -20 docs/progress.txt
echo
echo "=== Active Worktrees ==="
git worktree list
echo
echo "=== Running Agents ==="
ps aux | grep -E "claude|ralph" | grep -v grep
'
```

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

## Configuration

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

### Demo Script

Create example tasks in running Vibe Kanban:

```bash
./scripts/ralph/vibe_demo.sh [PORT]
```

Creates 7 tasks simulating N_WT=3 parallel execution with realistic TDD workflow
details (RED/GREEN/REFACTOR phases, worktree paths, agent assignments).

## Sources

- [Vibe Kanban GitHub](https://github.com/BloopAI/vibe-kanban)
- [Vibe Kanban MCP Server Docs](https://vibekanban.com/docs/integrations/vibe-kanban-mcp-server)
- [Model Context Protocol](https://modelcontextprotocol.io)
