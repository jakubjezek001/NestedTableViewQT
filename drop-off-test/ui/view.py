"""Main view component with table and drop areas."""

import ast
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QTextEdit,
    QLabel,
    QPushButton,
    QSplitter,
)
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtGui import QFont, QPainter, QPixmap, QDrag


class DragTableView(QTableView):
    """Custom table view with drag preview support."""

    def startDrag(self, supportedActions):
        """Override startDrag to create custom drag pixmap."""
        indexes = self.selectedIndexes()
        if not indexes:
            return

        # Create drag pixmap showing selected rows count
        selected_rows = set(idx.row() for idx in indexes)
        pixmap = QPixmap(200, 30)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setOpacity(0.5)
        painter.fillRect(pixmap.rect(), Qt.darkGray)
        painter.setOpacity(1.0)
        painter.setPen(Qt.white)
        painter.drawText(
            pixmap.rect(), Qt.AlignCenter, f"{len(selected_rows)} item(s)"
        )
        painter.end()

        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(self.model().mimeData(indexes))
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        drag.exec_(supportedActions)


class DropZone(QPushButton):
    """Drop zone widget for receiving dragged items."""

    item_dropped = Signal(list, str)
    item_clicked = Signal(str)

    def __init__(self, title: str, action_name: str, parent=None):
        """Initialize drop zone.

        Args:
            title: Display title for the zone
            action_name: Action identifier
            parent: Parent widget
        """
        super().__init__(title, parent)
        self.title = title
        self.action_name = action_name
        self.setup_ui()

    def setup_ui(self):
        """Setup drop zone UI."""
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setObjectName("dropZone")
        font = QFont()
        font.setBold(True)
        self.setFont(font)
        self.clicked.connect(lambda: self.item_clicked.emit(self.action_name))

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasFormat("application/x-item-data"):
            event.acceptProposedAction()
            self.setStyleSheet("background-color: rgba(100, 150, 200, 50);")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.setStyleSheet("")

    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasFormat("application/x-item-data"):
            data = event.mimeData().data("application/x-item-data")
            try:
                items = ast.literal_eval(data.data().decode())
                self.item_dropped.emit(items, self.action_name)
                event.acceptProposedAction()
            except Exception as e:
                print(f"Error processing dropped data: {e}")
                event.ignore()
        else:
            event.ignore()

        self.setStyleSheet("")


class MainView(QWidget):
    """Main view component containing table and drop areas."""

    def __init__(self, model, delegate, controller, parent=None):
        """Initialize main view.

        Args:
            model: Table model
            delegate: Table delegate
            controller: Data controller
            parent: Parent widget
        """
        super().__init__(parent)
        self.model = model
        self.delegate = delegate
        self.controller = controller
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup main UI layout."""
        main_layout = QVBoxLayout(self)

        # Create main splitter
        splitter = QSplitter(Qt.Vertical)

        # Top section with table and drop zones
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)

        # Left side - Table view
        self.table_view = DragTableView()
        self.table_view.setModel(self.model)
        self.table_view.setItemDelegate(self.delegate)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)
        self.table_view.setDragEnabled(True)
        self.table_view.setDefaultDropAction(Qt.CopyAction)
        self.table_view.resizeColumnsToContents()

        top_layout.addWidget(self.table_view, 2)

        # Right side - Drop zones
        drop_zones_layout = QVBoxLayout()

        # First drop zone
        self.viewer_zone = DropZone("Loading to Viewer", "load_viewer")
        drop_zones_layout.addWidget(self.viewer_zone)

        # Second drop zone
        self.timeline_zone = DropZone("Adding to Timeline", "add_timeline")
        drop_zones_layout.addWidget(self.timeline_zone)

        drop_zones_widget = QWidget()
        drop_zones_widget.setLayout(drop_zones_layout)
        drop_zones_widget.setMinimumWidth(200)

        top_layout.addWidget(drop_zones_widget, 1)

        splitter.addWidget(top_widget)

        # Bottom section - Output area
        output_label = QLabel("Output:")
        output_label.setObjectName("outputLabel")

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMaximumHeight(150)
        self.output_area.setPlaceholderText("Drop actions will appear here...")

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addWidget(output_label)
        bottom_layout.addWidget(self.output_area)

        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 150])

        main_layout.addWidget(splitter)

    def connect_signals(self):
        """Connect widget signals."""
        self.viewer_zone.item_dropped.connect(self.handle_item_drop)
        self.timeline_zone.item_dropped.connect(self.handle_item_drop)
        self.viewer_zone.item_clicked.connect(self.handle_button_click)
        self.timeline_zone.item_clicked.connect(self.handle_button_click)

    def handle_item_drop(self, items: list, action: str):
        """Handle item drop on drop zones.

        Args:
            items: List of dropped items
            action: Action identifier
        """
        # Clear output area before showing new results
        self.output_area.clear()

        action_names = {
            "load_viewer": "Loading to Viewer Action",
            "add_timeline": "Adding to Timeline Action",
        }

        action_title = action_names.get(action, f"{action} Action")

        for i, item in enumerate(items, 1):
            self.output_area.append(f"Item {i} ({action_title}):")
            self.output_area.append(f"  Name: {item.get('name', 'N/A')}")
            self.output_area.append(f"  Path: {item.get('file_path', 'N/A')}")
            self.output_area.append(
                f"  Product: {item.get('product_name', 'N/A')}"
            )
            self.output_area.append(
                f"  Type: {item.get('product_type', 'N/A')}"
            )
            self.output_area.append(f"  Version: {item.get('version', 'N/A')}")
            if i < len(
                items
            ):  # Add blank line between items, but not after last
                self.output_area.append("")

    def handle_button_click(self, action: str):
        """Handle button click on drop zones with selected items."""
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            return

        # Get unique rows from selected indexes
        rows = set(
            index.row() for index in selected_indexes if index.isValid()
        )
        items = []

        for row in sorted(rows):
            item = self.controller.get_item_by_index(row)
            if item:
                items.append(item)

        if items:
            self.handle_item_drop(items, action)

    def refresh_table(self):
        """Refresh table data."""
        self.model.refresh()
        self.table_view.resizeColumnsToContents()
