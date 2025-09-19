from pathlib import Path
from typing import Any, Dict, Optional

from parse import parse


INPUT_PATH_STRING = "260822_VFX_Pull_038_VFX/exrs/15TS_2500_bg03_v05/4315x2428/15TS_2300_bg01_v05.1552.exr"
INPUT_TEMPLATE_STRING = "/{width:4}x{height:4d}/{project_name}_{shot}_{product_type:.2}{product_variant:.2}_v{version:d}.{padding}.{extension}"


class Tokenizer:
    """A minimalist path tokenizer that extracts tokens from file paths using templates.

    Process:
    1. Break path and template into parts using pathlib
    2. Reverse order to process from end (right to left)
    3. Use parse package to match template parts with path parts
    4. If first match (filename) fails, template is wrong - stop immediately
    5. Return all captured tokens or None if tokenization fails
    """

    def __init__(self, input_path: str, input_template: str) -> None:
        """Initialize tokenizer with input path and template.

        Args:
            input_path: The file path to tokenize
            input_template: The template string with tokens like {token_name}
        """
        self.input_path = input_path
        self.input_template = input_template

    def extract_template_tokens(self, template: str = None) -> list[str]:
        """Extract token placeholders from a template string.

        This function identifies token patterns in the template for validation.
        Common patterns might be {token}, <token>, ${token}, etc.

        Args:
            template: The template string to analyze.

        Returns:
            List of token names found in the template.
        """
        import re

        template_string = template or self.input_template

        if template_string and not template_string.strip():
            return []

        # Pattern to match common token formats: {token}
        patterns = [
            r"\{([^}:]+)(?::[^}]*)?\}",  # {token}
        ]

        tokens = []
        for pattern in patterns:
            matches = re.findall(pattern, template_string)
            tokens.extend(matches)

        return list(set(tokens))  # Remove duplicates

    def get_tokens(self) -> tuple[Optional[Dict[str, Any]], list[str]]:
        """Extract tokens from input path using the template.

        Process from right to left (filename first, then directories).
        If filename parsing fails, template is considered wrong.

        Returns:
            Tuple containing a dictionary of tokens and a list of token names.
        """
        # Convert paths to pathlib objects and get parts
        template_path = Path(self.input_template)
        input_path = Path(self.input_path)

        template_parts = list(template_path.parts)
        path_parts = list(input_path.parts)

        # Reverse both lists to process from end (right to left)
        template_parts.reverse()
        path_parts.reverse()

        # Check if we have enough path parts for the template
        if len(path_parts) < len(template_parts):
            msg = "Error: Path has fewer parts than template"
            print(msg)
            return None, [msg]

        all_tokens = {}
        error_list = []

        # first add all tokens with empty values
        for token in self.extract_template_tokens():
            all_tokens[token] = None

        # Process from end (filename first, then directories)
        for i, template_part in enumerate(template_parts):
            if i >= len(path_parts):
                message = f"Error: No corresponding path part for template part '{template_part}'"
                print(message)
                error_list.append(message)
                return None, error_list

            path_part = path_parts[i]

            # Try to parse path part using template part
            result = parse(template_part, path_part)

            if result is None:
                message = f"Error: Failed to match template '{template_part}' with path '{path_part}'"
                print(message)
                error_list.append(message)
                # If first iteration (filename) fails, stop immediately
                if i == 0:
                    print("First match (filename) failed - template is wrong")
                    return None, error_list

            # Extract tokens from parse result
            # The parse function returns a Result object with .named and .fixed attributes
            # Use safe attribute access to avoid type checker warnings
            named_tokens = getattr(result, "named", {})
            fixed_tokens = getattr(result, "fixed", ())

            if named_tokens:
                # Named tokens
                all_tokens.update(named_tokens)

            if fixed_tokens:
                # Anonymous tokens (shouldn't happen in our use case, but handle anyway)
                print(f"Matched fixed tokens: {fixed_tokens}")

            # If no tokens matched but parse succeeded, it's an exact match (no tokens)
            if not named_tokens and not fixed_tokens:
                continue

        return all_tokens, error_list
