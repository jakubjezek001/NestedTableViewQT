#!/usr/bin/env python3
"""Custom table view for tokenizer template tester.

This module contains the custom table view component for displaying token data.
"""

from typing import Optional

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QTableView,
    QWidget,
    QHeaderView,
    QAbstractItemView,
    QLabel,
    QVBoxLayout,
    QStackedWidget,
)


class TokenTableView(QStackedWidget):
    """Custom table view with warning message capability."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the token table view.

        Args:
            parent: Parent widget, defaults to None.
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        # Create the actual table view
        self._table = QTableView()
        self._table.setObjectName("tokenTableView")

        # Set table properties
        self._table.setAlternatingRowColors(
            False
        )  # We handle this in delegate
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)

        # Configure headers
        horizontal_header = self._table.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Custom styling will be handled via CSS and model data roles

        # Create warning message widget
        self._warning_widget = QWidget()
        warning_layout = QVBoxLayout(self._warning_widget)
        warning_layout.setContentsMargins(20, 20, 20, 20)
        warning_layout.setAlignment(Qt.AlignCenter)

        self._warning_label = QLabel("No tokens found in template")
        self._warning_label.setAlignment(Qt.AlignCenter)
        self._warning_label.setObjectName("warningLabel")
        self._warning_label.setStyleSheet("""
            QLabel#warningLabel {
                color: #888888;
                font-size: 14px;
                font-style: italic;
            }
        """)

        warning_layout.addWidget(self._warning_label)

        # Add both widgets to stacked widget
        self.addWidget(self._table)
        self.addWidget(self._warning_widget)

        # Start with table view
        self.setCurrentWidget(self._table)

    def setModel(self, model) -> None:
        """Set the model for the table view.

        Args:
            model: The table model to use.
        """
        self._table.setModel(model)

        # Connect to model changes to update view state
        if model:
            model.modelReset.connect(self._on_model_changed)

    def _on_model_changed(self) -> None:
        """Handle model data changes to show/hide warning message."""
        model = self._table.model()
        if model and hasattr(model, "is_empty"):
            if model.is_empty():
                self.setCurrentWidget(self._warning_widget)
            else:
                self.setCurrentWidget(self._table)
                self.resizeColumnsToContents()

    def resizeColumnsToContents(self) -> None:
        """Resize table columns to fit content."""
        if self.currentWidget() == self._table:
            self._table.resizeColumnsToContents()

    def model(self):
        """Get the current table model.

        Returns:
            The table model currently in use.
        """
        return self._table.model()

    def setVisible(self, visible: bool) -> None:
        """Set the visibility of the table view.

        Args:
            visible: Whether the view should be visible.
        """
        super().setVisible(visible)

    def get_table_widget(self) -> QTableView:
        """Get the underlying QTableView widget.

        Returns:
            The QTableView instance used internally.
        """
        return self._table

    def show_warning(
        self, message: str = "No tokens found in template"
    ) -> None:
        """Show a warning message instead of the table.

        Args:
            message: Warning message to display.
        """
        self._warning_label.setText(message)
        self.setCurrentWidget(self._warning_widget)

    def show_table(self) -> None:
        """Show the token table."""
        self.setCurrentWidget(self._table)
