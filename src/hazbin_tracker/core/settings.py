import logging
from hazbin_tracker.core.constants import SETTINGS_FILE_PATH
from PySide6 import QtCore

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HazbinSettings(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self._settings = QtCore.QSettings(
            str(SETTINGS_FILE_PATH), QtCore.QSettings.IniFormat
        )
        LOGGER.debug(f"Settings file: {self._settings.fileName()}")

    # ----------------------
    # Pushover
    # ----------------------

    @property
    def pushover_enabled(self) -> bool:
        return self._settings.value(
            "pushover/enabled", defaultValue=False, type=bool
        )

    @pushover_enabled.setter
    def pushover_enabled(self, state: bool):
        self._settings.setValue("pushover/enabled", state)

    @property
    def pushover_user_key(self) -> str:
        return self._settings.value(
            "pushover/user_key", defaultValue="", type=str
        )

    @pushover_user_key.setter
    def pushover_user_key(self, value: str):
        self._settings.setValue("pushover/user_key", value)

    @property
    def pushover_app_key(self) -> str:
        return self._settings.value(
            "pushover/app_key", defaultValue="", type=str
        )

    @pushover_app_key.setter
    def pushover_app_key(self, value: str):
        self._settings.setValue("pushover/app_key", value)

    @QtCore.Slot()
    def sync(self):
        self._settings.sync()
