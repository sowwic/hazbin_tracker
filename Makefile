# Common targets come from sowwic/makefiles, fetched into .make/ (commit it). `make update-make` fetches them again.
APP_NAME = HazbinTracker
PACKAGE_NAME = hazbin_tracker
RELEASE_BRANCH = master
BUILD_PREREQS = qrc update-version

MAKEFILES_REF ?= v1
MAKEFILES_URL ?= https://raw.githubusercontent.com/sowwic/makefiles/$(MAKEFILES_REF)
MAKEFILES_MODULES = general/python general/qt general/bundle general/repo

.make/%.mk:
	@mkdir -p $(dir $@)
	@curl -fsSL $(MAKEFILES_URL)/$*.mk -o $@
include $(MAKEFILES_MODULES:%=.make/%.mk)

APP_PATH = $(DIST_DIR)/$(APP_NAME).app
APPLICATIONS_DIR = /Applications

.PHONY: app
app: bundle ## Build the macOS app: dist/HazbinTracker.app

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
	$(call banner, Installing $(APP_NAME) v$(VERSION) into $(APPLICATIONS_DIR)...)
	@cp -R "$(APP_PATH)" "$(APPLICATIONS_DIR)/"
	@printf "$(GREEN)Installation complete.$(RESET)\n"

.PHONY: pushover-check
pushover-check:  ## Validate the Pushover keys of the config without sending a notification
	@uv run python scripts/check_pushover.py
