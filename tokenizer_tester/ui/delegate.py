#!/usr/bin/env python3
"""UI delegates for tokenizer template tester.

This module contains custom delegates for various UI components in the tokenizer
template tester application.
"""

from typing import Optional

from qtpy.QtCore import Qt, QRect
from qtpy.QtWidgets import (
    QStyledItemDelegate,
    QWidget,
    QStyleOptionViewItem,
    QStyle,
    QApplication,
)
from qtpy.QtGui import QPainter, QColor, QPen, QFontMetrics


class TokenTableItemDelegate(QStyledItemDelegate):
    """Custom delegate for styling token table items with enhanced error display."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the token table item delegate.

        Args:
            parent: Parent widget, defaults to None.
        """
        super().__init__(parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index,
    ) -> None:
        """Custom paint method for token table cells.

        Args:
            painter: QPainter object for drawing.
            option: Style options for the item.
            index: Model index of the item being painted.
        """
        painter.save()

        # Get model and data
        model = index.model()
        if not model:
            super().paint(painter, option, index)
            painter.restore()
            return

        # Determine if this is an error cell
        is_error_cell = False
        is_token_column = index.column() == 0

        if hasattr(model, "_token_list") and index.row() < len(
            model._token_list
        ):
            token_name, token_value = model._token_list[index.row()]
            is_error_cell = index.column() == 1 and token_value is None

        # Set background color
        bg_color = self._get_background_color(
            index.row(), is_token_column, is_error_cell
        )
        painter.fillRect(option.rect, bg_color)

        # Set text color
        text_color = QColor("#ff6b6b") if is_error_cell else QColor("white")
        option.palette.setColor(option.palette.Text, text_color)

        # Draw the text
        text = model.data(index, Qt.DisplayRole) or ""
        if is_error_cell:
            text = "❌ Unresolved"  # Add visual indicator for errors

        painter.setPen(QPen(text_color))
        painter.drawText(
            option.rect.adjusted(8, 0, -8, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            text,
        )

        # Draw horizontal grid lines only
        if index.row() < model.rowCount() - 1:  # Not the last row
            pen = QPen(QColor("#404040"))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(
                option.rect.bottomLeft(), option.rect.bottomRight()
            )

        painter.restore()

    def _get_background_color(
        self, row: int, is_token_column: bool, is_error_cell: bool
    ) -> QColor:
        """Get the appropriate background color for a cell.

        Args:
            row: Row index of the cell.
            is_token_column: Whether this is the token name column.
            is_error_cell: Whether this cell contains an error.

        Returns:
            QColor object representing the background color.
        """
        # Base colors
        base_color = "#2b2b2b"  # Main background
        token_color = "#252525"  # Token column (10% darker)
        dimmed_color = "#1f1f1f"  # Alternating rows
        token_dimmed_color = "#1a1a1a"  # Token column dimmed
        error_color = "#4a2828"  # Error cells
        error_dimmed_color = "#3d1f1f"  # Error cells dimmed

        if is_error_cell:
            return QColor(error_dimmed_color if row % 2 == 1 else error_color)
        elif is_token_column:
            return QColor(token_dimmed_color if row % 2 == 1 else token_color)
        else:
            return QColor(dimmed_color if row % 2 == 1 else base_color)

    def sizeHint(self, option: QStyleOptionViewItem, index) -> None:
        """Return the size hint for the item.

        Args:
            option: Style options for the item.
            index: Model index of the item.

        Returns:
            QSize representing the preferred size for the item.
        """
        size = super().sizeHint(option, index)
        # Ensure minimum height for better readability
        size.setHeight(max(size.height(), 28))
        return size


class InputFieldDelegate(QStyledItemDelegate):
    """Custom delegate for input field styling and behavior."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the input field delegate.

        Args:
            parent: Parent widget, defaults to None.
        """
        super().__init__(parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index,
    ) -> None:
        """Custom paint method for input fields.

        Args:
            painter: QPainter object for drawing.
            option: Style options for the item.
            index: Model index of the item being painted.
        """
        # This delegate is primarily for custom editing behavior
        # The actual styling is handled by CSS
        super().paint(painter, option, index)

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index
    ):
        """Create a custom editor widget if needed.

        Args:
            parent: Parent widget for the editor.
            option: Style options for the item.
            index: Model index of the item being edited.

        Returns:
            Custom editor widget or None to use default.
        """
        # For now, use the default editor
        return super().createEditor(parent, option, index)


class HeaderDelegate(QStyledItemDelegate):
    """Custom delegate for table headers with enhanced styling."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the header delegate.

        Args:
            parent: Parent widget, defaults to None.
        """
        super().__init__(parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index,
    ) -> None:
        """Custom paint method for header cells.

        Args:
            painter: QPainter object for drawing.
            option: Style options for the item.
            index: Model index of the item being painted.
        """
        painter.save()

        # Draw background
        bg_color = QColor("#353535")
        painter.fillRect(option.rect, bg_color)

        # Draw text
        text_color = QColor("white")
        painter.setPen(QPen(text_color))

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        model = index.model()
        text = (
            model.headerData(index.column(), Qt.Horizontal, Qt.DisplayRole)
            or ""
        )

        painter.drawText(
            option.rect.adjusted(8, 0, -8, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            text,
        )

        # Draw bottom border
        pen = QPen(QColor("#404040"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> None:
        """Return the size hint for the header item.

        Args:
            option: Style options for the item.
            index: Model index of the item.

        Returns:
            QSize representing the preferred size for the header.
        """
        size = super().sizeHint(option, index)
        # Ensure adequate height for headers
        size.setHeight(max(size.height(), 32))
        return size
