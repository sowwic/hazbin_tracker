import typing
from PySide6 import QtWidgets

if typing.TYPE_CHECKING:
    from ..core.settings import HazbinSettings


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: "HazbinSettings", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = settings

        layout = QtWidgets.QVBoxLayout(self)

        # --- Pushover Section ---
        self.pushover_group = QtWidgets.QGroupBox("Pushover")
        self.pushover_group.setCheckable(True)
        self.pushover_group.setChecked(self.settings.pushover_enabled)

        group_layout = QtWidgets.QFormLayout()

        self.user_key_edit = QtWidgets.QLineEdit(self.settings.pushover_user_key)
        self.app_key_edit = QtWidgets.QLineEdit(self.settings.pushover_app_key)

        group_layout.addRow("User Key:", self.user_key_edit)
        group_layout.addRow("App Key:", self.app_key_edit)

        self.pushover_group.setLayout(group_layout)
        layout.addWidget(self.pushover_group)

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
        self.settings.sync()  # write to disk
        super().accept()

    def center_on_screen(self):
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
