---
title: Commit all changes with a generated Message
name: commit-with-message
description: Generate commit message, pause for approval, then commit all changes. This slash command automates the commit workflow while giving you control over the commit message.
argument-hint: (no arguments needed)
tools: Bash, Read, Glob, Grep, MultiEdit
---

I'll commit all changes with a generated message following these steps:

## Step 1: Analyze Changes

Using Bash tool:

- `git status --porcelain` - List all changed files
- `git diff --staged` and `git diff` - Review changes
- `git log --oneline -10` - Check recent commit style

Using Read/Glob tools as needed to understand file purposes.

## Step 2: Generate Commit Message

Format:

```text
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: feat, fix, refactor, test, docs, chore

## Step 3: Pause for Approval

**Please review the commit message.**

- **Approve**: "yes", "y", "commit", "go ahead"
- **Edit**: Provide your preferred message
- **Cancel**: "no", "cancel", "stop"

## Step 4: Commit

Once approved:

- `git add .` - Stage all changes
- `git commit -m "[message]"` - Commit with approved message
- `git status` - Verify success
