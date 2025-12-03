import typing
import datetime
import pathlib
import json
import requests
import logging

from PySide6 import QtCore
from PySide6 import QtWidgets

from .scrapper import get_all_cards
from .constants import APP_DATA_DIR

if typing.TYPE_CHECKING:
    from ..ui.application import HazbinTrackerApplication

LOGGER = logging.getLogger(__name__)


class CardsTracker(QtCore.QObject):
    TRACK_FILE_NAME = "track_data.json"
    cards_updated = QtCore.Signal()
    check_time_updated = QtCore.Signal()
    new_cards_found = QtCore.Signal(list)

    def __repr__(self):
        return (
            f"<CardsTracker last_check_time={self.nice_last_checked_time},"
            " cards_count="
            f"{len(self._cards_data) if self._cards_data else 0},"
            f" frequency={self.application.settings.tracker_check_minute_frequency} min>"
        )

    def __init__(self):
        super().__init__()
        self._last_check_time = None
        self._cards_data = None

        # Timer
        self._check_timer = QtCore.QTimer(self)
        self._check_timer.timeout.connect(self.run_check)

        # Initial data
        self.populate_cards_data()

        # Signals
        self.new_cards_found.connect(self.on_new_cards_found)
        self.application.settings.tracker_frequency_changed.connect(
            self.start_periodic_check_timer
        )
        LOGGER.info(f"Started tracker: {self}")

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
    def nice_last_checked_time(self):
        if not self.last_check_time:
            return "Never"
        return self.last_check_time.strftime("%d-%m-%Y at %H:%M:%S")

    @property
    def track_file_path(self) -> pathlib.Path:
        return APP_DATA_DIR / self.TRACK_FILE_NAME

    @property
    def application(self):
        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()
        return app

    def start_periodic_check_timer(self):
        LOGGER.debug("Starting check timer...")
        if self._check_timer.isActive():
            self._check_timer.stop()
        self._check_timer.setInterval(
            self.application.settings.tracker_check_minute_frequency * 60 * 1000
        )  # minutes in msƒ
        self._check_timer.start()
        LOGGER.debug(f"Check Timer: {self._check_timer.interval()}ms")

    def run_check(self) -> list[dict]:
        LOGGER.info("Running cards check...")
        source_cards = get_all_cards()

        new_cards = []
        for card in source_cards:
            cards_published_at = datetime.datetime.fromisoformat(card["published_at"])
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
        LOGGER.debug("Populating tracker cards data")
        try:
            self.fetch_cards_data_from_cache()
        except (FileNotFoundError, json.JSONDecodeError):
            LOGGER.debug("Failed to load cards from cache")
            self.fetch_cards_data_from_source()
            self.create_cache()

    def fetch_cards_data_from_cache(self):
        LOGGER.debug("Loading cards from cache")
        with self.track_file_path.open() as cache_file:
            cache_data = json.load(cache_file)
        self._cards_data = cache_data.get("cards", [])
        self.record_time(
            time_override=datetime.datetime.fromisoformat(
                cache_data.get("last_check_time")
            )
        )
        LOGGER.debug(f"Loaded {len(self._cards_data)} cards from {self.track_file_path}")

    def fetch_cards_data_from_source(self):
        LOGGER.debug("Fetching cards data from source")
        self._cards_data = get_all_cards()
        self.record_time()

    def create_cache(self):
        LOGGER.debug("Creating cache")
        cache_content = {
            "last_check_time": self.last_check_time.isoformat(),
            "cards": self.cards_data,
        }
        with self.track_file_path.open("w") as cache_file:
            json.dump(cache_content, cache_file, indent=4)

    def record_time(self, time_override: datetime.datetime = None):
        LOGGER.debug("Recording time...")
        new_time = (
            time_override if time_override else datetime.datetime.now(datetime.UTC)
        )
        self.last_check_time = new_time
        LOGGER.debug(f"Recorded time: {self.last_check_time}")

    def generate_new_cards_message(self, new_cards: list[dict]) -> str:
        LOGGER.debug("Generating new cards message...")
        message = f"Found {len(new_cards)} new Hazbin cards:"
        for card in new_cards:
            message += f"\n- {card.get('title')}"
        return message

    def on_new_cards_found(self, new_cards: list):
        if not self.application.settings.pushover_enabled:
            LOGGER.debug("Push notifications are disabled, skipping...")
            return

        try:
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": self.application.settings.pushover_app_key,
                    "user": self.application.settings.pushover_user_key,
                    "title": "HazbinTracker - New Cards available!",
                    "message": self.generate_new_cards_message(new_cards),
                },
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            LOGGER.exception(
                "Failed to send Pushover notification for new cards due to HTTP error."
            )
        except Exception:
            LOGGER.exception(
                "Failed to send Pushover notification due to unhandled error."
            )
