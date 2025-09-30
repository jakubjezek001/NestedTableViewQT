"""Extended string formatter with jinja2 support."""

from __future__ import annotations

import re

import jinja2

# find every ocurrence of token within string with multiple tokens
token_regex_pattern = re.compile(r"\{[^{}]+\}")

# detect expression tokens with single curly braces but exclude tokens
# with double curly braces
expression_token_regex_pattern = re.compile(
    r"\{(?![a-zA-Z_][a-zA-Z0-9_]*:[0-9a-zA-Z#+\- .]+\})[^{}]+\}(?!\})"
)


def format_jinja2_template_string(
    template_string: str, context: dict[str, str | int | float]
) -> str:
    """Format a template string using jinja2.

    Args:
        template_string (str): The template string to format.
        context (dict[str, str]): The context to use for formatting.

    Returns:
        str: The formatted string.
    """
    template = jinja2.Template(template_string)
    return template.render(context)


def extended_format(
    template_string: str, context: dict[str, str | int | float]
) -> str:
    """Format a template string using both str.format and jinja2.

    This function first tries to format the string using str.format. If there
    are any remaining tokens, it will then format the string using jinja2.

    Args:
        template_string (str): The template string to format.
        context (dict[str, str]): The context to use for formatting.

    Returns:
        str: The formatted string.
    """
    output_string = template_string

    # first convert all expression tokens to double curly braces
    # but keep those which are already in jinja2 format
    # with double curly braces
    expression_tokens = expression_token_regex_pattern.findall(template_string)
    print(f"expression_tokens: {expression_tokens}")
    if expression_tokens:
        for token in expression_tokens:
            if not token:
                continue
            # convert to jinja2 format
            jinja2_token = "{{ " + token[1:-1] + " }}"
            output_string = output_string.replace(token, jinja2_token)

    # lets format any string which is formattable with str.format
    output_string = output_string.format(**context)

    # Lets return back any remaining tokens to jinja2 format
    # they were converted to single curly braces by str.format
    # so we need to convert them back to double curly braces
    output_string = token_regex_pattern.sub(
        lambda match: "{{" + match.group(0)[1:-1] + "}}", output_string
    )

    return format_jinja2_template_string(output_string, context)


if __name__ == "__main__":
    TEMPLATE_STRING = "{{'_'.join(name.split('_')[:2]).upper()}}_v{version:03d}.{name.split('.')[-1]}"

    # at first lets try to format starndart string tempate
    context = {"name": "123_alpha_this_not.ext", "version": 1}

    output_string = extended_format(TEMPLATE_STRING, context)
    print(output_string)
