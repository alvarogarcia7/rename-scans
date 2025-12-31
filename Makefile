include makefiles/docker-compose.mk
include makefiles/uv.mk

install-githooks: check-uv
	uv run pre-commit install
.PHONY: install-githooks

test: check-uv typecheck test-python ## Execute all tests
.PHONY: test

pre-commit: test ## Git hook for pre-commit
.PHONY: pre-commit
