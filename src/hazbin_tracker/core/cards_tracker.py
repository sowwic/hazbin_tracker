import typing
import datetime
import pathlib
import json
import requests
import logging

from PySide6 import QtCore
from PySide6 import QtWidgets

from .scrapper import get_all_cards
from .constants import APP_DATA_DIR, CHECK_HISTORY_FILE_PATH

if typing.TYPE_CHECKING:
    from ..ui.application import HazbinTrackerApplication

LOGGER = logging.getLogger(__name__)


class CardsTracker(QtCore.QObject):
    """Tracker class to monitor Hazbin cards for new releases."""

    TRACK_FILE_NAME = "track_data.json"
    NICE_TIME_FORMAT = "%d-%m-%Y at %H:%M:%S"

    cards_updated = QtCore.Signal()
    check_time_updated = QtCore.Signal()
    new_cards_found = QtCore.Signal(list)
    check_completed = QtCore.Signal(list)

    def __repr__(self):
        """Repr override.

        Returns:
            str: string representation
        """
        return (
            f"<CardsTracker last_check_time={self.nice_last_checked_time},"
            " cards_count="
            f"{len(self._cards_data) if self._cards_data else 0},"
            f" frequency={self.application.settings.tracker_check_minute_frequency} min>"
        )

    def __init__(self):
        """Instance constructor."""
        super().__init__()
        self._last_check_time = None
        self._cards_data = None

        # Timer
        self._check_timer = QtCore.QTimer(self)

        # Initial data
        self.populate_cards_data()
        self._create_signals()
        LOGGER.info(f"Started tracker: {self}")

    def _create_signals(self):
        """Create signals and connect them."""
        self._check_timer.timeout.connect(self.run_check)
        self.new_cards_found.connect(self.on_new_cards_found)
        self.application.settings.tracker_frequency_changed.connect(
            self.start_periodic_check_timer
        )
        self.check_completed.connect(self.record_check_result)
        LOGGER.info(f"Started tracker: {self}")

    @property
    def cards_data(self):
        """Get cards data."""
        return self._cards_data

    @cards_data.setter
    def cards_data(self, value):
        self._cards_data = value
        self.cards_updated.emit()

    @property
    def last_check_time(self):
        """Get last check time.

        Returns:
            datetime.datetime: last check time
        """
        return self._last_check_time

    @last_check_time.setter
    def last_check_time(self, value):
        self._last_check_time = value
        self.check_time_updated.emit()

    @property
    def nice_last_checked_time(self):
        """Get nicely formatted last checked time.

        Returns:
            str: nicely formatted last checked time
        """
        if not self.last_check_time:
            return "Never"
        return self.last_check_time.strftime(self.NICE_TIME_FORMAT)

    @property
    def track_file_path(self) -> pathlib.Path:
        """Get the path to the track file.

        Returns:
            pathlib.Path: path to the track file
        """
        return APP_DATA_DIR / self.TRACK_FILE_NAME

    @property
    def application(self):
        """Get the main application instance.

        Returns:
            HazbinTrackerApplication: main application instance
        """
        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()
        return app

    @property
    def latest_publish_time(self) -> datetime.datetime:
        """Get the latest published card time.

        Returns:
            datetime.datetime: latest published card time
        """
        if not self.cards_data:
            return None
        latest_time = max(
            datetime.datetime.fromisoformat(card["published_at"])
            for card in self.cards_data
        )
        return latest_time

    @property
    def nice_latest_publish_time(self) -> str:
        """Get nicely formatted latest published card time.

        Returns:
            str: nicely formatted latest published card time
        """
        latest_time = self.latest_publish_time
        if not latest_time:
            return "N/A"
        return latest_time.strftime(self.NICE_TIME_FORMAT)

    def start_periodic_check_timer(self):
        """Start the periodic check timer."""
        LOGGER.debug("Starting check timer...")
        if self._check_timer.isActive():
            self._check_timer.stop()
        self._check_timer.setInterval(
            self.application.settings.tracker_check_minute_frequency * 60 * 1000
        )  # minutes in msƒ
        self._check_timer.start()
        LOGGER.debug(f"Check Timer: {self._check_timer.interval()}ms")

    def run_check(self) -> list[dict]:
        """Run a check for new cards.

        Returns:
            list[dict]: list of new cards found
        """
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
        self.check_completed.emit(new_cards)
        if new_cards:
            self.new_cards_found.emit(new_cards)
        return new_cards

    def populate_cards_data(self):
        """Populate cards data from cache or source."""
        LOGGER.debug("Populating tracker cards data")
        try:
            self.fetch_cards_data_from_cache()
        except (FileNotFoundError, json.JSONDecodeError):
            LOGGER.debug("Failed to load cards from cache")
            self.fetch_cards_data_from_source()
            self.create_cache()

    def fetch_cards_data_from_cache(self):
        """Fetch cards data from cache file."""
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
        """Fetch cards data from source."""
        LOGGER.debug("Fetching cards data from source")
        self._cards_data = get_all_cards()
        self.record_time()

    def create_cache(self):
        """Create cache file with current cards data and last check time."""
        LOGGER.debug("Creating cache")
        cache_content = {
            "last_check_time": self.last_check_time.isoformat(),
            "cards": self.cards_data,
        }
        with self.track_file_path.open("w") as cache_file:
            json.dump(cache_content, cache_file, indent=4)

    def record_time(self, time_override: datetime.datetime = None):
        """Record the current time as last check time.

        Args:
            time_override (datetime.datetime, optional): time to set as last check time.
                Defaults to None, which uses the current time.
        """
        LOGGER.debug("Recording time...")
        new_time = (
            time_override if time_override else datetime.datetime.now(datetime.UTC)
        )
        self.last_check_time = new_time
        LOGGER.debug(f"Recorded time: {self.last_check_time}")

    def generate_new_cards_message(self, new_cards: list[dict]) -> str:
        """Generate a message for new cards found.

        Args:
            new_cards (list[dict]): list of new cards found
        Returns:
            str: generated message
        """
        LOGGER.debug("Generating new cards message...")
        message = f"Found {len(new_cards)} new Hazbin cards:"
        for card in new_cards:
            message += f"\n- {card.get('title')}"
        return message

    def on_new_cards_found(self, new_cards: list):
        """Handle new cards found event.

        Args:
            new_cards (list): list of new cards found
        """
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

    def record_check_result(self, new_cards: list[dict]):
        """Record the result of a check.

        Args:
            new_cards (list[dict]): list of new cards found
        """
        record = {
            "timestamp": self.nice_last_checked_time,
            "new_cards": new_cards,
        }
        if CHECK_HISTORY_FILE_PATH.exists():
            try:
                history = json.loads(CHECK_HISTORY_FILE_PATH.read_text())
            except Exception:
                LOGGER.warning("Failed to read check history file, starting fresh.")
                history = []
        else:
            history = []

        history.insert(0, record)

        # Trim history if it exceeds the maximum size
        history = history[: self.application.settings.check_history_size]
        CHECK_HISTORY_FILE_PATH.write_text(json.dumps(history, indent=4))
        LOGGER.debug(f"Recorded check result to history: {CHECK_HISTORY_FILE_PATH}")
