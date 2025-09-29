"""
Tree model for hierarchical product and representation data.
Handles products as parent items with representations as children.
"""

from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
from qtpy.QtGui import QFont
from typing import Any, List, Optional, Dict


class TreeItem:
    """A single item in the tree structure."""

    def __init__(
        self,
        data: Dict[str, Any] = None,
        parent: "TreeItem" = None,
        item_type: str = "root",
    ):
        """Initialize tree item.

        Args:
            data: Item data dictionary
            parent: Parent tree item
            item_type: Type of item ('root', 'product', 'representation')
        """
        self.item_data = data or {}
        self.parent_item = parent
        self.child_items: List["TreeItem"] = []
        self.item_type = item_type

    def append_child(self, child: "TreeItem") -> None:
        """Add a child item."""
        child.parent_item = self
        self.child_items.append(child)

    def child(self, row: int) -> Optional["TreeItem"]:
        """Get child at given row."""
        if 0 <= row < len(self.child_items):
            return self.child_items[row]
        return None

    def child_count(self) -> int:
        """Get number of children."""
        return len(self.child_items)

    def row(self) -> int:
        """Get row number of this item in parent."""
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def parent(self) -> Optional["TreeItem"]:
        """Get parent item."""
        return self.parent_item

    def data(self, column_name: str) -> Any:
        """Get data for column."""
        return self.item_data.get(column_name)

    def set_data(self, column_name: str, value: Any) -> None:
        """Set data for column."""
        self.item_data[column_name] = value

    def has_data(self, column_name: str) -> bool:
        """Check if item has data for column."""
        return column_name in self.item_data


