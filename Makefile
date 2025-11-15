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
	ruff check custom_components tests

format: ## Format code with ruff
	ruff format custom_components tests

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
	@make test
	@echo "✓ All checks passed!"

release-zip: ## Create release zip file
	@echo "Creating release zip..."
	@cd custom_components && zip -r ../trinnov_altitude.zip trinnov_altitude/
	@echo "✓ Created trinnov_altitude.zip"

release: release-check release-zip ## Create a new release (runs checks, creates zip)
	@echo ""
	@echo "Release package ready!"
	@echo "Next steps:"
	@echo "  1. Update version in manifest.json"
	@echo "  2. git add custom_components/trinnov_altitude/manifest.json"
	@echo "  3. git commit -m 'Release vX.Y.Z'"
	@echo "  4. git tag vX.Y.Z"
	@echo "  5. git push origin master --tags"
