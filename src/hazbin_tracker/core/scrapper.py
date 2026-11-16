import dataclasses
import logging
import time

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

from .constants import (
    DEFAULT_SORT_KEY,
    FETCH_BACKOFF_BASE,
    FETCH_TIMEOUT,
    HAZBIN_CARDS_PRODUCTS_JSON_URL,
    IMPERSONATE_BROWSER,
    MAX_FETCH_RETRIES,
    MAX_RETRY_DELAY,
    PAGE_DELAY,
    PRODUCT_TITLE_PREFIX,
    PRODUCTS_REQUEST_LIMIT,
)

LOGGER = logging.getLogger(__name__)

RATE_LIMITED_STATUS = 429
SERVER_ERROR_STATUS = 500


class ScraperError(Exception):
    """Raised when the cards can't be fetched from the store."""


class RateLimitedError(ScraperError):
    """Raised when the store keeps responding with 429 Too Many Requests."""

    retry_after: int | None = None


@dataclasses.dataclass(frozen=True)
class ScraperConfig:
    """Settings of the cards scraper."""

    products_url: str = HAZBIN_CARDS_PRODUCTS_JSON_URL
    page_limit: int = PRODUCTS_REQUEST_LIMIT
    timeout: float = FETCH_TIMEOUT
    max_retries: int = MAX_FETCH_RETRIES
    backoff_base: float = FETCH_BACKOFF_BASE
    max_retry_delay: float = MAX_RETRY_DELAY
    page_delay: float = PAGE_DELAY
    impersonate: str = IMPERSONATE_BROWSER
    title_prefix: str = PRODUCT_TITLE_PREFIX
    sort_key: str = DEFAULT_SORT_KEY


class CardsScraper:
    """Fetches trading cards from the store products endpoint."""

    def __init__(self, config: ScraperConfig | None = None):
        """Instance constructor.

        Args:
            config (ScraperConfig, optional): Scraper settings. Defaults to None.
        """
        self.config = config or ScraperConfig()

    def get_all_cards(self) -> list[dict]:
        """Get all trading cards sorted by the configured sort key.

        Returns:
            list[dict]: A list of sorted cards dictionaries.

        Raises:
            ScraperError: If the cards can't be fetched.
        """
        cards = [self._clean_title(product) for product in self.fetch_products()]
        return sorted(cards, key=lambda card: card[self.config.sort_key], reverse=True)

    def fetch_products(self) -> list[dict]:
        """Fetch every product page of the cards collection.

        Returns:
            list[dict]: Raw product dictionaries.
        """
        products = []
        page = 1
        while True:
            page_products = self._fetch_page(page)
            products.extend(page_products)
            LOGGER.info(f"Page {page}: {len(page_products)} products")
            if len(page_products) < self.config.page_limit:
                return products
            page += 1
            time.sleep(self.config.page_delay)

    def _fetch_page(self, page: int) -> list[dict]:
        params = {"limit": self.config.page_limit, "page": page}
        try:
            return self._get_with_retry(params).json().get("products", [])
        except ValueError as exc:
            raise ScraperError(f"Invalid products response: {exc}") from exc

    def _get_with_retry(self, params: dict):
        """GET the products endpoint, retrying rate limits and transient failures."""
        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            if attempt:
                self._sleep_before_retry(attempt, last_error)
            try:
                response = self._get(params)
            except RequestException as exc:
                last_error = exc
                continue
            if response.status_code == RATE_LIMITED_STATUS:
                last_error = self._rate_limit_error(response)
                continue
            if response.status_code >= SERVER_ERROR_STATUS:
                last_error = ScraperError(f"Store error {response.status_code}")
                continue
            if not response.ok:
                raise ScraperError(f"Store responded with {response.status_code}")
            return response

        if isinstance(last_error, RateLimitedError):
            raise last_error
        raise ScraperError(f"Failed to fetch products: {last_error}") from last_error

    def _get(self, params: dict):
        return requests.get(
            self.config.products_url,
            params=params,
            impersonate=self.config.impersonate,
            timeout=self.config.timeout,
        )

    def _sleep_before_retry(self, attempt: int, error: Exception | None):
        retry_after = getattr(error, "retry_after", None)
        delay = retry_after or self.config.backoff_base**attempt
        delay = min(delay, self.config.max_retry_delay)
        LOGGER.warning(f"Fetch failed ({error}). Retrying in {delay}s...")
        time.sleep(delay)

    @staticmethod
    def _rate_limit_error(response) -> RateLimitedError:
        error = RateLimitedError("Store is rate limiting requests (429).")
        header = response.headers.get("Retry-After", "")
        error.retry_after = int(header) if header.isdigit() else None
        return error

    def _clean_title(self, product: dict) -> dict:
        """Get a copy of the product without the shared title prefix."""
        title = product.get("title")
        if isinstance(title, str) and title.startswith(self.config.title_prefix):
            title = title.removeprefix(self.config.title_prefix).strip()
        return {**product, "title": title}


def get_all_cards() -> list[dict]:
    """Get all trading cards using the default scraper configuration.

    Returns:
        list[dict]: A list of sorted cards dictionaries.
    """
    return CardsScraper().get_all_cards()
