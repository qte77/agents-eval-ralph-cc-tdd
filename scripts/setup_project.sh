#!/bin/bash
# Setup script to customize template with project details

set -e

# Display usage information
show_help() {
	cat <<EOF
Setup script to customize template with project details

Usage:
  bash scripts/setup_project.sh                    # Interactive mode
  make setup_project                               # Via Makefile
  bash scripts/setup_project.sh help              # Show this help

Interactive Prompts (with auto-detection where possible):
  1. GitHub org/repo      - Auto-detected from git remote
  2. Project name         - Derived from repo or prompted (kebab-case)
  3. App name             - Python package name (defaults to project name in snake_case)
  4. Description          - Project description
  5. Author/Organization  - Auto-detected from org or prompted
  6. Python version       - Auto-detected from 'python --version' (default: 3.13)

Environment Variables (optional - skip interactive prompts):
  GITHUB_REPO     - GitHub repository (org/repo format)
  PROJECT         - Project name (kebab-case)
  DESCRIPTION     - Project description
  AUTHOR          - Author/Organization name
  PYTHON_VERSION  - Python version (e.g., 3.13)

  Note: App name is always prompted interactively

Examples:
  # Interactive mode (recommended)
  make setup_project

  # Pre-set some values, prompt for others
  PROJECT=my-project DESCRIPTION="My app" make setup_project
EOF
	exit 0
}

