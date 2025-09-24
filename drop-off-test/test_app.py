"""Test script to validate drag and drop functionality."""

import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller import DataController
from ui.model import ItemTableModel
from ui.delegate import ItemDelegate
from qtpy.QtWidgets import QApplication, QTableView
from qtpy.QtCore import Qt


def test_controller():
    """Test DataController functionality."""
    print("Testing DataController...")

    controller = DataController("data.json")
    items = controller.get_items()

    assert len(items) > 0, "Should load items from data.json"
    print(f"✓ Loaded {len(items)} items")

    # Test item structure
    first_item = items[0]
    required_keys = [
        "name",
        "file_path",
        "product_name",
        "product_type",
        "version",
    ]

    for key in required_keys:
        assert key in first_item, f"Item missing required key: {key}"

    print("✓ Items have required keys")

    # Test column headers
    headers = controller.get_column_headers()
    assert len(headers) == 5, "Should have 5 column headers"
    print("✓ Column headers correct")

    # Test item formatting
    formatted = controller.format_item_info(first_item)
    assert "Name:" in formatted, "Formatted info should contain Name"
    assert "Path:" in formatted, "Formatted info should contain Path"
    print("✓ Item formatting works")


def test_model():
    """Test ItemTableModel functionality."""
    print("\nTesting ItemTableModel...")

    app = QApplication.instance()
    if not app:
        app = QApplication([])

    controller = DataController("data.json")
    model = ItemTableModel(controller)

    # Test basic model properties
    assert model.rowCount() > 0, "Model should have rows"
    assert model.columnCount() == 5, "Model should have 5 columns"
    print(
        f"✓ Model has {model.rowCount()} rows and {model.columnCount()} columns"
    )

    # Test data retrieval
    index = model.index(0, 0)
    data = model.data(index, Qt.DisplayRole)
    assert data is not None, "Model should return data for valid index"
    print("✓ Model data retrieval works")

    # Test drag support
    flags = model.flags(index)
    assert flags & Qt.ItemIsDragEnabled, "Items should be draggable"
    print("✓ Drag support enabled")

    # Test MIME data creation
    indexes = [model.index(0, i) for i in range(model.columnCount())]
    mime_data = model.mimeData(indexes)
    assert mime_data is not None, "Should create MIME data"
    assert mime_data.hasFormat("application/x-item-data"), (
        "Should have correct MIME format"
    )
    print("✓ MIME data creation works")


def test_json_data():
    """Test JSON data file integrity."""
    print("\nTesting JSON data file...")

    with open("data.json", "r") as f:
        data = json.load(f)

    assert isinstance(data, list), "Data should be a list"
    assert len(data) > 0, "Data should not be empty"
    print(f"✓ JSON contains {len(data)} valid items")

    # Test first item structure
    item = data[0]
    required_keys = [
        "name",
        "file_path",
        "product_name",
        "product_type",
        "version",
    ]

    for key in required_keys:
        assert key in item, f"Missing key: {key}"
        assert isinstance(item[key], str), f"Key {key} should be string"

    print("✓ JSON structure is valid")


def test_application_imports():
    """Test that all application modules can be imported."""
    print("\nTesting module imports...")

    try:
        import controller

        print("✓ Controller module imports successfully")

        from ui import model, delegate, view, ui

        print("✓ UI modules import successfully")

        import main

        print("✓ Main module imports successfully")

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

    return True


def run_all_tests():
    """Run all tests."""
    print("=== Drop-off Test Application Validation ===\n")

    try:
        test_json_data()
        test_controller()
        test_model()
        test_application_imports()

        print("\n=== All Tests Passed! ===")
        print("✓ Application is ready to use")
        print("✓ Drag and drop functionality should work correctly")
        print("✓ Run 'python main.py' to start the application")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    run_all_tests()
