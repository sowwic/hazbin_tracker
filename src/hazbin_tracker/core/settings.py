import logging
from hazbin_tracker.core.constants import SETTINGS_FILE_PATH
from PySide6 import QtCore

LOGGER = logging.getLogger(__name__)


class HazbinSettings(QtCore.QObject):
    """QSettings manager for Hazbin Tracker application."""

    TRACKER_CHECK_FREQUENCY_MINIMUM = 1
    TRACKER_CHECK_FREQUENCY_DEFAULT = 60
    CHECK_HISTORY_SIZE_DEFAULT = 50
    CHECK_HISTORY_SIZE_MINIMUM = 10

    tracker_frequency_changed = QtCore.Signal(int)

    def __init__(self):
        """Instance constructor."""
        super().__init__()
        self._settings = QtCore.QSettings(
            str(SETTINGS_FILE_PATH), QtCore.QSettings.IniFormat
        )
        LOGGER.debug(f"Settings file: {self._settings.fileName()}")

    @QtCore.Slot()
    def sync(self):
        """Sync settings to disk."""
        self._settings.sync()

    # ----------------------
    # Pushover
    # ----------------------

    @property
    def pushover_enabled(self) -> bool:
        """Get whether Pushover notifications are enabled."""
        return self._settings.value("pushover/enabled", defaultValue=False, type=bool)

    @pushover_enabled.setter
    def pushover_enabled(self, state: bool):
        self._settings.setValue("pushover/enabled", state)
        LOGGER.debug(f"Pushover enabled set: {state}")

    @property
    def pushover_user_key(self) -> str:
        """Get the Pushover user key."""
        return self._settings.value("pushover/user_key", defaultValue="", type=str)

    @pushover_user_key.setter
    def pushover_user_key(self, value: str):
        self._settings.setValue("pushover/user_key", value)
        LOGGER.debug(f"Pushover user key set: {value}")

    @property
    def pushover_app_key(self) -> str:
        """Get the Pushover application key."""
        return self._settings.value("pushover/app_key", defaultValue="", type=str)

    @pushover_app_key.setter
    def pushover_app_key(self, value: str):
        self._settings.setValue("pushover/app_key", value)
        LOGGER.debug(f"Pushover app key set: {value}")

    # ----------------------  Tracker ----------------------
    @property
    def tracker_check_minute_frequency(self) -> int:
        """Get the tracker check frequency in minutes."""
        return self._settings.value(
            "tracker/check_frequency",
            defaultValue=self.TRACKER_CHECK_FREQUENCY_DEFAULT,
            type=int,
        )

    @tracker_check_minute_frequency.setter
    def tracker_check_minute_frequency(self, value: int):
        if value < self.TRACKER_CHECK_FREQUENCY_MINIMUM:
            LOGGER.warning(
                f"Frequency can't be less that {self.TRACKER_CHECK_FREQUENCY_MINIMUM}min"
            )
            return
        self._settings.setValue("tracker/check_frequency", value)
        LOGGER.info(f"Check frequency set to: {value}min")
        self.tracker_frequency_changed.emit(value)

    @property
    def check_history_size(self) -> int:
        """Get the size of the check history.

        Returns:
            int: number of entries in the check history
        """
        return self._settings.value(
            "tracker/check_history_size",
            defaultValue=self.CHECK_HISTORY_SIZE_DEFAULT,
            type=int,
        )

    @check_history_size.setter
    def check_history_size(self, value: int):
        if value < self.CHECK_HISTORY_SIZE_MINIMUM:
            LOGGER.warning(
                "Check history size can't be less "
                f"than {self.CHECK_HISTORY_SIZE_MINIMUM}"
            )
            value = self.CHECK_HISTORY_SIZE_MINIMUM
        self._settings.setValue("tracker/check_history_size", value)
        LOGGER.info(f"Check history size set to: {value}")
