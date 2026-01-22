---
title: Review and Prune LEARNINGS.md
name: review-learnings
description: Review LEARNINGS.md for quality, remove duplicates/obsolete entries, and keep it focused and actionable. Part of compound engineering workflow.
argument-hint: (no arguments needed)
tools: Read, Edit, Glob, Grep
---

I'll review `docs/ralph/LEARNINGS.md` to ensure quality and relevance following these steps:

## Step 1: Read Current State

Using Read tool:
- Read `docs/ralph/LEARNINGS.md` - Review all accumulated learnings
- Note section organization and entry patterns

## Step 2: Quality Assessment

Review each entry against compound engineering criteria:

**Quality Checklist:**
- [ ] **Actionable?** - Can future agents use this immediately?
- [ ] **Focused?** - Single clear point, no rambling?
- [ ] **Non-duplicate?** - Unique insight (not repeated)?
- [ ] **Still valid?** - Not obsoleted by recent codebase changes?
- [ ] **Goal-oriented?** - Helps future work, not just historical note?

**Identify entries to:**
- ✅ **Keep** - High quality, actionable, unique
- ✏️ **Edit** - Good insight but needs clarity/focus
- ❌ **Remove** - Duplicate, obsolete, or not actionable

## Step 3: Propose Changes

List findings in this format:

```markdown
### Keep (X entries)
- [STORY-XXX] Entry text (reason: clear, actionable)

### Edit (Y entries)
- [STORY-XXX] Current: "..."
  Proposed: "..." (reason: more focused)

### Remove (Z entries)
- [STORY-XXX] Entry text (reason: duplicate of STORY-YYY)
- [STORY-ABC] Entry text (reason: obsolete - pattern changed)
```

## Step 4: Execute Changes

Using Edit tool, apply approved changes:
- Remove obsolete/duplicate entries
- Rewrite entries for clarity and focus
- Preserve section structure

## Step 5: Summary

Report:
- Total entries reviewed: X
- Kept: X | Edited: Y | Removed: Z
- Current state: Focused and actionable

**Note**: This review should run periodically (e.g., every 5-10 completed stories) to prevent knowledge base bloat.
