SHELL := /bin/bash

APP_NAME = HazbinTracker
DIST_DIR = dist
APP_PATH = $(DIST_DIR)/$(APP_NAME).app
APPLICATIONS_DIR = /Applications


clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf src/**/__pycache__
	rm -rf tests/**/__pycache__
	rm -rf build
	rm -rf dist
	rm -rf .test_output

lint:
	poetry run flake8 src tests

pytest:
	poetry run pytest tests

check: lint pytest

qrc:
	pyside6-rcc resources/resources.qrc -o resources/resources_rc.py

app: qrc update-version
	pyinstaller HazbinTracker.spec

update-version:
	@VERSION=$$(cat VERSION); \
	echo "Updating pyproject.toml version to $$VERSION"; \
	poetry version $$VERSION

iconset:
	mkdir -p resources/icons/HazbinTracker.iconset
	sips -z 16 16     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_16x16.png
	sips -z 32 32     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_16x16@2x.png
	sips -z 32 32     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_32x32.png
	sips -z 64 64     resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_32x32@2x.png
	sips -z 128 128   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_128x128.png
	sips -z 256 256   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_128x128@2x.png
	sips -z 256 256   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_256x256.png
	sips -z 512 512   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_256x256@2x.png
	sips -z 512 512   resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_512x512.png
	sips -z 1024 1024 resources/icons/hazbin.png --out resources/icons/HazbinTracker.iconset/icon_512x512@2x.png
	iconutil -c icns resources/icons/HazbinTracker.iconset -o resources/icons/HazbinTracker.icns
	rm -rf resources/icons/HazbinTracker.iconset

.PHONY: install
install:
	cp -R "$(APP_PATH)" "$(APPLICATIONS_DIR)/"