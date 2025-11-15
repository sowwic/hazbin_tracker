from PySide6 import QtWidgets
import platformdirs
import pathlib

from hazbin_tracker.core.constants import (
    APPLICATION_TITLE,
    ORGANIZATION_NAME,
    HAZBIN_TRACKER_VERSION
)

from .tray import HazbinTrackerSystemTrayIcon
from ..core.cards_tracker import CardsTracker


class HazbinTrackerApplication(QtWidgets.QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APPLICATION_TITLE)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setApplicationVersion(HAZBIN_TRACKER_VERSION)

        self.cards_tracker = CardsTracker()

        self.tray_icon = HazbinTrackerSystemTrayIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        )
        self.tray_icon.show()

    @property
    def app_data_dir(self) -> pathlib.Path:
        return pathlib.Path(platformdirs.user_data_dir(
            appname=APPLICATION_TITLE,
            appauthor=ORGANIZATION_NAME,
            roaming=False,
            ensure_exists=True
        ))
