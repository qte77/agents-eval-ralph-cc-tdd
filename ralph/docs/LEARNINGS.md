# Agent Learnings

Accumulated knowledge from previous Ralph runs. Read this before starting each story, append relevant learnings after story completion.

## Validation Fixes

<!-- Append fixes that resolved validation errors -->
<!-- Format: "- [STORY-XXX] Brief description of fix" -->
- [STORY-001] Other story test files may cause type check failures - scope validation to current story files only
- [STORY-001] Create stub modules for all imported classes to resolve import errors before implementation (from fixing validation)
- [STORY-000] Use PYTHONPATH to ensure correct module loading in Ralph worktree environments
- [STORY-002] Ralph worktrees load code from parent dir - edit both worktree and parent /workspaces/agents-eval-ralph-cc-tdd/src/ files
- [STORY-002] After verifying tests pass in worktree, copy implementation to parent dir for pytest to use correct code
- [STORY-003] Optional return types (float | None) need proper handling in metrics models - check Pydantic field definitions

## Code Patterns

<!-- Append discovered codebase conventions -->
<!-- Format: "- Pattern description (discovered in STORY-XXX)" -->
- Use Pydantic BaseModel for data validation and serialization (discovered in STORY-001)
- Use httpx.Client for HTTP requests with context manager pattern (discovered in STORY-001)
- Store dataset metadata separately from data files for integrity verification (discovered in STORY-001)
- Return bool for simple success/failure indication in utility functions (discovered in STORY-001)
- Place default config in src/package/config/default.json for auto-discovery (discovered in STORY-000)
- Use Path(__file__).parent for config file path resolution (discovered in STORY-000)
- Parse JSON with context manager pattern and explicit encoding (discovered in STORY-002)
- Use .get() with defaults for optional fields when parsing JSON to models (discovered in STORY-002)
- Implement convenience functions that accept multiple parameter combinations and calculate metrics dynamically (discovered in STORY-003)
- Return None for optional metric fields when calculation is not possible (e.g., empty interaction list) (discovered in STORY-003)

## Common Mistakes

<!-- Append mistakes to avoid -->
<!-- Format: "- Mistake description (from STORY-XXX)" -->
- Tests may already exist in repo - adapt TDD cycle to commit stubs first, then implementation (from STORY-001)
- Don't forget to create stub modules before writing tests to avoid import errors (from STORY-000)
- Always verify story completion by running story-specific tests before marking complete (from STORY-000)
- Check if story is already completed before starting work - implementation may exist from previous runs (from STORY-001)
- Run pytest on story-specific test file first to check if all tests pass before assuming story needs work (from STORY-002)
- Return values with `or 0.0` fallback works for optional metrics only if the metric is not truly optional in the Metrics model (from STORY-003)

## Testing Strategies

<!-- Append effective testing approaches -->
<!-- Format: "- Strategy description (from STORY-XXX)" -->
- Use unittest.mock to patch external HTTP calls in tests (from STORY-001)
- Test both success and failure paths for external API calls (from STORY-001)
- Verify checksum validation with both valid and invalid checksums (from STORY-001)
- Use tmp_path fixture for isolated file system testing (from STORY-001)
- Test Pydantic validation errors using pytest.raises(ValidationError) (from STORY-000)
- Verify config loading with both default and custom paths (from STORY-000)
- Create mock JSON files in tmp_path for data loader tests (from STORY-002)
- Test batch loading with different batch sizes to verify slicing logic (from STORY-002)
- Test coordination quality calculation with edge cases: perfect score, mixed success/failure, empty list (from STORY-003)
- Verify ValueError is raised for invalid temporal ranges (end before start) using pytest.raises (from STORY-003)
- Test batch evaluation to ensure each run is processed independently with correct calculations (from STORY-003)
