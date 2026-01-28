import typing
import logging
from PySide6 import QtCore, QtWidgets

from .models.check_history import CheckHistoryModel

if typing.TYPE_CHECKING:
    from hazbin_tracker.ui.application import HazbinTrackerApplication


LOGGER = logging.getLogger(__name__)


class CheckHistoryDialog(QtWidgets.QDialog):
    """Dialog to display the check history."""

    refresh_requested = QtCore.Signal()

    def __init__(self, parent=None):
        """Instance constructor.

        Args:
            parent (QtWidgets.QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Check History")
        self.resize(800, 400)

        self._history_model = CheckHistoryModel()

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

        self.refresh_requested.emit()

    def _create_widgets(self) -> None:
        """Create and arrange widgets in the dialog."""
        self._latest_publish_label = QtWidgets.QLabel(self)

        # Table view
        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setModel(self._history_model)
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.table_view.resizeColumnsToContents()
        self.table_view.setAlternatingRowColors(True)

        # Enable custom context menu
        self.table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

    def _create_layouts(self) -> None:
        """Create and set the layout for the dialog."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self._latest_publish_label)
        main_layout.addWidget(self.table_view)
        self.setLayout(main_layout)

    def _create_connections(self) -> None:
        """Create signal-slot connections."""
        self.refresh_requested.connect(self.on_refresh_requested)
        self._history_model.layoutChanged.connect(self.adjust_size_to_contents)

    def application(self) -> "HazbinTrackerApplication":
        """Get the HazbinTrackerApplication instance."""
        app: HazbinTrackerApplication = QtWidgets.QApplication.instance()
        return app

    @QtCore.Slot()
    def adjust_size_to_contents(self) -> None:
        """Adjust the dialog size to fit contents."""
        LOGGER.debug("Adjusting table to fit contents...")
        # Resize first column to fit contents (time)
        self.table_view.resizeColumnToContents(0)
        self.table_view.resizeColumnToContents(1)

        # Make the second column ("New Cards") stretch to take remaining space
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        # Allow rows to adjust height automatically to fit content
        self.table_view.resizeRowsToContents()
        self.table_view.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents
        )

    @QtCore.Slot()
    def on_refresh_requested(self) -> None:
        """Handle refresh request."""
        self.refresh_history()
        self.refresh_latest_publish_label()

    @QtCore.Slot()
    def refresh_latest_publish_label(self) -> None:
        """Refresh the latest publish label."""
        LOGGER.debug("Refreshing latest publish label...")
        latest_publish_time = (
            self.application().cards_tracker.nice_latest_publish_time or "N/A"
        )
        self._latest_publish_label.setText(
            f"Latest Publish: <b>{latest_publish_time}</b>"
        )
        publish_details_tooltip = "No new cards published."
        latest_cards = self.application().cards_tracker.latest_published_cards
        if latest_cards:
            publish_details_tooltip = "<br>".join(
                [card["title"] for card in latest_cards]
            )
        self._latest_publish_label.setToolTip(publish_details_tooltip)

    @QtCore.Slot()
    def refresh_history(self):
        """Refresh the check history data."""
        LOGGER.debug("Refreshing check history...")
        self._history_model.load()

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, position: QtCore.QPoint):
        """Show context menu at the given position.

        Args:
            position (QtCore.QPoint): Position to show the context menu
        """
        menu = QtWidgets.QMenu()

        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_history)

        menu.exec(self.table_view.viewport().mapToGlobal(position))
