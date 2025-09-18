#!/usr/bin/env python3
"""
Test script for Nested Table View Qt Application.

This script verifies that all components are working correctly
without requiring the full GUI to be displayed.
"""

import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        import qtpy

        print("  ✓ qtpy imported successfully")
    except ImportError as e:
        print(f"  ✗ qtpy import failed: {e}")
        return False

    try:
        from qtpy.QtWidgets import QApplication

        print("  ✓ QtWidgets imported successfully")
    except ImportError as e:
        print(f"  ✗ QtWidgets import failed: {e}")
        return False

    try:
        from controller import DataController

        print("  ✓ DataController imported successfully")
    except ImportError as e:
        print(f"  ✗ DataController import failed: {e}")
        return False

    try:
        from ui.model import (
            ProductItemsTableModel,
            RepresentationItemsTableModel,
            NestedTableProxyModel,
        )

        print("  ✓ UI models imported successfully")
    except ImportError as e:
        print(f"  ✗ UI models import failed: {e}")
        return False

    try:
        from ui.view import NestedTableView, NestedTableWidget

        print("  ✓ UI views imported successfully")
    except ImportError as e:
        print(f"  ✗ UI views import failed: {e}")
        return False

    try:
        from ui.delegate import NestedTableDelegate, HeaderDelegate

        print("  ✓ UI delegates imported successfully")
    except ImportError as e:
        print(f"  ✗ UI delegates import failed: {e}")
        return False

    try:
        from ui.ui import MainWindow, create_main_window

        print("  ✓ Main UI imported successfully")
    except ImportError as e:
        print(f"  ✗ Main UI import failed: {e}")
        return False

    return True


def test_data_file():
    """Test that the data file exists and is valid JSON."""
    print("\nTesting data file...")

    data_file = project_root / "data.json"

    if not data_file.exists():
        print(f"  ✗ data.json not found at {data_file}")
        return False

    try:
        with open(data_file, "r") as f:
            data = json.load(f)
        print("  ✓ data.json is valid JSON")
    except json.JSONDecodeError as e:
        print(f"  ✗ data.json is invalid JSON: {e}")
        return False

    # Check structure
    if "ProductItems" not in data:
        print("  ✗ data.json missing 'ProductItems' key")
        return False

    product_items = data["ProductItems"]
    if not isinstance(product_items, list):
        print("  ✗ 'ProductItems' should be a list")
        return False

    if len(product_items) == 0:
        print("  ✗ No product items found")
        return False

    print(f"  ✓ Found {len(product_items)} product items")

    # Check first product item structure
    first_item = product_items[0]
    required_keys = ["id", "data", "RepresentationItems"]
    for key in required_keys:
        if key not in first_item:
            print(f"  ✗ Product item missing '{key}' key")
            return False

    repr_items = first_item["RepresentationItems"]
    if not isinstance(repr_items, list):
        print("  ✗ 'RepresentationItems' should be a list")
        return False

    print(f"  ✓ First product has {len(repr_items)} representation items")
    print("  ✓ Data file structure is valid")

    return True


def test_controller():
    """Test the DataController functionality."""
    print("\nTesting DataController...")

    try:
        from controller import DataController

        controller = DataController()
        print("  ✓ DataController created successfully")
    except Exception as e:
        print(f"  ✗ DataController creation failed: {e}")
        return False

    try:
        product_count = controller.get_product_item_count()
        print(f"  ✓ Product count: {product_count}")
    except Exception as e:
        print(f"  ✗ Failed to get product count: {e}")
        return False

    try:
        product_columns = controller.get_product_columns()
        print(
            f"  ✓ Product columns ({len(product_columns)}): {product_columns[:3]}..."
        )
    except Exception as e:
        print(f"  ✗ Failed to get product columns: {e}")
        return False

    try:
        repr_columns = controller.get_representation_columns()
        print(
            f"  ✓ Representation columns ({len(repr_columns)}): {repr_columns[:3]}..."
        )
    except Exception as e:
        print(f"  ✗ Failed to get representation columns: {e}")
        return False

    try:
        if product_count > 0:
            repr_count = controller.get_representation_item_count(0)
            print(f"  ✓ First product has {repr_count} representations")
    except Exception as e:
        print(f"  ✗ Failed to get representation count: {e}")
        return False

    return True


def test_models():
    """Test the model creation."""
    print("\nTesting models...")

    try:
        from controller import DataController
        from ui.model import (
            ProductItemsTableModel,
            RepresentationItemsTableModel,
            NestedTableProxyModel,
        )
        from qtpy.QtWidgets import QApplication

        # Create minimal QApplication for models
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        controller = DataController()

        # Test ProductItemsTableModel
        product_model = ProductItemsTableModel(controller)
        print(
            f"  ✓ ProductItemsTableModel created - rows: {product_model.rowCount()}, cols: {product_model.columnCount()}"
        )

        # Test RepresentationItemsTableModel
        if controller.get_product_item_count() > 0:
            repr_model = RepresentationItemsTableModel(controller, 0)
            print(
                f"  ✓ RepresentationItemsTableModel created - rows: {repr_model.rowCount()}, cols: {repr_model.columnCount()}"
            )

        # Test NestedTableProxyModel
        proxy_model = NestedTableProxyModel(controller)
        print(
            f"  ✓ NestedTableProxyModel created - rows: {proxy_model.rowCount()}, cols: {proxy_model.columnCount()}"
        )

    except Exception as e:
        print(f"  ✗ Model creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_main_window():
    """Test main window creation."""
    print("\nTesting main window creation...")

    try:
        from qtpy.QtWidgets import QApplication
        from ui.ui import create_main_window

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        main_window = create_main_window()
        print("  ✓ Main window created successfully")

        # Test that window has expected attributes
        if hasattr(main_window, "controller") and main_window.controller:
            print("  ✓ Controller initialized in main window")
        else:
            print("  ! Warning: Controller not initialized (data file issue?)")

        if hasattr(main_window, "table_widget"):
            print("  ✓ Table widget initialized")
        else:
            print("  ✗ Table widget not initialized")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Main window creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Nested Table View Qt Application Test")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Data File Test", test_data_file),
        ("Controller Test", test_controller),
        ("Models Test", test_models),
        ("Main Window Test", test_main_window),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ {test_name} crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(tests)}")

    if passed == len(tests):
        print("\n🎉 All tests passed! The application should work correctly.")
        print("\nYou can now run: python main.py")
    else:
        print(
            f"\n❌ {len(tests) - passed} test(s) failed. Please check the issues above."
        )

    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
