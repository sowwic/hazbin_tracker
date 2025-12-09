import typing
from PySide6 import QtWidgets

if typing.TYPE_CHECKING:
    from ..core.settings import HazbinSettings


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog for Hazbin Tracker application."""

    def __init__(self, settings: "HazbinSettings", parent: QtWidgets.QWidget = None):
        """Instance constructor.

        Args:
            settings (HazbinSettings): The settings manager instance.
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.settings = settings

        # --- Tracker Section ---
        self.tracker_group = QtWidgets.QGroupBox("Tracker")
        tracker_group_layout = QtWidgets.QFormLayout()
        self.tracker_check_frequency_spinbox = QtWidgets.QSpinBox()
        self.tracker_check_frequency_spinbox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons
        )
        self.tracker_check_frequency_spinbox.setValue(
            self.settings.tracker_check_minute_frequency
        )
        self.tracker_check_frequency_spinbox.setMinimum(
            self.settings.TRACKER_CHECK_FREQUENCY_MINIMUM
        )
        self.tracker_check_frequency_spinbox.setMinimumWidth(50)
        tracker_group_layout.addRow(
            "Check Frequency (min):", self.tracker_check_frequency_spinbox
        )
        self.tracker_group.setLayout(tracker_group_layout)

        # --- Pushover Section ---
        self.pushover_group = QtWidgets.QGroupBox("Pushover")
        self.pushover_group.setCheckable(True)
        self.pushover_group.setChecked(self.settings.pushover_enabled)

        pushover_group_layout = QtWidgets.QFormLayout()

        self.user_key_edit = QtWidgets.QLineEdit(self.settings.pushover_user_key)
        self.app_key_edit = QtWidgets.QLineEdit(self.settings.pushover_app_key)
        for key_edit in [self.user_key_edit, self.app_key_edit]:
            key_edit.setMinimumWidth(200)
            key_edit.setToolTip(key_edit.text())

        pushover_group_layout.addRow("User Key:", self.user_key_edit)
        pushover_group_layout.addRow("App Key:", self.app_key_edit)

        self.pushover_group.setLayout(pushover_group_layout)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tracker_group)
        layout.addWidget(self.pushover_group)
        layout.addStretch()

        # --- Dialog Buttons ---
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        """Save changes to settings."""
        self.settings.pushover_enabled = self.pushover_group.isChecked()
        self.settings.pushover_user_key = self.user_key_edit.text()
        self.settings.pushover_app_key = self.app_key_edit.text()
        self.settings.tracker_check_minute_frequency = (
            self.tracker_check_frequency_spinbox.value()
        )

        self.settings.sync()  # write to disk
        super().accept()

    def center_on_screen(self):
        """Center the dialog on the screen."""
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
