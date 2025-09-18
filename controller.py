import json
import os
from typing import Dict, List, Any, Set, Optional
from collections import OrderedDict


class DataController:
    """Controller class for managing ProductItem and RepresentationItem data."""

    def __init__(self, data_file: str = "data.json"):
        self.data_file = data_file
        self.product_items = []
        self.load_data()

    def load_data(self) -> None:
        """Load data from JSON file."""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file {self.data_file} not found")

        with open(self.data_file, "r") as f:
            data = json.load(f)

        self.product_items = data.get("ProductItems", [])

    def save_data(self) -> None:
        """Save current data back to JSON file."""
        data = {"ProductItems": self.product_items}
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_product_items(self) -> List[Dict[str, Any]]:
        """Get all product items."""
        return self.product_items

    def get_product_item(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a specific product item by index."""
        if 0 <= index < len(self.product_items):
            return self.product_items[index]
        return None

    def get_representation_items(
        self, product_index: int
    ) -> List[Dict[str, Any]]:
        """Get representation items for a specific product item."""
        product_item = self.get_product_item(product_index)
        if product_item:
            return product_item.get("RepresentationItems", [])
        return []

    def get_product_columns(self) -> List[str]:
        """Get all unique columns across all product items, maintaining order."""
        columns = OrderedDict()

        for item in self.product_items:
            data = item.get("data", {})
            for col in data.keys():
                columns[col] = True

        return list(columns.keys())

    def get_representation_columns(self) -> List[str]:
        """Get all unique columns across all representation items, maintaining order."""
        columns = OrderedDict()

        for product_item in self.product_items:
            repr_items = product_item.get("RepresentationItems", [])
            for repr_item in repr_items:
                data = repr_item.get("data", {})
                for col in data.keys():
                    columns[col] = True

        return list(columns.keys())

    def get_product_data_for_row(self, product_index: int) -> Dict[str, Any]:
        """Get product data for a specific row, filling missing columns with None."""
        product_item = self.get_product_item(product_index)
        if not product_item:
            return {}

        data = product_item.get("data", {})
        all_columns = self.get_product_columns()

        # Fill missing columns with None
        row_data = {}
        for col in all_columns:
            row_data[col] = data.get(col, None)

        return row_data

    def get_representation_data_for_row(
        self, product_index: int, repr_index: int
    ) -> Dict[str, Any]:
        """Get representation data for a specific row, filling missing columns with None."""
        repr_items = self.get_representation_items(product_index)
        if repr_index >= len(repr_items):
            return {}

        data = repr_items[repr_index].get("data", {})
        all_columns = self.get_representation_columns()

        # Fill missing columns with None
        row_data = {}
        for col in all_columns:
            row_data[col] = data.get(col, None)

        return row_data

    def get_required_columns(self, columns: List[str]) -> List[str]:
        """Get columns that are marked as required (surrounded by < >)."""
        return [
            col for col in columns if col.startswith("<") and col.endswith(">")
        ]

    def is_required_column(self, column: str) -> bool:
        """Check if a column is marked as required."""
        return column.startswith("<") and column.endswith(">")

    def get_representation_columns_for_item(
        self, product_index: int, repr_index: int
    ) -> Set[str]:
        """Get the specific columns that exist for a particular representation item."""
        repr_items = self.get_representation_items(product_index)
        if repr_index >= len(repr_items):
            return set()

        data = repr_items[repr_index].get("data", {})
        return set(data.keys())

    def has_data_for_column(
        self, product_index: int, repr_index: int, column: str
    ) -> bool:
        """Check if a specific representation item has data for a given column."""
        item_columns = self.get_representation_columns_for_item(
            product_index, repr_index
        )
        return column in item_columns

    def get_product_columns_for_item(self, product_index: int) -> Set[str]:
        """Get the specific columns that exist for a particular product item."""
        product_item = self.get_product_item(product_index)
        if not product_item:
            return set()

        data = product_item.get("data", {})
        return set(data.keys())

    def has_product_data_for_column(
        self, product_index: int, column: str
    ) -> bool:
        """Check if a specific product item has data for a given column."""
        item_columns = self.get_product_columns_for_item(product_index)
        return column in item_columns

    def update_product_data(
        self, product_index: int, column: str, value: Any
    ) -> bool:
        """Update product item data."""
        if 0 <= product_index < len(self.product_items):
            if "data" not in self.product_items[product_index]:
                self.product_items[product_index]["data"] = {}
            self.product_items[product_index]["data"][column] = value
            return True
        return False

    def update_representation_data(
        self, product_index: int, repr_index: int, column: str, value: Any
    ) -> bool:
        """Update representation item data."""
        repr_items = self.get_representation_items(product_index)
        if repr_index < len(repr_items):
            if "data" not in repr_items[repr_index]:
                repr_items[repr_index]["data"] = {}
            repr_items[repr_index]["data"][column] = value
            return True
        return False

    def add_product_item(self, data: Dict[str, Any]) -> None:
        """Add a new product item."""
        new_item = {
            "id": f"ProdItem{len(self.product_items)}",
            "data": data,
            "RepresentationItems": [],
        }
        self.product_items.append(new_item)

    def add_representation_item(
        self, product_index: int, data: Dict[str, Any]
    ) -> bool:
        """Add a new representation item to a product item."""
        if 0 <= product_index < len(self.product_items):
            repr_items = self.product_items[product_index].get(
                "RepresentationItems", []
            )
            new_item = {"id": f"ReprItem{len(repr_items)}", "data": data}
            repr_items.append(new_item)
            return True
        return False

    def get_product_item_count(self) -> int:
        """Get the total number of product items."""
        return len(self.product_items)

    def get_representation_item_count(self, product_index: int) -> int:
        """Get the number of representation items for a specific product."""
        repr_items = self.get_representation_items(product_index)
        return len(repr_items)
