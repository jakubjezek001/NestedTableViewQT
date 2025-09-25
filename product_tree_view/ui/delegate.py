"""
Custom delegate for product tree view.
Handles checkboxes and disabled cell rendering.
"""

from qtpy.QtWidgets import (
    QStyledItemDelegate,
    QCheckBox,
    QStyle,
    QStyleOptionButton,
)
from qtpy.QtCore import Qt, QRect, QEvent
from qtpy.QtGui import QPalette, QPainter


class ProductTreeDelegate(QStyledItemDelegate):
    """Custom delegate for product/representation tree view."""

    def __init__(self, controller, parent=None):
        """Initialize delegate with data controller."""
        super().__init__(parent)
        self.controller = controller

    def paint(self, painter, option, index):
        """Custom paint method for cells."""
        if not index.isValid():
            super().paint(painter, option, index)
            return

        # Get item and column info
        item = index.internalPointer()
        if item is None:
            super().paint(painter, option, index)
            return

        column_idx = index.column()

        # Determine column name based on item type
        item_type = getattr(item, "item_type", None)

        # Special painting for representation headers
        if item_type == "representation_header":
            self._paint_representation_header(painter, option, index)
            return

        if item_type == "product":
            columns = self.controller.get_product_columns()
        elif item_type == "representation":
            columns = self.controller.get_representation_columns()
        else:
            super().paint(painter, option, index)
            return

        if column_idx >= len(columns):
            super().paint(painter, option, index)
            return

        column_name = columns[column_idx]

        # Check if cell should be disabled (no data)
        has_data = item.has_data(column_name)

        # Handle checkbox columns
        if self.controller.is_checkbox_column(column_name):
            self._paint_checkbox(painter, option, index, has_data)
        else:
            # Handle regular cells
            if not has_data:
                self._paint_disabled_cell(painter, option, index)
            else:
                super().paint(painter, option, index)

    def _paint_checkbox(self, painter, option, index, has_data):
        """Paint checkbox for enabled column."""
        # Get style from various sources
        style = None
        if hasattr(option, "widget") and option.widget:
            style = option.widget.style()
        elif self.parent():
            style = self.parent().style()
        else:
            from qtpy.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                style = app.style()

        if not style:
            # Fallback: draw a simple checkbox representation
            self._paint_simple_checkbox(painter, option, index, has_data)
            return

        # Create proper QStyleOptionButton for checkbox
        checkbox_option = QStyleOptionButton()
        checkbox_option.rect = option.rect
        checkbox_option.palette = option.palette
        checkbox_option.fontMetrics = option.fontMetrics

        # Calculate checkbox size and center it
        checkbox_size = style.pixelMetric(
            QStyle.PM_IndicatorWidth, checkbox_option
        )
        checkbox_rect = QRect(
            option.rect.x() + (option.rect.width() - checkbox_size) // 2,
            option.rect.y() + (option.rect.height() - checkbox_size) // 2,
            checkbox_size,
            checkbox_size,
        )
        checkbox_option.rect = checkbox_rect

        # Set checkbox state
        checkbox_option.state = QStyle.State_Enabled

        if has_data:
            value = index.data(Qt.CheckStateRole)
            if value == Qt.Checked:
                checkbox_option.state |= QStyle.State_On
            else:
                checkbox_option.state |= QStyle.State_Off
        else:
            checkbox_option.state |= QStyle.State_Off

        # Handle disabled state
        if not has_data or not (index.flags() & Qt.ItemIsEnabled):
            checkbox_option.state &= ~QStyle.State_Enabled
            painter.save()
            painter.setOpacity(0.4)

        # Draw the checkbox
        style.drawPrimitive(
            QStyle.PE_IndicatorCheckBox, checkbox_option, painter
        )

        # Restore painter state if we modified it
        if not has_data or not (index.flags() & Qt.ItemIsEnabled):
            painter.restore()

    def _paint_simple_checkbox(self, painter, option, index, has_data):
        """Paint a simple checkbox when style is not available."""
        painter.save()

        # Calculate checkbox rect
        checkbox_size = 16
        checkbox_rect = QRect(
            option.rect.x() + (option.rect.width() - checkbox_size) // 2,
            option.rect.y() + (option.rect.height() - checkbox_size) // 2,
            checkbox_size,
            checkbox_size,
        )

        # Draw checkbox border
        painter.setPen(option.palette.color(option.palette.Text))
        painter.drawRect(checkbox_rect)

        # Fill if checked
        if has_data:
            value = index.data(Qt.CheckStateRole)
            if value == Qt.Checked:
                inner_rect = checkbox_rect.adjusted(3, 3, -3, -3)
                painter.fillRect(
                    inner_rect, option.palette.color(option.palette.Text)
                )

        # Apply disabled appearance if needed
        if not has_data or not (index.flags() & Qt.ItemIsEnabled):
            painter.setOpacity(0.4)

        painter.restore()

    def _paint_representation_header(self, painter, option, index):
        """Paint representation header row with special styling."""
        painter.save()

        # Draw header background
        from qtpy.QtGui import QColor

        header_color = QColor("#505050")

        if option.state & QStyle.State_MouseOver:
            header_color = QColor("#5a5a5a")
        elif option.state & QStyle.State_Selected:
            header_color = QColor("#606060")

        painter.fillRect(option.rect, header_color)

        # Draw border
        border_color = QColor("#666666")
        painter.setPen(border_color)
        painter.drawLine(option.rect.topLeft(), option.rect.topRight())
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        # Draw text
        text = str(index.data(Qt.DisplayRole) or "")
        painter.setPen(QColor("#ffffff"))

        # Use bold font
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        # Center the text
        text_rect = option.rect.adjusted(4, 0, -4, 0)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.AlignVCenter, text)

        painter.restore()

    def _paint_disabled_cell(self, painter, option, index):
        """Paint disabled cell for missing data."""
        painter.save()

        # Use disabled palette colors
        palette = option.palette
        disabled_color = palette.color(QPalette.Disabled, QPalette.Text)
        bg_color = palette.color(QPalette.Disabled, QPalette.Base)

        # Fill background with disabled color
        painter.fillRect(option.rect, bg_color)

        # Draw disabled text if any
        painter.setPen(disabled_color)
        painter.setOpacity(0.5)

        # Draw "N/A" or empty indicator
        text_rect = option.rect.adjusted(4, 0, -4, 0)
        painter.drawText(
            text_rect,
            Qt.AlignVCenter | Qt.AlignLeft,
            "—",  # Em dash to indicate no data
        )

        painter.restore()

    def createEditor(self, parent, option, index):
        """Create editor widget for cell."""
        if not index.isValid():
            return None

        try:
            # Get item and column info
            item = index.internalPointer()
            if item is None:
                return None

            column_idx = index.column()

            # Determine column name
            item_type = getattr(item, "item_type", None)
            if item_type == "product":
                columns = self.controller.get_product_columns()
            elif (
                item_type == "representation"
                or item_type == "representation_header"
            ):
                columns = self.controller.get_representation_columns()
            else:
                return None

            if column_idx >= len(columns):
                return None

            column_name = columns[column_idx]

            # For checkbox columns, return None (handled by paint method)
            if self.controller.is_checkbox_column(column_name):
                return None

            # Don't create editor for header rows
            if item_type == "representation_header":
                return None

            # Don't create editor for cells that shouldn't be edited
            # (e.g., representation cells that don't have data)
            if item_type == "representation" and not item.has_data(
                column_name
            ):
                return None

            # Create text editor for editable columns
            from qtpy.QtWidgets import QLineEdit

            editor = QLineEdit(parent)
            editor.setFrame(False)
            editor.selectAll()  # Select all text when editing starts
            return editor

        except Exception as e:
            # Log error and return None to prevent crashes
            print(f"Error creating editor: {e}")
            return None

    def editorEvent(self, event, model, option, index):
        """Handle editor events, particularly for checkboxes."""
        if not index.isValid():
            return False

        # Get item and column info
        item = index.internalPointer()
        if item is None:
            return False

        column_idx = index.column()

        # Determine column name
        item_type = getattr(item, "item_type", None)
        if item_type == "product":
            columns = self.controller.get_product_columns()
        elif (
            item_type == "representation"
            or item_type == "representation_header"
        ):
            columns = self.controller.get_representation_columns()
        else:
            return False

        if column_idx >= len(columns):
            return False

        column_name = columns[column_idx]

        # Don't handle events for header rows
        if item_type == "representation_header":
            return False

        # Handle checkbox clicks
        if (
            self.controller.is_checkbox_column(column_name)
            and item.has_data(column_name)
            and (index.flags() & Qt.ItemIsEnabled)
        ):
            if (
                event.type() == QEvent.MouseButtonPress
                and event.button() == Qt.LeftButton
            ):
                # Toggle checkbox state
                current_state = index.data(Qt.CheckStateRole)
                new_state = (
                    Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
                )

                return model.setData(index, new_state, Qt.CheckStateRole)

        return super().editorEvent(event, model, option, index)

    def setEditorData(self, editor, index):
        """Set the data to be displayed and edited by the editor."""
        if not index.isValid() or editor is None:
            return

        try:
            # Get the current data
            data = index.data(Qt.DisplayRole)

            from qtpy.QtWidgets import QLineEdit

            if isinstance(editor, QLineEdit):
                # Convert data to string, handle None values
                text = str(data) if data is not None else ""
                editor.setText(text)
                editor.selectAll()  # Select all text for easy replacement
        except Exception as e:
            print(f"Error setting editor data: {e}")

    def setModelData(self, editor, model, index):
        """Get data from the editor widget and store it in the specified model."""
        if not index.isValid() or editor is None or model is None:
            return

        try:
            from qtpy.QtWidgets import QLineEdit

            if isinstance(editor, QLineEdit):
                text = editor.text()
                # Only update if the text has actually changed
                current_data = index.data(Qt.DisplayRole)
                if str(current_data) != text:
                    success = model.setData(index, text, Qt.EditRole)
                    if not success:
                        print(
                            f"Failed to set data for index {index.row()}, {index.column()}"
                        )
        except Exception as e:
            print(f"Error setting model data: {e}")

    def updateEditorGeometry(self, editor, option, index):
        """Update the editor for the item specified by index according to the style option."""
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        """Provide size hint for cells."""
        if not index.isValid():
            return super().sizeHint(option, index)

        # Get default size
        size = super().sizeHint(option, index)

        # Ensure minimum height for checkboxes
        item = index.internalPointer()
        if item is None:
            return size

        column_idx = index.column()

        item_type = getattr(item, "item_type", None)
        if item_type == "product":
            columns = self.controller.get_product_columns()
        elif item_type == "representation":
            columns = self.controller.get_representation_columns()
        else:
            return size

        if column_idx < len(columns):
            column_name = columns[column_idx]
            if self.controller.is_checkbox_column(column_name):
                # Ensure checkbox has enough space
                size.setHeight(max(size.height(), 24))
                size.setWidth(max(size.width(), 60))

        return size
