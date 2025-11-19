import requests
import logging

from .constants import (
    HAZBIN_CARDS_PRODUCTS_JSON_URL,
    PRODUCTS_REQUEST_LIMIT,
    DEFAULT_SORT_KEY,
)

LOGGER = logging.getLogger(__name__)


def get_all_products() -> list[dict]:
    """Get all products from the Hazbin Hotel trading cards collection.

    Returns:
        list: A list of all product dictionaries.
    """
    all_products = []
    page = 1
    while True:
        resp = requests.get(
            HAZBIN_CARDS_PRODUCTS_JSON_URL,
            params={"limit": PRODUCTS_REQUEST_LIMIT, "page": page},
        )
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
    return sorted(products, key=lambda x: x[DEFAULT_SORT_KEY], reverse=True)
