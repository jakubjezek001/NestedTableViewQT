"""
Styles module for loading and applying CSS styles to Qt application.
Handles CSS file loading and color template processing.
"""

import os
from typing import Dict, Any, Optional
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QFile, QTextStream
from qtpy.QtGui import QColor, QPalette


class StyleManager:
    """Manages application styles and theming."""

    def __init__(self, style_file: str = "style.css"):
        """Initialize style manager with CSS file."""
        # Construct full path relative to this module's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(
            current_dir
        )  # Go up one level from ui/ to product_tree_view/
        self.style_file = os.path.join(parent_dir, style_file)
        self._raw_css = ""
        self._processed_css = ""
        self._color_palette = {}
        self._setup_default_colors()

    def _setup_default_colors(self) -> None:
        """Setup default color palette."""
        # Get system palette for defaults
        app = QApplication.instance()
        if app:
            palette = app.palette()

            # Extract system colors
            base_color = palette.color(QPalette.Base)
            text_color = palette.color(QPalette.Text)
            disabled_color = palette.color(QPalette.Disabled, QPalette.Text)

            self._color_palette = {
                "bg": "#2b2b2b",  # Dark background
                "font": "#ffffff",  # Light text
                "font-disabled": "#808080",  # Gray disabled text
                "accent": "#0078d4",  # Blue accent
                "accent-hover": "#106ebe",  # Darker blue
                "border": "#555555",  # Dark gray border
                "border-focus": "#0078d4",  # Blue focus border
                "success": "#107c10",  # Green
                "warning": "#ff8c00",  # Orange
                "error": "#d13438",  # Red
                # Input/Form colors
                "bg-inputs": "#3c3c3c",
                "border-hover": "#0078d4",
                # Button colors
                "bg-buttons": "#404040",
                "bg-buttons-hover": "#4a4a4a",
                "font-hover": "#ffffff",
                # View colors
                "bg-view": "#323232",
                "bg-view-alternate": "#2e2e2e",
                "bg-view-hover": "#3a3a3a",
                "bg-view-selection": "#0078d4",
                "font-view-selection": "#ffffff",
                "bg-view-selection-hover": "#106ebe",
                "bg-view-header": "#404040",
                # Tab widget colors
                "tab-widget:bg": "#404040",
                "tab-widget:color": "#ffffff",
                "tab-widget:bg-selected": "#323232",
                "tab-widget:color-selected": "#ffffff",
                "tab-widget:bg-hover": "#4a4a4a",
                "tab-widget:color-hover": "#ffffff",
                # Menu and separator colors
                "bg-menu-separator": "#555555",
                "bg-scroll-handle": "#606060",
                # Special button colors
                "delete-btn-bg": "#d13438",
                "restart-btn-bg": "#ff8c00",
                # Publisher colors
                "publisher:success": "#107c10",
                "publisher:error": "#d13438",
                "publisher:crash": "#8b0000",
                "publisher:warning": "#ff8c00",
                "publisher:progress": "#0078d4",
                "publisher:tab-bg": "#f3f3f3",
                # Overlay message colors
                "overlay-messages:bg-success": "#1e4620",
                "overlay-messages:bg-success-hover": "#2d5a2f",
                "overlay-messages:bg-error": "#4a1e1e",
                "overlay-messages:bg-error-hover": "#5a2d2d",
                "overlay-messages:bg-info": "#1e3a4a",
                "overlay-messages:bg-info-hover": "#2d4a5a",
                # Settings-specific colors
                "settings:label-fg": "#ffffff",
                "settings:label-fg-hover": "#0078d4",
                "settings:focus-border": "#0078d4",
                "settings:modified-light": "#4a3d1a",
                "settings:modified-mid": "#5a4720",
                "settings:modified-dark": "#ff8c00",
                "settings:studio-light": "#1a2d3d",
                "settings:studio-dark": "#0277bd",
                "settings:studio-label-hover": "#01579b",
                "settings:invalid-light": "#4a1e1e",
                "settings:invalid-dark": "#d13438",
                "settings:project-light": "#1e4a1e",
                "settings:project-mid": "#2d5a2d",
                "settings:project-dark": "#4caf50",
                "settings:source-version": "#28a745",
                "settings:source-version-outdated": "#ffc107",
                "settings:breadcrumbs-btn-bg": "#404040",
                "settings:breadcrumbs-btn-bg-hover": "#4a4a4a",
                # Font overrides
                "font-overridden": "#ff6b35",
                # Additional common colors
                "primary": "#0078d4",
                "secondary": "#6c757d",
                "hover": "#3a3a3a",
                "selected": "#0078d4",
            }
        else:
            # Fallback colors if no app instance
            self._color_palette = {
                "bg": "#2b2b2b",
                "font": "#ffffff",
                "font-disabled": "#808080",
                "accent": "#0078d4",
                "accent-hover": "#106ebe",
                "border": "#555555",
                "border-focus": "#0078d4",
                "success": "#107c10",
                "warning": "#ff8c00",
                "error": "#d13438",
                # Input/Form colors
                "bg-inputs": "#3c3c3c",
                "border-hover": "#0078d4",
                # Button colors
                "bg-buttons": "#404040",
                "bg-buttons-hover": "#4a4a4a",
                "font-hover": "#ffffff",
                # View colors
                "bg-view": "#323232",
                "bg-view-alternate": "#2e2e2e",
                "bg-view-hover": "#3a3a3a",
                "bg-view-selection": "#0078d4",
                "font-view-selection": "#ffffff",
                "bg-view-selection-hover": "#106ebe",
                "bg-view-header": "#404040",
                # Tab widget colors
                "tab-widget:bg": "#404040",
                "tab-widget:color": "#ffffff",
                "tab-widget:bg-selected": "#323232",
                "tab-widget:color-selected": "#ffffff",
                "tab-widget:bg-hover": "#4a4a4a",
                "tab-widget:color-hover": "#ffffff",
                # Menu and separator colors
                "bg-menu-separator": "#555555",
                "bg-scroll-handle": "#606060",
                # Special button colors
                "delete-btn-bg": "#d13438",
                "restart-btn-bg": "#ff8c00",
                # Publisher colors
                "publisher:success": "#107c10",
                "publisher:error": "#d13438",
                "publisher:crash": "#8b0000",
                "publisher:warning": "#ff8c00",
                "publisher:progress": "#0078d4",
                "publisher:tab-bg": "#f3f3f3",
                # Overlay message colors
                "overlay-messages:bg-success": "#1e4620",
                "overlay-messages:bg-success-hover": "#2d5a2f",
                "overlay-messages:bg-error": "#4a1e1e",
                "overlay-messages:bg-error-hover": "#5a2d2d",
                "overlay-messages:bg-info": "#1e3a4a",
                "overlay-messages:bg-info-hover": "#2d4a5a",
                # Settings-specific colors
                "settings:label-fg": "#ffffff",
                "settings:label-fg-hover": "#0078d4",
                "settings:focus-border": "#0078d4",
                "settings:modified-light": "#4a3d1a",
                "settings:modified-mid": "#5a4720",
                "settings:modified-dark": "#ff8c00",
                "settings:studio-light": "#1a2d3d",
                "settings:studio-dark": "#0277bd",
                "settings:studio-label-hover": "#01579b",
                "settings:invalid-light": "#4a1e1e",
                "settings:invalid-dark": "#d13438",
                "settings:project-light": "#1e4a1e",
                "settings:project-mid": "#2d5a2d",
                "settings:project-dark": "#4caf50",
                "settings:source-version": "#28a745",
                "settings:source-version-outdated": "#ffc107",
                "settings:breadcrumbs-btn-bg": "#404040",
                "settings:breadcrumbs-btn-bg-hover": "#4a4a4a",
                # Font overrides
                "font-overridden": "#ff6b35",
                # Additional common colors
                "primary": "#0078d4",
                "secondary": "#6c757d",
                "hover": "#3a3a3a",
                "selected": "#0078d4",
            }

    def load_css(self) -> bool:
        """Load CSS from file."""
        if not os.path.exists(self.style_file):
            print(f"Warning: Style file not found: {self.style_file}")
            return False

        try:
            with open(self.style_file, "r", encoding="utf-8") as file:
                self._raw_css = file.read()
                self._process_css()
                return True
        except Exception as e:
            print(f"Error loading CSS: {e}")
            return False

    def _process_css(self) -> None:
        """Process CSS templates and color variables."""
        import re

        processed = self._raw_css

        # Replace color variables like {color:bg} with actual values
        for key, value in self._color_palette.items():
            placeholder = f"{{color:{key}}}"
            processed = processed.replace(placeholder, value)

        # Handle any remaining undefined color variables by providing fallbacks
        def replace_undefined_colors(match):
            color_key = match.group(1).strip()

            # Handle malformed color variables that contain actual color values
            if color_key.startswith("#") or color_key.startswith("rgb"):
                # This is already a color value, just return it without the wrapper
                return color_key.rstrip(";")

            # Provide fallback colors for common undefined variables
            fallback_colors = {
                "text": "#000000",
                "background": "#ffffff",
                "disabled": "#808080",
                "highlight": "#0078d4",
            }

            # Try to find a reasonable fallback
            for fallback_key, fallback_value in fallback_colors.items():
                if fallback_key in color_key.lower():
                    return fallback_value

            # If no fallback found, use a neutral color
            print(
                f"Warning: Undefined color variable {{color:{color_key}}}, using fallback"
            )
            return "#666666"  # Neutral gray fallback

        # Replace any remaining {color:*} patterns
        processed = re.sub(
            r"\{color:([^}]+)\}", replace_undefined_colors, processed
        )

        self._processed_css = processed

    def get_css(self) -> str:
        """Get processed CSS string."""
        if not self._processed_css and self._raw_css:
            self._process_css()
        return self._processed_css

    def apply_to_application(self, app: QApplication) -> None:
        """Apply styles to the entire application."""
        css = self.get_css()
        if css:
            app.setStyleSheet(css)

    def apply_to_widget(self, widget, additional_css: str = "") -> None:
        """Apply styles to specific widget with optional additional CSS."""
        css = self.get_css()
        if additional_css:
            css += "\n" + additional_css

        if css:
            widget.setStyleSheet(css)

    def set_color(self, color_key: str, color_value: str) -> None:
        """Set a color in the palette and reprocess CSS."""
        self._color_palette[color_key] = color_value
        if self._raw_css:
            self._process_css()

    def get_color(self, color_key: str) -> Optional[str]:
        """Get color value from palette."""
        return self._color_palette.get(color_key)

    def get_color_palette(self) -> Dict[str, str]:
        """Get complete color palette."""
        return self._color_palette.copy()

    def create_tree_view_styles(self) -> str:
        """Create specific styles for the tree view."""
        return f"""
        QTreeView {{
            border: 1px solid {self.get_color("border")};
            background-color: {self.get_color("bg-view")};
            alternate-background-color: {self.get_color("bg-view-alternate")};
            selection-background-color: {self.get_color("bg-view-selection")};
            selection-color: {self.get_color("font-view-selection")};
            color: {self.get_color("font")};
            outline: none;
            gridline-color: {self.get_color("border")};
        }}

        QTreeView::item {{
            height: 24px;
            padding: 2px;
            border: none;
            color: {self.get_color("font")};
        }}

        QTreeView::item:selected {{
            background-color: {self.get_color("bg-view-selection")};
            color: {self.get_color("font-view-selection")};
        }}

        QTreeView::item:hover {{
            background-color: {self.get_color("bg-view-hover")};
            color: {self.get_color("font")};
        }}

        QTreeView::item:selected:hover {{
            background-color: {self.get_color("bg-view-selection-hover")};
            color: {self.get_color("font-view-selection")};
        }}

        QTreeView::branch {{
            background: transparent;
        }}

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            background: transparent;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNEwxMCA4TDYgMTJWNFoiIGZpbGw9IiNGRkZGRkYiLz4KPHN2Zz4K);
        }}

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            background: transparent;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDZINFoiIGZpbGw9IiNGRkZGRkYiLz4KPHN2Zz4K);
        }}

        QHeaderView::section {{
            background-color: {self.get_color("bg-view-header")};
            border: 1px solid {self.get_color("border")};
            border-bottom: 2px solid {self.get_color("accent")};
            padding: 6px 4px;
            font-weight: bold;
            font-size: 9pt;
            color: {self.get_color("font")};
        }}

        QHeaderView::section:hover {{
            background-color: {self.get_color("bg-buttons-hover")};
        }}

        QScrollBar:vertical {{
            background-color: {self.get_color("bg")};
            width: 12px;
            border: none;
        }}

        QScrollBar::handle:vertical {{
            background-color: {self.get_color("bg-scroll-handle")};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self.get_color("accent")};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by the given factor."""
        try:
            color = QColor(hex_color)
            h, s, l, a = color.getHslF()
            l = min(1.0, l + factor)
            new_color = QColor.fromHslF(h, s, l, a)
            return new_color.name()
        except:
            return hex_color  # Return original if conversion fails


# Global style manager instance
style_manager = StyleManager()


def load_styles() -> StyleManager:
    """Load styles and return manager instance."""
    style_manager.load_css()
    return style_manager


def apply_styles_to_app(app: QApplication) -> None:
    """Apply loaded styles to application."""
    style_manager.apply_to_application(app)


def get_tree_view_styles() -> str:
    """Get specific tree view styles."""
    return style_manager.create_tree_view_styles()
