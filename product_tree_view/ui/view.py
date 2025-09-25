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

        # Set minimum row height for better checkbox visibility
        self.setStyleSheet("""
            QTreeView::item {
                height: 24px;
                padding: 2px;
            }
            QTreeView::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeView::item:hover {
                background-color: rgba(0, 120, 212, 0.1);
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QHeaderView::section {
                background-color: #f0f0f0;  /* 10% brighter than typical background */
                border: 1px solid #cccccc;
                border-bottom: 2px solid #999999;
                padding: 6px 4px;
                font-weight: bold;
                font-size: 9pt;
                color: #333333;
            }
            QHeaderView::section:hover {
                background-color: #f5f5f5;  /* Slightly brighter on hover */
            }
        """)

    def setModel(self, model):
        """Set model and configure initial state."""
        super().setModel(model)

        if model:
            # Expand all product items by default
            self._expand_all_products()

    def _expand_all_products(self):
        """Expand all product items initially."""
        if not self.model():
            return

        for row in range(self.model().rowCount()):
            product_index = self.model().index(row, 0)
            if product_index.isValid():
                self.expand(product_index)

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
                # Check if click was in the first column (where expand icon is)
                if index.column() == 0:
                    item_rect = self.visualRect(index)
                    indent = self.indentation()

                    # If click is in the indent area, let default behavior handle it
                    if event.pos().x() < item_rect.x():
                        super().mousePressEvent(event)
                        return

                    # For clicks in the content area, toggle expand state
                    if self.isExpanded(index):
                        self.collapse(index)
                    else:
                        self.expand(index)
                    return

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events - enable editing for any cell."""
        index = self.indexAt(event.pos())

        if index.isValid():
            # Start editing on double-click for any valid cell
            self.edit(index)
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard events for navigation and expand/collapse."""
        current_index = self.currentIndex()

        # Handle F2 key for editing
        if event.key() == Qt.Key_F2 and current_index.isValid():
            self.edit(current_index)
            return

        if current_index.isValid() and self.model():
            item_type = self.model().get_item_type(current_index)

            if item_type == "product":
                if event.key() == Qt.Key_Left:
                    if self.isExpanded(current_index):
                        self.collapse(current_index)
                    else:
                        # Move to parent if already collapsed
                        super().keyPressEvent(event)
                    return
                elif event.key() == Qt.Key_Right:
                    if not self.isExpanded(current_index):
                        self.expand(current_index)
                    else:
                        # Move to first child if already expanded
                        super().keyPressEvent(event)
                    return

        super().keyPressEvent(event)

    def expand_all_products(self):
        """Public method to expand all product items."""
        self._expand_all_products()

    def collapse_all_products(self):
        """Collapse all product items."""
        if not self.model():
            return

        for row in range(self.model().rowCount()):
            product_index = self.model().index(row, 0)
            if product_index.isValid():
                self.collapse(product_index)

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
