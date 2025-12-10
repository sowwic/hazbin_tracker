from PySide6 import QtCore, QtWidgets


from .models.check_history import CheckHistoryModel


class CheckHistoryDialog(QtWidgets.QDialog):
    """Dialog to display the check history."""

    def __init__(self, parent=None):
        """Instance constructor.

        Args:
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Check History")
        self.resize(800, 400)

        self._history_model = CheckHistoryModel()
        self._history_model.load()

        # Table view
        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setModel(self._history_model)
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.table_view.resizeColumnsToContents()

        # Enable custom context menu
        self.table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

        # Resize first column to fit contents (time)
        self.table_view.resizeColumnToContents(1)

        # Make the second column ("New Cards") stretch to take remaining space
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        # Allow rows to adjust height automatically to fit content
        self.table_view.resizeRowsToContents()
        self.table_view.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table_view)

        self.setLayout(layout)

    def refresh_history(self):
        """Refresh the check history data."""
        self._history_model.load()

    def show_context_menu(self, position: QtCore.QPoint):
        """Show right-click context menu."""
        menu = QtWidgets.QMenu()

        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_history)

        menu.exec(self.table_view.viewport().mapToGlobal(position))
