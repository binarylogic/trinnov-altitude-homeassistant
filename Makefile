.PHONY: help install test test-cov lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install test dependencies
	pip install -r requirements_test.txt

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	pytest --no-cov

lint: ## Run ruff linter
	ruff check custom_components tests

format: ## Format code with ruff
	ruff format custom_components tests

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf **/__pycache__
	rm -rf **/*.pyc
