"""
UI package for Product Tree View application.
Contains all UI-related components including model, view, delegate, and styles.
"""

from .ui import ProductTreeMainWindow, create_main_window
from .model import ProductTreeModel, TreeItem
from .view import ProductTreeView
from .delegate import ProductTreeDelegate
from .styles import StyleManager, load_styles, apply_styles_to_app

__version__ = "1.0.0"

__all__ = [
    "ProductTreeMainWindow",
    "create_main_window",
    "ProductTreeModel",
    "TreeItem",
    "ProductTreeView",
    "ProductTreeDelegate",
    "StyleManager",
    "load_styles",
    "apply_styles_to_app",
]
