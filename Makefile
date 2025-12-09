SHELL := /bin/bash

APP_NAME = HazbinTracker
DIST_DIR = dist
APP_PATH = $(DIST_DIR)/$(APP_NAME).app
APPLICATIONS_DIR = /Applications

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

clean:
	$(call banner, Cleaning project...)
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf src/**/__pycache__
	@rm -rf tests/**/__pycache__
	@rm -rf build
	@rm -rf dist
	@rm -rf .test_output
	@printf "$(GREEN)Clean up complete.$(RESET)\n"

lint:
	$(call banner, Running Ruff linter...)
	@poetry run ruff check src tests || true

format:
	$(call banner, Running Ruff formatter...)
	@poetry run ruff format src tests

.PHONY: pytest
pytest:
	$(call banner, Running pytest...)
	@poetry run pytest tests

pytest-pdb:
	$(call banner, Cleaning pytest output dir...)
	@rm -rf $(TEST_OUTPUT_DIR)
	$(call banner, Running pytest with pdb...)
	@poetry run pytest --pdb tests

check: lint pytest

qrc:
	$(call banner, Generating QRC resources...)
	@pyside6-rcc resources/resources.qrc -o resources/resources_rc.py
	@printf "$(GREEN)QRC generation complete.$(RESET)\n"

app: update-version
	$(call banner, Building $(APP_NAME)...)
	@pyinstaller HazbinTracker.spec

update-version:
	@VERSION=$$(cat VERSION); \
	printf "$(CYAN)==>$(RESET) Updating pyproject.toml version to %s\n" "$$VERSION"; \
	poetry version $$VERSION

iconset:
	$(call banner, Generating iconset...)
	@mkdir -p resources/icons/HazbinTracker.iconset
	@sips -z 16 16     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_16x16.png
	@sips -z 32 32     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_16x16@2x.png
	@sips -z 32 32     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_32x32.png
	@sips -z 64 64     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_32x32@2x.png
	@sips -z 128 128   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_128x128.png
	@sips -z 256 256   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_128x128@2x.png
	@sips -z 256 256   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_256x256.png
	@sips -z 512 512   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_256x256@2x.png
	@sips -z 512 512   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_512x512.png
	@sips -z 1024 1024 resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_512x512@2x.png
	@iconutil -c icns resources/icons/HazbinTracker.iconset -o resources/icons/HazbinTracker.icns
	@printf "$(YELLOW)Removing temp iconset files...$(RESET)\n"
	@rm -rf resources/icons/HazbinTracker.iconset
	@printf "$(GREEN)Iconset generation complete.$(RESET)\n"

install:
	@VERSION=$$(cat VERSION); \
	printf "$(CYAN)==>$(RESET) Installing $(APP_NAME) v%s into $(APPLICATIONS_DIR)...\n" "$$VERSION"; \
	cp -R "$(APP_PATH)" "$(APPLICATIONS_DIR)/"; \
	printf "$(GREEN)Installation complete.$(RESET)\n"