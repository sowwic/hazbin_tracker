import logging
from PySide6 import (
    QtCore,
    QtGui,
    QtWidgets,
)
import resources.resources_rc  # noqa: F401

from hazbin_tracker.core.constants import (
    APPLICATION_TITLE,
    ORGANIZATION_NAME,
)

from ..version import __version__
from ..core.cards_tracker import CardsTracker
from .tray import HazbinTrackerSystemTrayIcon
from ..core.settings import HazbinSettings
from ..ui.settings_dialog import SettingsDialog


LOGGER = logging.getLogger(__name__)


class HazbinTrackerApplication(QtWidgets.QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APPLICATION_TITLE)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setApplicationVersion(__version__)
        self.setWindowIcon(QtGui.QIcon(":/icons/hazbin.png"))

        self.settings = HazbinSettings()
        self.main_window = QtWidgets.QMainWindow()
        self.main_window.hide()
        self._setup_pushover()

        self.cards_tracker = CardsTracker()
        self.tray_icon = HazbinTrackerSystemTrayIcon(
            QtGui.QIcon(":/icons/cards.png"))

        self.tray_icon.show()
        self.cards_tracker.run_check()
        self.cards_tracker.start_periodic_check_timer()

    def _setup_pushover(self):
        if not self.settings.pushover_enabled:
            self.settings.pushover_enabled = False
            return

        if not (
            self.settings.pushover_user_key and self.settings.pushover_app_key
        ):
            self.show_settings_dialog()
            if not self.settings.pushover_app_key:
                self.settings.pushover_app_key = ""
            if not self.settings.pushover_user_key:
                self.settings.pushover_user_key = ""

    @QtCore.Slot()
    def show_settings_dialog(self):
        dialog = SettingsDialog(self.settings, parent=self.main_window)
        dialog.center_on_screen()
        dialog.raise_()
        dialog.exec()
