#!/usr/bin/env python3
"""Main entry point for the Batch Ingest tokenizer template tester.

This module initializes and runs the Qt application for testing tokenizer templates.
"""

import os
import sys
from typing import Optional

from qtpy.QtWidgets import QApplication

# Add the current directory to Python path to enable proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.ui import TokenizerTesterApp


def main() -> Optional[int]:
    """Initialize and run the tokenizer tester application.

    Returns:
        Exit code from the application, or None if successful.
    """
    app = QApplication(sys.argv)

    # Create and show the main window
    window = TokenizerTesterApp()
    window.show()

    # Run the application event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
