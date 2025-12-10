import json
from PySide6 import QtCore

from ...core.constants import CHECK_HISTORY_FILE_PATH


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
        if CHECK_HISTORY_FILE_PATH.exists():
            try:
                self._records = json.loads(CHECK_HISTORY_FILE_PATH.read_text())
            except Exception:
                self._records = []
        else:
            self._records = []

        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Get the number of rows in the model."""
        return len(self._records)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """Get the number of columns in the model."""
        return 2

    def data(self, index: QtCore.QModelIndex, role: int):
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
        """Get header data for the model."""
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return ["Time", "Result"][section]
        return str(section)