class ProductTreeModel(QAbstractItemModel):
    """Tree model for products with nested representations."""

    def __init__(self, controller, parent=None):
        """Initialize model with data controller."""
        super().__init__(parent)
        self.controller = controller
        self.root_item = TreeItem(item_type="root")
        self.product_columns = []
        self.representation_columns = []
        self._setup_model()

    def _setup_model(self) -> None:
        """Setup model data from controller."""
        if not self.controller._data:
            self.controller.load_data()

        self.product_columns = self.controller.get_product_columns()
        self.representation_columns = (
            self.controller.get_representation_columns()
        )

        # Build tree structure
        products = self.controller.get_products()
        for product_data in products:
            product_item = TreeItem(
                data=product_data["data"],
                parent=self.root_item,
                item_type="product",
            )
            self.root_item.append_child(product_item)

            # Add representation header as first child
            if product_data["representations"]:
                header_data = {col: col for col in self.representation_columns}
                print(f">> header_data: {header_data}")
                header_item = TreeItem(
                    data=header_data,
                    parent=product_item,
                    item_type="representation_header",
                )
                product_item.append_child(header_item)

            # Add representation children
            for repr_data in product_data["representations"]:
                repr_item = TreeItem(
                    data=repr_data["data"],
                    parent=product_item,
                    item_type="representation",
                )
                product_item.append_child(repr_item)

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        """Create model index for given row, column, parent."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Get parent index for given index."""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item or parent_item is None:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of rows under parent."""
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of columns."""
        # Use the maximum of product and representation columns
        return max(len(self.product_columns), len(self.representation_columns))

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Get data for index and role."""
        if not index.isValid():
            return None

        item = index.internalPointer()
        if item is None:
            return None

        column_idx = index.column()

        # Determine which column set to use based on item type
        if item.item_type == "product":
            columns = self.product_columns
        elif (
            item.item_type == "representation"
            or item.item_type == "representation_header"
        ):
            columns = self.representation_columns
        else:
            return None

        if column_idx >= len(columns):
            return None

        column_name = columns[column_idx]

        # Handle different roles
        if role == Qt.DisplayRole:
            # Add expand/collapse indicator for products in first column
            if item.item_type == "product" and column_idx == 0:
                # Get expansion state indicator (default to collapsed)
                indicator = getattr(item, "_expand_indicator", "▶")
                return indicator

            if self.controller.is_checkbox_column(column_name):
                # Show column name for representation headers even if it's a boolean column
                if item.item_type == "representation_header":
                    return column_name
                return None  # Checkboxes don't show text

            if not item.has_data(column_name):
                return None

            # Get the raw value
            raw_value = item.data(column_name)
            if raw_value is None:
                return None

            # Determine column type for proper formatting
            is_product = item.item_type == "product"
            column_type = self.controller.get_column_type(
                column_name, is_product
            )

            # Format based on data type
            if column_type == bool:
                return "True" if raw_value else "False"
            elif column_type == int:
                try:
                    return str(int(raw_value))
                except (ValueError, TypeError):
                    return str(raw_value)
            elif column_type == float:
                try:
                    # Format floats to avoid unnecessary decimal places
                    float_val = float(raw_value)
                    if float_val.is_integer():
                        return f"{float_val:.1f}"
                    else:
                        return f"{float_val:.6g}"  # Use general format, up to 6 significant digits
                except (ValueError, TypeError):
                    return str(raw_value)
            else:  # str
                return str(raw_value)

        elif role == Qt.CheckStateRole:
            if self.controller.is_checkbox_column(column_name):
                if item.has_data(column_name):
                    value = item.data(column_name)
                    return Qt.Checked if value else Qt.Unchecked
                return Qt.Unchecked

        elif role == Qt.FontRole:
            if (
                item.item_type == "product"
                or item.item_type == "representation_header"
            ):
                font = QFont()
                font.setBold(True)
                return font

        elif role == Qt.TextAlignmentRole:
            if self.controller.is_checkbox_column(column_name):
                return Qt.AlignCenter
            elif item.item_type == "representation_header":
                return Qt.AlignCenter

        elif role == Qt.ToolTipRole:
            if item.item_type == "representation_header":
                return f"Header for representation column: {column_name}"
            elif not item.has_data(column_name):
                return f"No data for '{column_name}' in this item"
            return str(item.data(column_name))

        elif role == Qt.BackgroundRole:
            if item.item_type == "representation_header":
                from qtpy.QtGui import QColor

                return QColor("#404040")  # Darker background for header

        return None

    def setData(
        self, index: QModelIndex, value: Any, role: int = Qt.EditRole
    ) -> bool:
        """Set data for index."""
        if not index.isValid():
            return False

        item = index.internalPointer()
        if item is None:
            return False

        column_idx = index.column()

        # Determine column name
        if item.item_type == "product":
            columns = self.product_columns
            is_product = True
        elif (
            item.item_type == "representation"
            or item.item_type == "representation_header"
        ):
            columns = self.representation_columns
            is_product = False
        else:
            return False

        if column_idx >= len(columns):
            return False

        column_name = columns[column_idx]

        # Don't allow editing of header rows
        if item.item_type == "representation_header":
            return False

        if role == Qt.CheckStateRole:
            if self.controller.is_checkbox_column(column_name):
                item.set_data(column_name, value == Qt.Checked)
                self.dataChanged.emit(index, index, [role])
                return True

        elif role == Qt.EditRole:
            # Get the expected data type for this column
            column_type = self.controller.get_column_type(
                column_name, is_product
            )

            # Convert value to the appropriate type
            converted_value = self.controller.convert_value_to_type(
                value, column_type
            )

            item.set_data(column_name, converted_value)
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get item flags for index."""
        if not index.isValid():
            return Qt.NoItemFlags

        item = index.internalPointer()
        if item is None:
            return Qt.NoItemFlags

        column_idx = index.column()

        # Determine column name
        if item.item_type == "product":
            columns = self.product_columns
        elif (
            item.item_type == "representation"
            or item.item_type == "representation_header"
        ):
            columns = self.representation_columns
        else:
            return Qt.NoItemFlags

        if column_idx >= len(columns):
            return Qt.NoItemFlags

        column_name = columns[column_idx]

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # Header rows are not editable but are selectable
        if item.item_type == "representation_header":
            return flags

        # Disable cell if item doesn't have data for this column
        if not item.has_data(column_name):
            # Only show as enabled if it's a representation missing data
            if item.item_type == "representation":
                return Qt.NoItemFlags

        # Make checkboxes user checkable
        if self.controller.is_checkbox_column(column_name):
            flags |= Qt.ItemIsUserCheckable
        else:
            # Make non-checkbox columns editable
            flags |= Qt.ItemIsEditable

        return flags

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        """Get header data."""
        if (
            orientation != Qt.Horizontal
            or role != Qt.DisplayRole
            or section >= self.columnCount()
        ):
            return None

        # Show product columns in header (they're typically more comprehensive)
        if section < len(self.product_columns):
            return self.product_columns[section]
        elif section < len(self.representation_columns):
            return self.representation_columns[section]

        return f"Column {section}"

    def get_item_type(self, index: QModelIndex) -> str:
        """Get type of item at index."""
        if not index.isValid():
            return "root"

        item = index.internalPointer()
        if item is None:
            return "root"

        return getattr(item, "item_type", "unknown")

    def update_expand_indicator(self, index: QModelIndex, expanded: bool):
        """Update the expand/collapse indicator for a product item."""
        if not index.isValid():
            return

        item = index.internalPointer()
        if item is None or item.item_type != "product":
            return

        # Set the indicator based on expansion state
        item._expand_indicator = "▼" if expanded else "▶"

        # Emit data changed for the first column only
        first_col_index = self.index(index.row(), 0, index.parent())
        self.dataChanged.emit(
            first_col_index, first_col_index, [Qt.DisplayRole]
        )

    def get_columns_for_item(self, index: QModelIndex) -> List[str]:
        """Get appropriate column list for item at index."""
        if not index.isValid():
            return []

        item = index.internalPointer()
        if item is None:
            return []

        item_type = getattr(item, "item_type", None)
        if item_type == "product":
            return self.product_columns
        elif item_type == "representation":
            return self.representation_columns
        return []
