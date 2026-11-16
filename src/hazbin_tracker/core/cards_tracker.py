import datetime
import json
import logging
import typing

import requests
from PySide6 import QtCore, QtGui, QtWidgets

from .constants import (
    APP_DATA_DIR,
    CHECK_HISTORY_FILE_PATH,
    MAX_CONSECUTIVE_FAILED_CHECKS,
)
from .scrapper import CardsScraper, ScraperError, get_all_cards

if typing.TYPE_CHECKING:
    from ..core.config import CardsTrackerConfigValues, PushoverConfigValues
    from ..ui.application import HazbinTrackerApplication

LOGGER = logging.getLogger(__name__)


class CheckWorkerSignals(QtCore.QObject):
    """Signals emitted by the check worker."""

    finished = QtCore.Signal(list)
    failed = QtCore.Signal(str)


class CheckWorker(QtCore.QRunnable):
    """Fetches cards from the source outside of the GUI thread."""

    def __init__(self, scraper: CardsScraper | None = None):
        """Instance constructor.

        Args:
            scraper (CardsScraper, optional): Scraper to use. Defaults to None.
        """
        super().__init__()
        self.setAutoDelete(False)
        self.signals = CheckWorkerSignals()
        self._scraper = scraper or CardsScraper()

    def run(self):
        """Fetch the cards and report the outcome through signals."""
        try:
            cards = self._scraper.get_all_cards()
        except ScraperError as exc:
            self.signals.failed.emit(str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - nothing may escape a worker thread
            LOGGER.exception("Unexpected error during cards check")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(cards)


class CardsTracker(QtCore.QObject):
    """Tracker class to monitor Hazbin cards for new releases."""

    TRACK_FILE_PATH = APP_DATA_DIR / "track_data.json"
    NICE_TIME_FORMAT = "%d-%m-%Y at %H:%M:%S"

    cards_updated = QtCore.Signal()
    check_time_updated = QtCore.Signal()
    new_cards_found = QtCore.Signal(list)
    check_completed = QtCore.Signal(list)
    check_failed = QtCore.Signal(str)
    repeated_checks_failed = QtCore.Signal(int)

    def __repr__(self):
        """Repr override.

        Returns:
            str: string representation
        """
        return (
            f"<CardsTracker last_check_time={self.nice_last_checked_time},"
            " cards_count="
            f"{len(self._cards_data) if self._cards_data else 0},"
            f" frequency={self.config_values.frequency_min} min>"
        )

    def __init__(self):
        """Instance constructor."""
        super().__init__()
        self._last_check_time: datetime.datetime | None = None
        self._cards_data = None
        self._check_worker: CheckWorker | None = None
        self._failed_checks_in_a_row = 0

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
        self.application.configChanged.connect(self.start_periodic_check_timer)
        self.check_completed.connect(self.record_check_result)

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
    def application(self) -> "HazbinTrackerApplication":
        """Get the main application instance.

        Returns:
            HazbinTrackerApplication: main application instance
        """
        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()  # ty: ignore
        return app

    @property
    def config_values(self) -> "CardsTrackerConfigValues":
        """Get the cards tracker config values."""
        return self.application.config.values.cards_tracker

    @property
    def pushover_config_values(self) -> "PushoverConfigValues":
        """Get the Pushover config values."""
        return self.application.config.values.pushover

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

    @property
    def latest_published_cards(self) -> list[dict]:
        """Get cards with the latest published time.

        Returns:
            list[dict]: list of cards published at the latest time
        """
        if not self.cards_data:
            return []

        latest_time = self.latest_publish_time
        if not latest_time:
            return []

        latest_cards = [
            card
            for card in self.cards_data
            if datetime.datetime.fromisoformat(card["published_at"]) == latest_time
        ]

        return latest_cards

    def start_periodic_check_timer(self):
        """Start the periodic check timer."""
        LOGGER.debug("Starting check timer...")
        if self._check_timer.isActive():
            self._check_timer.stop()
        self._check_timer.setInterval(
            self.config_values.frequency_min * 60 * 1000
        )  # minutes in msƒ
        self._check_timer.start()
        LOGGER.debug(f"Check Timer: {self._check_timer.interval()}ms")

    @property
    def failed_checks_in_a_row(self) -> int:
        """Number of consecutive failed checks since the last success."""
        return self._failed_checks_in_a_row

    @property
    def is_check_running(self) -> bool:
        """Whether a check is currently in progress."""
        return self._check_worker is not None

    def run_check(self) -> bool:
        """Start a check for new cards in the background.

        Returns:
            bool: True if a check was started, False if one is already running
        """
        if self.is_check_running:
            LOGGER.debug("Check already in progress, skipping")
            return False
        LOGGER.info("Running cards check...")
        worker = CheckWorker()
        worker.signals.finished.connect(self._on_check_finished)
        worker.signals.failed.connect(self._on_check_failed)
        self._check_worker = worker
        QtCore.QThreadPool.globalInstance().start(worker)
        return True

    @QtCore.Slot(list)
    def _on_check_finished(self, source_cards: list[dict]):
        """Handle fetched cards: detect new ones, update data and cache.

        Args:
            source_cards (list[dict]): cards fetched from the source
        """
        self._check_worker = None
        self._failed_checks_in_a_row = 0
        new_cards = self.find_new_cards(source_cards)
        LOGGER.info(f"Found {len(new_cards)} new cards.")
        self.cards_data = source_cards
        self.record_time()
        self.create_cache()
        self.check_completed.emit(new_cards)
        if new_cards:
            self.new_cards_found.emit(new_cards)

    @QtCore.Slot(str)
    def _on_check_failed(self, message: str):
        """Handle a failed check; the next scheduled check retries.

        Args:
            message (str): failure description
        """
        self._check_worker = None
        self._failed_checks_in_a_row += 1
        LOGGER.warning(
            f"Cards check failed ({self._failed_checks_in_a_row} in a row): {message}"
        )
        self.check_failed.emit(message)
        if self._failed_checks_in_a_row == MAX_CONSECUTIVE_FAILED_CHECKS:
            self.repeated_checks_failed.emit(self._failed_checks_in_a_row)

    def find_new_cards(self, source_cards: list[dict]) -> list[dict]:
        """Get cards published after the last check.

        Args:
            source_cards (list[dict]): cards fetched from the source

        Returns:
            list[dict]: cards published after the last check time
        """
        if self.last_check_time is None:
            return []
        return [
            card
            for card in source_cards
            if datetime.datetime.fromisoformat(card["published_at"])
            > self.last_check_time
        ]

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
        with self.TRACK_FILE_PATH.open() as cache_file:
            cache_data = json.load(cache_file)
        self._cards_data = cache_data.get("cards", [])
        self.record_time(
            time_override=datetime.datetime.fromisoformat(
                cache_data.get("last_check_time")
            )
        )
        LOGGER.debug(f"Loaded {len(self._cards_data)} cards from {self.TRACK_FILE_PATH}")

    def fetch_cards_data_from_source(self):
        """Fetch cards data from source."""
        LOGGER.debug("Fetching cards data from source")
        try:
            self._cards_data = get_all_cards()
        except ScraperError as exc:
            LOGGER.warning(f"Failed to fetch initial cards: {exc}")
            self._cards_data = []
        self.record_time()

    def create_cache(self):
        """Create cache file with current cards data and last check time."""
        LOGGER.debug("Creating cache")
        cache_content = {
            "last_check_time": self.last_check_time.isoformat(),
            "cards": self.cards_data,
        }
        with self.TRACK_FILE_PATH.open("w") as cache_file:
            json.dump(cache_content, cache_file, indent=4)

    def record_time(self, time_override: datetime.datetime | None = None):
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
            available_variants = [
                variant
                for variant in card.get("variants", [])
                if variant.get("available")
            ]
            message += (
                f"\n- {card.get('title')}"
                f"{'(Not Available)' if not available_variants else ''}"
            )
        return message

    def on_new_cards_found(self, new_cards: list):
        """Handle new cards found event.

        Args:
            new_cards (list): list of new cards found
        """
        if not self.pushover_config_values.enabled:
            LOGGER.debug("Push notifications are disabled, skipping...")
            return

        try:
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": self.pushover_config_values.app_key,
                    "user": self.pushover_config_values.user_key,
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
        history = history[: self.config_values.history_size]
        CHECK_HISTORY_FILE_PATH.write_text(json.dumps(history, indent=4))
        LOGGER.debug(f"Recorded check result to history: {CHECK_HISTORY_FILE_PATH}")

    def build_open_track_file_action(self) -> QtGui.QAction:
        """Build the action to open the track file.

        Returns:
            QtGui.QAction: The action to open the track file.
        """
        action = QtGui.QAction("Track File", self)
        action.setToolTip("Open the track file")
        action.setStatusTip("Opens the track file")
        action.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(self.TRACK_FILE_PATH)
            )
        )
        return action
