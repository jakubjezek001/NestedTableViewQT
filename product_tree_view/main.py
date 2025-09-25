#!/usr/bin/env python3
"""
Main entry point for Product Tree View application.
Demonstrates hierarchical product/representation data in Qt tree view.
"""

import sys
import os
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from controller import DataController
from ui.ui import create_main_window


def setup_application():
    """Setup and configure Qt application."""
    app = QApplication(sys.argv)

    # Application properties
    app.setApplicationName("Product Tree View")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("YNPUT")
    app.setOrganizationDomain("ynput.io")

    # High DPI scaling is automatically handled in newer Qt versions

    return app


def main():
    """Main application function."""
    try:
        # Create Qt application
        app = setup_application()

        # Initialize data controller
        data_file = os.path.join(current_dir, "data.json")
        controller = DataController(data_file)

        # Create and show main window
        main_window = create_main_window(controller)
        main_window.show()

        # Start application event loop
        return app.exec_()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0

    except Exception as e:
        print(f"Error starting application: {e}")
        return 1


def test_mode():
    """Test mode for running unit tests."""
    # This can be extended for automated testing
    print("Test mode - running basic validation")

    try:
        # Test data loading
        data_file = os.path.join(current_dir, "data.json")
        controller = DataController(data_file)
        controller.load_data()

        summary = controller.get_data_summary()
        print(f"Data loaded successfully: {summary}")

        print("Basic validation passed")
        return 0

    except Exception as e:
        print(f"Test failed: {e}")
        return 1


if __name__ == "__main__":
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        exit_code = test_mode()
    else:
        exit_code = main()

    sys.exit(exit_code)
