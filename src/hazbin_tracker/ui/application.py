from PySide6 import QtWidgets
from PySide6 import QtGui
import resources.resources_rc  # noqa: F401

from hazbin_tracker.core.constants import (
    APPLICATION_TITLE,
    ORGANIZATION_NAME,
)

from .tray import HazbinTrackerSystemTrayIcon
from ..core.cards_tracker import CardsTracker


class HazbinTrackerApplication(QtWidgets.QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APPLICATION_TITLE)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setWindowIcon(QtGui.QIcon(":/icons/hazbin.png"))

        self.cards_tracker = CardsTracker()

        icon = QtGui.QIcon(":/icons/cards.png")
        self.tray_icon = HazbinTrackerSystemTrayIcon(icon)
        self.tray_icon.show()
