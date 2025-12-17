import json
import typing
import logging
from PySide6 import QtCore

from ...core.constants import CHECK_HISTORY_FILE_PATH


LOGGER = logging.getLogger(__name__)


class CheckHistoryModel(QtCore.QAbstractTableModel):
    """Model for the check history table view."""

    def __init__(self, parent=None):
        """Instance constructor.

        Args:
            parent (QtCore.QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)
        self._records: list[dict] = []

    def load(self):
        """Load check history from the JSON file."""
        LOGGER.debug("Loading check history from file: %s", CHECK_HISTORY_FILE_PATH)
        if CHECK_HISTORY_FILE_PATH.exists():
            try:
                self._records = json.loads(CHECK_HISTORY_FILE_PATH.read_text())
            except Exception:
                LOGGER.exception("Failed to load check history, initializing new one.")
                self._records = []
        else:
            self._records = []

        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        """Get the number of rows in the model.

        Args:
            parent (QtCore.QModelIndex, optional): Parent index.

        Returns:
            int: Number of rows.
        """
        return len(self._records)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        """Get the number of columns in the model.

        Args:
            parent (QtCore.QModelIndex, optional): Parent index.

        Returns:
            int: Number of columns.
        """
        return 2

    def data(self, index: QtCore.QModelIndex, role: int) -> typing.Any:
        """Get data for a given index and role.

        Args:
            index (QtCore.QModelIndex): The index to retrieve data for.
            role (int, optional): The role for which data is requested.

        Returns:
            Any: The data for the given index and role.
        """
        if not index.isValid():
            return None

        record = self._records[index.row()]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return record.get("timestamp", "")

            if index.column() == 1:
                return self.format_record_new_cards(record)

        return None

    def format_record_new_cards(self, record: dict) -> str:
        """Format the new cards list for display.

        Args:
            record (dict): A record containing check info.

        Returns:
            str: Formatted string of new cards.
        """
        new_cards = record.get("new_cards", [])
        if not new_cards:
            return "No new cards"
        result_string = ""
        for card_info in new_cards:
            card_title = card_info.get("title")
            result_string += f"- {card_title}\n"
        return result_string.strip()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Get header data for the model.

        Args:
            section (int): Section index.
            orientation (QtCore.Qt.Orientation): Orientation (horizontal/vertical).
            role (int, optional): Role for which data is requested.

        Returns:
            Any: Header data for the given section, orientation, and role.
        """
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return ["Time", "Result"][section]
        return str(section)
