"""Model component for table data management."""

from qtpy.QtCore import Qt, QAbstractTableModel, QMimeData
from qtpy.QtGui import QStandardItem
from typing import List, Dict, Any, Optional


class ItemTableModel(QAbstractTableModel):
    """Table model for managing item data with drag/drop support."""

    def __init__(self, controller, parent=None):
        """Initialize model with data controller.

        Args:
            controller: DataController instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.controller = controller
        self.headers = controller.get_column_headers()
        self.keys = controller.get_column_keys()

    def rowCount(self, parent=None):
        """Return number of rows."""
        return len(self.controller.get_items())

    def columnCount(self, parent=None):
        """Return number of columns."""
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role."""
        if not index.isValid():
            return None

        item = self.controller.get_item_by_index(index.row())
        if not item:
            return None

        if role == Qt.DisplayRole:
            key = self.keys[index.column()]
            return item.get(key, "")

        elif role == Qt.UserRole:
            return item

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data."""
        if (
            orientation == Qt.Horizontal
            and role == Qt.DisplayRole
            and 0 <= section < len(self.headers)
        ):
            return self.headers[section]
        return None

    def flags(self, index):
        """Return item flags for drag/drop support."""
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

    def supportedDragActions(self):
        """Return supported drag actions."""
        return Qt.CopyAction

    def mimeTypes(self):
        """Return supported MIME types for drag operations."""
        return ["application/x-item-data"]

    def mimeData(self, indexes):
        """Create MIME data for drag operation."""
        if not indexes:
            return None

        # Get unique rows from selected indexes
        rows = set(index.row() for index in indexes if index.isValid())
        items = []

        for row in sorted(rows):
            item = self.controller.get_item_by_index(row)
            if item:
                items.append(item)

        if not items:
            return None

        mime_data = QMimeData()
        mime_data.setData("application/x-item-data", str(items).encode())
        return mime_data

    def refresh(self):
        """Refresh model data."""
        self.beginResetModel()
        self.controller.load_data()
        self.endResetModel()
