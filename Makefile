# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Note: UV_LINK_MODE could be configured in .devcontainer/project/devcontainer.json
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: setup_dev setup_claude_code setup_markdownlint setup_project run_markdownlint ruff test_all test_quick test_coverage test_e2e type_check validate validate_quick quick_validate ralph_validate_json ralph_userstory ralph_prd ralph_init_loop ralph_run ralph_status ralph_clean ralph_archive ralph_abort ralph_watch ralph_log vibe_start vibe_stop vibe_status vibe_demo vibe_cleanup help
.DEFAULT_GOAL := help

# MARK: setup


setup_dev:  ## Install uv and deps, Download and start Ollama 
	echo "Setting up dev environment ..."
	pip install uv -q
	uv sync --all-groups
	echo "npm version: $$(npm --version)"
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_markdownlint

setup_claude_code:  ## Setup claude code CLI, node.js and npm have to be present
	echo "Setting up Claude Code CLI ..."
	npm install -gs @anthropic-ai/claude-code
	echo "Claude Code CLI version: $$(claude --version)"

setup_markdownlint:  ## Setup markdownlint CLI, node.js and npm have to be present
	echo "Setting up markdownlint CLI ..."
	npm install -gs markdownlint-cli
	echo "markdownlint version: $$(markdownlint --version)"

setup_project:  ## Customize template with your project details. Run with help: bash scripts/setup_project.sh help
	bash scripts/setup_project.sh || { echo ""; echo "ERROR: Project setup failed. Please check the error messages above."; exit 1; }


# MARK: run markdownlint


run_markdownlint:  ## Lint markdown files. Usage from root dir: make run_markdownlint INPUT_FILES="docs/**/*.md"
	if [ -z "$(INPUT_FILES)" ]; then
		echo "Error: No input files specified. Use INPUT_FILES=\"docs/**/*.md\""
		exit 1
	fi
	markdownlint $(INPUT_FILES) --fix


# MARK: Sanity


ruff:  ## Lint: Format and check with ruff
	uv run ruff format --exclude tests
	uv run ruff check --fix --exclude tests

test_all:  ## Run all tests (excludes E2E tests by default)
	uv run pytest

test_quick:  ## Quick test - rerun only failed tests (use during fix iterations)
	uv run pytest --lf -x

test_coverage:  ## Run tests with coverage threshold (configured in pyproject.toml)
	echo "Running tests with coverage gate (fail_under=70% in pyproject.toml)..."
	uv run pytest --cov

test_e2e:  ## Run E2E tests only (Ralph parallel loop tests)
	echo "Running E2E tests..."
	bash scripts/ralph/tests/test_parallel_ralph.sh
	uv run pytest -m e2e -v

type_check:  ## Check for static typing errors
	uv run pyright

validate:  ## Complete pre-commit validation sequence
	set -e
	echo "Running complete validation sequence..."
	$(MAKE) -s ruff
	$(MAKE) -s type_check
	$(MAKE) -s test_coverage
	echo "Validation completed successfully"

validate_quick:  ## Quick validation for fix iterations (no coverage check)
	set -e
	echo "Running quick validation (no coverage check)..."
	$(MAKE) -s ruff
	$(MAKE) -s type_check
	$(MAKE) -s test_quick
	echo "Quick validation completed"

quick_validate:  ## Fast development cycle validation
	echo "Running quick validation ..."
	$(MAKE) -s ruff
	-$(MAKE) -s type_check
	echo "Quick validation completed (check output for any failures)"


# MARK: ralph

ralph_validate_json:  ## Internal: Validate prd.json syntax
	bash scripts/ralph/lib/validate_json.sh

ralph_userstory:  ## [Optional] Create UserStory.md interactively. Usage: make ralph_userstory
	echo "Creating UserStory.md through interactive Q&A ..."
	claude /build-userstory

ralph_prd:  ## [Optional] Generate PRD.md from UserStory.md
	echo "Generating PRD.md from UserStory.md ..."
	claude /generate-prd-md-from-userstory

ralph_init_loop:  ## Initialize Ralph loop environment
	echo "Initializing Ralph loop environment ..."
	claude -p '/generate-prd-json-from-md'
	bash scripts/ralph/init.sh
	$(MAKE) -s ralph_validate_json

