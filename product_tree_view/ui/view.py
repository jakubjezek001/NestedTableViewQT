"""
Custom tree view for product and representation items.
Simplified implementation focusing on core collapsible functionality.
"""

from qtpy.QtWidgets import QTreeView, QHeaderView, QAbstractItemView
from qtpy.QtCore import Qt, QModelIndex


class ProductTreeView(QTreeView):
    """Custom tree view with collapsible products."""

    def __init__(self, parent=None):
        """Initialize tree view."""
        super().__init__(parent)

        # Configure tree view behavior
        self.setExpandsOnDoubleClick(False)
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setUniformRowHeights(True)

        # Enable tree functionality
        self.setItemsExpandable(True)
        self.setIndentation(20)

        # Configure header
        header = self.header()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(120)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setMinimumSectionSize(80)
        header.setVisible(True)  # Ensure header is visible

        # Set minimum row height for better checkbox visibility and dark theme
        self.setStyleSheet("""
            QTreeView {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid #555555;
                alternate-background-color: #2e2e2e;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            QTreeView::item {
                height: 24px;
                padding: 2px;
                color: #ffffff;
            }
            QTreeView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeView::item:hover {
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QTreeView::item:selected:hover {
                background-color: #106ebe;
                color: #ffffff;
            }

            QHeaderView::section {
                background-color: #404040;
                border: 1px solid #555555;
                border-bottom: 2px solid #0078d4;
                padding: 6px 4px;
                font-weight: bold;
                font-size: 9pt;
                color: #ffffff;
            }
            QHeaderView::section:hover {
                background-color: #4a4a4a;
            }
        """)

    def setModel(self, model):
        """Set model and configure initial state."""
        super().setModel(model)

        # Products are collapsed by default - no auto-expansion
        if model:
            self._initialize_product_indicators()

    def _expand_all_products(self):
        """Expand all product items initially."""
        if not self.model():
            return

        for row in range(self.model().rowCount()):
            product_index = self.model().index(row, 0)
            if product_index.isValid():
                self.expand(product_index)

    def _initialize_product_indicators(self):
        """Initialize all product items with collapsed indicators."""
        if not self.model():
            return

        for row in range(self.model().rowCount()):
            product_index = self.model().index(row, 0)
            if product_index.isValid():
                item_type = self.model().get_item_type(product_index)
                if item_type == "product":
                    # Initialize with collapsed indicator
                    self.model().update_expand_indicator(product_index, False)

    def _update_product_expand_indicators(self):
        """Update expand/collapse indicators for product items."""
        if not self.model():
            return

        # Force a repaint to update the indicators
        self.viewport().update()

    def mousePressEvent(self, event):
        """Handle mouse press events for expand/collapse."""
        index = self.indexAt(event.pos())

        if (
            index.isValid()
            and event.button() == Qt.LeftButton
            and self.model()
        ):
            item_type = self.model().get_item_type(index)

            # Handle product expand/collapse on any click in the row
            if item_type == "product":
                # Check if this is a checkbox column - if so, don't handle expand/collapse
                column_idx = index.column()
                product_columns = self.model().controller.get_product_columns()

                if column_idx < len(product_columns):
                    column_name = product_columns[column_idx]
                    if self.model().controller.is_checkbox_column(column_name):
                        # Let the delegate handle checkbox interaction
                        super().mousePressEvent(event)
                        return

                # Check if click was in the first column (where expand icon is)
                if index.column() == 0:
                    item_rect = self.visualRect(index)
                    indent = self.indentation()

                    # If click is in the indent area or on the indicator, toggle expansion
                    # Make the first ~30 pixels of the cell clickable for expansion
                    indicator_area_width = 30
                    if event.pos().x() < item_rect.x() + indicator_area_width:
                        if self.isExpanded(index):
                            self.collapse(index)
                        else:
                            self.expand(index)
                        self._update_product_expand_indicators()
                        return

                    # For other clicks in the content area, also toggle expand state for convenience
                    if self.isExpanded(index):
                        self.collapse(index)
                    else:
                        self.expand(index)
                    self._update_product_expand_indicators()
                    return

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events - enable editing for any cell."""
        index = self.indexAt(event.pos())

        if index.isValid():
            try:
                # Check if the cell is actually editable
                if index.flags() & Qt.ItemIsEditable:
                    # Start editing on double-click for any valid cell
                    self.edit(index)
                else:
                    # If not editable, fall back to default behavior
                    super().mouseDoubleClickEvent(event)
            except Exception as e:
                print(f"Error starting edit mode: {e}")
                super().mouseDoubleClickEvent(event)
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard events for navigation and expand/collapse."""
        current_index = self.currentIndex()

        # Handle F2 key for editing
        if event.key() == Qt.Key_F2 and current_index.isValid():
            try:
                if current_index.flags() & Qt.ItemIsEditable:
                    self.edit(current_index)
                else:
                    print("Cell is not editable")
            except Exception as e:
                print(f"Error starting edit mode with F2: {e}")
            return

        if current_index.isValid() and self.model():
            item_type = self.model().get_item_type(current_index)

            if item_type == "product":
                if event.key() == Qt.Key_Left:
                    if self.isExpanded(current_index):
                        self.collapse(current_index)
                        # Indicator is updated automatically by overridden collapse method
                    else:
                        # Move to parent if already collapsed
                        super().keyPressEvent(event)
                    return
                elif event.key() == Qt.Key_Right:
                    if not self.isExpanded(current_index):
                        self.expand(current_index)
                        # Indicator is updated automatically by overridden expand method
                    else:
                        # Move to first child if already expanded
                        super().keyPressEvent(event)
                    return

        super().keyPressEvent(event)

    def expand_all_products(self):
        """Public method to expand all product items."""
        self._expand_all_products()
        self._update_product_expand_indicators()

    def collapse_all_products(self):
        """Collapse all product items."""
        if not self.model():
            return

        for row in range(self.model().rowCount()):
            product_index = self.model().index(row, 0)
            if product_index.isValid():
                self.collapse(product_index)
        self._update_product_expand_indicators()

    def expand(self, index):
        """Override expand to update indicators."""
        super().expand(index)

        # Update indicator for product items
        if self.model() and index.isValid():
            item_type = self.model().get_item_type(index)
            if item_type == "product":
                self.model().update_expand_indicator(index, True)

    def collapse(self, index):
        """Override collapse to update indicators."""
        super().collapse(index)

        # Update indicator for product items
        if self.model() and index.isValid():
            item_type = self.model().get_item_type(index)
            if item_type == "product":
                self.model().update_expand_indicator(index, False)

    def get_selected_products(self):
        """Get list of selected product indices."""
        selected_products = []

        for index in self.selectedIndexes():
            if (
                index.column() == 0 and self.model()
            ):  # Only consider first column
                item_type = self.model().get_item_type(index)
                if item_type == "product":
                    selected_products.append(index)

        return selected_products

    def get_selected_representations(self):
        """Get list of selected representation indices."""
        selected_representations = []

        for index in self.selectedIndexes():
            if (
                index.column() == 0 and self.model()
            ):  # Only consider first column
                item_type = self.model().get_item_type(index)
                if item_type == "representation":
                    selected_representations.append(index)

        return selected_representations

    def resizeColumnsToContents(self):
        """Resize all columns to fit their contents."""
        if not self.model():
            return

        header = self.header()
        for column in range(self.model().columnCount()):
            header.resizeSection(column, header.sectionSizeHint(column))

    def sizeHint(self):
        """Provide size hint for the view."""
        size = super().sizeHint()
        size.setWidth(max(size.width(), 800))
        size.setHeight(max(size.height(), 600))
        return size
