import os
import datetime
import pathlib
import json
import requests
import logging

from PySide6 import QtCore

from hazbin_tracker.core import config
from hazbin_tracker.core.scrapper import get_all_cards
from hazbin_tracker.core.constants import APP_DATA_DIR


LOGGER = logging.getLogger(__name__)


class CardsTracker(QtCore.QObject):

    TRACK_FILE_NAME = "tracked_cards.json"
    CHECK_INTERVAL_HOURS = 1
    cards_updated = QtCore.Signal()
    check_time_updated = QtCore.Signal()
    new_cards_found = QtCore.Signal(list)

    def __repr__(self):
        return (f"<CardsTracker last_check_time={self._last_check_time}"
                " cards_count="
                f"{len(self._cards_data) if self._cards_data else 0}>")

    def __init__(self):
        super().__init__()
        self._last_check_time = None
        self._cards_data = None
        self.user_key, self.api_key = config.load_keys()
        if not self.user_key or not self.api_key:
            raise ValueError(
                (
                    "Pushover USER_KEY and APP_KEY"
                    f" must be set in config: {config.CONFIG_FILE_PATH}")
            )

        self.populate_cards_data()
        self.new_cards_found.connect(self.on_new_cards_found)
        self.run_check()
        self.create_periodic_timer()

    def create_periodic_timer(self):
        self._check_timer = QtCore.QTimer(self)
        self._check_timer.setInterval(
            self.CHECK_INTERVAL_HOURS * 3600 * 1000)  # 1 hour in ms
        self._check_timer.timeout.connect(self.run_check)
        self._check_timer.start()

    def run_check(self) -> list[dict]:
        LOGGER.info("Running cards check...")
        source_cards = get_all_cards()

        new_cards = []
        for card in source_cards:
            cards_published_at = datetime.datetime.fromisoformat(
                card["published_at"]
            )
            if cards_published_at > self._last_check_time:
                new_cards.append(card)

        LOGGER.info(f"Found {len(new_cards)} new cards.")
        self.cards_data = source_cards
        self.record_time()
        self.create_cache()
        if new_cards:
            self.new_cards_found.emit(new_cards)
        return new_cards

    def populate_cards_data(self):
        try:
            self.fetch_cards_data_from_cache()
        except (FileNotFoundError, json.JSONDecodeError):
            self.fetch_cards_data_from_source()
            self.create_cache()

    def fetch_cards_data_from_cache(self):
        with self.track_file_path.open() as cache_file:
            cache_data = json.load(cache_file)
        self._cards_data = cache_data.get("cards", [])
        self._last_check_time = datetime.datetime.fromisoformat(
            cache_data.get("last_check_time")
        )
        LOGGER.info(
            f"Loaded {len(self._cards_data)} cards from {self.track_file_path}")

    def fetch_cards_data_from_source(self):
        self._cards_data = get_all_cards()
        self.record_time()

    def create_cache(self):
        cache_content = {
            "last_check_time": self.last_check_time.isoformat(),
            "cards": self.cards_data
        }
        with self.track_file_path.open("w") as cache_file:
            json.dump(cache_content, cache_file, indent=4)

    def record_time(self):
        self.last_check_time = datetime.datetime.now(datetime.timezone.utc)

    def on_new_cards_found(self, new_cards: list):
        message = f"Found {len(new_cards)} new Hazbin cards:"
        for card in new_cards:
            message += f"\n- {card.get('title')}"
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": self.api_key,
                "user": self.user_key,
                "title": "HazbinTracker - New Cards available!",
                "message": message,
            }
        )

    @property
    def cards_data(self):
        return self._cards_data

    @cards_data.setter
    def cards_data(self, value):
        self._cards_data = value
        self.cards_updated.emit()

    @property
    def last_check_time(self):
        return self._last_check_time

    @last_check_time.setter
    def last_check_time(self, value):
        self._last_check_time = value
        self.check_time_updated.emit()

    @property
    def track_file_path(self) -> pathlib.Path:
        return APP_DATA_DIR / self.TRACK_FILE_NAME
