#!/usr/bin/env python3
"""
Test script for type preservation logic in the delegate.

This tests the type conversion logic used in setModelData to ensure
integer values stay integers, floats stay floats, etc.
"""

def preserve_data_type(new_value, original_value):
    """
    Simulate the type preservation logic from the delegate.
    This mirrors the logic in delegate.py setModelData method.
    """
    if original_value is None:
        return new_value
    
    if not isinstance(new_value, type(original_value)):
        try:
            if isinstance(original_value, bool):
                # Handle boolean conversion
                if isinstance(new_value, str):
                    return new_value.lower() in ["true", "1", "yes", "on"]
                else:
                    return bool(new_value)
            elif isinstance(original_value, int):
                # Convert to int, handling empty strings
                return int(float(str(new_value))) if str(new_value).strip() else 0
            elif isinstance(original_value, float):
                # Convert to float, handling empty strings
                return float(str(new_value)) if str(new_value).strip() else 0.0
            elif isinstance(original_value, str):
                # Keep as string
                return str(new_value)
        except (ValueError, TypeError):
            # If conversion fails, keep original type's default
            if isinstance(original_value, (int, float)):
                return type(original_value)(0)
            elif isinstance(original_value, bool):
                return False
            else:
                return str(new_value)
    
    return new_value


def test_type_preservation():
    """Test the type preservation logic."""
    print("Testing type preservation logic...")
    print("=" * 50)
    
    test_cases = [
        # (original_value, editor_value, expected_result, expected_type)
        (1920, "1920", 1920, int),
        (1080, "1080", 1080, int),
        (24.0, "24.0", 24.0, float),
        (True, "true", True, bool),
        (False, "false", False, bool),
        (True, "1", True, bool),
        (False, "0", False, bool),
        ("hello", "world", "world", str),
        (42, "42.5", 42, int),  # Float string to int should truncate
        (3.14, "2.71", 2.71, float),
        (100, "", 0, int),  # Empty string to int
        (3.14, "", 0.0, float),  # Empty string to float
    ]
    
    passed = 0
    failed = 0
    
    for i, (original, editor_val, expected, expected_type) in enumerate(test_cases, 1):
        result = preserve_data_type(editor_val, original)
        result_type = type(result)
        
        test_passed = (result == expected and result_type == expected_type)
        
        status = "✓ PASS" if test_passed else "✗ FAIL"
        print(f"Test {i:2d}: {status}")
        print(f"  Original: {original} ({type(original).__name__})")
        print(f"  Editor:   {editor_val} ({type(editor_val).__name__})")
        print(f"  Result:   {result} ({result_type.__name__})")
        print(f"  Expected: {expected} ({expected_type.__name__})")
        
        if test_passed:
            passed += 1
        else:
            failed += 1
            print(f"  ERROR: Expected {expected} ({expected_type.__name__}), got {result} ({result_type.__name__})")
        
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All type preservation tests passed!")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        return False


def test_real_world_scenario():
    """Test with real data from the JSON file."""
    print("\nTesting with real-world data scenarios...")
    print("=" * 50)
    
    # Simulate data from the JSON file
    real_data_cases = [
        # ProductItem data
        (1920, "1920"),  # Width
        (1080, "1080"),  # Height
        (1.0, "1.0"),    # Pixel Aspect
        (24.0, "24.0"),  # FPS
        (8, "8"),        # Handles
        ("v003", "v004"), # Version (string to string)
        (True, "true"),   # Slate Exists
        (False, "false"), # Boolean field
    ]
    
    print("Simulating user editing cells in the application:")
    for original, user_input in real_data_cases:
        result = preserve_data_type(user_input, original)
        type_preserved = type(result) == type(original)
        
        status = "✓" if type_preserved else "✗"
        print(f"{status} {original} → '{user_input}' → {result} ({type(result).__name__})")
    
    print("\nThis simulates what happens when a user:")
    print("1. Double-clicks a cell (e.g., Width: 1920)")  
    print("2. Edits the value in the text editor")
    print("3. Presses Enter to save")
    print("4. The delegate preserves the original type (int)")


if __name__ == "__main__":
    success = test_type_preservation()
    test_real_world_scenario()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Type preservation logic is working correctly!")
        print("The delegate will now preserve data types when saving to JSON.")
    else:
        print("❌ Type preservation logic needs fixing.")