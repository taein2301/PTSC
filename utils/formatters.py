"""
Code Formatting Utilities

This module provides functions for formatting and beautifying code:
- C code indentation
- XML code indentation
- Code alignment
- Comment formatting
"""

import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List


def format_c_code(code: str, indent_size: int = 4) -> str:
    """
    Format C code with proper indentation.

    Args:
        code: C code as string
        indent_size: Number of spaces per indentation level

    Returns:
        Formatted C code

    Example:
        >>> code = "int main(){\\nif(true){\\nreturn 0;\\n}\\n}"
        >>> print(format_c_code(code))
    """
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    in_multiline_comment = False

    for line in lines:
        stripped = line.strip()

        # Handle empty lines
        if not stripped:
            formatted_lines.append('')
            continue

        # Track multiline comments
        if '/*' in stripped and '*/' not in stripped:
            in_multiline_comment = True
        elif '*/' in stripped:
            in_multiline_comment = False

        # Don't reformat preprocessor directives
        if stripped.startswith('#'):
            formatted_lines.append(stripped)
            continue

        # Decrease indent for closing braces
        if stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)

        # Add indentation
        if in_multiline_comment and not stripped.startswith('/*'):
            # Keep multiline comment indentation
            formatted_lines.append(' ' * (indent_level * indent_size) + ' ' + stripped)
        else:
            formatted_lines.append(' ' * (indent_level * indent_size) + stripped)

        # Increase indent after opening braces
        if stripped.endswith('{'):
            indent_level += 1
        # Handle closing brace on same line
        elif '}' in stripped and '{' in stripped:
            pass  # No change in indent level
        elif stripped.endswith('}'):
            pass  # Already decreased above

    return '\n'.join(formatted_lines)


