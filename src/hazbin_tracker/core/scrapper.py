import requests
import logging

from .constants import (
    HAZBIN_CARDS_PRODUCTS_JSON_URL,
    PRODUCTS_REQUEST_LIMIT,
    DEFAULT_SORT_KEY,
)

LOGGER = logging.getLogger(__name__)

PRODUCT_TITLE_PREFIX = "Hazbin Hotel Trading Cards"


def get_all_products() -> list[dict]:
    """Get all products from the Hazbin Hotel trading cards collection.

    Returns:
        list: A list of all product dictionaries.
    """
    all_products = []
    page = 1
    while True:
        try:
            resp = requests.get(
                HAZBIN_CARDS_PRODUCTS_JSON_URL,
                params={"limit": PRODUCTS_REQUEST_LIMIT, "page": page},
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            LOGGER.error("No network connection.")
            break
        resp.raise_for_status()
        data = resp.json().get("products")
        if not data:
            break
        all_products.extend(data)
        page += 1
    return all_products


def get_all_cards() -> list[dict]:
    """Get all trading card sorted by the default sort key.

    Returns:
        list[dict]: A list of sorted cards dictionaries.
    """
    products = get_all_products()
    for product in products:
        title = product.get("title")
        if isinstance(title, str) and title.startswith(PRODUCT_TITLE_PREFIX):
            product["title"] = title.split(PRODUCT_TITLE_PREFIX, maxsplit=1)[-1].strip()

    return sorted(products, key=lambda x: x[DEFAULT_SORT_KEY], reverse=True)
