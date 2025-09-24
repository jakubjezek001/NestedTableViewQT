"""Delegate component for custom item rendering."""

from qtpy.QtWidgets import QStyledItemDelegate, QApplication, QStyle
from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QPen, QColor, QBrush


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
        # Check if item is selected and paint brighter background
        if option.state & QStyle.State_Selected:
            painter.save()
            # Get current background color and make it 20% brighter
            bg_color = option.palette.highlight().color()
            brighter_color = QColor(
                min(255, int(bg_color.red() * 1.2)),
                min(255, int(bg_color.green() * 1.2)),
                min(255, int(bg_color.blue() * 1.2)),
            )
            painter.fillRect(option.rect, QBrush(brighter_color))
            painter.restore()

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
