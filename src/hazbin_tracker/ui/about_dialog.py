from PySide6 import QtWidgets, QtGui, QtCore

from ..core.constants import AUTHOR_NAME, RELEASE_YEAR


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Hazbin Tracker")
        # Remove "?" button
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(300, 180)

        layout = QtWidgets.QVBoxLayout(self)

        # Icon at the top
        icon_label = QtWidgets.QLabel(self)
        icon = QtGui.QIcon(":/icons/hazbin.png")
        pixmap = icon.pixmap(64, 64)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title_label = QtWidgets.QLabel("<h2>Hazbin Cards Tracker</h2>", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Version & developer info
        info_label = QtWidgets.QLabel(
            (
                f"Version {QtWidgets.QApplication.applicationVersion()}<br>"
                f"Developed by {AUTHOR_NAME}<br>&copy; {RELEASE_YEAR}"
            ),
            self,
        )
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info_label)

        # Close button
        close_button = QtWidgets.QPushButton("Close", self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=QtCore.Qt.AlignCenter)

        self.center_on_screen()

    def center_on_screen(self):
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
