.PHONY: help install lock test test-cov test-fast lint format format-check typecheck clean check

VENV_PYTHON := .venv/bin/python
RUFF := .venv/bin/ruff
PYTEST := .venv/bin/pytest
TY := .venv/bin/ty
TRINNOV_LIB_PATH ?= ../py-trinnov-altitude
UV_CACHE_DIR ?= .uv-cache

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies with uv
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv sync --locked --no-sources
	@if [ -d "$(TRINNOV_LIB_PATH)" ]; then \
		UV_CACHE_DIR=$(UV_CACHE_DIR) uv pip install -p $(VENV_PYTHON) -e $(TRINNOV_LIB_PATH); \
	fi

lock: ## Update the uv lockfile from published package metadata
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv lock --no-sources

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
