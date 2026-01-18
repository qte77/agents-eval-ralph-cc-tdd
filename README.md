# Python Ralph-Loop Template

> What a time to be alive

Out-of-the-box Python project template using Ralph Loop autonomous development with Claude Code (plugins, skills, rules), TDD, uv, ruff, pyright, pytest.

![Version](https://img.shields.io/badge/version-0.0.0-58f4c2.svg)
[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
[![CodeQL](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/codeql.yaml/badge.svg)](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/YOUR-ORG/YOUR-PROJECT-NAME/badge)](https://www.codefactor.io/repository/github/YOUR-ORG/YOUR-PROJECT-NAME)
[![ruff](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/ruff.yaml/badge.svg)](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/ruff.yaml)
[![pyright](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/pyright.yaml/badge.svg)](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/pyright.yaml)
[![pytest](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/pytest.yaml/badge.svg)](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/links-fail-fast.yaml)
[![Deploy Docs](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/YOUR-ORG/YOUR-PROJECT-NAME/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)

## Features

- **Ralph Loop** - Autonomous development using a shell loop
- **Claude Code** - Pre-configured skills, plugins, rules, and commands for AI-assisted development
- **Makefile** - Build automation, Ralph orchestration, and validation commands
- **Python Tooling** - ruff (linting/formatting), pyright (type checking), pytest (testing)
- **MkDocs** - Auto-generated documentation with GitHub Pages deployment
- **GitHub Actions** - CI/CD workflows (CodeQL, ruff, pyright, pytest, link checking, docs deployment)
- **DevContainers** - Template (Alpine ~10MB) and actual project (Python/Node/Docker ~1GB+)
- **VS Code** - Workspace settings, tasks, and extensions for optimal Python development

## Quick Start

```bash
# 1. Customize template with your project details
# The devcontainer needs a rebuild, if the python version was changed
make setup_project

# 2. Setup development environment, if not done by devcontainer.json
make setup_dev

# Optional
make ralph_userstory            # Interactive User Story using CC
make ralph_prd                  # Generate PRD.md from UserStory.md 

# 3. Write requirements in docs/PRD.md, then run Ralph
make ralph_init                 # Initialize (creates prd.json)
make ralph_run [ITERATIONS=25]  # Run autonomous development
make ralph_status               # Check progress

# 4. Post-run options
# Reset state (removes prd.json, progress.txt)
make ralph_clean
# Archive and start new iteration
make ralph_reorganize NEW_PRD=docs/PRD-v2.md [VERSION=2]
```

For detailed setup and usage, see [docs/TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md).

## Workflow

```text
Document Flow:
  UserStory.md (Why) → PRD.md (What) → prd.json → Implementation → progress.txt

Human Workflow (Manual):
  Write PRD.md → make ralph_init → make ralph_run

Human Workflow (Assisted - Optional):
  make ralph_userstory → make ralph_prd → make ralph_init → make ralph_run

Agent Workflow:
  PRD.md → prd.json (generating-prd skill) → Ralph Loop → src/ + tests/
  Uses: .claude/skills/, .claude/rules/

Mandatory for Both:
  CONTRIBUTING.md - Core principles (KISS, DRY, YAGNI)
  Makefile        - Build automation and validation
  .gitmessage     - Commit message format
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, core principles, and contribution guidelines.
