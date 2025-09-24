import sys
import os
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from qtpy.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMenuBar,
    QMenu,
    QAction,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QSplitter,
    QGroupBox,
    QLabel,
)
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QKeySequence, QIcon

from ui.view import NestedTableWidget
from ui.model import NestedTableProxyModel
from controller import DataController


class MainWindow(QMainWindow):
    """Main application window for the Nested Table View."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize controller
        try:
            self.controller = DataController()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")
            self.controller = None

        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.load_styles()
        self.setup_model()

        # Auto-refresh timer
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_data)

    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(
            "Nested Table View - ProductItems & RepresentationItems"
        )
        self.setMinimumSize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Toolbar section
        toolbar_layout = QHBoxLayout()

        # Control buttons
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.setToolTip("Expand all product items")
        self.expand_all_btn.clicked.connect(self.expand_all)
        toolbar_layout.addWidget(self.expand_all_btn)

        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.setToolTip("Collapse all product items")
        self.collapse_all_btn.clicked.connect(self.collapse_all)
        toolbar_layout.addWidget(self.collapse_all_btn)

        toolbar_layout.addSpacing(20)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setToolTip("Refresh data from file")
        self.refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(self.refresh_btn)

        toolbar_layout.addSpacing(20)

        # File operations
        self.open_btn = QPushButton("Open Data File")
        self.open_btn.setToolTip("Open a different data file")
        self.open_btn.clicked.connect(self.open_data_file)
        toolbar_layout.addWidget(self.open_btn)

        self.export_btn = QPushButton("Export Data")
        self.export_btn.setToolTip("Export current data to file")
        self.export_btn.clicked.connect(self.export_data)
        toolbar_layout.addWidget(self.export_btn)

        toolbar_layout.addStretch()

        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton("Auto-refresh: Off")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.setToolTip("Toggle automatic data refresh")
        self.auto_refresh_btn.toggled.connect(self.toggle_auto_refresh)
        toolbar_layout.addWidget(self.auto_refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)

        # Table widget (main area)
        if self.controller:
            self.table_widget = NestedTableWidget(self.controller)
        else:
            # Create dummy widget if no controller
            self.table_widget = QLabel(
                "No data available - check data.json file"
            )
            self.table_widget.setAlignment(Qt.AlignCenter)

        content_splitter.addWidget(self.table_widget)

        # Info panel (optional - can be collapsed)
        info_panel = self.create_info_panel()
        content_splitter.addWidget(info_panel)

        # Set splitter proportions (info panel collapsed by default)
        content_splitter.setSizes([1000, 0])

        main_layout.addWidget(content_splitter, 1)

    def create_info_panel(self):
        """Create the information panel."""
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)

        # Data statistics
        self.stats_label = QLabel("Loading...")
        self.stats_label.setWordWrap(True)
        self.stats_label.setObjectName("stats-label")
        info_layout.addWidget(self.stats_label)

        info_layout.addSpacing(10)

        # Instructions
        instructions = QLabel("""
<b>Usage Instructions:</b><br>
• Click ▶ or double-click to expand product items<br>
• Required columns are highlighted in yellow<br>
• Disabled cells show diagonal lines<br>
• Use Ctrl+E to expand all<br>
• Use Ctrl+C to collapse all<br>
• Use F5 to refresh data
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("instructions-label")
        info_layout.addWidget(instructions)

        info_layout.addStretch()
        return info_group

    def setup_menu(self):
        """Set up the application menu."""
        menubar = self.menuBar()

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """Set up the status bar."""
        self.statusBar().showMessage("Ready")

    def setup_model(self):
        """Set up the table model."""
        if not self.controller:
            return

        try:
            # Create the nested table model
            self.model = NestedTableProxyModel(self.controller)

            # Set model to table widget
            if hasattr(self.table_widget, "set_model"):
                self.table_widget.set_model(self.model)

            self.update_stats()
            self.statusBar().showMessage("Data loaded successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to setup model: {e}")
            self.statusBar().showMessage("Failed to load data")

    def update_stats(self):
        """Update the statistics display."""
        if not self.controller:
            self.stats_label.setText("No data available")
            return

        try:
            product_count = self.controller.get_product_item_count()

            total_repr = 0
            required_cols = set()

            # Count representations and collect required columns
            for i in range(product_count):
                total_repr += self.controller.get_representation_item_count(i)

            product_cols = self.controller.get_product_columns()
            repr_cols = self.controller.get_representation_columns()

            product_required = [
                col
                for col in product_cols
                if self.controller.is_required_column(col)
            ]
            repr_required = [
                col
                for col in repr_cols
                if self.controller.is_required_column(col)
            ]

            stats_text = f"""
<b>Data Statistics:</b><br>
Products: {product_count}<br>
Representations: {total_repr}<br>
<br>
<b>Product Columns:</b> {len(product_cols)}<br>
Required: {len(product_required)}<br>
<br>
<b>Representation Columns:</b> {len(repr_cols)}<br>
Required: {len(repr_required)}<br>
            """

            self.stats_label.setText(stats_text.strip())

        except Exception as e:
            self.stats_label.setText(f"Error updating stats: {e}")

    def expand_all(self):
        """Expand all product items."""
        if hasattr(self.table_widget, "table_view"):
            self.table_widget.table_view.expand_all_products()
            self.statusBar().showMessage("All products expanded")

    def collapse_all(self):
        """Collapse all product items."""
        if hasattr(self.table_widget, "table_view"):
            self.table_widget.table_view.collapse_all_products()
            self.statusBar().showMessage("All products collapsed")

    def refresh_data(self):
        """Refresh data from the source file."""
        if not self.controller:
            return

        try:
            self.controller.load_data()

            if self.model:
                self.model.refresh()

            if hasattr(self.table_widget, "refresh"):
                self.table_widget.refresh()

            self.update_stats()
            self.statusBar().showMessage("Data refreshed successfully")

        except Exception as e:
            QMessageBox.warning(
                self, "Refresh Error", f"Failed to refresh data: {e}"
            )
            self.statusBar().showMessage("Failed to refresh data")

    def toggle_auto_refresh(self, enabled):
        """Toggle automatic data refresh."""
        if enabled:
            self.auto_refresh_timer.start(5000)  # Refresh every 5 seconds
            self.auto_refresh_btn.setText("Auto-refresh: On")
            self.statusBar().showMessage("Auto-refresh enabled")
        else:
            self.auto_refresh_timer.stop()
            self.auto_refresh_btn.setText("Auto-refresh: Off")
            self.statusBar().showMessage("Auto-refresh disabled")

    def open_data_file(self):
        """Open a different data file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                self.controller = DataController(file_path)
                self.setup_model()
                self.statusBar().showMessage(f"Loaded data from {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to load file: {e}"
                )

    def export_data(self):
        """Export current data to a file."""
        if not self.controller:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                # Save current changes first
                self.controller.save_data()

                import shutil

                shutil.copy(self.controller.data_file, file_path)
                self.statusBar().showMessage(f"Data exported to {file_path}")
                QMessageBox.information(
                    self, "Export", "Data exported successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export data: {e}"
                )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Nested Table View",
            """