# Check for help flag
if [[ "$1" == "help" ]] || [[ "$1" == "h" ]] || [[ "$1" == "?" ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
	show_help
fi

echo ""
echo "Project Setup"
echo "============="
echo "(Leave inputs empty to use found, default or empty values)"
echo ""

# Check if already customized
if [ ! -d "src/your_project_name" ] && [ -z "$GITHUB_REPO" ]; then
	echo "WARNING: Appears already customized (src/your_project_name/ not found)"
	read -p "Continue anyway? [y/N]: " confirm
	[ "$confirm" != "y" ] && exit 0
fi

# Get GITHUB_REPO (auto-detect from git, user can override)
GIT_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$GIT_URL" ]; then
	DEFAULT_REPO=$(echo "$GIT_URL" | sed -E 's#.*[:/]([^/]+/[^/]+?)(\.git)?$#\1#')
else
	DEFAULT_REPO=""
fi
if [ -z "$GITHUB_REPO" ]; then
	if [ -n "$DEFAULT_REPO" ]; then
		read -p "GitHub org/repo (found '$DEFAULT_REPO'): " GITHUB_REPO
		GITHUB_REPO=${GITHUB_REPO:-$DEFAULT_REPO}
	else
		read -p "GitHub org/repo (e.g., acme/my-app): " GITHUB_REPO
	fi
else
	read -p "GitHub org/repo (found '$GITHUB_REPO'): " INPUT_REPO
	GITHUB_REPO=${INPUT_REPO:-$GITHUB_REPO}
fi
GITHUB_REPO=$(echo "$GITHUB_REPO" | tr ' ' '_')

# Derive PROJECT from GITHUB_REPO if not provided
if [ -z "$PROJECT" ]; then
	PROJECT=${PROJECT:-$(echo "$GITHUB_REPO" | cut -d'/' -f2)}
	if [ -z "$PROJECT" ]; then
		read -p "Project name (kebab-case, e.g., my-app): " PROJECT
	fi
else
	PROJECT="$PROJECT"
fi

# Derive default app name from PROJECT
PROJECT_SNAKE=$(echo "$PROJECT" | tr '-' '_')

# Get APP_NAME (prompt with PROJECT_SNAKE as default)
read -p "App name (Python package name, default '$PROJECT_SNAKE'): " APP_NAME
APP_NAME=${APP_NAME:-$PROJECT_SNAKE}

# Get DESCRIPTION (prompt if empty)
if [ -z "$DESCRIPTION" ]; then
	read -p "Project description: " DESCRIPTION
else
	DESCRIPTION="$DESCRIPTION"
fi

# Get AUTHOR (auto-detect from org, user can override)
DEFAULT_AUTHOR=$(echo "$GITHUB_REPO" | cut -d'/' -f1)
if [ -z "$AUTHOR" ]; then
	if [ -n "$DEFAULT_AUTHOR" ]; then
		read -p "Author/Organization name (found '$DEFAULT_AUTHOR'): " AUTHOR
		AUTHOR=${AUTHOR:-$DEFAULT_AUTHOR}
	else
		read -p "Author/Organization name: " AUTHOR
	fi
else
	read -p "Author/Organization name (found '$AUTHOR'): " INPUT_AUTHOR
	AUTHOR=${INPUT_AUTHOR:-$AUTHOR}
fi
AUTHOR=$(echo "$AUTHOR" | tr ' ' '_')

# Get Python version (auto-detect from python --version, user can override)
DETECTED_PY=$(python --version 2>&1 | sed -E 's/Python ([0-9]+\.[0-9]+).*/\1/' || python3 --version 2>&1 | sed -E 's/Python ([0-9]+\.[0-9]+).*/\1/' || echo "3.13")
if [ -z "$PYTHON_VERSION" ]; then
	read -p "Python version (found '$DETECTED_PY', default '3.13'): " PYTHON_VERSION
	PYTHON_VERSION=${PYTHON_VERSION:-$DETECTED_PY}
else
	read -p "Python version (found '$PYTHON_VERSION', default '3.13'): " INPUT_PY
	PYTHON_VERSION=${INPUT_PY:-$PYTHON_VERSION}
fi

# Derive year and Python version short
YEAR=$(date +%Y)
PYTHON_VERSION_SHORT=$(echo "$PYTHON_VERSION" | tr -d '.')

# Show summary
echo ""
echo "Applying:"
echo "  GitHub repo: $GITHUB_REPO"
echo "  Project: $PROJECT"
echo "  App name: $APP_NAME"
echo "  Description: $DESCRIPTION"
echo "  Author: $AUTHOR"
echo "  Year: $YEAR"
echo "  Python version: $PYTHON_VERSION (py$PYTHON_VERSION_SHORT)"
echo ""

# Perform replacements
sed -i "s|YOUR-ORG/YOUR-PROJECT-NAME|$GITHUB_REPO|g" README.md
sed -i "s|Python Ralph-Loop Template|$PROJECT|g" README.md
sed -i "s|> What a time to be alive|$DESCRIPTION|g" README.md
sed -i "/Out-of-the-box Python project template using Ralph Loop autonomous development/{N;d;}" README.md
sed -i "s|\\[PROJECT NAME\\]|$PROJECT|g" pyproject.toml
sed -i "s|\\[PROJECT DESCRIPTION\\]|$DESCRIPTION|g" pyproject.toml
sed -i "s|\\[PYTHON VERSION\\]|$PYTHON_VERSION|g" pyproject.toml
sed -i "s|\\[PYTHON VERSION SHORT\\]|$PYTHON_VERSION_SHORT|g" pyproject.toml
sed -i "s|your_project_name|$APP_NAME|g" pyproject.toml
sed -i "s|\\[YEAR\\]|$YEAR|g" LICENSE.md
sed -i "s|\\[YOUR NAME OR ORGANIZATION\\]|$AUTHOR|g" LICENSE.md
sed -i "s|your-project-name|$PROJECT|g" scripts/ralph/init.sh
sed -i "s|your-project-name|$PROJECT|g" docs/ralph/templates/progress.txt.template
sed -i "s|your-project-name|$PROJECT|g" docs/ralph/templates/prd.json.template
sed -i "s|\\[PROJECT NAME\\]|$PROJECT|g" mkdocs.yaml
sed -i "s|\\[PROJECT DESCRIPTION\\]|$DESCRIPTION|g" mkdocs.yaml
sed -i "s|\\[GITHUB REPO\\]|$GITHUB_REPO|g" mkdocs.yaml
sed -i "s|devcontainers\/python|devcontainers\/python:$PYTHON_VERSION|g" .devcontainer/project/devcontainer.json

# Rename source directory
if [ -d "src/your_project_name" ]; then
	mv src/your_project_name "src/$APP_NAME"
fi

# Verify replacements
REMAINING=$(grep -r "YOUR-ORG\|\[PROJECT NAME\]\|\[YEAR\]\|\[YOUR NAME\|\[PROJECT DESCRIPTION\]\|\[GITHUB REPO\]\|\[PYTHON VERSION" . --exclude-dir=.git --exclude="TEMPLATE_USAGE.md" --exclude="Makefile" 2>/dev/null | wc -l)
if [ $REMAINING -gt 0 ]; then
	echo ""
	echo "WARNING: Some placeholders may remain. Review with:"
	echo "  grep -r 'YOUR-ORG\|your-project-name' . --exclude-dir=.git"
fi

echo ""
echo "Project setup complete!"
echo ""
echo "IMPORTANT: Devcontainer needs to be rebuilt to apply Python version changes."
echo ""
echo "To rebuild:"
echo "  1. Press Ctrl/Cmd+Shift+P"
echo "  2. Type 'Dev Containers: Rebuild Container'"
echo "  3. Press Enter"
echo ""
