.PHONY: help install test test-cov test-fast lint format format-check typecheck clean check

VENV_PYTHON := .venv/bin/python
RUFF := .venv/bin/ruff
PYTEST := .venv/bin/pytest
TY := .venv/bin/ty
TRINNOV_LIB_PATH ?= ../py-trinnov-altitude

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install test dependencies with uv
	UV_CACHE_DIR=.uv-cache uv venv --clear .venv
	UV_CACHE_DIR=.uv-cache uv pip install -p $(VENV_PYTHON) -r requirements_test.txt
	@if [ -d "$(TRINNOV_LIB_PATH)" ]; then \
		UV_CACHE_DIR=.uv-cache uv pip install -p $(VENV_PYTHON) -e $(TRINNOV_LIB_PATH); \
	else \
		UV_CACHE_DIR=.uv-cache uv pip install -p $(VENV_PYTHON) "trinnov-altitude @ git+https://github.com/binarylogic/py-trinnov-altitude.git"; \
	fi
	UV_CACHE_DIR=.uv-cache uv pip install -p $(VENV_PYTHON) ty

test: ## Run tests
	$(PYTEST)

test-cov: ## Run tests with coverage report
	$(PYTEST) --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	$(PYTEST) --no-cov

lint: ## Run ruff linter
	$(RUFF) check custom_components tests

format: ## Format code with ruff
	$(RUFF) format custom_components tests

format-check: ## Check code formatting without modifying
	$(RUFF) format --check custom_components tests

typecheck: ## Run ty type checks
	$(TY) check custom_components tests

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf .ruff_cache
	rm -rf trinnov_altitude.zip

check: ## Run all checks (lint, format, test)
	@echo "Running checks..."
	@make lint
	@make format-check
	@make typecheck
	@make test
	@echo "✓ All checks passed!"
