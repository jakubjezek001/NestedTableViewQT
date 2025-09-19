#!/usr/bin/env python3
"""Main UI module for the Batch Ingest tokenizer template tester.

This module contains the main application window and handles the user interface.
"""

import os
from typing import Optional

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QSizePolicy,
)

from ui.view import TokenTableView
from ui.model import TokenTableModel
from controller import parse_tokens


class TokenizerTesterApp(QMainWindow):
    """Main application window for the tokenizer template tester."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the tokenizer tester application window.

        Args:
            parent: Parent widget, defaults to None.
        """
        super().__init__(parent)
        self._setup_ui()
        self._load_styles()
        self._connect_signals()

        # Timer for debounced input updates
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._update_tokens)

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        self.setWindowTitle("Batch Ingest tokenizer template tester")
        self.setFixedSize(400, 500)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # Testing path input field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter testing path...")
        self.path_input.setObjectName("pathInput")
        main_layout.addWidget(self.path_input)

        # Template input field
        self.template_input = QLineEdit()
        self.template_input.setPlaceholderText("Enter template with tokens...")
        self.template_input.setObjectName("templateInput")
        main_layout.addWidget(self.template_input)

        # Create table model and view
        self.table_model = TokenTableModel()
        self.table_view = TokenTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setObjectName("tokenTable")

        # Set size policy for table to expand and fill remaining space
        self.table_view.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        main_layout.addWidget(self.table_view)

    def _load_styles(self) -> None:
        """Load and apply CSS styles from external file."""
        css_file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "styles.css"
        )

        if os.path.exists(css_file_path):
            try:
                with open(css_file_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except (IOError, OSError) as e:
                print(f"Warning: Could not load CSS file: {e}")
                self._apply_fallback_styles()
        else:
            # Apply fallback styles if CSS file doesn't exist
            self._apply_fallback_styles()

    def _apply_fallback_styles(self) -> None:
        """Apply basic fallback styles if CSS file is not available."""
        fallback_style = """
        QMainWindow {
            background-color: #2b2b2b;
            color: white;
        }
        QLineEdit {
            background-color: #353535;
            color: white;
            border: none;
            padding: 8px;
            font-size: 12px;
        }
        QTableView {
            background-color: #1e1e1e;
            color: white;
            border: none;
            border-radius: 5px;
            gridline-color: #404040;
        }
        QHeaderView::section {
            background-color: #353535;
            color: white;
            border: none;
            padding: 8px;
            font-weight: bold;
        }
        """
        self.setStyleSheet(fallback_style)

    def _connect_signals(self) -> None:
        """Connect UI signals to their respective handlers."""
        # Connect input field changes to debounced update
        self.path_input.textChanged.connect(self._on_input_changed)
        self.template_input.textChanged.connect(self._on_input_changed)

    def _on_input_changed(self) -> None:
        """Handle input field changes with debouncing.

        This method is called whenever either input field changes.
        It uses a timer to debounce rapid changes and avoid excessive updates.
        """
        # Restart the timer to debounce rapid input changes
        self._update_timer.stop()
        self._update_timer.start(300)  # 300ms delay

    def _update_tokens(self) -> None:
        """Update the token table with parsed results from current inputs."""
        path_text = self.path_input.text().strip()
        template_text = self.template_input.text().strip()

        # Parse tokens using the controller
        try:
            tokens = parse_tokens(path_text, template_text)
            self.table_model.update_tokens(tokens)

            # Show/hide table based on whether we have tokens
            if tokens:
                self.table_view.setVisible(True)
                self.table_view.resizeColumnsToContents()
            else:
                # For now, just show empty table - warning message will be handled in view
                self.table_view.setVisible(True)
                self.table_model.update_tokens({})

        except Exception as e:
            print(f"Error parsing tokens: {e}")
            # Show empty table on error
            self.table_model.update_tokens({})

    def get_current_path(self) -> str:
        """Get the current path from the input field.

        Returns:
            Current path string from the input field.
        """
        return self.path_input.text().strip()

    def get_current_template(self) -> str:
        """Get the current template from the input field.

        Returns:
            Current template string from the input field.
        """
        return self.template_input.text().strip()

    def set_path(self, path: str) -> None:
        """Set the path input field value.

        Args:
            path: Path string to set in the input field.
        """
        self.path_input.setText(path)

    def set_template(self, template: str) -> None:
        """Set the template input field value.

        Args:
            template: Template string to set in the input field.
        """
        self.template_input.setText(template)
