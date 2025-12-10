from PySide6 import QtWidgets


def center_dialog_on_screen(dialog: QtWidgets.QDialog):
    """Center the given dialog on the primary screen.

    Args:
        dialog (QtWidgets.QDialog): The dialog to center.
    """
    screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
    x = (screen_geometry.width() - dialog.width()) // 2
    y = (screen_geometry.height() - dialog.height()) // 2
    dialog.move(x, y)