<h3>Nested Table View</h3>
<p>A Qt application for displaying nested ProductItems and RepresentationItems data.</p>

<p><b>Features:</b></p>
<ul>
<li>Expandable/collapsible product rows</li>
<li>Flexible column handling</li>
<li>Required column highlighting</li>
<li>Disabled cell visualization</li>
<li>Auto-refresh capability</li>
</ul>

<p><b>Controls:</b></p>
<ul>
<li>Click ▶ or double-click to expand/collapse</li>
<li>Ctrl+E: Expand all</li>
<li>Ctrl+Shift+E: Collapse all</li>
<li>F5 or Ctrl+R: Refresh</li>
</ul>
            """,
        )

    def load_styles(self):
        """Load and apply CSS styles with color placeholder replacement."""
        css_file = Path(__file__).parent.parent / "style.css"

        if css_file.exists():
            try:
                with open(css_file, "r", encoding="utf-8") as f:
                    stylesheet = f.read()

                # Replace color placeholders with actual values
                color_map = {
                    # Primary colors
                    "{color:font}": "#E0E0E0",
                    "{color:bg}": "#2B2B2B",
                    "{color:font-disabled}": "#808080",
                    "{color:font-hover}": "#FFFFFF",
                    "{color:font-title}": "#FFFFFF",
                    "{color:font-secondary}": "#B0B0B0",
                    "{color:font-stats}": "#D0D0D0",
                    "{color:font-instructions}": "#B0B0B0",
                    "{color:font-group-title}": "#B0B0B0",
                    # Borders
                    "{color:border}": "#555555",
                    "{color:border-hover}": "#4A90E2",
                    "{color:border-focus}": "#4A90E2",
                    "{color:border-header}": "#555555",
                    "{color:border-tooltip}": "#666666",
                    "{color:border-disabled}": "#444444",
                    # Backgrounds - inputs
                    "{color:bg-inputs}": "#3A3A3A",
                    "{color:bg-inputs-disabled}": "#2B2B2B",
                    # Backgrounds - buttons
                    "{color:bg-buttons}": "#404040",
                    "{color:bg-buttons-hover}": "#4A4A4A",
                    "{color:bg-buttons-pressed}": "#3A3A3A",
                    "{color:bg-buttons-disabled}": "#2B2B2B",
                    "{color:bg-buttons-checked}": "#4A90E2",
                    "{color:bg-buttons-primary}": "#4A90E2",
                    "{color:bg-buttons-primary-hover}": "#357ABD",
                    "{color:bg-buttons-secondary}": "#4A4A4A",
                    "{color:bg-buttons-secondary-hover}": "#565656",
                    "{color:bg-buttons-file}": "#484848",
                    "{color:bg-buttons-file-hover}": "#565656",
                    "{color:bg-buttons-toggle}": "#404040",
                    "{color:bg-buttons-toggle-hover}": "#4A4A4A",
                    "{color:bg-buttons-toggle-checked}": "#4A90E2",
                    "{color:font-buttons-primary}": "#FFFFFF",
                    "{color:font-buttons-secondary}": "#E0E0E0",
                    "{color:font-buttons-file}": "#E0E0E0",
                    "{color:font-buttons-toggle}": "#E0E0E0",
                    "{color:font-buttons-toggle-checked}": "#FFFFFF",
                    # Backgrounds - views
                    "{color:bg-view}": "#353535",
                    "{color:bg-view-alternate}": "#3A3A3A",
                    "{color:bg-view-hover}": "#484848",
                    "{color:bg-view-selection}": "#4A90E2",
                    "{color:bg-view-selection-hover}": "#357ABD",
                    "{color:bg-view-disabled}": "#2B2B2B",
                    "{color:bg-view-alternate-disabled}": "#303030",
                    "{color:font-view-selection}": "#FFFFFF",
                    # Backgrounds - headers
                    "{color:bg-header}": "#404040",
                    "{color:bg-header-hover}": "#4A4A4A",
                    "{color:font-header}": "#E0E0E0",
                    # Backgrounds - other elements
                    "{color:bg-group}": "#353535",
                    "{color:bg-statusbar}": "#404040",
                    "{color:bg-menu}": "#404040",
                    "{color:bg-menu-hover}": "#4A4A4A",
                    "{color:bg-menu-pressed}": "#3A3A3A",
                    "{color:bg-menu-separator}": "#555555",
                    "{color:bg-splitter-handle}": "#555555",
                    "{color:bg-splitter-handle-hover}": "#777777",
                    "{color:bg-tooltip}": "#404040",
                    "{color:font-tooltip}": "#E0E0E0",
                    "{color:separator}": "#555555",
                    # Scroll bars
                    "{color:bg-scroll}": "#404040",
                    "{color:bg-scroll-handle}": "#707070",
                    "{color:bg-scroll-handle-hover}": "#808080",
                    # Progress bars
                    "{color:bg-progress}": "#353535",
                    "{color:bg-progress-chunk}": "#4A90E2",
                    # Checkboxes and radio buttons
                    "{color:bg-checkbox}": "#3A3A3A",
                    "{color:bg-checkbox-checked}": "#4A90E2",
                    "{color:bg-checkbox-disabled}": "#2B2B2B",
                    "{color:bg-radio}": "#3A3A3A",
                    "{color:bg-radio-checked}": "#4A90E2",
                    # Required columns styling
                    "{color:required-bg}": "#5D4E37",  # Dark brown-yellow
                    "{color:required-border}": "#8B7355",  # Dark gold border
                    "{color:required-text}": "#FFD700",  # Bright gold text
                    "{color:required-header-bg}": "#5D4E37",  # Required header bg
                    # Disabled cells styling
                    "{color:disabled-bg}": "#2F2F2F",  # Very dark gray
                    "{color:disabled-text}": "#707070",  # Medium gray
                    "{color:disabled-border}": "#444444",  # Dark border
                    # Expansion indicator styling
                    "{color:expansion-hover}": "#4A4A70",  # Blue hover for indicators
                    # Representation headers
                    "{color:repr-header-section-bg}": "#2D3E50",  # Dark slate blue
                    "{color:repr-header-section-text}": "#FFFFFF",  # White
                    "{color:repr-header-column-bg}": "#34495E",  # Blue-gray
                    "{color:repr-header-column-text}": "#ECF0F1",  # Light gray
                    "{color:repr-header-border}": "#1A252F",  # Dark blue
                }

                for placeholder, color in color_map.items():
                    stylesheet = stylesheet.replace(placeholder, color)

                # Add any additional custom CSS for specific components
                custom_css = """
                /* Additional custom styling for nested table view */
                QPushButton#expandAllBtn {
                    min-width: 100px;
                }
                QPushButton#collapseAllBtn {
                    min-width: 100px;
                }
                QPushButton#refreshBtn {
                    min-width: 80px;
                }
                QPushButton#autoRefreshBtn {
                    min-width: 120px;
                }
                """

                self.setStyleSheet(stylesheet + custom_css)

                # Set object names for styled buttons
                self.expand_all_btn.setObjectName("expandAllBtn")
                self.collapse_all_btn.setObjectName("collapseAllBtn")
                self.refresh_btn.setObjectName("refreshBtn")
                self.auto_refresh_btn.setObjectName("autoRefreshBtn")

            except Exception as e:
                print(f"Error loading styles: {e}")
                # Fallback to basic dark theme
                self.setStyleSheet("""
                QMainWindow { background-color: #2B2B2B; color: #E0E0E0; }
                QWidget { background-color: #2B2B2B; color: #E0E0E0; }
                QPushButton { background-color: #404040; color: #E0E0E0; padding: 4px 8px; }
                QPushButton:hover { background-color: #4A4A4A; }
                QTableView { background-color: #353535; color: #E0E0E0; }
                """)

    def closeEvent(self, event):
        """Handle application close event."""
        # Stop auto-refresh timer
        if self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()

        # Save any pending changes
        if self.controller:
            try:
                self.controller.save_data()
            except:
                pass  # Ignore save errors on exit

        event.accept()


def create_main_window():
    """Factory function to create the main window."""
    return MainWindow()
