from qtpy.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from qtpy.QtGui import QFont
from typing import Any, List, Optional, Union


class ProductItemsTableModel(QAbstractTableModel):
    """Table model for ProductItems with support for expandable rows."""

    # Signal emitted when expansion state changes
    expansionChanged = Signal(int, bool)  # row, is_expanded

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.expanded_rows = set()  # Track which product rows are expanded
        self._columns = []
        self._refresh_columns()

    def _refresh_columns(self):
        """Refresh the column list from controller."""
        self._columns = self.controller.get_product_columns()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self.controller.get_product_item_count()

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._columns) + 1  # +1 for expansion indicator column

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # First column is expansion indicator
            if col == 0:
                if role == Qt.DisplayRole:
                    return "▼" if row in self.expanded_rows else "▶"
                return None

            # Get product data
            column_name = self._columns[col - 1]
            product_data = self.controller.get_product_data_for_row(row)
            value = product_data.get(column_name, None)

            if value is None:
                return "" if role == Qt.DisplayRole else None

            return str(value)

        elif role == Qt.FontRole:
            if col == 0:  # Expansion indicator column
                font = QFont()
                font.setPointSize(12)
                return font

        elif role == Qt.TextAlignmentRole:
            if col == 0:  # Center align expansion indicator
                return Qt.AlignCenter

        elif role == Qt.UserRole:
            # Return the raw value for editing
            if col == 0:
                return None
            column_name = self._columns[col - 1]
            product_data = self.controller.get_product_data_for_row(row)
            return product_data.get(column_name, None)

        elif role == Qt.UserRole + 1:  # Custom role for required status
            if col == 0:
                return False
            column_name = self._columns[col - 1]
            return self.controller.is_required_column(column_name)

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        # Can't edit expansion indicator
        if col == 0:
            return False

        column_name = self._columns[col - 1]
        success = self.controller.update_product_data(row, column_name, value)

        if success:
            self.dataChanged.emit(index, index, [role])

        return success

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # Expansion indicator column is not editable
        if index.column() == 0:
            return flags

        flags |= Qt.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return ""  # Empty header for expansion column
                elif section <= len(self._columns):
                    return self._columns[section - 1]
            elif orientation == Qt.Vertical:
                return str(section + 1)

        elif role == Qt.UserRole + 1:  # Custom role for required status
            if orientation == Qt.Horizontal and section > 0:
                if section <= len(self._columns):
                    column_name = self._columns[section - 1]
                    return self.controller.is_required_column(column_name)

        return None

    def toggle_expansion(self, row):
        """Toggle expansion state of a row."""
        if row in self.expanded_rows:
            self.expanded_rows.remove(row)
            expanded = False
        else:
            self.expanded_rows.add(row)
            expanded = True

        # Update the expansion indicator
        index = self.createIndex(row, 0)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

        # Emit signal for view to handle
        self.expansionChanged.emit(row, expanded)

        return expanded

    def is_expanded(self, row):
        """Check if a row is expanded."""
        return row in self.expanded_rows

    def refresh(self):
        """Refresh the model data."""
        self.beginResetModel()
        self._refresh_columns()
        self.expanded_rows.clear()
        self.endResetModel()


