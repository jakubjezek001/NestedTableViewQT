#!/usr/bin/env python3
"""Test script for the Batch Ingest tokenizer template tester.

This script validates the application functionality and runs basic tests
to ensure all components work correctly.
"""

import sys
import os
import time
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QTimer
from qtpy.QtTest import QTest

from ui.ui import TokenizerTesterApp
from controller import parse_tokens, validate_path
from tokenization import Tokenizer


def test_controller_functions():
    """Test the controller functions independently."""
    print("Testing controller functions...")

    # Test parse_tokens function
    print("  - Testing parse_tokens...")
    tokenizer = Tokenizer(
        "/some/test/path.exr", "{root}/{type}/{file}.{extension}"
    )
    tokens, errors = tokenizer.get_tokens()
    print(f"    Errors: {errors}")
    print(f"    Mock tokens generated: {len(tokens.keys())} tokens")
    print(f"    Sample tokens: {dict(list(tokens.items())[:3])}")

    # Test with empty inputs
    empty_tokens = parse_tokens("", "")
    assert len(empty_tokens) == 0, "Empty inputs should return empty dict"
    print("    ✓ Empty inputs handled correctly")

    # Test validate_path function
    print("  - Testing validate_path...")
    assert validate_path("") == False, "Empty path should be invalid"
    assert validate_path(__file__) == True, "Current file should be valid"
    print("    ✓ Path validation works correctly")

    # Test extract_template_tokens function
    print("  - Testing extract_template_tokens...")

    extracted = tokenizer.extract_template_tokens(
        "{project}_{shot}_v{version}.{extension}"
    )
    expected_tokens = {"project", "shot", "version", "extension"}
    assert set(extracted) == expected_tokens, (
        f"Expected {expected_tokens}, got {set(extracted)}"
    )
    print(f"    ✓ Extracted tokens: {extracted}")

    print("✓ Controller functions tests passed!\n")


def test_ui_components():
    """Test the UI components."""
    print("Testing UI components...")

    app = QApplication.instance() or QApplication(sys.argv)

    # Create main window
    window = TokenizerTesterApp()
    print("  - Main window created successfully")

    # Test setting values
    test_path = "/260822_VFX_Pull_038_VFX/exrs/15TS_2500_bg03_v05/4315x2428/15TS_2300_bg01_v05.1552.exr"
    test_template = "/{width:4}x{height:4d}/{project_name}_{shot}_{product_type:.2}{product_variant:.2}_v{version:d}.{padding}.{extension}"

    window.set_path(test_path)
    window.set_template(test_template)

    assert window.get_current_path() == test_path, (
        "Path setting/getting failed"
    )
    assert window.get_current_template() == test_template, (
        "Template setting/getting failed"
    )
    print("  - Input field operations work correctly")

    # Show window for visual testing
    window.show()
    print("  - Window displayed successfully")

    # Test model updates
    print("  - Testing model updates...")
    tokens = parse_tokens(test_path, test_template)
    window.table_model.update_tokens(tokens)

    row_count = window.table_model.rowCount()
    col_count = window.table_model.columnCount()
    print(f"    Model has {row_count} rows and {col_count} columns")

    # Test error handling
    error_tokens = {"valid_token": "value", "error_token": None}
    window.table_model.update_tokens(error_tokens)

    assert window.table_model.has_errors(), "Error detection should work"
    error_list = window.table_model.get_error_tokens()
    assert "error_token" in error_list, "Error tokens should be identified"
    print("    ✓ Error handling works correctly")

    print("✓ UI components tests passed!\n")
    return window


def run_interactive_test():
    """Run an interactive test with the full application."""
    print("Running interactive test...")

    app = QApplication.instance() or QApplication(sys.argv)

    window = TokenizerTesterApp()
    window.show()

    # Populate with test data after a short delay
    def populate_test_data():
        test_cases = [
            (
                "/project/seq001/shot010/lighting/master_v001.exr",
                "{project}/{sequence}/{shot}/{department}/{task}_v{version}.{extension}",
            ),
            (
                "/shows/testshow/assets/character/hero/modeling/publish_v003.ma",
                "{root}/{show}/assets/{assetType}/{assetName}/{task}/{status}_v{version}.{extension}",
            ),
            (
                "C:/projects/movie/shots/010/comp/comp_v005.nk",
                "{drive}/{projects}/{show}/shots/{shot}/{department}/{task}_v{version}.{extension}",
            ),
        ]

        # Cycle through test cases
        for i, (path, template) in enumerate(test_cases):
            QTimer.singleShot(
                i * 3000,
                lambda p=path, t=template: (
                    window.set_path(p),
                    window.set_template(t),
                ),
            )

    # Start populating test data after 1 second
    QTimer.singleShot(1000, populate_test_data)

    print("Interactive test started. You should see:")
    print(
        "  1. A dark-themed window with the title 'Batch Ingest tokenizer template tester'"
    )
    print("  2. Two input fields at the top (path and template)")
    print("  3. A table showing tokens and their values")
    print("  4. Test data will populate automatically every 3 seconds")
    print("  5. Some tokens should show as red/error cells (unresolved)")
    print("\nWindow should be 400x500px with 10px margins")
    print("Close the window to continue...")

    return window


def main():
    """Run all tests."""
    print("=" * 60)
    print("TOKENIZER TEMPLATE TESTER - VALIDATION TESTS")
    print("=" * 60)
    print()

    try:
        # Test controller functions
        test_controller_functions()

        # Test UI components
        window = test_ui_components()

        # Ask user if they want to run interactive test
        print("All automated tests passed!")
        print()
        response = (
            input("Run interactive visual test? (y/N): ").lower().strip()
        )

        if response in ["y", "yes"]:
            interactive_window = run_interactive_test()

            # Run the Qt event loop
            app = QApplication.instance()
            if app:
                print("\nRunning interactive test... (close window to exit)")
                return app.exec_()
        else:
            print("Skipping interactive test.")

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
