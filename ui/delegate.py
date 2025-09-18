from qtpy.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from qtpy.QtCore import Qt, QRect
from qtpy.QtGui import QPalette, QFont, QPen, QBrush, QColor
from typing import Optional


class NestedTableDelegate(QStyledItemDelegate):
    """Custom delegate for nested table view with special rendering for required columns and disabled cells."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Colors for different cell states
        self.required_color = QColor(
            255, 248, 220
        )  # Light yellow for required columns
        self.disabled_color = QColor(
            240, 240, 240
        )  # Light gray for disabled cells
        self.disabled_text_color = QColor(
            160, 160, 160
        )  # Gray text for disabled
        self.expansion_hover_color = QColor(
            230, 230, 250
        )  # Light blue for expansion hover

    def paint(self, painter, option, index):
        """Custom paint method to handle different cell states."""
        if not index.isValid():
            return super().paint(painter, option, index)

        # Get custom roles data
        is_required = (
            index.data(Qt.UserRole + 1) or False
        )  # Required column status
        has_data = index.data(
            Qt.UserRole + 2
        )  # Data availability (None means not applicable)

        # Create a copy of the option to modify
        opt = QStyleOptionViewItem(option)

        # Handle expansion indicator column (column 0 for product items)
        if index.column() == 0 and index.data(Qt.DisplayRole) in ["▶", "▼"]:
            self._paint_expansion_indicator(painter, opt, index)
            return

        # Handle disabled cells (representation items without data for this column)
        if has_data is False:  # Explicitly False means no data available
            self._paint_disabled_cell(painter, opt, index)
            return

        # Handle required columns
        if is_required:
            self._paint_required_cell(painter, opt, index)
            return

        # Default painting
        super().paint(painter, option, index)

    def _paint_expansion_indicator(self, painter, option, index):
        """Paint the expansion indicator with hover effects."""
        # Check if mouse is hovering
        if option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, self.expansion_hover_color)

        # Get the text and font
        text = index.data(Qt.DisplayRole) or ""
        font = index.data(Qt.FontRole) or option.font

        painter.save()
        painter.setFont(font)

        # Draw the expansion indicator centered
        painter.setPen(QPen(option.palette.text().color()))
        painter.drawText(option.rect, Qt.AlignCenter, text)

        painter.restore()

    def _paint_disabled_cell(self, painter, option, index):
        """Paint disabled cells with grayed out appearance."""
        # Fill background with disabled color
        painter.fillRect(option.rect, self.disabled_color)

        # Draw border
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.drawRect(option.rect.adjusted(0, 0, -1, -1))

        # Draw diagonal lines to indicate disabled state
        painter.setPen(QPen(QColor(220, 220, 220), 1, Qt.SolidLine))

        # Draw diagonal pattern
        for i in range(0, option.rect.width() + option.rect.height(), 8):
            start_x = option.rect.left() + i
            start_y = option.rect.top()
            end_x = option.rect.left()
            end_y = option.rect.top() + i

            if start_x > option.rect.right():
                start_x = option.rect.right()
                start_y = option.rect.top() + (i - option.rect.width())

            if end_y > option.rect.bottom():
                end_y = option.rect.bottom()
                end_x = option.rect.left() + (i - option.rect.height())

            painter.drawLine(start_x, start_y, end_x, end_y)

    def _paint_required_cell(self, painter, option, index):
        """Paint required cells with highlighted background."""
        # Create modified option for required cells
        opt = QStyleOptionViewItem(option)

        # Set background color for required fields
        painter.fillRect(opt.rect, self.required_color)

        # Draw a subtle border to indicate required status
        painter.setPen(QPen(QColor(255, 215, 0), 1))  # Gold border
        painter.drawRect(opt.rect.adjusted(0, 0, -1, -1))

        # Get display text
        text = index.data(Qt.DisplayRole) or ""

        # Draw the text
        painter.save()
        painter.setPen(opt.palette.text().color())
        font = opt.font

        # Make required column headers bold
        if text and text.startswith("<") and text.endswith(">"):
            font.setBold(True)

        painter.setFont(font)

        # Calculate text rectangle with padding
        text_rect = opt.rect.adjusted(4, 2, -4, -2)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        painter.restore()

    def createEditor(self, parent, option, index):
        """Create appropriate editor for the cell."""
        if not index.isValid():
            return None

        # Don't create editors for expansion indicators
        if index.column() == 0 and index.data(Qt.DisplayRole) in ["▶", "▼"]:
            return None

        # Don't create editors for disabled cells
        has_data = index.data(Qt.UserRole + 2)
        if has_data is False:
            return None

        # Use default editor for other cells
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """Set data in the editor from the model."""
        if not index.isValid() or not editor:
            return

        # Get the raw value for editing
        value = index.data(Qt.UserRole)  # Raw value
        if value is None:
            value = index.data(Qt.DisplayRole)  # Fallback to display value

        # Set editor data based on editor type
        if hasattr(editor, "setText"):
            editor.setText(str(value) if value is not None else "")
        elif hasattr(editor, "setValue"):
            try:
                if isinstance(value, (int, float)):
                    editor.setValue(value)
                else:
                    editor.setValue(float(value) if value else 0)
            except (ValueError, TypeError):
                editor.setValue(0)
        elif hasattr(editor, "setChecked"):
            if isinstance(value, bool):
                editor.setChecked(value)
            else:
                editor.setChecked(
                    str(value).lower() in ["true", "1", "yes", "on"]
                )

    def setModelData(self, editor, model, index):
        """Set data in the model from the editor."""
        if not index.isValid() or not editor:
            return

        # Get data from editor based on its type
        value = None
        if hasattr(editor, "text"):
            value = editor.text()
        elif hasattr(editor, "value"):
            value = editor.value()
        elif hasattr(editor, "isChecked"):
            value = editor.isChecked()

        if value is not None:
            model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """Update the geometry of the editor."""
        if editor:
            editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        """Return size hint for the item."""
        if not index.isValid():
            return super().sizeHint(option, index)

        # Get default size hint
        size = super().sizeHint(option, index)

        # Ensure minimum height for better readability
        min_height = 24
        if size.height() < min_height:
            size.setHeight(min_height)

        # Special handling for expansion indicator
        if index.column() == 0 and index.data(Qt.DisplayRole) in ["▶", "▼"]:
            size.setWidth(30)  # Fixed width for expansion column

        return size

    def editorEvent(self, event, model, option, index):
        """Handle editor events, particularly for expansion indicators."""
        if not index.isValid():
            return False

        # Handle clicks on expansion indicators
        if (
            index.column() == 0
            and index.data(Qt.DisplayRole) in ["▶", "▼"]
            and hasattr(model, "toggle_expansion")
        ):
            from qtpy.QtCore import QEvent
            from qtpy.QtGui import QMouseEvent

            if (
                event.type() == QEvent.MouseButtonPress
                and isinstance(event, QMouseEvent)
                and event.button() == Qt.LeftButton
            ):
                # Toggle expansion
                model.toggle_expansion(index.row())
                return True

        return super().editorEvent(event, model, option, index)


class HeaderDelegate(QStyledItemDelegate):
    """Custom delegate for table headers to highlight required columns."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.required_color = QColor(
            255, 248, 220
        )  # Light yellow for required columns

    def paint(self, painter, option, index):
        """Custom paint for headers with required column highlighting."""
        if not index.isValid():
            return super().paint(painter, option, index)

        # Check if this is a required column
        is_required = False
        header_text = index.data(Qt.DisplayRole) or ""

        # Check using custom role
        is_required_role = index.data(Qt.UserRole + 1)
        if is_required_role is not None:
            is_required = is_required_role
        else:
            # Fallback: check if text has < > markers
            is_required = header_text.startswith("<") and header_text.endswith(
                ">"
            )

        if is_required:
            # Create modified option
            opt = QStyleOptionViewItem(option)

            # Fill background with required color
            painter.fillRect(opt.rect, self.required_color)

            # Draw text with bold font
            painter.save()
            font = opt.font
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(opt.palette.text().color())

            # Add padding and draw text
            text_rect = opt.rect.adjusted(4, 2, -4, -2)
            painter.drawText(
                text_rect, Qt.AlignLeft | Qt.AlignVCenter, header_text
            )

            painter.restore()
        else:
            # Use default painting
            super().paint(painter, option, index)
