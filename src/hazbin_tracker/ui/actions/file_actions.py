import logging

from PySide6 import QtCore, QtGui

from hazbin_tracker.core.constants import (
    CHECK_HISTORY_FILE_PATH,
    SETTINGS_FILE_PATH,
)

LOGGER = logging.getLogger(__name__)


class OpenSettingsFileAction(QtGui.QAction):
    """Action to open the settings file."""

    SETTINGS_FILE_URL = QtCore.QUrl.fromLocalFile(SETTINGS_FILE_PATH.as_posix())
    DEFAULT_TEXT = "Open Settings File"

    def __init__(self, text: str | None = None, parent=None):
        """Initialize the action.

        Args:
            text (str | None): The text to display on the action.
            parent (QtCore.QObject | None): The parent object.
        """
        super().__init__(text or self.DEFAULT_TEXT, parent)
        self.setToolTip("Open the settings file")
        self.setStatusTip("Opens the settings file")
        self.triggered.connect(self.open_settings)

    def open_settings(self):
        """Open the settings file."""
        LOGGER.info("Opening settings file: %s", self.SETTINGS_FILE_URL)
        QtGui.QDesktopServices.openUrl(self.SETTINGS_FILE_URL)


class OpenLogFileAction(QtGui.QAction):
    """Action to open the log file."""

    LOG_FILE_PATH = QtCore.QUrl.fromLocalFile(LOGGER.LOG_FILE_PATH)  # ty: ignore
    DEFAULT_TEXT = "Open Log File"

    def __init__(self, text: str | None = None, parent: QtCore.QObject | None = None):
        """Initialize the action.

        Args:
            text (str | None): The text to display on the action.
            parent (QtCore.QObject | None): The parent object.
        """
        super().__init__(text or self.DEFAULT_TEXT, parent)
        self.setToolTip("Open the log file")
        self.setStatusTip("Opens the log file")
        self.triggered.connect(self.open_log)

    def open_log(self):
        """Open the log file."""
        LOGGER.info("Opening log file: %s", self.LOG_FILE_PATH)
        QtGui.QDesktopServices.openUrl(self.LOG_FILE_PATH)


class OpenCheckHistoryFileAction(QtGui.QAction):
    """Action to open the check history file."""

    CHECK_HISTORY_FILE_URL = QtCore.QUrl.fromLocalFile(
        CHECK_HISTORY_FILE_PATH.as_posix()
    )
    DEFAULT_TEXT = "Open Check History File"

    def __init__(self, text: str | None = None, parent: QtCore.QObject | None = None):
        """Initialize the action.

        Args:
            text (str | None): The text to display on the action.
            parent (QtCore.QObject | None): The parent object.
        """
        super().__init__(text or self.DEFAULT_TEXT, parent)
        self.setToolTip("Open the check history file")
        self.setStatusTip("Opens the check history file")
        self.triggered.connect(self.open_check_history)

    def open_check_history(self):
        """Open the check history file."""
        LOGGER.info("Opening check history file: %s", self.CHECK_HISTORY_FILE_URL)
        QtGui.QDesktopServices.openUrl(self.CHECK_HISTORY_FILE_URL)