class RepresentationItemsTableModel(QAbstractTableModel):
    """Table model for RepresentationItems within a ProductItem."""

    def __init__(self, controller, product_index, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.product_index = product_index
        self._columns = []
        self._refresh_columns()

    def _refresh_columns(self):
        """Refresh the column list from controller."""
        self._columns = self.controller.get_representation_columns()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self.controller.get_representation_item_count(
            self.product_index
        )

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            column_name = self._columns[col]
            repr_data = self.controller.get_representation_data_for_row(
                self.product_index, row
            )
            value = repr_data.get(column_name, None)

            if value is None:
                return "" if role == Qt.DisplayRole else None

            return str(value)

        elif role == Qt.UserRole:
            # Return the raw value for editing
            column_name = self._columns[col]
            repr_data = self.controller.get_representation_data_for_row(
                self.product_index, row
            )
            return repr_data.get(column_name, None)

        elif role == Qt.UserRole + 1:  # Custom role for required status
            column_name = self._columns[col]
            return self.controller.is_required_column(column_name)

        elif role == Qt.UserRole + 2:  # Custom role for data availability
            column_name = self._columns[col]
            return self.controller.has_data_for_column(
                self.product_index, row, column_name
            )

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        column_name = self._columns[col]

        # Check if this item should have data for this column
        if not self.controller.has_data_for_column(
            self.product_index, row, column_name
        ):
            return False  # Don't allow editing cells that shouldn't have data

        success = self.controller.update_representation_data(
            self.product_index, row, column_name, value
        )

        if success:
            self.dataChanged.emit(index, index, [role])

        return success

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        row = index.row()
        col = index.column()
        column_name = self._columns[col]

        # Only allow editing if this representation item has data for this column
        if self.controller.has_data_for_column(
            self.product_index, row, column_name
        ):
            flags |= Qt.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and section < len(self._columns):
                return self._columns[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)

        elif role == Qt.UserRole + 1:  # Custom role for required status
            if orientation == Qt.Horizontal and section < len(self._columns):
                column_name = self._columns[section]
                return self.controller.is_required_column(column_name)

        return None

    def refresh(self):
        """Refresh the model data."""
        self.beginResetModel()
        self._refresh_columns()
        self.endResetModel()

    def set_product_index(self, product_index):
        """Update the product index this model represents."""
        self.beginResetModel()
        self.product_index = product_index
        self.endResetModel()


class NestedTableProxyModel(QAbstractTableModel):
    """Proxy model that combines ProductItems and RepresentationItems for nested display."""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.product_model = ProductItemsTableModel(controller, self)

        # Connect to product model signals
        self.product_model.expansionChanged.connect(self._on_expansion_changed)
        self.product_model.dataChanged.connect(self._on_product_data_changed)

        # Track representation models
        self.representation_models = {}

        self._build_row_mapping()

    def _build_row_mapping(self):
        """Build mapping between proxy rows and source models."""
        self.row_mapping = []  # List of (model_type, model_index, source_row)

        for product_row in range(self.product_model.rowCount()):
            # Add product row
            self.row_mapping.append(("product", product_row, 0))

            # Add representation rows if expanded
            if self.product_model.is_expanded(product_row):
                if product_row not in self.representation_models:
                    self.representation_models[product_row] = (
                        RepresentationItemsTableModel(
                            self.controller, product_row, self
                        )
                    )

                # Add header row for representation items
                self.row_mapping.append(("repr_header", product_row, 0))

                repr_model = self.representation_models[product_row]
                for repr_row in range(repr_model.rowCount()):
                    self.row_mapping.append(
                        ("representation", product_row, repr_row)
                    )

    def _on_expansion_changed(self, product_row, expanded):
        """Handle expansion state changes."""
        self.beginResetModel()
        self._build_row_mapping()
        self.endResetModel()

    def _on_product_data_changed(self, top_left, bottom_right, roles):
        """Handle product model data changes."""
        # Find corresponding proxy rows and emit dataChanged
        product_row = top_left.row()
        proxy_row = None

        for i, (model_type, model_index, source_row) in enumerate(
            self.row_mapping
        ):
            if model_type == "product" and model_index == product_row:
                proxy_row = i
                break

        if proxy_row is not None:
            proxy_index = self.createIndex(proxy_row, top_left.column())
            self.dataChanged.emit(proxy_index, proxy_index, roles)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.row_mapping)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        # Use the maximum columns from both models
        product_cols = self.product_model.columnCount()
        repr_cols = (
            len(self.controller.get_representation_columns())
            if hasattr(self.controller, "get_representation_columns")
            else 0
        )
        return max(product_cols, repr_cols)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.row_mapping):
            return None

        model_type, model_index, source_row = self.row_mapping[index.row()]

        if model_type == "product":
            source_index = self.product_model.createIndex(
                model_index, index.column()
            )
            return self.product_model.data(source_index, role)

        elif model_type == "repr_header":
            # Handle representation header row
            if role == Qt.DisplayRole:
                if index.column() == 0:
                    return "RepresentationItems"
                elif index.column() <= len(
                    self.controller.get_representation_columns()
                ):
                    repr_cols = self.controller.get_representation_columns()
                    col_index = index.column() - 1
                    if col_index < len(repr_cols):
                        return repr_cols[col_index]
            elif role == Qt.FontRole:
                from qtpy.QtGui import QFont

                font = QFont()
                font.setBold(True)
                font.setItalic(True)
                return font
            elif role == Qt.UserRole + 1:  # Required column check
                if index.column() > 0:
                    repr_cols = self.controller.get_representation_columns()
                    col_index = index.column() - 1
                    if col_index < len(repr_cols):
                        return self.controller.is_required_column(
                            repr_cols[col_index]
                        )
            return None

        elif model_type == "representation":
            if model_index in self.representation_models:
                repr_model = self.representation_models[model_index]
                # Skip the first column (expansion indicator) for representation data
                repr_col = index.column() - 1
                if repr_col >= 0 and repr_col < repr_model.columnCount():
                    source_index = repr_model.createIndex(source_row, repr_col)
                    return repr_model.data(source_index, role)

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or index.row() >= len(self.row_mapping):
            return False

        model_type, model_index, source_row = self.row_mapping[index.row()]

        if model_type == "product":
            source_index = self.product_model.createIndex(
                model_index, index.column()
            )
            return self.product_model.setData(source_index, value, role)

        elif model_type == "repr_header":
            # Header rows are not editable
            return False

        elif model_type == "representation":
            if model_index in self.representation_models:
                repr_model = self.representation_models[model_index]
                # Skip the first column (expansion indicator) for representation data
                repr_col = index.column() - 1
                if repr_col >= 0 and repr_col < repr_model.columnCount():
                    source_index = repr_model.createIndex(source_row, repr_col)
                    return repr_model.setData(source_index, value, role)

        return False

    def flags(self, index):
        if not index.isValid() or index.row() >= len(self.row_mapping):
            return Qt.NoItemFlags

        model_type, model_index, source_row = self.row_mapping[index.row()]

        if model_type == "product":
            source_index = self.product_model.createIndex(
                model_index, index.column()
            )
            return self.product_model.flags(source_index)

        elif model_type == "repr_header":
            # Header rows are selectable but not editable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        elif model_type == "representation":
            if model_index in self.representation_models:
                repr_model = self.representation_models[model_index]
                # Skip the first column (expansion indicator) for representation data
                repr_col = index.column() - 1
                if repr_col >= 0 and repr_col < repr_model.columnCount():
                    source_index = repr_model.createIndex(source_row, repr_col)
                    return repr_model.flags(source_index)

        return Qt.NoItemFlags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            # Try to get header from product model first
            product_header = self.product_model.headerData(
                section, orientation, role
            )
            if product_header and section < self.product_model.columnCount():
                return product_header

            # If not available, try representation columns
            repr_cols = self.controller.get_representation_columns()
            if section < len(repr_cols):
                return repr_cols[section]

        return None

    def refresh(self):
        """Refresh all models."""
        self.beginResetModel()
        self.product_model.refresh()
        for repr_model in self.representation_models.values():
            repr_model.refresh()
        self._build_row_mapping()
        self.endResetModel()

    def toggle_expansion(self, row):
        """Toggle expansion at a specific proxy row."""
        if row >= len(self.row_mapping):
            return False

        model_type, model_index, source_row = self.row_mapping[row]
        if model_type == "product":
            return self.product_model.toggle_expansion(model_index)

        return False
