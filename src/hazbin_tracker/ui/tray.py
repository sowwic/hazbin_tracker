import typing
import webbrowser
from PySide6 import QtCore
from PySide6 import QtWidgets

from .about_dialog import AboutDialog
from ..core.constants import APPLICATION_TITLE, HAZBIN_WEBSITE_URL

if typing.TYPE_CHECKING:
    from hazbin_tracker.ui.application import HazbinTrackerApplication
    from hazbin_tracker.core.cards_tracker import CardsTracker


class SystemTrayContextMenu(QtWidgets.QMenu):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_check_info_action = self.addAction("Last checked: Never")
        self.last_check_info_action.setEnabled(False)
        self.check_for_updates_action = self.addAction("Check for New Cards")
        self.settings_action = self.addAction("Settings...")
        self.about_action = self.addAction("About...")
        self.addSeparator()
        self.exit_action = self.addAction(f"Quit {APPLICATION_TITLE}")

        self.tracker.check_time_updated.connect(self.update_last_checked_action)
        self.settings_action.triggered.connect(
            self.tracker.application.show_settings_dialog)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.exit_action.triggered.connect(QtWidgets.QApplication.quit)

    @property
    def tracker(self) -> "CardsTracker":
        app: "HazbinTrackerApplication" = QtWidgets.QApplication.instance()
        return app.cards_tracker

    @QtCore.Slot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    @QtCore.Slot()
    def update_last_checked_action(self):
        self.last_check_info_action.setText(
            f"Last checked: {self.tracker.nice_last_checked_time}"
        )


class HazbinTrackerSystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("Hazbin Tracker")
        self.context_menu = SystemTrayContextMenu(parent)
        self.setContextMenu(self.context_menu)

        self.context_menu.check_for_updates_action.triggered.connect(
            self.onCheckRequested
        )
        self.tracker.new_cards_found.connect(self.show_new_cards_message)
        self.messageClicked.connect(self.open_hazbin_website)

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

    @QtCore.Slot(list)
    def show_new_cards_message(self, new_cards):
        self.showMessage(
            "Hazbin Tracker",
            self.tracker.generate_new_cards_message(new_cards),
            QtWidgets.QSystemTrayIcon.NoIcon,
            0
        )

    @QtCore.Slot()
    def open_hazbin_website(self):
        webbrowser.open_new_tab(HAZBIN_WEBSITE_URL)
