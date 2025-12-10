import sys
import logging
import pathlib
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
from .pyside_utils import center_dialog_on_screen


LOGGER = logging.getLogger(__name__)


class HazbinTrackerApplication(QtWidgets.QApplication):
    """Main application class for Hazbin Tracker."""

    LOCK_FILE = pathlib.Path(QtCore.QDir.tempPath()) / "hazbin_tracker.lock"

    def __init__(self, argv):
        """Instance constructor.

        Args:
            argv (list): Command line arguments.
        """
        super().__init__(argv)
        self.lock_check()

        self.setApplicationName(APPLICATION_TITLE)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setApplicationVersion(__version__)
        self.setWindowIcon(QtGui.QIcon(":/icons/hazbin.png"))

        self.settings = HazbinSettings()
        self.main_window = QtWidgets.QMainWindow()
        center_dialog_on_screen(self.main_window)
        self.main_window.hide()
        self._setup_pushover()

        self.cards_tracker = CardsTracker()
        self.tray_icon = HazbinTrackerSystemTrayIcon(QtGui.QIcon(":/icons/cards.png"))

        self.tray_icon.show()
        self.cards_tracker.start_periodic_check_timer()

    def _setup_pushover(self):
        """Set up Pushover notifications based on settings."""
        if not self.settings.pushover_enabled:
            self.settings.pushover_enabled = False
            return

        if not (self.settings.pushover_user_key and self.settings.pushover_app_key):
            self.show_settings_dialog()
            if not self.settings.pushover_app_key:
                self.settings.pushover_app_key = ""
            if not self.settings.pushover_user_key:
                self.settings.pushover_user_key = ""

    @QtCore.Slot()
    def show_settings_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.settings, parent=self.main_window)
        center_dialog_on_screen(dialog)
        dialog.raise_()
        dialog.exec()

    def lock_check(self):
        """Check for existing application instance using a lock file."""
        self.lock_file = QtCore.QLockFile(self.LOCK_FILE.as_posix())
        self.lock_file.setStaleLockTime(0)

        if not self.lock_file.tryLock(0):
            LOGGER.warning("App instance is already running.")
            sys.exit(0)
