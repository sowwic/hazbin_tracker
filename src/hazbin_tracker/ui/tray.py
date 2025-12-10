import typing
import webbrowser
from PySide6 import QtCore
from PySide6 import QtWidgets

from .about_dialog import AboutDialog
from .check_history_dialog import CheckHistoryDialog
from ..core.constants import APPLICATION_TITLE, HAZBIN_WEBSITE_URL

if typing.TYPE_CHECKING:
    from hazbin_tracker.ui.application import HazbinTrackerApplication
    from hazbin_tracker.core.cards_tracker import CardsTracker


class SystemTrayContextMenu(QtWidgets.QMenu):
    """System tray context menu for Hazbin Tracker."""

    def __init__(self, parent: QtWidgets.QWidget = None):
        """Instance constructor.

        Args:
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.last_check_info_action = self.addAction("Last checked: Never")
        self.last_check_info_action.setEnabled(False)
        self.check_for_updates_action = self.addAction("Check for New Cards")
        self.history_action = self.addAction("History...")
        self.settings_action = self.addAction("Settings...")
        self.about_action = self.addAction("About...")
        self.addSeparator()
        self.exit_action = self.addAction(f"Quit {APPLICATION_TITLE}")

        # Initial updates
        self.update_last_checked_action()

        # Signals
        self.history_action.triggered.connect(self.show_history_dialog)
        self.tracker.check_time_updated.connect(self.update_last_checked_action)
        self.settings_action.triggered.connect(
            self.tracker.application.show_settings_dialog
        )
        self.about_action.triggered.connect(self.show_about_dialog)
        self.exit_action.triggered.connect(QtWidgets.QApplication.quit)

    @property
    def application(self) -> "HazbinTrackerApplication":
        """Get the HazbinTrackerApplication instance."""
        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()
        return app

    @property
    def tracker(self) -> "CardsTracker":
        """Get the CardsTracker instance from the application."""
        return self.application.cards_tracker

    @QtCore.Slot()
    def show_about_dialog(self):
        """Show the About dialog."""
        dialog = AboutDialog(self.application.main_window)
        dialog.exec()

    @QtCore.Slot()
    def update_last_checked_action(self):
        """Update the last checked info in the context menu."""
        self.last_check_info_action.setText(
            f"Last checked: {self.tracker.nice_last_checked_time}"
        )

    @QtCore.Slot()
    def show_history_dialog(self):
        """Show the check history dialog."""
        dialog = CheckHistoryDialog(self.application.main_window)
        dialog.exec()


class HazbinTrackerSystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """System tray icon for Hazbin Tracker."""

    def __init__(self, icon, parent: QtWidgets.QWidget = None):
        """Instance constructor.

        Args:
            icon (QtGui.QIcon): The icon to display in the system tray.
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
        """
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
        """Get the CardsTracker instance from the application."""
        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()
        return app.cards_tracker

    @QtCore.Slot()
    def onCheckRequested(self):
        """Handle user request to check for new cards."""
        new_cards = self.tracker.run_check()
        if not new_cards:
            self.showMessage(
                "Hazbin Tracker",
                "No new Hazbin cards found.",
                QtWidgets.QSystemTrayIcon.NoIcon,
                5000,
            )

    @QtCore.Slot(list)
    def show_new_cards_message(self, new_cards: list):
        """Show a system tray message for new cards found.

        Args:
            new_cards (list): List of new cards found.
        """
        self.showMessage(
            "Hazbin Tracker",
            self.tracker.generate_new_cards_message(new_cards),
            QtWidgets.QSystemTrayIcon.NoIcon,
            0,
        )

    @QtCore.Slot()
    def open_hazbin_website(self):
        """Open the Hazbin website in the default web browser."""
        webbrowser.open_new_tab(HAZBIN_WEBSITE_URL)
