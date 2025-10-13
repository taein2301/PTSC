"""
File Validation Utilities

This module provides functions to validate uploaded files including:
- File extension validation
- File size validation
- MIME type validation
- XML format validation
- C file syntax validation
"""

import os
from typing import Tuple, Optional
import xml.etree.ElementTree as ET


# Maximum file size: 10MB
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'jmx': ['.jmx'],
    'c': ['.c', '.h'],
    'all': ['.jmx', '.c', '.h']
}


def validate_file_extension(filename: str, expected_type: str = 'all') -> Tuple[bool, str]:
    """
    Validate if the file has the correct extension.

    Args:
        filename: Name of the file to validate
        expected_type: Expected file type ('jmx', 'c', or 'all')

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_file_extension("test.jmx", "jmx")
        (True, "")
        >>> validate_file_extension("test.txt", "jmx")
        (False, "Invalid file extension. Expected: .jmx")
    """
    if not filename:
        return False, "Filename is empty"

    ext = os.path.splitext(filename)[1].lower()

    if expected_type not in SUPPORTED_EXTENSIONS:
        return False, f"Unknown file type: {expected_type}"

    allowed_extensions = SUPPORTED_EXTENSIONS[expected_type]

    if ext not in allowed_extensions:
        expected_str = ", ".join(allowed_extensions)
        return False, f"Invalid file extension. Expected: {expected_str}, Got: {ext}"

    return True, ""


def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE_BYTES) -> Tuple[bool, str]:
    """
    Validate if the file size is within acceptable limits.

    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed file size in bytes

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_file_size(1024 * 1024)  # 1MB
        (True, "")
        >>> validate_file_size(20 * 1024 * 1024)  # 20MB
        (False, "File size exceeds maximum limit...")
    """
    if file_size <= 0:
        return False, "File is empty"

    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        return False, f"File size ({actual_mb:.2f}MB) exceeds maximum limit of {max_mb:.0f}MB"

    return True, ""


def validate_xml_format(content: str) -> Tuple[bool, str]:
    """
    Validate if the content is valid XML format.

    Args:
        content: XML content as string

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_xml_format("<root><child>test</child></root>")
        (True, "")
        >>> validate_xml_format("<root><child>test</root>")
        (False, "XML parsing error: ...")
    """
    if not content or not content.strip():
        return False, "XML content is empty"

    try:
        ET.fromstring(content)
        return True, ""
    except ET.ParseError as e:
        return False, f"XML parsing error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error while parsing XML: {str(e)}"


def validate_jmx_format(content: str) -> Tuple[bool, str]:
    """
    Validate if the content is a valid JMeter JMX file.

    Args:
        content: JMX file content as string

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> jmx_content = '<?xml version="1.0"?><jmeterTestPlan>...</jmeterTestPlan>'
        >>> validate_jmx_format(jmx_content)
        (True, "")
    """
    # First validate XML format
    is_valid, error_msg = validate_xml_format(content)
    if not is_valid:
        return False, error_msg

    # Check for JMeter root element
    try:
        root = ET.fromstring(content)
        if root.tag != 'jmeterTestPlan':
            return False, "Not a valid JMeter JMX file: root element must be 'jmeterTestPlan'"

        # Check for required attributes
        if 'version' not in root.attrib and 'properties' not in root.attrib:
            return False, "JMX file missing required attributes"

        return True, ""
    except Exception as e:
        return False, f"Error validating JMX format: {str(e)}"


def validate_c_file_syntax(content: str) -> Tuple[bool, str]:
    """
    Basic validation for LoadRunner C script syntax.

    Args:
        content: C file content as string

    Returns:
        Tuple of (is_valid, error_message)

    Note:
        This is a basic validation that checks for common LoadRunner patterns.
        It does not perform full C syntax validation.
    """
    if not content or not content.strip():
        return False, "C file content is empty"

    # Check for basic C file indicators
    has_include = '#include' in content
    has_function = any(func in content for func in ['vuser_init', 'Action', 'vuser_end'])

    if not has_include and not has_function:
        return False, "File does not appear to be a valid C script (missing includes or functions)"

    # Check for balanced braces (basic check)
    open_braces = content.count('{')
    close_braces = content.count('}')

    if open_braces != close_braces:
        return False, f"Unbalanced braces: {open_braces} opening, {close_braces} closing"

    return True, ""


def detect_encoding(file_bytes: bytes) -> str:
    """
    Detect the encoding of a file.

    Args:
        file_bytes: Raw bytes of the file

    Returns:
        Detected encoding name ('utf-8', 'euc-kr', 'latin-1', etc.)

    Example:
        >>> with open('file.txt', 'rb') as f:
        ...     encoding = detect_encoding(f.read())
    """
    # Try common encodings in order
    encodings = ['utf-8', 'utf-8-sig', 'euc-kr', 'cp949', 'latin-1', 'ascii']

    for encoding in encodings:
        try:
            file_bytes.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue

    # Default to utf-8 if all fail
    return 'utf-8'


def check_malicious_patterns(content: str) -> Tuple[bool, Optional[str]]:
    """
    Check for potentially malicious patterns in file content.

    Args:
        content: File content to check

    Returns:
        Tuple of (is_safe, warning_message)

    Note:
        This is a basic security check and should not be relied upon
        as the sole security measure.
    """
    # Patterns that might indicate malicious content
    dangerous_patterns = [
        'eval(',
        'exec(',
        'system(',
        '__import__',
        'subprocess',
        'os.system',
        'shell=True',
    ]

    # Check for suspicious patterns
    found_patterns = []
    content_lower = content.lower()

    for pattern in dangerous_patterns:
        if pattern.lower() in content_lower:
            found_patterns.append(pattern)

    if found_patterns:
        warning = f"Warning: Found potentially dangerous patterns: {', '.join(found_patterns)}"
        return False, warning

    return True, None


def validate_file(filename: str, content: str, file_type: str) -> Tuple[bool, str]:
    """
    Comprehensive file validation combining all checks.

    Args:
        filename: Name of the file
        content: File content as string
        file_type: Expected file type ('jmx' or 'c')

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_file("test.jmx", jmx_content, "jmx")
        >>> if not is_valid:
        ...     print(f"Validation failed: {error}")
    """
    # Validate extension
    is_valid, error = validate_file_extension(filename, file_type)
    if not is_valid:
        return False, error

    # Validate content size
    content_size = len(content.encode('utf-8'))
    is_valid, error = validate_file_size(content_size)
    if not is_valid:
        return False, error

    # Check for malicious patterns
    is_safe, warning = check_malicious_patterns(content)
    if not is_safe:
        return False, warning

    # Validate format based on file type
    if file_type == 'jmx':
        is_valid, error = validate_jmx_format(content)
    elif file_type == 'c':
        is_valid, error = validate_c_file_syntax(content)
    else:
        return False, f"Unsupported file type: {file_type}"

    if not is_valid:
        return False, error

    return True, ""
