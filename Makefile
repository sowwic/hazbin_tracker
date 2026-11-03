SHELL := /bin/bash

APP_NAME = HazbinTracker
DIST_DIR = dist
APP_PATH = $(DIST_DIR)/$(APP_NAME).app
APPLICATIONS_DIR = /Applications
RELEASE_BRANCH ?= master
DEVELOP_BRANCH ?= develop
GH_WORKFLOWS_REF ?= v1

# Colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
MAGENTA := \033[35m
CYAN := \033[36m
RESET := \033[0m

# Banner helper
define banner
	@printf "$(CYAN)==>$(RESET) $(1)\n"
endef

.PHONY: help 
help: ## Show this help message
	@echo "Available make targets:"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS=":.*?##"}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""

.PHONY: clean
clean: ## Clean up build artifacts and caches
	$(call banner, Cleaning project...)
	@rm -rf build
	@rm -rf dist
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf .test_output
	@rm -rf .site
	@rm -rf .coverage
	@rm -rf __pycache__
	@rm -rf src/**/__pycache__
	@rm -rf tests/**/__pycache__
	@printf "$(GREEN)Clean up complete.$(RESET)\n"

.PHONY: lint
lint:  ## Run the Ruff linter on source and test files
	$(call banner, Running Ruff linter...)
	@uv run ruff check src tests || true

.PHONY: format
format:  ## Run the Ruff formatter on source and test files
	$(call banner, Running Ruff formatter...)
	@uv run ruff format src tests

.PHONY: pytest
pytest:  ## Run pytest on the tests directory
	$(call banner, Running pytest...)
	@uv run pytest tests

.PHONY: pytest-cov
pytest-pdb:  ## Run pytest with pdb on failure
	$(call banner, Cleaning pytest output dir...)
	@rm -rf $(TEST_OUTPUT_DIR)
	$(call banner, Running pytest with pdb...)
	@uv run pytest --pdb tests

.PHONY: mkdocs
mkdocs:  ## Run MkDocs development server
	$(call banner, Building MkDocs documentation...)
	@uv run mkdocs serve

.PHONY: check
check: lint pytest ## Run all checks (linting and testing)

.PHONY: qrc
qrc:  ## Generate QRC resources
	$(call banner, Generating QRC resources...)
	@pyside6-rcc src/hazbin_tracker/resources/resources.qrc -o src/hazbin_tracker/resources/resources_rc.py
	@printf "$(GREEN)QRC generation complete.$(RESET)\n"

.PHONY: app
app:  ## Build the application using PyInstaller
	$(call banner, Building $(APP_NAME)...)
	@pyinstaller HazbinTracker.spec

.PHONY: bump-version
bump-version:  ## Set version in VERSION, pyproject.toml and uv.lock: make bump-version VERSION=X.Y.Z
	$(if $(VERSION),,$(error VERSION is required, e.g. make bump-version VERSION=1.2.3))
	@echo "$(VERSION)" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$$' || { printf "$(RED)Invalid version '$(VERSION)', expected X.Y.Z$(RESET)\n"; exit 1; }
	$(call banner, Bumping version to $(VERSION)...)
	@echo "$(VERSION)" > VERSION
	@uv version $(VERSION)

.PHONY: release
release:  ## Tag, push and back-merge a release: make release VERSION=x.y.z [RELEASE_TITLE=...]
	$(if $(VERSION),,$(error VERSION is required, e.g. make release VERSION=1.2.3))
	$(call banner, Releasing $(APP_NAME) v$(VERSION)...)
	@curl -fsSL https://raw.githubusercontent.com/sowwic/gh-workflows/$(GH_WORKFLOWS_REF)/scripts/release.py | \
		python3 - $(VERSION) --release-branch $(RELEASE_BRANCH) --develop-branch $(DEVELOP_BRANCH) $(if $(RELEASE_TITLE),--title "$(RELEASE_TITLE)")

.PHONY: iconset
iconset:  ## Generate the .icns iconset from the source PNG icon
	$(call banner, Generating iconset...)
	@mkdir -p src/hazbin_tracker/resources/icons/HazbinTracker.iconset
	@sips -z 16 16     src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_16x16.png
	@sips -z 32 32     src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_16x16@2x.png
	@sips -z 32 32     src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_32x32.png
	@sips -z 64 64     src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_32x32@2x.png
	@sips -z 128 128   src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_128x128.png
	@sips -z 256 256   src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_128x128@2x.png
	@sips -z 256 256   src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_256x256.png
	@sips -z 512 512   src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_256x256@2x.png
	@sips -z 512 512   src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_512x512.png
	@sips -z 1024 1024 src/hazbin_tracker/resources/icons/hazbin.png --out src/hazbin_tracker/resources/icons/HazbinTracker.iconset/icon_512x512@2x.png
	@iconutil -c icns src/hazbin_tracker/resources/icons/HazbinTracker.iconset -o src/hazbin_tracker/resources/icons/HazbinTracker.icns
	@printf "$(YELLOW)Removing temp iconset files...$(RESET)\n"
	@rm -rf src/hazbin_tracker/resources/icons/HazbinTracker.iconset
	@printf "$(GREEN)Iconset generation complete.$(RESET)\n"

.PHONY: install
install:  ## Install the built application into the Applications directory
	@VERSION=$$(cat VERSION); \
	printf "$(CYAN)==>$(RESET) Installing $(APP_NAME) v%s into $(APPLICATIONS_DIR)...\n" "$$VERSION"; \
	cp -R "$(APP_PATH)" "$(APPLICATIONS_DIR)/"; \
	printf "$(GREEN)Installation complete.$(RESET)\n"
