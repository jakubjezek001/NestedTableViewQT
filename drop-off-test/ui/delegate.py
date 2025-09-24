"""Delegate component for custom item rendering."""

from qtpy.QtWidgets import QStyledItemDelegate, QApplication
from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QPen, QColor


class ItemDelegate(QStyledItemDelegate):
    """Custom delegate for item rendering in table view."""

    def __init__(self, parent=None):
        """Initialize delegate.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

    def paint(self, painter, option, index):
        """Custom paint method for item rendering.

        Args:
            painter: QPainter instance
            option: Style option
            index: Model index
        """
        # Use default painting
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        """Return size hint for item.

        Args:
            option: Style option
            index: Model index

        Returns:
            Size hint
        """
        size = super().sizeHint(option, index)
        # Add some padding
        size.setHeight(max(size.height(), 24))
        return size

    def createEditor(self, parent, option, index):
        """Create editor widget for item editing.

        Args:
            parent: Parent widget
            option: Style option
            index: Model index

        Returns:
            Editor widget or None if not editable
        """
        # No editing for this application
        return None
