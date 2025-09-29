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
        self._product_columns = []
        self._representation_columns = []
        self._product_column_types = {}
        self._representation_column_types = {}

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

        # Collect all unique columns from products in order of first appearance
        for product in self._data["ProductItems"]:
            if "data" in product:
                for key in product["data"].keys():
                    if key not in self._product_columns:
                        self._product_columns.append(key)

            # Collect all unique columns from representations in order of first appearance
            if "RepresentationItems" in product:
                for repr_item in product["RepresentationItems"]:
                    if "data" in repr_item:
                        for key in repr_item["data"].keys():
                            if key not in self._representation_columns:
                                self._representation_columns.append(key)

        # Analyze data types for all columns
        self._analyze_column_types()

    def _analyze_column_types(self) -> None:
        """Analyze data types for all columns based on actual values."""
        if not self._data or "ProductItems" not in self._data:
            return

        # Analyze product column types
        for column in self._product_columns:
            values = []
            for product in self._data["ProductItems"]:
                if "data" in product and column in product["data"]:
                    values.append(product["data"][column])

            if values:
                self._product_column_types[column] = (
                    self._determine_column_type(values)
                )

        # Analyze representation column types
        for column in self._representation_columns:
            values = []
            for product in self._data["ProductItems"]:
                if "RepresentationItems" in product:
                    for repr_item in product["RepresentationItems"]:
                        if "data" in repr_item and column in repr_item["data"]:
                            values.append(repr_item["data"][column])

            if values:
                self._representation_column_types[column] = (
                    self._determine_column_type(values)
                )

    def _determine_column_type(self, values: List[Any]) -> type:
        """Determine the most appropriate type for a column based on its values."""
        if not values:
            return str

        # Remove None values for type analysis
        with_values = [v for v in values if v is not None]
        if not with_values:
            return str

        # Check if all values are boolean
        if all(isinstance(v, bool) for v in with_values):
            return bool

        # Check if all values are integers (but not bool, since bool is subclass of int)
        if all(
            isinstance(v, int) and not isinstance(v, bool) for v in with_values
        ):
            return int

        # Check if all values are floats or can be converted to float
        try:
            float_values = []
            for v in with_values:
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    float_values.append(float(v))
                elif isinstance(v, str):
                    # Try to convert string to float
                    float_val = float(v)
                    float_values.append(float_val)
                else:
                    raise ValueError("Cannot convert to float")

            # If all values can be converted to float and at least one is actually float
            if len(float_values) == len(with_values):
                # Check if any original value was a float or string representing decimal
                has_decimal = any(
                    isinstance(v, float)
                    or (isinstance(v, str) and "." in str(v))
                    for v in with_values
                )
                if has_decimal:
                    return float
                else:
                    return int  # All are whole numbers
        except (ValueError, TypeError):
            pass

        # Default to string
        return str

    def get_product_columns(self) -> List[str]:
        """Get all unique product columns in order of first appearance."""
        return self._product_columns.copy()

    def get_representation_columns(self) -> List[str]:
        """Get all unique representation columns in order of first appearance."""
        return self._representation_columns.copy()

    def get_column_type(self, column: str, is_product: bool = True) -> type:
        """Get the data type for a specific column."""
        if is_product:
            return self._product_column_types.get(column, str)
        else:
            return self._representation_column_types.get(column, str)

    def convert_value_to_type(self, value: Any, target_type: type) -> Any:
        """Convert a value to the target type with proper error handling."""
        if value is None:
            return None

        try:
            if target_type == bool:
                if isinstance(value, str):
                    return value.lower() in (
                        "true",
                        "1",
                        "yes",
                        "on",
                        "false",
                        "0",
                        "no",
                        "off",
                    )
                return bool(value)
            elif target_type == int:
                if isinstance(value, str):
                    # Handle empty strings
                    if not value.strip():
                        return 0
                    return int(float(value))  # Handle strings like "24.0"
                return int(value)
            elif target_type == float:
                if isinstance(value, str):
                    # Handle empty strings
                    if not value.strip():
                        return 0.0
                    return float(value)
                return float(value)
            else:  # str
                return str(value)
        except (ValueError, TypeError):
            # If conversion fails, return the original value
            return value

    def is_numeric_column(self, column: str, is_product: bool = True) -> bool:
        """Check if column contains numeric data (int or float)."""
        column_type = self.get_column_type(column, is_product)
        return column_type in (int, float)

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
        # Check if column is boolean type in either product or representation columns
        return (
            self._product_column_types.get(column) == bool
            or self._representation_column_types.get(column) == bool
        )

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
            "product_column_types": dict(self._product_column_types),
            "representation_column_types": dict(
                self._representation_column_types
            ),
        }
