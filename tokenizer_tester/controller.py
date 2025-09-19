#!/usr/bin/env python3
"""Controller module for tokenizer template tester.

This module handles data preparation and tokenizer logic for the template tester.
"""

import os
import random
from typing import Any, Dict


def parse_tokens(input_path: str, input_template: str) -> Dict[str, Any]:
    """Parse tokens from input path using the provided template.

    This is a mockup function that generates random token data for testing purposes.
    In the future, this will be replaced with actual tokenizer parsing logic.

    Args:
        input_path: The file path to analyze for token extraction.
        input_template: The template string containing token placeholders.

    Returns:
        Dictionary mapping token names to their resolved values.
        Returns empty dict if no tokens are found.
    """
    # If either input is empty, return empty dict
    if not input_path.strip() or not input_template.strip():
        return {}

    # Mock token data for testing the UI
    mock_tokens = {
        "project": "TestProject",
        "sequence": "001_intro",
        "shot": "shot_010",
        "version": "v001",
        "artist": "john.doe",
        "department": "lighting",
        "task": "master",
        "frame": "1001",
        "extension": "exr",
        "resolution": "2048x1080",
        "date": "2024-01-15",
        "time": "14:30:25",
    }

    # Randomly remove some tokens to test error handling (red cells)
    tokens_to_remove = random.sample(
        list(mock_tokens.keys()), k=random.randint(0, 3)
    )
    for token in tokens_to_remove:
        del mock_tokens[token]

    # Add some tokens with None values to test error display
    error_tokens = ["missing_token", "unresolved_var"]
    num_errors = random.randint(0, 2)
    for i in range(num_errors):
        if i < len(error_tokens):
            mock_tokens[error_tokens[i]] = None

    return mock_tokens


def validate_path(path: str) -> bool:
    """Validate if the provided path exists and is accessible.

    Args:
        path: File or directory path to validate.

    Returns:
        True if path exists and is accessible, False otherwise.
    """
    if not path.strip():
        return False

    try:
        return os.path.exists(path)
    except (OSError, ValueError):
        return False


def extract_template_tokens(template: str) -> list[str]:
    """Extract token placeholders from a template string.

    This function identifies token patterns in the template for validation.
    Common patterns might be {token}, <token>, ${token}, etc.

    Args:
        template: The template string to analyze.

    Returns:
        List of token names found in the template.
    """
    import re

    if not template.strip():
        return []

    # Pattern to match common token formats: {token}, <token>, ${token}
    patterns = [
        r"\{([^}]+)\}",  # {token}
        r"<([^>]+)>",  # <token>
        r"\$\{([^}]+)\}",  # ${token}
    ]

    tokens = []
    for pattern in patterns:
        matches = re.findall(pattern, template)
        tokens.extend(matches)

    return list(set(tokens))  # Remove duplicates
