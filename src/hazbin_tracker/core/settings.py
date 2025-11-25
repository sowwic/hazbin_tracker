import logging
from hazbin_tracker.core.constants import SETTINGS_FILE_PATH
from PySide6 import QtCore

LOGGER = logging.getLogger(__name__)


class HazbinSettings(QtCore.QObject):
    TRACKER_CHECK_FREQUENCY_MINIMUM = 0.1

    def __init__(self):
        super().__init__()
        self._settings = QtCore.QSettings(
            str(SETTINGS_FILE_PATH), QtCore.QSettings.IniFormat
        )
        LOGGER.debug(f"Settings file: {self._settings.fileName()}")

    @QtCore.Slot()
    def sync(self):
        self._settings.sync()

    # ----------------------
    # Pushover
    # ----------------------

    @property
    def pushover_enabled(self) -> bool:
        return self._settings.value("pushover/enabled", defaultValue=False, type=bool)

    @pushover_enabled.setter
    def pushover_enabled(self, state: bool):
        self._settings.setValue("pushover/enabled", state)

    @property
    def pushover_user_key(self) -> str:
        return self._settings.value("pushover/user_key", defaultValue="", type=str)

    @pushover_user_key.setter
    def pushover_user_key(self, value: str):
        self._settings.setValue("pushover/user_key", value)

    @property
    def pushover_app_key(self) -> str:
        return self._settings.value("pushover/app_key", defaultValue="", type=str)

    @pushover_app_key.setter
    def pushover_app_key(self, value: str):
        self._settings.setValue("pushover/app_key", value)

    @property
    def tracker_check_hour_frequency(self) -> float:
        self._settings.value("tracker/check_frequency", defaultValue=1.0, type=float)

    @tracker_check_hour_frequency.setter
    def tracker_check_hour_frequency(self, value: float):
        if value < self.TRACKER_CHECK_FREQUENCY_MINIMUM:
            LOGGER.warning("Frequency can't be less that 0.1h")
            return
        self._settings.setValue("tracker/check_frequency", value)
