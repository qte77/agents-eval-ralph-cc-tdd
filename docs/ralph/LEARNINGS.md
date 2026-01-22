# Agent Learnings

Accumulated knowledge from previous Ralph runs. Read this before starting each story, append relevant learnings after story completion.

## Validation Fixes

<!-- Append fixes that resolved validation errors -->
<!-- Format: "- [STORY-XXX] Brief description of fix" -->

## Code Patterns

<!-- Append discovered codebase conventions -->
<!-- Format: "- Pattern description (discovered in STORY-XXX)" -->
- Use Pydantic BaseModel for data validation and serialization (discovered in STORY-001)
- Use httpx.Client for HTTP requests with context manager pattern (discovered in STORY-001)
- Store dataset metadata separately from data files for integrity verification (discovered in STORY-001)

## Common Mistakes

<!-- Append mistakes to avoid -->
<!-- Format: "- Mistake description (from STORY-XXX)" -->

## Testing Strategies

<!-- Append effective testing approaches -->
<!-- Format: "- Strategy description (from STORY-XXX)" -->
- Use unittest.mock to patch external HTTP calls in tests (from STORY-001)
- Test both success and failure paths for external API calls (from STORY-001)
- Verify checksum validation with both valid and invalid checksums (from STORY-001)
- Use tmp_path fixture for isolated file system testing (from STORY-001)
