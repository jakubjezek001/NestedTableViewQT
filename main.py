#!/usr/bin/env python3
"""
Main entry point for the Nested Table View Qt Application.

This application demonstrates a nested table view implementation in Qt
for displaying ProductItems with expandable RepresentationItems.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from qtpy.QtWidgets import QApplication, QMessageBox
from qtpy.QtCore import Qt, QDir
from qtpy.QtGui import QIcon

from ui.ui import create_main_window


def setup_application():
    """Set up the QApplication with proper configuration."""
    # Create QApplication
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("NestedTableViewQT")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("YNPUT")
    app.setOrganizationDomain("ynput.io")

    # Set application style and appearance
    app.setStyle("Fusion")  # Use Fusion style for consistent appearance

    # Enable high DPI support (handled automatically in newer Qt versions)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Deprecated
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)     # Deprecated

    return app


def check_data_file():
    """Check if the data.json file exists and is readable."""
    data_file = project_root / "data.json"

    if not data_file.exists():
        QMessageBox.critical(
            None,
            "Data File Missing",
            f"Required data file not found: {data_file}\n\n"
            "Please ensure 'data.json' exists in the application directory.",
        )
        return False

    if not data_file.is_file():
        QMessageBox.critical(
            None,
            "Data File Error",
            f"Data file is not a regular file: {data_file}",
        )
        return False

    try:
        with open(data_file, "r") as f:
            # Just try to open it, don't validate JSON here
            # That will be done by the controller
            pass
    except PermissionError:
        QMessageBox.critical(
            None,
            "Permission Error",
            f"Cannot read data file: {data_file}\n\nCheck file permissions.",
        )
        return False
    except Exception as e:
        QMessageBox.critical(
            None,
            "File Error",
            f"Error accessing data file: {data_file}\n\nError: {e}",
        )
        return False

    return True


def main():
    """Main application entry point."""
    try:
        # Set up the application
        app = setup_application()

        # Set working directory to project root
        QDir.setCurrent(str(project_root))

        # Check data file availability
        if not check_data_file():
            return 1

        # Create and show the main window
        try:
            main_window = create_main_window()
            main_window.show()

            # Center window on screen
            screen = app.primaryScreen().availableGeometry()
            window_size = main_window.geometry()
            main_window.move(
                (screen.width() - window_size.width()) // 2,
                (screen.height() - window_size.height()) // 2,
            )

        except Exception as e:
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to create main window:\n\n{e}",
            )
            return 1

        # Show startup message in status bar
        main_window.statusBar().showMessage("Application started successfully")

        # Run the application event loop
        return app.exec_()

    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nMake sure all required dependencies are installed:")
        print("- qtpy")
        print("- PySide6 or PyQt5")
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Set up exception handling
    sys.excepthook = lambda exc_type, exc_value, exc_tb: (
        print(f"Unhandled exception: {exc_type.__name__}: {exc_value}"),
        traceback.print_tb(exc_tb),
    )

    # Run the application
    exit_code = main()
    sys.exit(exit_code)
