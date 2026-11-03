import pytest

from hazbin_tracker.core.scrapper import (
    CardsScraper,
    RateLimitedError,
    ScraperConfig,
    ScraperError,
)
from curl_cffi.requests.exceptions import RequestException


class FakeResponse:
    """Minimal stand-in for a curl_cffi response."""

    def __init__(self, products=None, status_code=200, headers=None):
        """Store the fake products, status and headers."""
        self._products = products
        self.status_code = status_code
        self.headers = headers or {}

    @property
    def ok(self):
        """Mirror response.ok."""
        return self.status_code < 400

    def json(self):
        """Return the fake body."""
        return {"products": self._products or []}


def _products(start, count):
    return [
        {
            "id": start + i,
            "title": f"Hazbin Hotel Trading Cards Card {start + i}",
            "published_at": f"2026-10-{start + i:02d}T00:00:00+00:00",
        }
        for i in range(count)
    ]


@pytest.fixture
def sleeps(mocker):
    """Record sleeps instead of waiting."""
    return mocker.patch("hazbin_tracker.core.scrapper.time.sleep")


def _scraper(mocker, responses, **config):
    scraper = CardsScraper(ScraperConfig(page_limit=2, **config))
    get = mocker.patch.object(scraper, "_get", side_effect=responses)
    return scraper, get


def test_get_all_cards_paginates_cleans_and_sorts(mocker, sleeps):
    """Pages are fetched until a short page, titles cleaned, newest first."""
    scraper, get = _scraper(
        mocker, [FakeResponse(_products(1, 2)), FakeResponse(_products(3, 1))]
    )
    cards = scraper.get_all_cards()

    assert get.call_count == 2
    assert [card["id"] for card in cards] == [3, 2, 1]
    assert cards[0]["title"] == "Card 3"
    sleeps.assert_called_once_with(scraper.config.page_delay)


def test_clean_title_does_not_mutate_input(mocker):
    """The raw product keeps its original title."""
    product = {"title": "Hazbin Hotel Trading Cards Vox"}
    cleaned = CardsScraper()._clean_title(product)
    assert cleaned["title"] == "Vox"
    assert product["title"] == "Hazbin Hotel Trading Cards Vox"


def test_retries_rate_limit_then_succeeds(mocker, sleeps):
    """A 429 honors Retry-After and the next attempt succeeds."""
    scraper, get = _scraper(
        mocker,
        [
            FakeResponse(status_code=429, headers={"Retry-After": "7"}),
            FakeResponse(_products(1, 1)),
        ],
    )
    assert len(scraper.get_all_cards()) == 1
    assert get.call_count == 2
    sleeps.assert_called_once_with(7)


def test_persistent_rate_limit_raises(mocker, sleeps):
    """Exhausted retries raise RateLimitedError instead of returning None."""
    scraper, get = _scraper(mocker, [FakeResponse(status_code=429)] * 3, max_retries=3)
    with pytest.raises(RateLimitedError):
        scraper.get_all_cards()
    assert get.call_count == 3
    assert sleeps.call_count == 2  # no sleep after the final attempt


def test_client_error_is_not_retried(mocker, sleeps):
    """A 404 fails immediately."""
    scraper, get = _scraper(mocker, [FakeResponse(status_code=404)])
    with pytest.raises(ScraperError):
        scraper.get_all_cards()
    assert get.call_count == 1
    sleeps.assert_not_called()


def test_network_error_is_retried_then_raised(mocker, sleeps):
    """Transport errors are retried and finally wrapped in ScraperError."""
    scraper, get = _scraper(mocker, [RequestException("boom")] * 2, max_retries=2)
    with pytest.raises(ScraperError):
        scraper.get_all_cards()
    assert get.call_count == 2
