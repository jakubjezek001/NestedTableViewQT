"""Controller module for data preparation and management."""

import json
import os
from typing import List, Dict, Any


class DataController:
    """Controller for managing item data from JSON source."""

    def __init__(self, data_file: str = "data.json"):
        """Initialize controller with data file path.

        Args:
            data_file: Path to JSON data file
        """
        self.data_file = data_file
        self._items = []
        self.load_data()

    def load_data(self) -> None:
        """Load items data from JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self._items = json.load(f)
            else:
                print(f"Warning: Data file '{self.data_file}' not found")
                self._items = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self._items = []

    def get_items(self) -> List[Dict[str, Any]]:
        """Get all items.

        Returns:
            List of item dictionaries
        """
        return self._items

    def get_item_by_index(self, index: int) -> Dict[str, Any]:
        """Get item by index.

        Args:
            index: Item index

        Returns:
            Item dictionary or empty dict if index invalid
        """
        if 0 <= index < len(self._items):
            return self._items[index]
        return {}

    def get_column_headers(self) -> List[str]:
        """Get column headers for table display.

        Returns:
            List of column header names
        """
        return ["Name", "File Path", "Product Name", "Product Type", "Version"]

    def get_column_keys(self) -> List[str]:
        """Get data keys corresponding to columns.

        Returns:
            List of data keys
        """
        return ["name", "file_path", "product_name", "product_type", "version"]

    def format_item_info(self, item: Dict[str, Any]) -> str:
        """Format item information for display.

        Args:
            item: Item dictionary

        Returns:
            Formatted string with item info
        """
        return (
            f"Name: {item.get('name', 'N/A')}\n"
            f"Path: {item.get('file_path', 'N/A')}\n"
            f"Product: {item.get('product_name', 'N/A')}\n"
            f"Type: {item.get('product_type', 'N/A')}\n"
            f"Version: {item.get('version', 'N/A')}"
        )
