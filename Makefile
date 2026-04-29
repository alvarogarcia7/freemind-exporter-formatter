include makefiles/docker-compose.mk
include makefiles/uv.mk

init: check-uv ## Initialize the project by syncing dependencies
	${MAKE} install-dev
	${MAKE} install-pre-commit
	@echo "Project initialized and dependencies synced!"
.PHONY: init

install-pre-commit: check-uv ## Install and configure pre-commit hooks
	@echo "Setting up pre-commit hooks..."
	uv run pre-commit install --install-hooks --hook-type pre-commit
	uv run pre-commit install --install-hooks --hook-type pre-push
	@echo "Pre-commit successfully installed and configured!"
.PHONY: install-pre-commit

test: check-uv typecheck test-python ## Execute all tests
.PHONY: test

pre-commit: ## Git hook for pre-commit
	uv run pre-commit run --all-files
.PHONY: pre-commit

ruff-check:
	uv run ruff check .
.PHONY: ruff-check

ruff-check-fix:
	uv run ruff check --fix .
.PHONY: ruff-check-fix

ruff-format:
	uv run ruff format .
.PHONY: ruff-format

ruff-format-check:
	uv run ruff format --check .
.PHONY: ruff-format-check

completions: check-uv ## Generate bash and zsh completion scripts
	uv run python generate_completions.py
.PHONY: completions
