from PySide6 import QtWidgets
from hazbin_tracker.core.constants import (
    APPLICATION_TITLE,
    ORGANIZATION_NAME,
    HAZBIN_TRACKER_VERSION
)


class SystemTrayContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exit_action = self.addAction("Exit")
        self.exit_action.triggered.connect(QtWidgets.QApplication.quit)


class HazbinTrackerSystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("Hazbin Tracker")
        self.context_menu = SystemTrayContextMenu(parent)
        self.setContextMenu(self.context_menu)


class HazbinTrackerApplication(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APPLICATION_TITLE)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setApplicationVersion(HAZBIN_TRACKER_VERSION)

        self.tray_icon = HazbinTrackerSystemTrayIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        )
        self.tray_icon.show()
