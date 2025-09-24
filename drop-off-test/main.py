"""Main application entry point for Drop-off Test GUI."""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.ui import create_app, show_main_window


def main():
    """Main application function."""
    try:
        # Create QApplication
        app = create_app()

        # Show main window
        window = show_main_window()

        # Start application event loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
