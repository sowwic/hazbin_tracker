import os
import pathlib
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
HAZBIN_CARDS_PRODUCTS_JSON_URL = ("https://hazbinhotel.com/"
                                  "collections/trading-cards/products.json"
                                  )
PRODUCTS_REQUEST_LIMIT = 250
DEFAULT_SORT_KEY = "published_at"

APP_DATA_DIR = pathlib.Path(platformdirs.user_data_dir(
    appname=APPLICATION_TITLE,
    appauthor=ORGANIZATION_NAME,
    roaming=False,
    ensure_exists=True
))

SETTINGS_FILE_PATH = APP_DATA_DIR / "settings.ini"
