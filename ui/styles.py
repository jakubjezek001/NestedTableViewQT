"""
Style manager for NestedTableViewQT application.

This module handles loading and applying CSS styles, and provides
color constants that match the CSS theme for use in custom painting.
"""

import os
from pathlib import Path
from qtpy.QtCore import QFile, QTextStream
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QApplication


class StyleManager:
    """Manages application styling and theming."""

    def __init__(self):
        self.css_content = ""
        self._colors = self._init_colors()

    def _init_colors(self):
        """Initialize color constants that match the CSS theme."""
        return {
            # Required column colors
            "required_bg": QColor(72, 72, 72),  # #fff8dc
            "required_border": QColor(72, 72, 72),  # #ffd700
            "required_text": QColor(51, 51, 51),  # #b8860b
            # Disabled cell colors
            "disabled_bg": QColor(240, 240, 240),  # #f0f0f0
            "disabled_text": QColor(160, 160, 160),  # #a0a0a0
            "disabled_border": QColor(200, 200, 200),  # #c8c8c8
            # Expansion indicator colors
            "expansion_hover": QColor(230, 230, 250),  # #e6e6fa
            # Representation header colors
            "repr_header_section_bg": QColor(100, 120, 180),  # #6478b4
            "repr_header_section_text": QColor(255, 255, 255),  # #ffffff
            "repr_header_column_bg": QColor(40, 40, 40),  # #c8d2f0
            "repr_header_column_text": QColor(200, 210, 240),  # #282828
            "repr_header_border": QColor(80, 80, 80),  # #505050
            "repr_header_required_border": QColor(255, 165, 0),  # #ffa500
            # General colors
            "text_primary": QColor(51, 51, 51),  # #333333
            "text_secondary": QColor(102, 102, 102),  # #666666
            "bg_primary": QColor(245, 245, 245),  # #f5f5f5
            "bg_content": QColor(255, 255, 255),  # #ffffff
            "border_color": QColor(204, 204, 204),  # #cccccc
            "accent_blue": QColor(52, 152, 219),  # #3498db
        }

    def load_stylesheet(self, css_file_path=None):
        """Load CSS stylesheet from file."""
        if css_file_path is None:
            # Default to styles.css in the project root
            project_root = Path(__file__).parent.parent
            css_file_path = project_root / "dark_theme.css"

        try:
            with open(css_file_path, "r", encoding="utf-8") as f:
                self.css_content = f.read()
            return True
        except Exception as e:
            print(f"Warning: Could not load stylesheet {css_file_path}: {e}")
            self.css_content = ""
            return False

    def apply_stylesheet(self, app_or_widget=None):
        """Apply the loaded stylesheet to application or widget."""
        if not self.css_content:
            return False

        if app_or_widget is None:
            app_or_widget = QApplication.instance()

        if app_or_widget:
            app_or_widget.setStyleSheet(self.css_content)
            return True

        return False

    def get_color(self, color_name):
        """Get a color by name from the theme."""
        return self._colors.get(color_name, QColor(0, 0, 0))

    def get_colors(self):
        """Get all theme colors."""
        return self._colors.copy()

    def set_color(self, color_name, color):
        """Update a theme color."""
        if isinstance(color, str):
            color = QColor(color)
        self._colors[color_name] = color

    def apply_widget_class(self, widget, class_name):
        """Apply a CSS class to a widget by setting its object name."""
        widget.setObjectName(class_name)
        # Force style refresh
        widget.style().unpolish(widget)
        widget.style().polish(widget)


# Global style manager instance
style_manager = StyleManager()


def load_and_apply_styles(app_or_widget=None):
    """Convenience function to load and apply styles."""
    style_manager.load_stylesheet()
    return style_manager.apply_stylesheet(app_or_widget)


def get_theme_color(color_name):
    """Convenience function to get a theme color."""
    return style_manager.get_color(color_name)


def apply_style_class(widget, class_name):
    """Convenience function to apply a CSS class to a widget."""
    return style_manager.apply_widget_class(widget, class_name)


# Color constants for easy access
class ThemeColors:
    """Easy access to theme colors for use in painting delegates."""

    @staticmethod
    def required_background():
        return style_manager.get_color("required_bg")

    @staticmethod
    def required_border():
        return style_manager.get_color("required_border")

    @staticmethod
    def disabled_background():
        return style_manager.get_color("disabled_bg")

    @staticmethod
    def disabled_text():
        return style_manager.get_color("disabled_text")

    @staticmethod
    def expansion_hover():
        return style_manager.get_color("expansion_hover")

    @staticmethod
    def repr_header_section_bg():
        return style_manager.get_color("repr_header_section_bg")

    @staticmethod
    def repr_header_section_text():
        return style_manager.get_color("repr_header_section_text")

    @staticmethod
    def repr_header_column_bg():
        return style_manager.get_color("repr_header_column_bg")

    @staticmethod
    def repr_header_column_text():
        return style_manager.get_color("repr_header_column_text")

    @staticmethod
    def repr_header_border():
        return style_manager.get_color("repr_header_border")
