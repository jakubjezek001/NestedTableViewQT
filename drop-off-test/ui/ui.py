"""Main UI entry point module."""

import os
from qtpy.QtWidgets import QMainWindow, QApplication
from qtpy.QtCore import Qt

from .model import ItemTableModel
from .delegate import ItemDelegate
from .view import MainView
from controller import DataController


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, parent=None):
        """Initialize main window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.controller = None
        self.model = None
        self.delegate = None
        self.main_view = None
        self.setup_ui()
        self.load_styles()

    def setup_ui(self):
        """Setup main UI components."""
        self.setWindowTitle("Drop-off Test Application")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # Initialize controller
        data_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data.json"
        )
        self.controller = DataController(data_file)

        # Initialize model
        self.model = ItemTableModel(self.controller)

        # Initialize delegate
        self.delegate = ItemDelegate()

        # Initialize main view
        self.main_view = MainView(self.model, self.delegate, self.controller)

        # Set central widget
        self.setCentralWidget(self.main_view)

    def load_styles(self):
        """Load and apply CSS styles."""
        css_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "style.css"
        )

        if os.path.exists(css_file):
            try:
                with open(css_file, "r", encoding="utf-8") as f:
                    stylesheet = f.read()

                # Replace color placeholders with actual values
                color_map = {
                    "{color:font}": "#E0E0E0",
                    "{color:bg}": "#2B2B2B",
                    "{color:font-disabled}": "#808080",
                    "{color:border}": "#555555",
                    "{color:bg-inputs}": "#3A3A3A",
                    "{color:bg-inputs-disabled}": "#2B2B2B",
                    "{color:border-hover}": "#4A90E2",
                    "{color:border-focus}": "#4A90E2",
                    "{color:bg-buttons}": "#404040",
                    "{color:bg-buttons-hover}": "#4A4A4A",
                    "{color:font-hover}": "#FFFFFF",
                    "{color:bg-buttons-disabled}": "#2B2B2B",
                    "{color:bg-view}": "#353535",
                }

                for placeholder, color in color_map.items():
                    stylesheet = stylesheet.replace(placeholder, color)

                # Add custom styling for drop zones
                custom_css = """
                QPushButton#dropZone {
                    background: #404040;
                    border: 2px dashed #666666;
                    border-radius: 8px;
                    font-size: 12pt;
                    font-weight: bold;
                    color: #E0E0E0;
                }
                QPushButton#dropZone:hover {
                    background: #4A4A4A;
                    border-color: #4A90E2;
                }
                QPushButton#dropZone:pressed {
                    background: #555555;
                }
                """

                self.setStyleSheet(stylesheet + custom_css)

            except Exception as e:
                print(f"Error loading styles: {e}")

    def refresh_data(self):
        """Refresh application data."""
        if self.main_view:
            self.main_view.refresh_table()

    def closeEvent(self, event):
        """Handle application close event.

        Args:
            event: Close event
        """
        event.accept()


def create_app():
    """Create and configure QApplication.

    Returns:
        QApplication instance
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    app.setApplicationName("Drop-off Test")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Test Organization")

    return app


def show_main_window():
    """Show main application window.

    Returns:
        MainWindow instance
    """
    window = MainWindow()
    window.show()
    return window
