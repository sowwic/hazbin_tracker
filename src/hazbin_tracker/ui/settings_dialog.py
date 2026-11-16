import typing

from PySide6 import QtWidgets

from .actions.file_actions import OpenLogFileAction, OpenSettingsFileAction
from .password_edit import PasswordLineEdit
from .pyside_utils import center_dialog_on_screen
from ..core.config import get_app_config
from ..core.constants import TRACKER_CHECK_FREQUENCY_MINIMUM, CHECK_HISTORY_SIZE_MINIMUM

if typing.TYPE_CHECKING:
    from .application import HazbinTrackerApplication


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog for Hazbin Tracker application."""

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """Instance constructor.

        Args:
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        # Menubar
        self.menubar = QtWidgets.QMenuBar(self)
        self.file_menu = self.menubar.addMenu("File")
        self.file_menu.addAction(OpenSettingsFileAction(parent=self))
        self.file_menu.addAction(OpenLogFileAction(parent=self))

        config = get_app_config()
        # --- Tracker Section ---
        tracker_config = config.values.cards_tracker
        self.tracker_group = QtWidgets.QGroupBox("Tracker")
        tracker_group_layout = QtWidgets.QFormLayout()

        # Tracker check frequency
        self.tracker_check_frequency_spinbox = QtWidgets.QSpinBox()
        self.tracker_check_frequency_spinbox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons
        )
        self.tracker_check_frequency_spinbox.setValue(tracker_config.frequency_min)
        self.tracker_check_frequency_spinbox.setMinimum(TRACKER_CHECK_FREQUENCY_MINIMUM)
        self.tracker_check_frequency_spinbox.setMinimumWidth(50)
        tracker_group_layout.addRow(
            "Check Frequency (min):", self.tracker_check_frequency_spinbox
        )

        self.check_history_size = QtWidgets.QSpinBox()
        self.check_history_size.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons
        )
        self.check_history_size.setValue(tracker_config.history_size)
        self.check_history_size.setMinimum(CHECK_HISTORY_SIZE_MINIMUM)
        self.check_history_size.setMinimumWidth(50)
        self.check_history_size.setToolTip("Number of check history entries to keep.")
        tracker_group_layout.addRow("Check History Size:", self.check_history_size)

        self.tracker_group.setLayout(tracker_group_layout)

        # --- Pushover Section ---
        pushover_config = config.values.pushover
        self.pushover_group = QtWidgets.QGroupBox("Pushover")
        self.pushover_group.setCheckable(True)
        self.pushover_group.setChecked(pushover_config.enabled)

        pushover_group_layout = QtWidgets.QFormLayout()

        self.user_key_edit = PasswordLineEdit(default_text=pushover_config.user_key)
        self.app_key_edit = PasswordLineEdit(default_text=pushover_config.app_key)

        pushover_group_layout.addRow("User Key:", self.user_key_edit)
        pushover_group_layout.addRow("App Key:", self.app_key_edit)

        self.pushover_group.setLayout(pushover_group_layout)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setMenuBar(self.menubar)
        layout.addWidget(self.tracker_group)
        layout.addWidget(self.pushover_group)
        layout.addStretch()

        # --- Dialog Buttons ---
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        center_dialog_on_screen(self)

    def accept(self):
        """Save changes to settings."""
        config = get_app_config()
        pushover_config = config.values.pushover
        pushover_config.enabled = self.pushover_group.isChecked()
        pushover_config.user_key = self.user_key_edit.text
        pushover_config.app_key = self.app_key_edit.text

        tracker_config = config.values.cards_tracker
        tracker_config.frequency_min = self.tracker_check_frequency_spinbox.value()
        tracker_config.history_size = self.check_history_size.value()

        config.save()

        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()  # ty: ignore
        app.configChanged.emit()

        super().accept()
