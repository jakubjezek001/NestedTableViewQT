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
                "bg": base_color.name(),
                "font": text_color.name(),
                "font-disabled": disabled_color.name(),
                "accent": "#0078d4",  # Blue accent
                "accent-hover": "#106ebe",  # Darker blue
                "border": "#cccccc",  # Light gray border
                "border-focus": "#0078d4",  # Blue focus border
                "success": "#107c10",  # Green
                "warning": "#ff8c00",  # Orange
                "error": "#d13438",  # Red
                # Settings-specific colors
                "settings:label-fg": text_color.name(),
                "settings:label-fg-hover": "#0078d4",
                # Additional common colors
                "primary": "#0078d4",
                "secondary": "#6c757d",
                "hover": "#f8f9fa",
                "selected": "#0078d4",
            }
        else:
            # Fallback colors if no app instance
            self._color_palette = {
                "bg": "#ffffff",
                "font": "#000000",
                "font-disabled": "#808080",
                "accent": "#0078d4",
                "accent-hover": "#106ebe",
                "border": "#cccccc",
                "border-focus": "#0078d4",
                "success": "#107c10",
                "warning": "#ff8c00",
                "error": "#d13438",
                # Settings-specific colors
                "settings:label-fg": "#000000",
                "settings:label-fg-hover": "#0078d4",
                # Additional common colors
                "primary": "#0078d4",
                "secondary": "#6c757d",
                "hover": "#f8f9fa",
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
            color_key = match.group(1)
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
            background-color: {self.get_color("bg")};
            alternate-background-color:
                {self._lighten_color(self.get_color("bg"), 0.05)};
            selection-background-color: {self.get_color("accent")};
            selection-color: white;
            outline: none;
        }}

        QTreeView::item {{
            height: 24px;
            padding: 2px;
            border: none;
        }}

        QTreeView::item:selected {{
            background-color: {self.get_color("accent")};
            color: white;
        }}

        QTreeView::item:hover {{
            background-color:
                {self._lighten_color(self.get_color("accent"), 0.8)};
        }}

        QTreeView::branch {{
            background: transparent;
        }}

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            background: transparent;
        }}

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            background: transparent;
        }}

        QHeaderView::section {{
            background-color:
                {self._lighten_color(self.get_color("bg"), 0.1)};
            border: 1px solid {self.get_color("border")};
            padding: 4px;
            font-weight: bold;
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
