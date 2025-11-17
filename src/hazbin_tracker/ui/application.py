from PySide6 import QtWidgets
from PySide6 import QtGui
import resources.resources_rc  # noqa: F401

from hazbin_tracker.core.constants import (
    APPLICATION_TITLE,
    ORGANIZATION_NAME,
)

from ..version import __version__
from ..core import config
from ..core.cards_tracker import CardsTracker
from .tray import HazbinTrackerSystemTrayIcon


class HazbinTrackerApplication(QtWidgets.QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APPLICATION_TITLE)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setApplicationVersion(__version__)
        self.setWindowIcon(QtGui.QIcon(":/icons/hazbin.png"))

        self._config: dict = config.load_config_file()
        self._setup_pushover()

        self.cards_tracker = CardsTracker()
        self.tray_icon = HazbinTrackerSystemTrayIcon(
            QtGui.QIcon(":/icons/cards.png"))

        self.tray_icon.show()
        self.cards_tracker.run_check()
        self.cards_tracker.start_periodic_check_timer()

    def _setup_pushover(self):
        if not self.is_pushover_enabled:
            return

        self._user_key, self._app_key = config.load_keys()
        if not self._user_key and self._api_key:
            raise ValueError(
                (
                    "Pushover USER_KEY and APP_KEY"
                    f" must be set in config: {config.CONFIG_FILE_PATH}")
            )

    @property
    def config(self):
        return self._config

    @property
    def is_pushover_enabled(self):
        return self.config.get("PUSHOVER_ENABLED", 0)

    @property
    def user_key(self) -> str:
        return self.config.get("PUSHOVER_USER_KEY")

    @property
    def app_key(self) -> str:
        return self.config.get("PUSHOVER_HAZBIN_APP_KEY")
