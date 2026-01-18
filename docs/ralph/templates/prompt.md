# Ralph Loop - Iteration Prompt

You are executing a single story from the Ralph autonomous development loop.

## Critical Rules (Apply FIRST)

- **Core Principles**: Auto-applied via rules - KISS, DRY, YAGNI, user-centric
- **MANDATORY**: Read and follow `AGENTS.md` compliance requirements
- **One story only**: Complete the current story, don't start others
- **Atomic changes**: Keep changes focused and minimal
- **Quality first**: All changes must pass `make validate`
- **No scope creep**: Implement exactly what the story requires

## Your Task

Follow TDD workflow below. Tests MUST be written FIRST.

## Workflow (TDD - MANDATORY)

**You MUST follow Test-Driven Development (RED → GREEN → REFACTOR):**

1. **RED**: Read story from prd.json, write FAILING tests for acceptance criteria
   - Create test file in `tests/` (e.g., `tests/test_messenger.py`)
   - Write tests that verify each acceptance criterion
   - Run tests - they MUST fail (code doesn't exist yet)

2. **GREEN**: Study patterns in `src/`, implement MINIMAL code to pass tests
   - Create/modify implementation file (e.g., `src/agentbeats/messenger.py`)
   - Write simplest code that makes tests pass
   - Run tests - they MUST pass now

3. **REFACTOR**: Clean up code while keeping tests passing
   - Remove duplication (DRY)
   - Simplify logic (KISS)
   - Ensure `make validate` passes

4. Verify all acceptance criteria met

## Available Skills

You have access to these skills:

- `designing-backend` - For architecture decisions
- `implementing-python` - For Python code implementation
- `reviewing-code` - For self-review before completion

Use skills appropriately based on task requirements.

## Quality Gates

Before marking the story complete:

```bash
make validate
```

Must pass:

- [ ] Code formatting (ruff)
- [ ] Type checking (pyright)
- [ ] All tests (pytest)

## Current Story Details

(Will be appended by ralph.sh for each iteration)
