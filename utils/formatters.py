"""
Code formatting utilities for PTSC
"""

import xml.dom.minidom as minidom
from typing import List

from .constants import CONVERSION_CONFIG


class CodeFormatter:
    """Formats code for display and output"""

    @staticmethod
    def format_xml(xml_string: str) -> str:
        """
        Format XML string with proper indentation

        Args:
            xml_string: XML content as string

        Returns:
            Formatted XML string
        """
        try:
            dom = minidom.parseString(xml_string)
            pretty_xml = dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

            # Remove extra blank lines
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            return '\n'.join(lines)

        except Exception as e:
            # If formatting fails, return original
            return xml_string

    @staticmethod
    def format_c_code(c_code: str, indent_size: int = None) -> str:
        """
        Format C code with proper indentation

        Args:
            c_code: C code as string
            indent_size: Number of spaces for indentation

        Returns:
            Formatted C code string
        """
        if indent_size is None:
            indent_size = CONVERSION_CONFIG['INDENT_SIZE']

        lines = c_code.split('\n')
        formatted_lines = []
        current_indent = 0
        in_comment = False

        for line in lines:
            stripped = line.strip()

            # Handle multi-line comments
            if '/*' in stripped:
                in_comment = True
            if '*/' in stripped:
                in_comment = False
                formatted_lines.append(' ' * (current_indent * indent_size) + stripped)
                continue

            # Skip empty lines
            if not stripped:
                formatted_lines.append('')
                continue

            # Handle braces
            if stripped.startswith('}'):
                current_indent = max(0, current_indent - 1)

            # Add indentation
            if in_comment:
                formatted_lines.append(' ' * (current_indent * indent_size) + stripped)
            else:
                formatted_lines.append(' ' * (current_indent * indent_size) + stripped)

            # Increase indent after opening brace
            if stripped.endswith('{') and not in_comment:
                current_indent += 1

        return '\n'.join(formatted_lines)

    @staticmethod
    def truncate_code(code: str, max_lines: int = 50) -> str:
        """
        Truncate code for preview

        Args:
            code: Code string
            max_lines: Maximum number of lines to show

        Returns:
            Truncated code with ellipsis if needed
        """
        lines = code.split('\n')

        if len(lines) <= max_lines:
            return code

        truncated = '\n'.join(lines[:max_lines])
        remaining = len(lines) - max_lines
        return f"{truncated}\n\n... ({remaining} more lines)"

    @staticmethod
    def add_line_numbers(code: str) -> str:
        """
        Add line numbers to code

        Args:
            code: Code string

        Returns:
            Code with line numbers
        """
        lines = code.split('\n')
        max_digits = len(str(len(lines)))

        numbered_lines = []
        for i, line in enumerate(lines, 1):
            line_num = str(i).rjust(max_digits)
            numbered_lines.append(f"{line_num} | {line}")

        return '\n'.join(numbered_lines)

    @staticmethod
    def highlight_errors(code: str, error_lines: List[int]) -> str:
        """
        Highlight error lines in code

        Args:
            code: Code string
            error_lines: List of line numbers with errors

        Returns:
            Code with error markers
        """
        lines = code.split('\n')

        highlighted_lines = []
        for i, line in enumerate(lines, 1):
            if i in error_lines:
                highlighted_lines.append(f">>> {line}  <-- ERROR")
            else:
                highlighted_lines.append(f"    {line}")

        return '\n'.join(highlighted_lines)

    @staticmethod
    def escape_c_string(text: str) -> str:
        """
        Escape special characters for C strings

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        return (text
                .replace('\\', '\\\\')
                .replace('"', '\\"')
                .replace('\n', '\\n')
                .replace('\r', '\\r')
                .replace('\t', '\\t'))

    @staticmethod
    def unescape_c_string(text: str) -> str:
        """
        Unescape C string

        Args:
            text: Escaped text

        Returns:
            Unescaped text
        """
        return (text
                .replace('\\n', '\n')
                .replace('\\r', '\r')
                .replace('\\t', '\t')
                .replace('\\"', '"')
                .replace('\\\\', '\\'))
