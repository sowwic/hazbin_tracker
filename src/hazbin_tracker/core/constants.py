import os
import pathlib
import shutil
import sys

import platformdirs

# Package
PACKAGE_NAME = "hazbin-tracker"
AUTHOR_NAME = "Dmitrii Shevchenko"
RELEASE_YEAR = 2025

# Application
APPLICATION_TITLE = "HazbinTracker"
ORGANIZATION_NAME = "Sowwic"
DEBUG = int(os.getenv("HAZBIN_DEBUG", 0))

# Scrapping
HAZBIN_WEBSITE_URL = "https://hazbinhotel.com/collections/trading-cards"
HAZBIN_CARDS_PRODUCTS_JSON_URL = (
    "https://hazbinhotel.com/collections/trading-cards/products.json"
)
PRODUCT_TITLE_PREFIX = "Hazbin Hotel Trading Cards"
PRODUCTS_REQUEST_LIMIT = 250
DEFAULT_SORT_KEY = "published_at"
FETCH_TIMEOUT = 30
MAX_FETCH_RETRIES = 3
FETCH_BACKOFF_BASE = 2
MAX_RETRY_DELAY = 60
PAGE_DELAY = 2
IMPERSONATE_BROWSER = "chrome"
MAX_CONSECUTIVE_FAILED_CHECKS = 5


def _get_app_data_dir() -> pathlib.Path:
    """Get the directory for user files of the application.

    Returns:
        pathlib.Path: `$XDG_CONFIG_HOME/<app>` (`~/.config/<app>` by default) on
            macOS and Linux, the platform data directory on Windows. Created if
            missing. On macOS the files of the former location
            (`~/Library/Application Support/<app>`) are moved there once.
    """
    if sys.platform == "win32":
        return pathlib.Path(
            platformdirs.user_data_dir(
                appname=APPLICATION_TITLE,
                appauthor=ORGANIZATION_NAME,
                roaming=False,
                ensure_exists=True,
            )
        )
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = pathlib.Path(config_home) if config_home else pathlib.Path.home() / ".config"
    app_dir = base / APPLICATION_TITLE
    if not app_dir.exists():
        legacy_dir = pathlib.Path(
            platformdirs.user_data_dir(
                appname=APPLICATION_TITLE,
                appauthor=ORGANIZATION_NAME,
                roaming=False,
            )
        )
        app_dir.parent.mkdir(parents=True, exist_ok=True)
        if legacy_dir.is_dir():
            shutil.move(legacy_dir, app_dir)
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


APP_DATA_DIR = _get_app_data_dir()

SETTINGS_FILE_PATH = APP_DATA_DIR / "settings.ini"
CONFIG_FILE_PATH = APP_DATA_DIR / "config.json"
CHECK_HISTORY_FILE_PATH = APP_DATA_DIR / "check_history.json"
TRACKER_CHECK_FREQUENCY_MINIMUM = 1
CHECK_HISTORY_SIZE_MINIMUM = 10
