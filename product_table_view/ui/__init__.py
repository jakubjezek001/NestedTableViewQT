"""
UI package for Nested Table View Qt Application.

This package contains all the user interface components including:
- MainWindow and UI components
- Table models for nested data display
- Custom delegates for cell rendering
- Table views with expansion/collapse functionality
"""

__version__ = "1.0.0"
__author__ = "YNPUT"

# Import main UI components for easier access
from ui.ui import MainWindow, create_main_window
from ui.view import NestedTableView, NestedTableWidget
from ui.model import (
    ProductItemsTableModel,
    RepresentationItemsTableModel,
    NestedTableProxyModel,
)
from ui.delegate import NestedTableDelegate, HeaderDelegate

__all__ = [
    "MainWindow",
    "create_main_window",
    "NestedTableView",
    "NestedTableWidget",
    "ProductItemsTableModel",
    "RepresentationItemsTableModel",
    "NestedTableProxyModel",
    "NestedTableDelegate",
    "HeaderDelegate",
]
