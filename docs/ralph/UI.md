# Ralph Loop UI Integration

## Overview

Ralph Loop can integrate with **Vibe Kanban** for real-time visual workflow
monitoring during parallel story execution.

## Why Vibe Kanban?

- **Compatible architecture**: Both use Git worktrees for isolation
- **MCP + REST API**: Multiple integration options
- **Real-time updates**: WebSocket streams for live progress
- **Team-ready**: Web UI accessible to stakeholders
- **Production-ready**: 9.4k+ stars, mature codebase

### Alternative: Flux

If Vibe Kanban proves too heavyweight,
[Flux](https://paddo.dev/blog/flux-kanban-for-ai-agents) offers:

- Terminal TUI instead of web browser
- Lighter resource footprint
- Similar MCP/CLI API surface

---

## Integration Approach

### Architecture

```text
parallel_ralph.sh ──REST API──> Vibe Kanban (Web UI)
     │
     ├─ ralph.sh (worktree 1) ──status──> /api/tasks/{id}
     ├─ ralph.sh (worktree 2) ──status──> /api/tasks/{id}
     └─ ralph.sh (worktree N) ──status──> /api/tasks/{id}
```

### Phase 1: Status Sync (MVP)

**Goal:** Ralph updates Vibe Kanban cards as stories progress.

**Implementation:**

1. Create `scripts/ralph/lib/kanban.sh` (~50 lines)
   - `kanban_init_project()` - Create/find project in Vibe Kanban
   - `kanban_sync_stories()` - Convert prd.json stories to cards
   - `kanban_update_status()` - Update card status (todo/inprogress/done)

2. Hook into `scripts/ralph/ralph.sh`
   - On story start → `kanban_update_status "inprogress"`
   - On story complete → `kanban_update_status "done"`

3. Hook into `scripts/ralph/parallel_ralph.sh`
   - On startup → `kanban_init_project && kanban_sync_stories`

### Phase 2: Real-Time Monitoring

**Goal:** Watch parallel execution live in browser.

**Implementation:**

1. Add `make ralph_ui` target
   - Launch `npx vibe-kanban` in background
   - Run `make ralph` with Kanban integration enabled

2. WebSocket progress streaming (optional)
   - Push iteration/story details to `/api/tasks/stream/ws`

### Phase 3: Bidirectional Control (Future)

**Goal:** Trigger Ralph actions from UI (pause/resume/cancel stories).

**Implementation:**

1. Event listener daemon
   - Subscribe to Vibe Kanban SSE stream
   - Map UI actions to Ralph control signals

---

## Configuration

```bash
# scripts/ralph/lib/config.sh
RALPH_KANBAN_ENABLED="${RALPH_KANBAN_ENABLED:-false}"
RALPH_KANBAN_PORT="${RALPH_KANBAN_PORT:-auto}"
RALPH_KANBAN_PROJECT="${RALPH_KANBAN_PROJECT:-ralph-loop}"
```

---

## Usage Options

### Option 1: Auto-Launch UI with Ralph

```bash
make ralph_ui N_WT=3 ITERATIONS=25
```

Launches Vibe Kanban web UI automatically, then starts Ralph with sync enabled.

### Option 2: Manual (Separate Terminals)

```bash
# Terminal 1: Start UI
npx vibe-kanban

# Terminal 2: Run Ralph with sync
make ralph KANBAN_ENABLED=1 N_WT=3
```

### Option 3: Connect to Existing Instance

```bash
RALPH_KANBAN_PORT=3000 make ralph N_WT=3
```

Use if Vibe Kanban already running (e.g., shared team instance).

---

## Vibe Kanban API Reference

### REST Endpoints

| Endpoint              | Method | Purpose                    |
| --------------------- | ------ | -------------------------- |
| `/api/projects`       | POST   | Create project             |
| `/api/projects`       | GET    | List projects              |
| `/api/tasks`          | POST   | Create task (story card)   |
| `/api/tasks`          | GET    | List tasks                 |
| `/api/tasks/{id}`     | PUT    | Update status/description  |
| `/api/tasks/stream/ws`| WS     | Real-time task events      |
| `/api/events`         | SSE    | Server-sent events stream  |

### MCP Server (Alternative)

```json
{
  "mcpServers": {
    "vibe_kanban": {
      "command": "npx",
      "args": ["-y", "vibe-kanban@latest", "--mcp"]
    }
  }
}
```

**MCP Tools:**

- `create_task` - Add story card
- `update_task` - Change status/description
- `list_tasks` - Query board state
- `start_workspace_session` - Launch agent execution (conflicts with Ralph's
  worktree management)

---

## Implementation Files

| File                              | Action | Purpose                      |
| --------------------------------- | ------ | ---------------------------- |
| `scripts/ralph/lib/kanban.sh`     | Create | Vibe Kanban API wrapper      |
| `scripts/ralph/ralph.sh`          | Modify | Add status update hooks      |
| `scripts/ralph/parallel_ralph.sh` | Modify | Add initialization hooks     |
| `scripts/ralph/lib/config.sh`     | Modify | Add Kanban config variables  |
| `Makefile`                        | Modify | Add `ralph_ui` target        |

---

## Verification Checklist

- [ ] `npx vibe-kanban` starts without errors
- [ ] Web UI accessible at displayed URL
- [ ] `make ralph_ui` launches both UI and Ralph
- [ ] Cards appear matching prd.json stories
- [ ] Card status updates during execution
- [ ] Completed run shows all cards in "done" column
- [ ] Multiple parallel worktrees visible simultaneously

---

## Sources

- [Vibe Kanban GitHub](https://github.com/BloopAI/vibe-kanban)
- [Vibe Kanban Docs](https://vibekanban.com/docs)
- [MCP Server Configuration](https://vibekanban.com/docs/integrations/mcp-server-configuration)
- [Flux Alternative](https://paddo.dev/blog/flux-kanban-for-ai-agents)
