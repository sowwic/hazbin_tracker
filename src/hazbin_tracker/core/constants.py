import pathlib
import platformdirs


# Package
PACKAGE_NAME = "hazbin-tracker"

# Application
APPLICATION_TITLE = "Hazbin Tracker"
ORGANIZATION_NAME = "Sowwic"

# Scrapping
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

CONFIG_FILE_PATH = APP_DATA_DIR / "config.json"
