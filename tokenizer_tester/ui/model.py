#!/usr/bin/env python3
"""Table model for tokenizer template tester.

This module contains the Qt table model for displaying token data in the UI.
"""

from typing import Any, Dict, List, Optional, Tuple

from qtpy.QtCore import QAbstractTableModel, QModelIndex, Qt
from qtpy.QtGui import QColor


class TokenTableModel(QAbstractTableModel):
    """Table model for displaying tokenizer tokens and their values."""

    def __init__(self, parent: Optional[object] = None) -> None:
        """Initialize the token table model.

        Args:
            parent: Parent object, defaults to None.
        """
        super().__init__(parent)
        self._tokens: Dict[str, Any] = {}
        self._token_list: List[Tuple[str, Any]] = []
        self._headers = ["Token", "Value"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model.

        Args:
            parent: Parent model index (unused for table model).

        Returns:
            Number of token rows.
        """
        return len(self._token_list)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns in the model.

        Args:
            parent: Parent model index (unused for table model).

        Returns:
            Number of columns (always 2: Token, Value).
        """
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for the given index and role.

        Args:
            index: Model index specifying row and column.
            role: Qt role determining what type of data to return.

        Returns:
            Data for the specified index and role, or None if invalid.
        """
        if not index.isValid() or index.row() >= len(self._token_list):
            return None

        token_name, token_value = self._token_list[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:  # Token column
                return token_name
            elif column == 1:  # Value column
                if token_value is None:
                    return ""  # Show empty for None values
                return str(token_value)

        elif role == Qt.BackgroundRole:
            if column == 0:  # Token column - darker background
                return QColor("#252525")  # 10% darker than main background
            elif column == 1 and token_value is None:  # Error cell
                return QColor("#4a2828")  # Dimmed red for missing values

        elif role == Qt.ForegroundRole:
            if column == 1 and token_value is None:
                return QColor("#ff6b6b")  # Red text for error values
            return QColor("white")

        elif role == Qt.ToolTipRole:
            if column == 1 and token_value is None:
                return f"Token '{token_name}' could not be resolved"
            return None

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        """Return header data for the given section.

        Args:
            section: Section number (column or row index).
            orientation: Horizontal or vertical orientation.
            role: Qt role determining what type of data to return.

        Returns:
            Header data for the specified section, or None if invalid.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None

    def update_tokens(self, tokens: Dict[str, Any]) -> None:
        """Update the model with new token data.

        Args:
            tokens: Dictionary mapping token names to their values.
                   None values indicate unresolvable tokens.
        """
        self.beginResetModel()

        self._tokens = tokens.copy()
        # Convert dict to sorted list of tuples for consistent ordering
        self._token_list = sorted(tokens.items(), key=lambda x: x[0])

        self.endResetModel()

    def get_tokens(self) -> Dict[str, Any]:
        """Get the current token data.

        Returns:
            Dictionary of current tokens and their values.
        """
        return self._tokens.copy()

    def has_errors(self) -> bool:
        """Check if any tokens have error values (None).

        Returns:
            True if any token values are None, False otherwise.
        """
        return any(value is None for value in self._tokens.values())

    def get_error_tokens(self) -> List[str]:
        """Get list of token names that have error values.

        Returns:
            List of token names with None values.
        """
        return [name for name, value in self._tokens.items() if value is None]

    def is_empty(self) -> bool:
        """Check if the model contains no token data.

        Returns:
            True if no tokens are present, False otherwise.
        """
        return len(self._tokens) == 0

    def clear(self) -> None:
        """Clear all token data from the model."""
        self.update_tokens({})
