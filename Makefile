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

release-check: ## Check if ready for release
	@echo "Running pre-release checks..."
	@make lint
	@make format-check
	@make test
	@echo "✓ All checks passed!"

release-zip: ## Create release zip file
	@echo "Creating release zip..."
	@cd custom_components && zip -r ../trinnov_altitude.zip trinnov_altitude/ -x "**/__pycache__/*" -x "**/*.pyc"
	@echo "✓ Created trinnov_altitude.zip"

release: release-check release-zip ## Create a new release (runs checks, creates zip)
	@echo ""
	@echo "Release package ready!"
	@echo "Next steps:"
	@echo "  1. git tag v<VERSION>"
	@echo "  2. git push origin master --tags"
	@echo ""
	@echo "The GitHub Actions release workflow will automatically:"
	@echo "  - Create a GitHub release with changelog"
	@echo "  - Build and attach trinnov_altitude.zip"
