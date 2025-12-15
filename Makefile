.PHONY: help install test test-cov lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install test dependencies with uv
	uv pip install -r requirements_test.txt

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	uv run pytest --no-cov

lint: ## Run ruff linter
	uv run ruff check custom_components tests

format: ## Format code with ruff
	uv run ruff format custom_components tests

format-check: ## Check code formatting without modifying
	uv run ruff format --check custom_components tests

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
	@make test
	@echo "✓ All checks passed!"
