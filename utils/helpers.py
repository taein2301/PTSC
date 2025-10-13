"""
Helper utilities for PTSC
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .constants import ERROR_CODES


class FileHelper:
    """Helper functions for file operations"""

    @staticmethod
    def generate_output_filename(input_filename: str, output_ext: str) -> str:
        """
        Generate output filename based on input filename

        Args:
            input_filename: Original filename
            output_ext: Extension for output file (.c or .jmx)

        Returns:
            Generated output filename
        """
        input_path = Path(input_filename)
        base_name = input_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"{base_name}_converted_{timestamp}{output_ext}"

    @staticmethod
    def get_file_info(filename: str, file_size: int) -> Dict[str, Any]:
        """
        Get file information dictionary

        Args:
            filename: Name of the file
            file_size: Size of file in bytes

        Returns:
            Dictionary with file information
        """
        path = Path(filename)

        return {
            'name': filename,
            'stem': path.stem,
            'extension': path.suffix,
            'size_bytes': file_size,
            'size_kb': file_size / 1024,
            'size_mb': file_size / (1024 * 1024)
        }


class StringHelper:
    """Helper functions for string operations"""

    @staticmethod
    def sanitize_variable_name(name: str) -> str:
        """
        Sanitize variable name to be valid in both JMeter and LoadRunner

        Args:
            name: Variable name to sanitize

        Returns:
            Sanitized variable name
        """
        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)

        # Ensure it starts with letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f"var_{sanitized}"

        return sanitized or "unnamed_var"

    @staticmethod
    def extract_jmeter_variable(text: str) -> list:
        """
        Extract JMeter variables from text (${varname})

        Args:
            text: Text containing variables

        Returns:
            List of variable names
        """
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, text)
        return matches

    @staticmethod
    def convert_jmeter_to_lr_variable(text: str) -> str:
        """
        Convert JMeter ${var} to LoadRunner lr_eval_string("{var}")

        Args:
            text: Text containing JMeter variables

        Returns:
            Text with LoadRunner variables
        """
        def replace_var(match):
            var_name = match.group(1)
            return f'lr_eval_string("{{{var_name}}}")'

        return re.sub(r'\$\{([^}]+)\}', replace_var, text)

    @staticmethod
    def convert_lr_to_jmeter_variable(text: str) -> str:
        """
        Convert LoadRunner {var} to JMeter ${var}

        Args:
            text: Text containing LoadRunner variables

        Returns:
            Text with JMeter variables
        """
        return re.sub(r'\{([^}]+)\}', r'${\1}', text)


class LogHelper:
    """Helper functions for logging and messages"""

    @staticmethod
    def format_error_message(error_code: str, message: str) -> str:
        """
        Format error message with code

        Args:
            error_code: Error code from ERROR_CODES
            message: Error message

        Returns:
            Formatted error message
        """
        return f"[{error_code}] {message}"

    @staticmethod
    def create_conversion_log(
        status: str,
        items_converted: int = 0,
        items_skipped: int = 0,
        warnings: Optional[list] = None,
        errors: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create conversion log dictionary

        Args:
            status: Conversion status (success/partial/failed)
            items_converted: Number of items successfully converted
            items_skipped: Number of items skipped
            warnings: List of warning messages
            errors: List of error messages

        Returns:
            Log dictionary
        """
        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'items_converted': items_converted,
            'items_skipped': items_skipped,
            'warnings': warnings or [],
            'errors': errors or [],
            'accuracy': items_converted / (items_converted + items_skipped) if (items_converted + items_skipped) > 0 else 0
        }

    @staticmethod
    def format_log_for_display(log: Dict[str, Any]) -> str:
        """
        Format log dictionary for display

        Args:
            log: Log dictionary from create_conversion_log

        Returns:
            Formatted log string
        """
        lines = []
        lines.append(f"Status: {log['status'].upper()}")
        lines.append(f"Timestamp: {log['timestamp']}")
        lines.append(f"Items Converted: {log['items_converted']}")
        lines.append(f"Items Skipped: {log['items_skipped']}")
        lines.append(f"Accuracy: {log['accuracy']:.1%}")

        if log['warnings']:
            lines.append("\nWarnings:")
            for warning in log['warnings']:
                lines.append(f"  ⚠️ {warning}")

        if log['errors']:
            lines.append("\nErrors:")
            for error in log['errors']:
                lines.append(f"  ❌ {error}")

        return '\n'.join(lines)


class ValidationHelper:
    """Helper functions for validation"""

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if string is a valid URL

        Args:
            url: URL string to validate

        Returns:
            True if valid URL
        """
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return bool(url_pattern.match(url))

    @staticmethod
    def is_valid_http_method(method: str) -> bool:
        """
        Check if string is a valid HTTP method

        Args:
            method: HTTP method string

        Returns:
            True if valid method
        """
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        return method.upper() in valid_methods

    @staticmethod
    def is_valid_content_type(content_type: str) -> bool:
        """
        Check if string is a valid content type

        Args:
            content_type: Content-Type string

        Returns:
            True if valid content type
        """
        # Basic content type pattern
        pattern = r'^[a-z]+/[a-z0-9\-\+\.]+(?:;\s*charset=[a-z0-9\-]+)?$'
        return bool(re.match(pattern, content_type.lower()))
