# This Makefile automates the build, test, and clean processes for the project.
# It provides a convenient way to run common tasks using the 'make' command.
# It is designed to work with the 'uv' tool for managing Python environments and dependencies.
# Note: UV_LINK_MODE could be configured in .devcontainer/project/devcontainer.json
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: setup_dev setup_claude_code setup_markdownlint setup_project run_markdownlint ruff test_all test_quick test_coverage type_check validate validate_quick quick_validate ralph_validate_json ralph_userstory ralph_prd ralph_full_init ralph_init_loop ralph_run ralph_status ralph_clean ralph_reorganize ralph_abort help
.DEFAULT_GOAL := help

# Ralph configuration - Quality thresholds
MIN_TEST_COVERAGE ?= 70
RALPH_MAX_ITERATIONS ?= 25
RALPH_MAX_FIX_ATTEMPTS ?= 3


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

test_all:  ## Run all tests
	uv run pytest

test_quick:  ## Quick test - rerun only failed tests (use during fix iterations)
	uv run pytest --lf -x

test_coverage:  ## Run tests with coverage threshold ($(MIN_TEST_COVERAGE)%)
	echo "Running tests with $(MIN_TEST_COVERAGE)% coverage gate..."
	uv run pytest --cov --cov-fail-under=$(MIN_TEST_COVERAGE)

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
	@if [ ! -f docs/ralph/prd.json ]; then
		echo "ERROR: prd.json not found"
		exit 1
	fi
	@if ! jq empty docs/ralph/prd.json 2>/dev/null; then
		echo "ERROR: Invalid JSON in docs/ralph/prd.json"
		exit 1
	fi
	@echo "✓ prd.json validated"

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

ralph_run:  ## Run Ralph autonomous development loop (use ITERATIONS=N to set max iterations)
	echo "Starting Ralph loop ..."
	$(MAKE) -s ralph_validate_json
	ITERATIONS=$${ITERATIONS:-25}
	bash scripts/ralph/ralph.sh $$ITERATIONS

ralph_status:  ## Show Ralph loop progress and status
	echo "Ralph Loop Status"
	echo "================="
	if [ -f docs/ralph/prd.json ]; then
		total=$$(jq '.stories | length' docs/ralph/prd.json)
		passing=$$(jq '[.stories[] | select(.passes == true)] | length' docs/ralph/prd.json)
		echo "Stories: $$passing/$$total completed"
		echo ""
		echo "Incomplete stories:"
		jq -r '.stories[] | select(.passes == false) | "  - [\(.id)] \(.title)"' docs/ralph/prd.json
	else
		echo "prd.json not found. Run 'make ralph_init_loop' first."
	fi

ralph_clean:  ## Reset Ralph state (WARNING: removes prd.json and progress.txt)
	echo "WARNING: This will reset Ralph loop state!"
	echo "Press Ctrl+C to cancel, Enter to continue..."
	read
	rm -f docs/ralph/prd.json docs/ralph/progress.txt
	echo "Ralph state cleaned. Run 'make ralph_init_loop' to reinitialize."

ralph_reorganize:  ## Archive current PRD and ralph state. Usage: make ralph_reorganize [ARCHIVE_LOGS=1]
	bash scripts/ralph/reorganize_prd.sh $(if $(filter 1,$(ARCHIVE_LOGS)),-l)

ralph_abort:  ## Abort all running Ralph loops
	bash scripts/ralph/abort.sh


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
