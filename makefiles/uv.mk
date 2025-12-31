# This Makefile provides targets for uv package and environment management
# uv is a fast Python package installer and resolver (https://astral.sh/uv)

# Ensure uv is installed
check-uv:
	@command -v uv >/dev/null 2>&1 || (echo "uv is not installed. Please install it from https://astral.sh/uv" && exit 1)
.PHONY: check-uv

# Sync dependencies and create virtual environment
sync: check-uv
	uv sync
.PHONY: sync

# Install only production dependencies (no dev deps)
install: check-uv
	uv sync --no-dev
.PHONY: install

# Upgrade all dependencies
upgrade: check-uv
	uv sync --upgrade
.PHONY: upgrade

# Typecheck with mypy using uv run
typecheck: check-uv
	uv run mypy . --exclude .venv --strict --warn-unreachable --warn-return-any --disallow-untyped-calls
.PHONY: typecheck

# Run Python tests with pytest using uv run
test-python: check-uv
	uv run pytest .
.PHONY: test-python
