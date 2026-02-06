from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui


class PasswordLineEdit(QtWidgets.QWidget):
    """Custom widget for password input with visibility toggle."""

    VISIBILITY_ON_ICON_PATH: str = ":/icons/visibility_on.png"
    VISIBILITY_OFF_ICON_PATH: str = ":/icons/visibility_off.png"

    visibility_changed: QtCore.Signal = QtCore.Signal(bool)

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        default_text: str = "",
        default_visibility: bool = False,
    ):
        """Instance constructor.

        Args:
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
            default_text (str): Default text to set in the line edit.
            default_visibility (bool): Default visibility state of the password.
        """
        super().__init__(parent)
        self._visibility_on_icon: QtGui.QIcon = QtGui.QIcon(self.VISIBILITY_ON_ICON_PATH)
        self._visibility_off_icon: QtGui.QIcon = QtGui.QIcon(
            self.VISIBILITY_OFF_ICON_PATH
        )
        self._line_edit = QtWidgets.QLineEdit(default_text)
        self._line_edit.setMinimumWidth(200)
        self._toggle_button = QtWidgets.QToolButton()
        self._toggle_button.setCheckable(True)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self._line_edit)
        layout.addWidget(self._toggle_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self._create_signals()

        self.set_password_visibility(default_visibility)

    def _create_signals(self):
        self._toggle_button.clicked.connect(self.toggle_password_visibility)
        self.visibility_changed.connect(self.on_visibility_changed)

    @QtCore.Slot(bool)
    def set_password_visibility(self, visible: bool):
        """Set the visibility of the password.

        Args:
            visible (bool): If True, show the password; otherwise, hide it.
        """
        if visible:
            self._line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self._line_edit.setToolTip(self._line_edit.text())
        else:
            self._line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self._line_edit.setToolTip("")
        self.visibility_changed.emit(visible)

    @QtCore.Slot()
    def toggle_password_visibility(self):
        """Toggle the visibility of the password."""
        visible: bool = self._line_edit.echoMode() == QtWidgets.QLineEdit.EchoMode.Normal
        self.set_password_visibility(not visible)

    def on_visibility_changed(self, state: bool):
        """Update the toggle button icon based on visibility state.

        Args:
            state (bool): The visibility state of the password.
        """
        self._toggle_button.setIcon(
            self._visibility_on_icon if state else self._visibility_off_icon
        )

    @property
    def text(self) -> str:
        """Get the current text in the line edit.

        Returns:
            str: The current text.
        """
        return self._line_edit.text()
