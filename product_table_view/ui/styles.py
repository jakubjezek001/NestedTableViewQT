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
            "required_bg": QColor(93, 78, 55),  # #5d4e37
            "required_border": QColor(139, 115, 85),  # #8b7355
            "required_text": QColor(255, 215, 0),  # #ffd700
            # Disabled cell colors
            "disabled_bg": QColor(47, 47, 47),  # #2f2f2f
            "disabled_text": QColor(112, 112, 112),  # #707070
            "disabled_border": QColor(68, 68, 68),  # #444444
            # Expansion indicator colors
            "expansion_hover": QColor(74, 74, 112),  # #4a4a70
            # Representation header colors
            "repr_header_section_bg": QColor(45, 62, 80),  # #2d3e50
            "repr_header_section_text": QColor(255, 255, 255),  # #ffffff
            "repr_header_column_bg": QColor(52, 73, 94),  # #34495e
            "repr_header_column_text": QColor(236, 240, 241),  # #ecf0f1
            "repr_header_border": QColor(26, 37, 47),  # #1a252f
            "repr_header_required_border": QColor(139, 115, 85),  # #8b7355
            # General colors
            "text_primary": QColor(224, 224, 224),  # #e0e0e0
            "text_secondary": QColor(176, 176, 176),  # #b0b0b0
            "bg_primary": QColor(43, 43, 43),  # #2b2b2b
            "bg_content": QColor(53, 53, 53),  # #353535
            "border_color": QColor(85, 85, 85),  # #555555
            "accent_blue": QColor(74, 144, 226),  # #4a90e2
        }

    def load_stylesheet(self, css_file_path=None):
        """Load CSS stylesheet from file."""
        if css_file_path is None:
            # Default to style.css in the project root
            project_root = Path(__file__).parent.parent
            css_file_path = project_root / "style.css"

        try:
            with open(css_file_path, "r", encoding="utf-8") as f:
                self.css_content = f.read()
            # Replace color placeholders with actual values
            self.css_content = self._replace_color_placeholders(
                self.css_content
            )
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

    def _replace_color_placeholders(self, css_content):
        """Replace color placeholders with actual color values."""
        color_map = {
            # Primary colors
            "{color:font}": "#E0E0E0",
            "{color:bg}": "#2B2B2B",
            "{color:font-disabled}": "#808080",
            "{color:font-hover}": "#FFFFFF",
            "{color:font-title}": "#FFFFFF",
            "{color:font-secondary}": "#B0B0B0",
            "{color:font-stats}": "#D0D0D0",
            "{color:font-instructions}": "#B0B0B0",
            "{color:font-group-title}": "#B0B0B0",
            # Borders
            "{color:border}": "#555555",
            "{color:border-hover}": "#4A90E2",
            "{color:border-focus}": "#4A90E2",
            "{color:border-header}": "#555555",
            "{color:border-tooltip}": "#666666",
            "{color:border-disabled}": "#444444",
            # Backgrounds - inputs
            "{color:bg-inputs}": "#3A3A3A",
            "{color:bg-inputs-disabled}": "#2B2B2B",
            # Backgrounds - buttons
            "{color:bg-buttons}": "#404040",
            "{color:bg-buttons-hover}": "#4A4A4A",
            "{color:bg-buttons-pressed}": "#3A3A3A",
            "{color:bg-buttons-disabled}": "#2B2B2B",
            "{color:bg-buttons-checked}": "#4A90E2",
            "{color:bg-buttons-primary}": "#4A90E2",
            "{color:bg-buttons-primary-hover}": "#357ABD",
            "{color:bg-buttons-secondary}": "#4A4A4A",
            "{color:bg-buttons-secondary-hover}": "#565656",
            "{color:bg-buttons-file}": "#484848",
            "{color:bg-buttons-file-hover}": "#565656",
            "{color:bg-buttons-toggle}": "#404040",
            "{color:bg-buttons-toggle-hover}": "#4A4A4A",
            "{color:bg-buttons-toggle-checked}": "#4A90E2",
            "{color:font-buttons-primary}": "#FFFFFF",
            "{color:font-buttons-secondary}": "#E0E0E0",
            "{color:font-buttons-file}": "#E0E0E0",
            "{color:font-buttons-toggle}": "#E0E0E0",
            "{color:font-buttons-toggle-checked}": "#FFFFFF",
            # Backgrounds - views
            "{color:bg-view}": "#353535",
            "{color:bg-view-alternate}": "#3A3A3A",
            "{color:bg-view-hover}": "#484848",
            "{color:bg-view-selection}": "#4A90E2",
            "{color:bg-view-selection-hover}": "#357ABD",
            "{color:bg-view-disabled}": "#2B2B2B",
            "{color:bg-view-alternate-disabled}": "#303030",
            "{color:font-view-selection}": "#FFFFFF",
            # Backgrounds - headers
            "{color:bg-header}": "#404040",
            "{color:bg-header-hover}": "#4A4A4A",
            "{color:font-header}": "#E0E0E0",
            # Backgrounds - other elements
            "{color:bg-group}": "#353535",
            "{color:bg-statusbar}": "#404040",
            "{color:bg-menu}": "#404040",
            "{color:bg-menu-hover}": "#4A4A4A",
            "{color:bg-menu-pressed}": "#3A3A3A",
            "{color:bg-menu-separator}": "#555555",
            "{color:bg-splitter-handle}": "#555555",
            "{color:bg-splitter-handle-hover}": "#777777",
            "{color:bg-tooltip}": "#404040",
            "{color:font-tooltip}": "#E0E0E0",
            "{color:separator}": "#555555",
            # Scroll bars
            "{color:bg-scroll}": "#404040",
            "{color:bg-scroll-handle}": "#707070",
            "{color:bg-scroll-handle-hover}": "#808080",
            # Progress bars
            "{color:bg-progress}": "#353535",
            "{color:bg-progress-chunk}": "#4A90E2",
            # Checkboxes and radio buttons
            "{color:bg-checkbox}": "#3A3A3A",
            "{color:bg-checkbox-checked}": "#4A90E2",
            "{color:bg-checkbox-disabled}": "#2B2B2B",
            "{color:bg-radio}": "#3A3A3A",
            "{color:bg-radio-checked}": "#4A90E2",
            # Required columns styling
            "{color:required-bg}": "#5D4E37",
            "{color:required-border}": "#8B7355",
            "{color:required-text}": "#FFD700",
            "{color:required-header-bg}": "#5D4E37",
            # Disabled cells styling
            "{color:disabled-bg}": "#2F2F2F",
            "{color:disabled-text}": "#707070",
            "{color:disabled-border}": "#444444",
            # Expansion indicator styling
            "{color:expansion-hover}": "#4A4A70",
            # Representation headers
            "{color:repr-header-section-bg}": "#2D3E50",
            "{color:repr-header-section-text}": "#FFFFFF",
            "{color:repr-header-column-bg}": "#34495E",
            "{color:repr-header-column-text}": "#ECF0F1",
            "{color:repr-header-border}": "#1A252F",
        }

        for placeholder, color in color_map.items():
            css_content = css_content.replace(placeholder, color)

        return css_content

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
