#!/usr/bin/env python3
"""
Test script for Product Tree View application.
Tests data loading, model creation, and basic functionality.
"""

import sys
import os
import unittest

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import Qt

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

from controller import DataController
from ui.model import ProductTreeModel


class TestProductTreeView(unittest.TestCase):
    """Test cases for product tree view components."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_file = os.path.join(current_dir, "data.json")
        self.controller = DataController(self.data_file)

    def test_data_file_exists(self):
        """Test that data file exists."""
        self.assertTrue(
            os.path.exists(self.data_file),
            f"Data file not found: {self.data_file}",
        )

    def test_controller_initialization(self):
        """Test controller initialization."""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.data_file, self.data_file)

    def test_data_loading(self):
        """Test data loading from JSON file."""
        data = self.controller.load_data()

        self.assertIsNotNone(data)
        self.assertIn("ProductItems", data)
        self.assertIsInstance(data["ProductItems"], list)
        self.assertGreater(len(data["ProductItems"]), 0)

    def test_column_analysis(self):
        """Test column analysis functionality."""
        self.controller.load_data()

        product_columns = self.controller.get_product_columns()
        repr_columns = self.controller.get_representation_columns()

        self.assertIsInstance(product_columns, list)
        self.assertIsInstance(repr_columns, list)
        self.assertGreater(len(product_columns), 0)
        self.assertGreater(len(repr_columns), 0)

        # Check required columns
        self.assertIn("Folder Path", product_columns)
        self.assertIn("Product Type", product_columns)
        self.assertIn("File Path", repr_columns)

    def test_products_retrieval(self):
        """Test product data retrieval."""
        self.controller.load_data()
        products = self.controller.get_products()

        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)

        # Check first product structure
        first_product = products[0]
        self.assertIn("id", first_product)
        self.assertIn("data", first_product)
        self.assertIn("representations", first_product)
        self.assertIsInstance(first_product["representations"], list)

    def test_data_summary(self):
        """Test data summary statistics."""
        self.controller.load_data()
        summary = self.controller.get_data_summary()

        self.assertIsInstance(summary, dict)
        self.assertIn("product_count", summary)
        self.assertIn("representation_count", summary)
        self.assertGreater(summary["product_count"], 0)
        self.assertGreater(summary["representation_count"], 0)

    def test_checkbox_column_detection(self):
        """Test checkbox column detection."""
        self.assertTrue(self.controller.is_checkbox_column("Enabled"))
        self.assertFalse(self.controller.is_checkbox_column("File Path"))

    @unittest.skipIf(not QT_AVAILABLE, "Qt not available")
    def test_model_creation_with_qt(self):
        """Test model creation with Qt available."""
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        try:
            model = ProductTreeModel(self.controller)
            self.assertIsNotNone(model)

            # Test model properties
            self.assertGreaterEqual(model.columnCount(), 1)
            self.assertGreaterEqual(model.rowCount(), 1)

        finally:
            if app:
                app.quit()

    def test_column_value_handling(self):
        """Test column value handling methods."""
        self.controller.load_data()
        products = self.controller.get_products()

        if products:
            first_product = products[0]
            product_data = first_product["data"]

            # Test has_column_value
            for key in product_data.keys():
                self.assertTrue(
                    self.controller.has_column_value(product_data, key)
                )

            self.assertFalse(
                self.controller.has_column_value(
                    product_data, "NonExistentKey"
                )
            )

            # Test get_column_value
            for key, expected_value in product_data.items():
                actual_value = self.controller.get_column_value(
                    product_data, key
                )
                self.assertEqual(actual_value, expected_value)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.data_file = os.path.join(current_dir, "data.json")

    def test_complete_workflow(self):
        """Test complete data loading and processing workflow."""
        # Initialize controller
        controller = DataController(self.data_file)

        # Load data
        data = controller.load_data()
        self.assertIsNotNone(data)

        # Get structured data
        products = controller.get_products()
        self.assertGreater(len(products), 0)

        # Check data integrity
        for product in products:
            self.assertIn("data", product)
            self.assertIn("representations", product)

            for repr_item in product["representations"]:
                self.assertIn("data", repr_item)

    def test_file_paths(self):
        """Test that all required files exist."""
        files_to_check = [
            "main.py",
            "controller.py",
            "data.json",
            "style.css",
            "run_app.ps1",
            os.path.join("ui", "ui.py"),
            os.path.join("ui", "model.py"),
            os.path.join("ui", "view.py"),
            os.path.join("ui", "delegate.py"),
            os.path.join("ui", "styles.py"),
        ]

        for file_path in files_to_check:
            full_path = os.path.join(current_dir, file_path)
            self.assertTrue(
                os.path.exists(full_path),
                f"Required file not found: {file_path}",
            )


def run_tests():
    """Run all tests and return results."""
    print("=== Product Tree View Test Suite ===")
    print(f"Python version: {sys.version}")
    print(f"Qt available: {QT_AVAILABLE}")
    print(f"Test directory: {current_dir}")
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestProductTreeView))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