ralph_run:  ## Run Ralph loop - Usage: make ralph_run [N_WT=<N>] [ITERATIONS=<N>] [DEBUG=1] [RALPH_JUDGE_ENABLED=true] [RALPH_SECURITY_REVIEW=true] [RALPH_MERGE_INTERACTIVE=true]
	echo "Starting Ralph loop (N_WT=$${N_WT:-default}, iterations=$${ITERATIONS:-default}) ..."
	$(MAKE) -s ralph_validate_json
	DEBUG=$${DEBUG:-0} \
	RALPH_JUDGE_ENABLED=$${RALPH_JUDGE_ENABLED:-false} \
	RALPH_JUDGE_MODEL=$${RALPH_JUDGE_MODEL:-sonnet} \
	RALPH_JUDGE_MAX_WT=$${RALPH_JUDGE_MAX_WT:-5} \
	RALPH_SECURITY_REVIEW=$${RALPH_SECURITY_REVIEW:-false} \
	RALPH_MERGE_INTERACTIVE=$${RALPH_MERGE_INTERACTIVE:-false} \
	bash scripts/ralph/parallel_ralph.sh "$${N_WT}" "$${ITERATIONS}"

ralph_status:  ## Show Ralph loop progress
	@bash scripts/ralph/parallel_ralph.sh status

ralph_abort:  ## Abort all running Ralph loops
	bash scripts/ralph/abort.sh

ralph_clean:  ## Clean Ralph state (worktrees + local) - Requires double confirmation
	bash scripts/ralph/clean.sh

ralph_archive:  ## Archive current run state. Usage: make ralph_archive [ARCHIVE_LOGS=1]
	bash scripts/ralph/archive.sh $(if $(filter 1,$(ARCHIVE_LOGS)),-l)

ralph_watch:  ## Live-watch Ralph loop output
	bash scripts/ralph/parallel_ralph.sh watch

ralph_log:  ## Show output of specific worktree - Usage: make ralph_log WT=2
	bash scripts/ralph/parallel_ralph.sh log $${WT:-1}


# MARK: vibe-kanban


vibe_start:  ## Start Vibe Kanban on configured port (default: 5173)
	VIBE_PORT=$${RALPH_VIBE_PORT:-5173}
	if pgrep -f "vibe-kanban" > /dev/null; then
		echo "Vibe Kanban already running"
		exit 1
	fi
	PORT=$$VIBE_PORT npx vibe-kanban > /tmp/vibe-kanban.log 2>&1 &
	echo "Vibe Kanban started on port $$VIBE_PORT"
	echo "View at: http://127.0.0.1:$$VIBE_PORT"

vibe_stop:  ## Stop Vibe Kanban
	if pkill -f "vibe-kanban" 2>/dev/null; then
		echo "Vibe Kanban stopped"
	else
		echo "Vibe Kanban not running"
	fi

vibe_status:  ## Check Vibe Kanban status
	VIBE_PORT=$${RALPH_VIBE_PORT:-5173}
	if pgrep -f "vibe-kanban" > /dev/null; then
		echo "Vibe Kanban is running on port $$VIBE_PORT"
		echo "PID: $$(pgrep -f vibe-kanban)"
		echo "View at: http://127.0.0.1:$$VIBE_PORT"
	else
		echo "Vibe Kanban is not running"
	fi

vibe_demo:  ## Populate Vibe Kanban with example tasks
	bash scripts/ralph/vibe_demo.sh

vibe_cleanup:  ## Remove all tasks from Vibe Kanban
	bash scripts/ralph/vibe_cleanup.sh


# MARK: help


help:  ## Displays this message with available recipes
	# TODO add stackoverflow source
	echo "Usage: make [recipe]"
	echo "Recipes:"
	awk '/^[a-zA-Z0-9_-]+:.*?##/ {
		helpMessage = match($$0, /## (.*)/)
		if (helpMessage) {
			recipe = $$1
			sub(/:/, "", recipe)
			printf "  \033[36m%-20s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH)
		}
	}' $(MAKEFILE_LIST)
