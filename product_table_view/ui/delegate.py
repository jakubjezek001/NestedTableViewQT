from qtpy.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
    QStyleOptionButton,
)
from qtpy.QtCore import Qt, QRect
from qtpy.QtGui import QPalette, QFont, QPen, QBrush, QColor
from typing import Optional
from ui.styles import ThemeColors


class NestedTableDelegate(QStyledItemDelegate):
    """Custom delegate for nested table view with special rendering for required columns and disabled cells."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def _brighten_color(self, color, factor=0.2):
        """Brighten a color by the specified factor (0.2 = 20% brighter)."""
        if isinstance(color, QColor):
            h, s, v, a = color.getHsv()
            # Increase value (brightness) by factor, capping at 255
            v = min(255, int(v * (1 + factor)))
            brightened = QColor()
            brightened.setHsv(h, s, v, a)
            return brightened
        return color

    def _is_representation_row(self, index):
        """Check if this index represents a representation item row."""
        if not index.isValid():
            return False

        # Get the model and check if it has row_mapping
        model = index.model()
        if not hasattr(model, "row_mapping") or index.row() >= len(
            model.row_mapping
        ):
            return False

        model_type, _, _ = model.row_mapping[index.row()]
        return model_type == "representation"

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

        # Check if this is a representation row for brightness enhancement
        is_repr_row = self._is_representation_row(index)
        if is_repr_row:
            # Brighten background colors for representation rows
            bg_color = opt.palette.color(QPalette.Base)
            if opt.state & QStyle.State_Selected:
                bg_color = opt.palette.color(QPalette.Highlight)
            elif opt.features & QStyleOptionViewItem.Alternate:
                bg_color = opt.palette.color(QPalette.AlternateBase)

            brightened_bg = self._brighten_color(bg_color)
            opt.palette.setColor(QPalette.Base, brightened_bg)
            opt.palette.setColor(QPalette.AlternateBase, brightened_bg)
            if opt.state & QStyle.State_Selected:
                opt.palette.setColor(
                    QPalette.Highlight, self._brighten_color(bg_color)
                )

        # Handle enabled checkbox column (column 0)
        if index.column() == 0 and index.data(Qt.DisplayRole) in ["✓", "✗"]:
            self._paint_checkbox(painter, opt, index, is_repr_row)
            return

        # Handle expansion indicator column (column 1 for product items)
        if index.column() == 1 and index.data(Qt.DisplayRole) in ["▶", "▼"]:
            self._paint_expansion_indicator(painter, opt, index)
            return

        # Handle representation header rows
        if self._is_repr_header_row(index):
            self._paint_repr_header_cell(painter, opt, index)
            return

        # Handle disabled cells (representation items without data for this column)
        if has_data is False:  # Explicitly False means no data available
            self._paint_disabled_cell(painter, opt, index, is_repr_row)
            return

        # Handle required columns
        if is_required:
            self._paint_required_cell(painter, opt, index, is_repr_row)
            return

        # Default painting
        super().paint(painter, opt, index)

    def _paint_checkbox(self, painter, option, index, is_repr_row=False):
        """Paint the enabled checkbox using Qt's native checkbox style."""
        # Get the enabled state
        enabled = index.data(Qt.UserRole) or False

        # Apply brightness enhancement for representation rows
        if is_repr_row:
            # Brighten the background
            bg_color = option.palette.color(QPalette.Base)
            if option.state & QStyle.State_Selected:
                bg_color = option.palette.color(QPalette.Highlight)
            elif option.features & QStyleOptionViewItem.Alternate:
                bg_color = option.palette.color(QPalette.AlternateBase)

            brightened_bg = self._brighten_color(bg_color)
            painter.fillRect(option.rect, brightened_bg)

        # Create checkbox style option
        checkbox_option = QStyleOptionButton()
        checkbox_option.rect = option.rect
        checkbox_option.state = QStyle.State_Enabled

        # Set checked state
        if enabled:
            checkbox_option.state |= QStyle.State_On
        else:
            checkbox_option.state |= QStyle.State_Off

        # Set hover state
        if option.state & QStyle.State_MouseOver:
            checkbox_option.state |= QStyle.State_MouseOver

        # Set selected state
        if option.state & QStyle.State_Selected:
            checkbox_option.state |= QStyle.State_Selected

        # Calculate centered checkbox rectangle
        checkbox_size = 18
        checkbox_rect = QRect(
            option.rect.center().x() - checkbox_size // 2,
            option.rect.center().y() - checkbox_size // 2,
            checkbox_size,
            checkbox_size,
        )
        checkbox_option.rect = checkbox_rect

        # Draw the checkbox using the application style
        style = (
            option.widget.style() if option.widget else option.widget.style()
        )
        if not style:
            from qtpy.QtWidgets import QApplication

            style = QApplication.style()

        style.drawControl(
            QStyle.CE_CheckBox, checkbox_option, painter, option.widget
        )

    def _paint_expansion_indicator(self, painter, option, index):
        """Paint the expansion indicator with hover effects."""
        # Check if mouse is hovering
        if option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, ThemeColors.expansion_hover())

        # Get the text and font
        text = index.data(Qt.DisplayRole) or ""
        font = index.data(Qt.FontRole) or option.font

        painter.save()
        painter.setFont(font)

        # Draw the expansion indicator centered
        painter.setPen(QPen(option.palette.text().color()))
        painter.drawText(option.rect, Qt.AlignCenter, text)

        painter.restore()

    def _paint_disabled_cell(self, painter, option, index, is_repr_row=False):
        """Paint disabled cells with grayed out appearance."""
        # Fill background with disabled color
        disabled_bg = ThemeColors.disabled_background()
        if is_repr_row:
            disabled_bg = self._brighten_color(disabled_bg)
        painter.fillRect(option.rect, disabled_bg)

        # Draw border
        disabled_text = ThemeColors.disabled_text()
        if is_repr_row:
            disabled_text = self._brighten_color(disabled_text)
        painter.setPen(QPen(disabled_text))
        painter.drawRect(option.rect.adjusted(0, 0, -1, -1))

        # Draw diagonal lines to indicate disabled state
        painter.setPen(QPen(disabled_text, 1, Qt.SolidLine))

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

    def _paint_required_cell(self, painter, option, index, is_repr_row=False):
        """Paint required cells with yellow background."""
        # Create modified option for required cells
        opt = QStyleOptionViewItem(option)

        # Set background color for required fields
        required_bg = ThemeColors.required_background()
        if is_repr_row:
            required_bg = self._brighten_color(required_bg)
        painter.fillRect(opt.rect, required_bg)

        # Draw a subtle border to indicate required status
        required_border = ThemeColors.required_border()
        if is_repr_row:
            required_border = self._brighten_color(required_border)
        painter.setPen(QPen(required_border, 1))
        painter.drawRect(opt.rect.adjusted(0, 0, -1, -1))

        # Get display text
        text = index.data(Qt.DisplayRole) or ""

        # Draw the text
        painter.save()
        text_color = opt.palette.text().color()
        if is_repr_row:
            text_color = self._brighten_color(text_color)
        painter.setPen(text_color)
        font = opt.font

        # Make required column headers bold
        if text and text.startswith("<") and text.endswith(">"):
            font.setBold(True)

        painter.setFont(font)

        # Calculate text rectangle with padding
        text_rect = opt.rect.adjusted(4, 2, -4, -2)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        painter.restore()

    def _is_repr_header_row(self, index):
        """Check if this index represents a representation header row."""
        if not index.isValid():
            return False

        # Get the model and check if it has row_mapping
        model = index.model()
        if not hasattr(model, "row_mapping") or index.row() >= len(
            model.row_mapping
        ):
            return False

        model_type, _, _ = model.row_mapping[index.row()]
        return model_type == "repr_header"

    def _paint_repr_header_cell(self, painter, option, index):
        """Paint representation header cells with special styling."""
        # Set header background color - more prominent
        if index.column() == 0:
            # First column gets a darker header color for "RepresentationItems" label
            header_color = ThemeColors.repr_header_section_bg()
            text_color = ThemeColors.repr_header_section_text()
        else:
            header_color = ThemeColors.repr_header_column_bg()
            text_color = ThemeColors.repr_header_column_text()

        painter.fillRect(option.rect, header_color)

        # Draw stronger border
        painter.setPen(QPen(ThemeColors.repr_header_border(), 2))
        painter.drawRect(option.rect.adjusted(0, 0, -1, -1))

        # Get display text
        text = index.data(Qt.DisplayRole) or ""

        # Set font (bold and italic for headers)
        font = index.data(Qt.FontRole) or option.font
        if index.column() == 0:
            font.setPointSize(
                font.pointSize() + 1
            )  # Larger text for section header
        painter.setFont(font)

        # Check if this is a required column
        # is_required = index.data(Qt.UserRole + 1) or False
        # if is_required and text.startswith("<") and text.endswith(">"):
        #     # Draw required column background
        #     painter.fillRect(option.rect, ThemeColors.required_background())
        #     # Draw gold border for required columns
        #     painter.setPen(QPen(ThemeColors.required_border(), 2))
        #     painter.drawRect(option.rect.adjusted(0, 0, -1, -1))
        #     text_color = ThemeColors.repr_header_column_text()

        # Draw text with appropriate color
        painter.setPen(text_color)
        text_rect = option.rect.adjusted(6, 3, -6, -3)
        alignment = (
            Qt.AlignCenter
            if index.column() == 0
            else Qt.AlignLeft | Qt.AlignVCenter
        )
        painter.drawText(text_rect, alignment, text)

    def createEditor(self, parent, option, index):
        """Create appropriate editor for the cell."""
        if not index.isValid():
            return None

        # Don't create editors for checkboxes (they are handled by editorEvent)
        if index.column() == 0:
            # Check if this is a checkbox cell by checking if it has enabled data
            enabled_data = index.data(Qt.UserRole)
            if isinstance(enabled_data, bool):
                return None

        # Don't create editors for expansion indicators
        if index.column() == 1 and index.data(Qt.DisplayRole) in ["▶", "▼"]:
            return None

        # Don't create editors for representation header rows
        if self._is_repr_header_row(index):
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

        # Get original value to preserve type
        original_value = index.data(Qt.UserRole)
        if original_value is None:
            original_value = index.data(Qt.DisplayRole)

        # Get data from editor based on its type
        value = None
        if hasattr(editor, "text"):
            value = editor.text()
        elif hasattr(editor, "value"):
            value = editor.value()
        elif hasattr(editor, "isChecked"):
            value = editor.isChecked()

        if value is not None:
            # Preserve original data type
            if original_value is not None and not isinstance(
                value, type(original_value)
            ):
                try:
                    if isinstance(original_value, bool):
                        # Handle boolean conversion
                        if isinstance(value, str):
                            value = value.lower() in ["true", "1", "yes", "on"]
                        else:
                            value = bool(value)
                    elif isinstance(original_value, int):
                        # Convert to int, handling empty strings
                        value = (
                            int(float(str(value))) if str(value).strip() else 0
                        )
                    elif isinstance(original_value, float):
                        # Convert to float, handling empty strings
                        value = (
                            float(str(value)) if str(value).strip() else 0.0
                        )
                    elif isinstance(original_value, str):
                        # Keep as string
                        value = str(value)
                except (ValueError, TypeError):
                    # If conversion fails, keep original type's default
                    if isinstance(original_value, (int, float)):
                        value = type(original_value)(0)
                    elif isinstance(original_value, bool):
                        value = False
                    else:
                        value = str(value)

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

        # Special handling for enabled checkbox
        if index.column() == 0:
            # Check if this is a checkbox cell
            enabled_data = index.data(Qt.UserRole)
            if isinstance(enabled_data, bool):
                size.setWidth(80)  # Fixed width for enabled column

        # Special handling for expansion indicator
        elif index.column() == 1 and index.data(Qt.DisplayRole) in ["▶", "▼"]:
            size.setWidth(30)  # Fixed width for expansion column

        return size

    def editorEvent(self, event, model, option, index):
        """Handle editor events, particularly for expansion indicators."""
        if not index.isValid():
            return False

        # Handle clicks on enabled checkboxes
        if index.column() == 0:
            # Check if this is a checkbox cell
            enabled_data = index.data(Qt.UserRole)
            if isinstance(enabled_data, bool):
                from qtpy.QtCore import QEvent
                from qtpy.QtGui import QMouseEvent

                if (
                    event.type() == QEvent.MouseButtonPress
                    and isinstance(event, QMouseEvent)
                    and event.button() == Qt.LeftButton
                ):
                    # Toggle enabled state
                    current_value = enabled_data
                    model.setData(index, not current_value, Qt.EditRole)
                    return True

        # Handle clicks on expansion indicators
        if (
            index.column() == 1
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

            # # Fill background with required color
            # painter.fillRect(opt.rect, ThemeColors.required_background())

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
