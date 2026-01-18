---
title: Phase Plan Implementation
name: phase-implement
description: Execute implementation plan following KISS/DRY/Python best practices with laser-focused goal orientation
argument-hint: [ralph] 
tools: Read, Edit, Write, Grep, Glob, Bash
---

Implement the plan following first-principles.

**Plan input (auto-detect in order):**

1. Latest plan file in `/home/vscode/.claude/plans/`
2. `docs/ralph/prd.json` (for Ralph autonomous execution)
3. Conversation context (from earlier `/phase-exec-planner` output)

If none found, prompt user for plan source.

**Validation:**

Before marking complete:

```bash
make validate
```

**Ralph Loop (Autonomous Execution):**

If `docs/ralph/prd.json` detected OR if "ralph" parameter provided run:
`make ralph_run ITERATIONS=N`

See `/phase-exec-planner` with "ralph" parameter for prd.json generation.

**Execute now:**

- **Manual**: Read plan → Implement tasks → Run `make validate` after each
- **Ralph**: Automatically runs if `docs/ralph/prd.json` detected
