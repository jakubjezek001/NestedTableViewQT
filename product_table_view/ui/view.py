from qtpy.QtWidgets import (
    QTableView,
    QHeaderView,
    QAbstractItemView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QFrame,
)
from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QFont, QPalette, QColor
from ui.delegate import NestedTableDelegate, HeaderDelegate


class NestedTableView(QTableView):
    """Custom table view for displaying nested ProductItem and RepresentationItem data."""

    # Signals
    expansionChanged = Signal(int, bool)  # row, is_expanded
    itemSelected = Signal(
        int, int
    )  # product_index, repr_index (-1 for product)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the table view
        self._setup_view()

        # Set custom delegate
        self.delegate = NestedTableDelegate(self)
        self.setItemDelegate(self.delegate)

        # Set up headers
        self._setup_headers()

        # Track selection state
        self.current_product_index = -1
        self.current_repr_index = -1

        # Timer for delayed resize
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_resize_columns)

    def _setup_view(self):
        """Set up basic table view properties."""
        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Grid and appearance
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        self.setAlternatingRowColors(True)

        # Enable sorting
        self.setSortingEnabled(False)  # Disable for nested structure

        # Scroll behavior
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Enable word wrap for better content display
        self.setWordWrap(True)

        # Set minimum row height
        self.verticalHeader().setDefaultSectionSize(28)

        # Selection signals will be connected when model is set

    def _setup_headers(self):
        """Set up table headers."""
        # Horizontal header
        h_header = self.horizontalHeader()
        h_header.setSectionsMovable(True)
        h_header.setSectionsClickable(True)
        h_header.setHighlightSections(True)
        h_header.setStretchLastSection(False)
        h_header.setSectionResizeMode(QHeaderView.Interactive)

        # Set custom delegate for header
        self.header_delegate = HeaderDelegate(self)

        # Vertical header
        v_header = self.verticalHeader()
        v_header.setSectionsClickable(True)
        v_header.setHighlightSections(True)
        v_header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def setModel(self, model):
        """Set the model and connect signals."""
        if self.model():
            # Disconnect from old model
            try:
                self.model().expansionChanged.disconnect()
            except:
                pass
            # Disconnect from old selection model
            try:
                self.selectionModel().selectionChanged.disconnect(
                    self._on_selection_changed
                )
            except:
                pass

        super().setModel(model)

        if model:
            # Connect to expansion signals
            if hasattr(model, "expansionChanged"):
                model.expansionChanged.connect(self._on_expansion_changed)

            # Connect to model reset for column resizing
            model.modelReset.connect(self._on_model_reset)

            # Connect selection signals now that model is set
            if self.selectionModel():
                self.selectionModel().selectionChanged.connect(
                    self._on_selection_changed
                )

            # Initial column setup
            self._setup_columns()

    def _setup_columns(self):
        """Set up column widths and properties."""
        if not self.model():
            return

        # Set enabled checkbox column width (column 0)
        if self.model().columnCount() > 0:
            self.setColumnWidth(0, 80)
            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)

        # Set expansion indicator column width (column 1)
        if self.model().columnCount() > 1:
            self.setColumnWidth(1, 30)
            self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)

        # Make all other columns resizable
        for col in range(2, self.model().columnCount()):
            self.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.Interactive
            )

        # Auto-resize other columns initially
        self._resize_timer.start(100)  # Delayed resize

    def _delayed_resize_columns(self):
        """Resize columns with delay to avoid performance issues."""
        if not self.model():
            return

        # Skip enabled checkbox (column 0) and expansion indicator (column 1)
        for col in range(2, self.model().columnCount()):
            self.resizeColumnToContents(col)

            # Set minimum and maximum widths for better UX
            current_width = self.columnWidth(col)
            min_width = max(100, current_width)  # Minimum 100px
            max_width = min(
                300, current_width * 1.2
            )  # Maximum 300px or 120% of content

            if current_width < min_width:
                self.setColumnWidth(col, min_width)
            elif current_width > max_width:
                self.setColumnWidth(col, max_width)

    def _on_model_reset(self):
        """Handle model reset."""
        self._setup_columns()

    def _on_expansion_changed(self, product_row, expanded):
        """Handle expansion state changes."""
        self.expansionChanged.emit(product_row, expanded)

        # Adjust row heights after expansion
        QTimer.singleShot(50, self._adjust_row_heights)

    def _adjust_row_heights(self):
        """Adjust row heights based on content."""
        if not self.model():
            return

        for row in range(self.model().rowCount()):
            self.resizeRowToContents(row)

    def _on_selection_changed(self, selected, deselected):
        """Handle selection changes."""
        if not selected.indexes():
            return

        index = selected.indexes()[0]
        self._update_current_selection(index.row())

    def _update_current_selection(self, row):
        """Update current selection tracking."""
        if not self.model() or not hasattr(self.model(), "row_mapping"):
            return

        if row >= len(self.model().row_mapping):
            return

        model_type, model_index, source_row = self.model().row_mapping[row]

        if model_type == "product":
            self.current_product_index = model_index
            self.current_repr_index = -1
            self.itemSelected.emit(model_index, -1)
        elif model_type == "representation":
            self.current_product_index = model_index
            self.current_repr_index = source_row
            self.itemSelected.emit(model_index, source_row)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events for expansion."""
        index = self.indexAt(event.pos())
        if index.isValid():
            # Handle expansion toggle on double-click for any cell in a product row
            if hasattr(self.model(), "row_mapping") and index.row() < len(
                self.model().row_mapping
            ):
                model_type, model_index, source_row = self.model().row_mapping[
                    index.row()
                ]
                # TODO: this will need to be reimplemented but now it blocks editing
                # if model_type == "product":
                #     if hasattr(self.model(), "toggle_expansion"):
                #         self.model().toggle_expansion(index.row())
                #         return

        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space]:
            # Toggle expansion on Enter/Space for product rows
            current_index = self.currentIndex()
            if current_index.isValid():
                if hasattr(
                    self.model(), "row_mapping"
                ) and current_index.row() < len(self.model().row_mapping):
                    model_type, model_index, source_row = (
                        self.model().row_mapping[current_index.row()]
                    )
                    if model_type == "product":
                        if hasattr(self.model(), "toggle_expansion"):
                            self.model().toggle_expansion(current_index.row())
                            return

        super().keyPressEvent(event)

    def get_current_selection(self):
        """Get current selection information."""
        return self.current_product_index, self.current_repr_index

    def expand_all_products(self):
        """Expand all product items."""
        if not hasattr(self.model(), "product_model"):
            return

        product_model = self.model().product_model
        for row in range(product_model.rowCount()):
            if not product_model.is_expanded(row):
                product_model.toggle_expansion(row)

    def collapse_all_products(self):
        """Collapse all product items."""
        if not hasattr(self.model(), "product_model"):
            return

        product_model = self.model().product_model
        for row in range(product_model.rowCount()):
            if product_model.is_expanded(row):
                product_model.toggle_expansion(row)

    def refresh_view(self):
        """Refresh the entire view."""
        if self.model():
            self.model().refresh()
            self._setup_columns()


class NestedTableWidget(QWidget):
    """Main widget containing the nested table view with additional controls."""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header section
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Product Items and Representations")
        title_label.setObjectName("title-label")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Info labels
        self.info_label = QLabel("0 products loaded")
        self.info_label.setObjectName("info-label")
        header_layout.addWidget(self.info_label)

        layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Main table view
        self.table_view = NestedTableView(self)
        layout.addWidget(self.table_view, 1)  # Give it most of the space

        # Connect signals
        self.table_view.expansionChanged.connect(self._on_expansion_changed)
        self.table_view.itemSelected.connect(self._on_item_selected)

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.selection_label = QLabel("")
        self.selection_label.setObjectName("selection-label")
        status_layout.addWidget(self.selection_label)

        layout.addLayout(status_layout)

    def set_model(self, model):
        """Set the table model."""
        self.table_view.setModel(model)
        self._update_info_label()

    def _update_info_label(self):
        """Update the info label with current data count."""
        if self.controller:
            product_count = self.controller.get_product_item_count()
            total_repr = sum(
                self.controller.get_representation_item_count(i)
                for i in range(product_count)
            )
            self.info_label.setText(
                f"{product_count} products, {total_repr} representations"
            )

    def _on_expansion_changed(self, product_row, expanded):
        """Handle expansion changes."""
        state = "expanded" if expanded else "collapsed"
        self.status_label.setText(f"Product {product_row + 1} {state}")

    def _on_item_selected(self, product_index, repr_index):
        """Handle item selection."""
        if repr_index == -1:
            self.selection_label.setText(
                f"Selected: Product {product_index + 1}"
            )
        else:
            self.selection_label.setText(
                f"Selected: Product {product_index + 1} > Representation {repr_index + 1}"
            )

    def refresh(self):
        """Refresh the widget."""
        self.table_view.refresh_view()
        self._update_info_label()
