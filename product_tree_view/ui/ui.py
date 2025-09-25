"""
Main UI module for product tree view application.
Handles window setup and component integration.
"""

from qtpy.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStatusBar,
    QSplitter,
)
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QIcon

from .model import ProductTreeModel
from .view import ProductTreeView
from .delegate import ProductTreeDelegate
from .styles import load_styles, apply_styles_to_app, get_tree_view_styles


class ProductTreeMainWindow(QMainWindow):
    """Main window for product tree view application."""

    def __init__(self, controller, parent=None):
        """Initialize main window with data controller."""
        super().__init__(parent)
        self.controller = controller

        # Initialize components
        self.model = None
        self.tree_view = None
        self.delegate = None

        # Setup UI
        self._setup_window()
        self._setup_central_widget()
        self._setup_tree_view()
        self._setup_toolbar()
        self._setup_status_bar()
        self._apply_styles()

        # Load data
        self._load_data()

    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("Product Tree View - QTPY Testing")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Center window on screen
        self._center_window()

    def _center_window(self):
        """Center window on screen."""
        from qtpy.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def _setup_central_widget(self):
        """Setup central widget with layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create splitter for potential future panels
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Tree view container
        self.tree_container = QWidget()
        tree_layout = QVBoxLayout(self.tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(5)

        self.main_splitter.addWidget(self.tree_container)

    def _setup_tree_view(self):
        """Setup tree view with model and delegate."""
        # Create model
        self.model = ProductTreeModel(self.controller)

        # Create tree view
        self.tree_view = ProductTreeView()
        self.tree_view.setModel(self.model)

        # Create and set delegate
        self.delegate = ProductTreeDelegate(self.controller)
        self.tree_view.setItemDelegate(self.delegate)

        # Add to layout
        tree_layout = self.tree_container.layout()
        tree_layout.addWidget(self.tree_view)

    def _setup_toolbar(self):
        """Setup toolbar with control buttons."""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        # Control buttons
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self._expand_all_products)

        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self._collapse_all_products)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_data)

        # Info label
        self.info_label = QLabel()
        self._update_info_label()

        # Add to toolbar
        toolbar_layout.addWidget(self.expand_all_btn)
        toolbar_layout.addWidget(self.collapse_all_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.info_label)

        # Add toolbar to tree container
        tree_layout = self.tree_container.layout()
        tree_layout.insertWidget(0, toolbar_widget)

    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _apply_styles(self):
        """Apply styles to the application."""
        # Load and apply global styles
        style_manager = load_styles()
        style_manager.apply_to_application(self.parent() or self)

        # Apply specific tree view styles
        if self.tree_view:
            tree_styles = get_tree_view_styles()
            self.tree_view.setStyleSheet(tree_styles)

    def _load_data(self):
        """Load data from controller."""
        try:
            self.controller.load_data()
            self._update_info_label()
            self.status_bar.showMessage("Data loaded successfully")
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            self.status_bar.showMessage(error_msg)
            print(error_msg)

    def _update_info_label(self):
        """Update info label with data statistics."""
        if not self.controller._data:
            self.info_label.setText("No data loaded")
            return

        summary = self.controller.get_data_summary()
        info_text = (
            f"Products: {summary.get('product_count', 0)} | "
            f"Representations: {summary.get('representation_count', 0)}"
        )
        self.info_label.setText(info_text)

    def _expand_all_products(self):
        """Expand all product items."""
        if self.tree_view:
            self.tree_view.expand_all_products()
            self.status_bar.showMessage("All products expanded")

    def _collapse_all_products(self):
        """Collapse all product items."""
        if self.tree_view:
            self.tree_view.collapse_all_products()
            self.status_bar.showMessage("All products collapsed")

    def _refresh_data(self):
        """Refresh data from file."""
        try:
            # Reload data
            self.controller.load_data()

            # Recreate model
            old_model = self.model
            self.model = ProductTreeModel(self.controller)
            self.tree_view.setModel(self.model)

            # Clean up old model
            if old_model:
                old_model.deleteLater()

            # Update UI
            self._update_info_label()
            self.status_bar.showMessage("Data refreshed successfully")

        except Exception as e:
            error_msg = f"Error refreshing data: {str(e)}"
            self.status_bar.showMessage(error_msg)
            print(error_msg)

    def get_tree_view(self):
        """Get tree view widget."""
        return self.tree_view

    def get_model(self):
        """Get tree model."""
        return self.model

    def get_controller(self):
        """Get data controller."""
        return self.controller

    def closeEvent(self, event):
        """Handle window close event."""
        self.status_bar.showMessage("Closing application...")
        event.accept()


def create_main_window(controller):
    """Factory function to create main window."""
    return ProductTreeMainWindow(controller)