def format_xml_code(xml_string: str, indent_size: int = 2) -> str:
    """
    Format XML code with proper indentation.

    Args:
        xml_string: XML content as string
        indent_size: Number of spaces per indentation level

    Returns:
        Formatted XML string

    Example:
        >>> xml = "<root><child>value</child></root>"
        >>> print(format_xml_code(xml))
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_string)

        # Convert to pretty string using minidom
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)

        # Get pretty XML with specified indentation
        pretty_xml = dom.toprettyxml(indent=' ' * indent_size)

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]

        return '\n'.join(lines)

    except Exception as e:
        # If formatting fails, return original
        return xml_string


def format_jmx_code(jmx_string: str) -> str:
    """
    Format JMeter JMX file with proper indentation.

    Args:
        jmx_string: JMX file content as string

    Returns:
        Formatted JMX string

    Note:
        Uses 2-space indentation which is standard for JMeter files.
    """
    return format_xml_code(jmx_string, indent_size=2)


def align_code_comments(code: str, column: int = 40) -> str:
    """
    Align inline comments in code to a specific column.

    Args:
        code: Code with inline comments
        column: Column number to align comments to

    Returns:
        Code with aligned comments

    Example:
        >>> code = "int x = 5; // comment\\nint y = 10; // another"
        >>> print(align_code_comments(code))
    """
    lines = code.split('\n')
    aligned_lines = []

    for line in lines:
        # Skip lines without inline comments
        if '//' not in line:
            aligned_lines.append(line)
            continue

        # Split code and comment
        parts = line.split('//', 1)
        code_part = parts[0].rstrip()
        comment_part = parts[1] if len(parts) > 1 else ''

        # Calculate spacing needed
        code_length = len(code_part)
        if code_length >= column:
            # If code is already past column, add 2 spaces
            aligned_line = f"{code_part}  //{comment_part}"
        else:
            # Align to column
            spaces_needed = column - code_length
            aligned_line = f"{code_part}{' ' * spaces_needed}//{comment_part}"

        aligned_lines.append(aligned_line)

    return '\n'.join(aligned_lines)


def remove_extra_blank_lines(code: str, max_consecutive: int = 2) -> str:
    """
    Remove excessive blank lines from code.

    Args:
        code: Code with potential extra blank lines
        max_consecutive: Maximum number of consecutive blank lines allowed

    Returns:
        Code with reduced blank lines

    Example:
        >>> code = "line1\\n\\n\\n\\n\\nline2"
        >>> result = remove_extra_blank_lines(code, max_consecutive=2)
        >>> # Result will have at most 2 blank lines between line1 and line2
    """
    lines = code.split('\n')
    result = []
    blank_count = 0

    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= max_consecutive:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)

    return '\n'.join(result)


def add_function_separators(code: str, separator_char: str = '=', length: int = 80) -> str:
    """
    Add visual separators between functions in C code.

    Args:
        code: C code
        separator_char: Character to use for separator
        length: Length of separator line

    Returns:
        Code with function separators

    Example:
        >>> code = "void func1() {\\n}\\n\\nvoid func2() {\\n}"
        >>> result = add_function_separators(code)
    """
    # Pattern to match function definitions
    function_pattern = r'^([\w\*\s]+\s+\w+\s*\([^)]*\)\s*\{)'

    lines = code.split('\n')
    result = []
    separator = '// ' + separator_char * (length - 3)

    for i, line in enumerate(lines):
        if re.match(function_pattern, line.strip()):
            # Add separator before function (except first function)
            if i > 0 and result:
                result.append('')
                result.append(separator)

        result.append(line)

    return '\n'.join(result)


def format_lr_parameters(param_string: str) -> str:
    """
    Format LoadRunner function parameters for better readability.

    Args:
        param_string: LoadRunner function parameters as string

    Returns:
        Formatted parameter string

    Example:
        >>> params = '"Name=value", "Mode=HTML", LAST'
        >>> print(format_lr_parameters(params))
    """
    # Split parameters
    parts = param_string.split(',')

    # Clean up each part
    formatted_parts = []
    for part in parts:
        stripped = part.strip()
        if stripped:
            formatted_parts.append(stripped)

    # If only a few parameters, keep on one line
    if len(formatted_parts) <= 3:
        return ', '.join(formatted_parts)

    # Otherwise, format with one parameter per line
    indent = '    '
    result = ',\n'.join(indent + part for part in formatted_parts)

    return '\n' + result + '\n'


def wrap_long_lines(code: str, max_length: int = 120) -> str:
    """
    Wrap long lines in code to a maximum length.

    Args:
        code: Code with potentially long lines
        max_length: Maximum line length

    Returns:
        Code with wrapped lines

    Note:
        This is a basic implementation and may not handle all cases perfectly.
    """
    lines = code.split('\n')
    wrapped_lines = []

    for line in lines:
        if len(line) <= max_length:
            wrapped_lines.append(line)
            continue

        # For lines that are too long, try to wrap at commas or operators
        indent = len(line) - len(line.lstrip())
        remaining = line

        while len(remaining) > max_length:
            # Find a good break point (comma, operator, etc.)
            break_point = max_length
            for i in range(max_length, max(indent, max_length // 2), -1):
                if remaining[i] in [',', '+', '-', '&', '|', ' ']:
                    break_point = i + 1
                    break

            # Add the line segment
            wrapped_lines.append(remaining[:break_point].rstrip())

            # Continue with remainder
            remaining = ' ' * (indent + 4) + remaining[break_point:].lstrip()

        # Add final segment
        if remaining.strip():
            wrapped_lines.append(remaining)

    return '\n'.join(wrapped_lines)


def beautify_c_code(code: str) -> str:
    """
    Apply all formatting rules to beautify C code.

    Args:
        code: Raw C code

    Returns:
        Beautified C code

    This is a convenience function that applies:
    - Indentation formatting
    - Extra blank line removal
    - Comment alignment
    - Line wrapping
    """
    # Apply formatting steps in order
    formatted = format_c_code(code)
    formatted = remove_extra_blank_lines(formatted)
    formatted = wrap_long_lines(formatted)

    return formatted


def beautify_xml_code(xml_string: str) -> str:
    """
    Apply all formatting rules to beautify XML code.

    Args:
        xml_string: Raw XML string

    Returns:
        Beautified XML string
    """
    formatted = format_xml_code(xml_string)
    formatted = remove_extra_blank_lines(formatted, max_consecutive=1)

    return formatted


def strip_comments(code: str, comment_type: str = 'all') -> str:
    """
    Remove comments from code.

    Args:
        code: Code with comments
        comment_type: Type of comments to remove ('single', 'multi', 'all')

    Returns:
        Code without specified comments

    Example:
        >>> code = "int x = 5; // comment\\n/* block */\\nint y = 10;"
        >>> result = strip_comments(code, 'all')
    """
    result = code

    if comment_type in ['single', 'all']:
        # Remove single-line comments
        result = re.sub(r'//.*?$', '', result, flags=re.MULTILINE)

    if comment_type in ['multi', 'all']:
        # Remove multi-line comments
        result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)

    return result


def add_header_comment(code: str, title: str, description: str = '') -> str:
    """
    Add a header comment block to code.

    Args:
        code: Code to add header to
        title: Title for the header
        description: Optional description

    Returns:
        Code with header comment

    Example:
        >>> code = "int main() { return 0; }"
        >>> result = add_header_comment(code, "Main Program", "Entry point")
    """
    header_lines = [
        '/*',
        f' * {title}',
    ]

    if description:
        header_lines.extend([
            ' *',
            f' * {description}',
        ])

    header_lines.extend([
        ' *',
        ' * Generated by Performance Test Script Converter',
        ' */',
        '',
    ])

    header = '\n'.join(header_lines)

    return header + '\n' + code
