import typing
from PySide6 import QtCore
from PySide6 import QtWidgets

if typing.TYPE_CHECKING:
    from hazbin_tracker.ui.application import HazbinTrackerApplication
    from hazbin_tracker.core.cards_tracker import CardsTracker


class SystemTrayContextMenu(QtWidgets.QMenu):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.check_for_updates_action = self.addAction("Check for Updates")
        self.exit_action = self.addAction("Exit")
        self.exit_action.triggered.connect(QtWidgets.QApplication.quit)

    @property
    def tracker(self) -> "CardsTracker":
        app: "HazbinTrackerApplication" = QtWidgets.QApplication.instance()
        return app.cards_tracker


class HazbinTrackerSystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("Hazbin Tracker")
        self.context_menu = SystemTrayContextMenu(parent)
        self.setContextMenu(self.context_menu)

        self.context_menu.check_for_updates_action.triggered.connect(
            self.onCheckRequested
        )

    @property
    def tracker(self) -> "CardsTracker":
        app: "HazbinTrackerApplication" = QtWidgets.QApplication.instance()
        return app.cards_tracker

    @QtCore.Slot()
    def onCheckRequested(self):
        new_cards = self.tracker.run_check()
        if not new_cards:
            self.showMessage(
                "Hazbin Tracker",
                "No new Hazbin cards found.",
                QtWidgets.QSystemTrayIcon.NoIcon,
                5000
            )
