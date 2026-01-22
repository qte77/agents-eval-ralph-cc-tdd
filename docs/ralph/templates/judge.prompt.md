---
title: Ralph Judge
description: Claude-as-Judge evaluation prompt for parallel worktree selection
---

# Worktree Comparison Task

Compare the worktrees below and select the BEST one based on code quality.

## Evaluation Criteria (Priority Order)

1. **Correctness** - All tests pass, meets acceptance criteria
2. **Test Quality** - Comprehensive coverage, meaningful edge cases
3. **Code Clarity** - Readable, maintainable, follows best practices

## Instructions

- Consider the quantitative metrics provided, but use your judgment
- Favor quality over quantity (fewer stories with better code > more stories with technical debt)
- Look for red flags: high error counts, low coverage, excessive churn

## Required Output Format

Output ONLY valid JSON (no markdown, no explanation):

```json
{
  "winner": <worktree_number>,
  "reason": "<one concise sentence explaining why>"
}
```

## Worktrees to Compare

(Data appended by judge.sh below)
