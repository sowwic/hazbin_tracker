import importlib

# Package
PACKAGE_NAME = "hazbin-tracker"
HAZBIN_TRACKER_VERSION = importlib.metadata.version("hazbin-tracker")

# Application
APPLICATION_TITLE = "Hazbin Tracker"
ORGANIZATION_NAME = "Sowwic"

# Scrapping
HAZBIN_CARDS_PRODUCTS_JSON_URL = ("https://hazbinhotel.com/"
                                  "collections/trading-cards/products.json"
                                  )
PRODUCTS_REQUEST_LIMIT = 250
DEFAULT_SORT_KEY = "published_at"
