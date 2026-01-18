---
title: Product Requirements Document
version: 1.0
applies-to: Agents and humans
purpose: Functional requirements and acceptance criteria for all user stories
---

# Product Requirements Document

## Project Overview

**Project Name**: [Your Project Name]

**Description**: [Brief description of what this project does]

**Goals**:
- [Primary goal 1]
- [Primary goal 2]

## Functional Requirements

### Core Features

#### Feature 1: [Feature Name]

**Description**: [What this feature does and why it's needed]

**User Stories**:
- As a [user type], I want to [action] so that [benefit]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

**Technical Requirements**:
- [Technical detail 1]
- [Technical detail 2]

**Files Expected**:
- `src/module_name.py` - [Description]
- `tests/test_module_name.py` - [Description]

---

#### Feature 2: [Feature Name]

**Description**: [What this feature does and why it's needed]

**User Stories**:
- As a [user type], I want to [action] so that [benefit]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]

**Technical Requirements**:
- [Technical detail 1]

**Files Expected**:
- `src/another_module.py` - [Description]

---

## Non-Functional Requirements

### Performance
- [Performance requirement 1]
- [Performance requirement 2]

### Security
- [Security requirement 1]
- [Security requirement 2]

### Code Quality
- All code must pass `make validate` (ruff, pyright, pytest)
- Follow KISS, DRY, YAGNI principles
- Test coverage > 80%

## Out of Scope

- [Feature explicitly not included]
- [Another excluded feature]

## Notes for Ralph Loop

When using the `generating-prd` skill to convert this PRD to `docs/ralph/prd.json`:

1. Each feature/user story becomes a separate atomic story
2. Stories should be implementable in a single context window (100-300 lines)
3. Acceptance criteria become the `acceptance` field
4. Files expected become the `files` field

Example story breakdown:
- "Feature 1" → STORY-001: Implement core functionality
- "Feature 1 tests" → STORY-002: Add test coverage
- "Feature 2" → STORY-003: Implement additional feature

Keep stories atomic, specific, and testable.
