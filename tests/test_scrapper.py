import requests
import logging
import json
import pathlib

from hazbin_tracker.api import HAZBIN_CARDS_PRODUCTS_JSON_URL
from hazbin_tracker.api import DEFAULT_SORT_KEY
from hazbin_tracker.core.scrapper import get_all_cards

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_hazbin_cards_page_accessible():
    response = requests.get(HAZBIN_CARDS_PRODUCTS_JSON_URL)
    assert response.status_code == 200


def test_get_cards_products(output_dir: pathlib.Path):
    data = get_all_cards()
    json.dump(data, open(output_dir / "cards.json", "w"), indent=4)
    assert len(data) > 0

    first_card: dict = data[0]
    assert first_card.get("id") is not None
    assert first_card.get("title") is not None
    assert first_card.get(DEFAULT_SORT_KEY) is not None
    assert first_card.get("images") is not None
