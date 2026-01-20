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

**RED → GREEN → REFACTOR cycle:**

### RED: Write failing tests FIRST

- Read story from prd.json, write FAILING tests for acceptance criteria
  - Create test file in `tests/` (e.g., `tests/test_messenger.py`)
  - Write tests that verify each acceptance criterion
  - Run tests - they MUST fail (code doesn't exist yet)
  - **RUN VALIDATION**: `make validate` - fix any errors before committing
  - **COMMIT TESTS FIRST**: `git add tests/ && git commit -m "test(STORY-XXX): add failing tests [RED]

Co-Authored-By: Claude <noreply@anthropic.com>"`

### GREEN: Minimal implementation

- Study patterns in `src/`, implement MINIMAL code to pass tests
  - Create/modify implementation file (e.g., `src/agentbeats/messenger.py`)
  - Write simplest code that makes tests pass
  - Run tests - they MUST pass now
  - **RUN VALIDATION**: `make validate` - fix any errors before committing
  - **COMMIT IMPLEMENTATION**: `git add src/ && git commit -m "feat(STORY-XXX): implement to pass tests [GREEN]

Co-Authored-By: Claude <noreply@anthropic.com>"`

### REFACTOR: Clean up

- Clean up code while keeping tests passing (see core-principles.md)
  - **RUN VALIDATION**: `make validate` before committing
  - **COMMIT REFACTORINGS** (if any): `git add . && git commit -m "refactor(STORY-XXX): cleanup [REFACTOR]

Co-Authored-By: Claude <noreply@anthropic.com>"`

**CRITICAL**: Tests MUST be committed BEFORE implementation. This ensures verifiable TDD compliance and provides audit trail for agent evaluation.

## Before Writing Code (DRY CHECK - MANDATORY)

**Automatically check for existing code to reuse:**

1. Run `ls src/*/config/` → Import existing config if present
2. Run `ls src/*/models/` → Import existing models if present
3. Run `grep -r "class.*BaseModel" src/` → Find existing Pydantic models

**Import existing code, don't duplicate:**
```python
# ✅ CORRECT - Reuse existing
from myproject.models import ExistingModel
from myproject.config import Config

# ❌ WRONG - Duplicate definition
class ExistingModel(BaseModel):  # Already exists elsewhere!
    pass
```

## Available Skills

You have access to these skills:

- `designing-backend` - For architecture decisions
- `implementing-python` - For Python code implementation
- `reviewing-code` - For self-review before completion

Use skills appropriately based on task requirements.

## Quality Gates

Run `make validate` before marking complete. See `CONTRIBUTING.md` for all validation commands.

## Current Story Details

(Will be appended by ralph.sh for each iteration)
