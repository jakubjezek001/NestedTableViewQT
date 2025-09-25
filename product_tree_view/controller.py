"""
Data controller for product tree view.
Handles loading and preparing data from JSON file for Qt model.
"""

import json
import os
from typing import Dict, List, Any, Optional


class DataController:
    """Controller for managing product and representation data."""

    def __init__(self, data_file: str = "data.json"):
        """Initialize controller with data file path."""
        self.data_file = data_file
        self._data = None
        self._product_columns = set()
        self._representation_columns = set()

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        with open(self.data_file, "r", encoding="utf-8") as file:
            self._data = json.load(file)

        self._analyze_columns()
        return self._data

    def _analyze_columns(self) -> None:
        """Analyze all columns from product and representation items."""
        if not self._data or "ProductItems" not in self._data:
            return

        # Collect all unique columns from products
        for product in self._data["ProductItems"]:
            if "data" in product:
                self._product_columns.update(product["data"].keys())

            # Collect all unique columns from representations
            if "RepresentationItems" in product:
                for repr_item in product["RepresentationItems"]:
                    if "data" in repr_item:
                        self._representation_columns.update(
                            repr_item["data"].keys()
                        )

    def get_product_columns(self) -> List[str]:
        """Get all unique product columns in consistent order."""
        if not self._product_columns:
            return []

        # Ensure 'Enabled' is first, required columns follow
        columns = []
        if "Enabled" in self._product_columns:
            columns.append("Enabled")

        required_cols = ["Folder Path", "Product Type"]
        for col in required_cols:
            if col in self._product_columns and col not in columns:
                columns.append(col)

        # Add remaining columns alphabetically
        remaining = sorted(
            [col for col in self._product_columns if col not in columns]
        )
        columns.extend(remaining)

        return columns

    def get_representation_columns(self) -> List[str]:
        """Get all unique representation columns in consistent order."""
        if not self._representation_columns:
            return []

        # Ensure 'Enabled' is first, required columns follow
        columns = []
        if "Enabled" in self._representation_columns:
            columns.append("Enabled")

        required_cols = ["File Path"]
        for col in required_cols:
            if col in self._representation_columns and col not in columns:
                columns.append(col)

        # Add remaining columns alphabetically
        remaining = sorted(
            [col for col in self._representation_columns if col not in columns]
        )
        columns.extend(remaining)

        return columns

    def get_products(self) -> List[Dict[str, Any]]:
        """Get list of product items with their data and children."""
        if not self._data or "ProductItems" not in self._data:
            return []

        products = []
        for product in self._data["ProductItems"]:
            product_data = {
                "id": product.get("id", ""),
                "data": product.get("data", {}),
                "representations": [],
            }

            # Add representation items
            if "RepresentationItems" in product:
                for repr_item in product["RepresentationItems"]:
                    repr_data = {
                        "id": repr_item.get("id", ""),
                        "data": repr_item.get("data", {}),
                    }
                    product_data["representations"].append(repr_data)

            products.append(product_data)

        return products

    def has_column_value(self, item_data: Dict[str, Any], column: str) -> bool:
        """Check if item has a value for the given column."""
        return column in item_data

    def get_column_value(self, item_data: Dict[str, Any], column: str) -> Any:
        """Get value for column from item data."""
        return item_data.get(column, None)

    def is_checkbox_column(self, column: str) -> bool:
        """Check if column should be rendered as checkbox."""
        return column == "Enabled"

    def get_data_summary(self) -> Dict[str, int]:
        """Get summary statistics about the loaded data."""
        if not self._data:
            return {}

        products = self._data.get("ProductItems", [])
        total_representations = sum(
            len(p.get("RepresentationItems", [])) for p in products
        )

        return {
            "product_count": len(products),
            "representation_count": total_representations,
            "product_columns": len(self._product_columns),
            "representation_columns": len(self._representation_columns),
        }
