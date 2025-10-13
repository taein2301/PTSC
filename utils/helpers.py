"""
Common Helper Functions

This module provides utility functions for:
- File I/O operations
- Encoding detection and handling
- String manipulation
- Timestamp generation
- Error message formatting
"""

import os
import re
from datetime import datetime
from typing import Optional, Tuple


def read_file(file_path: str, encoding: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Read a file with automatic encoding detection.

    Args:
        file_path: Path to the file
        encoding: Optional encoding (if None, will auto-detect)

    Returns:
        Tuple of (success, content, error_message)

    Example:
        >>> success, content, error = read_file("test.txt")
        >>> if success:
        ...     print(content)
    """
    if not os.path.exists(file_path):
        return False, "", f"File not found: {file_path}"

    try:
        if encoding:
            # Use specified encoding
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return True, content, ""
        else:
            # Auto-detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()

            # Try common encodings
            for enc in ['utf-8', 'utf-8-sig', 'euc-kr', 'cp949', 'latin-1']:
                try:
                    content = raw_data.decode(enc)
                    return True, content, ""
                except UnicodeDecodeError:
                    continue

            # If all fail, use utf-8 with error handling
            content = raw_data.decode('utf-8', errors='replace')
            return True, content, "Warning: Some characters may not have decoded correctly"

    except Exception as e:
        return False, "", f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> Tuple[bool, str]:
    """
    Write content to a file.

    Args:
        file_path: Path to the file
        content: Content to write
        encoding: Encoding to use (default: utf-8)

    Returns:
        Tuple of (success, error_message)

    Example:
        >>> success, error = write_file("output.txt", "Hello World")
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)

        return True, ""

    except Exception as e:
        return False, f"Error writing file: {str(e)}"


def generate_output_filename(input_filename: str, target_type: str) -> str:
    """
    Generate output filename based on input filename and target type.

    Args:
        input_filename: Original filename
        target_type: Target file type ('lr' for LoadRunner, 'jmx' for JMeter)

    Returns:
        Generated output filename

    Example:
        >>> generate_output_filename("test.jmx", "lr")
        'test_converted.c'
        >>> generate_output_filename("script.c", "jmx")
        'script_converted.jmx'
    """
    # Get base name without extension
    base_name = os.path.splitext(input_filename)[0]

    # Determine extension
    if target_type == 'lr':
        extension = '.c'
    elif target_type == 'jmx':
        extension = '.jmx'
    else:
        extension = '.txt'

    # Generate filename
    output_name = f"{base_name}_converted{extension}"

    return output_name


def generate_timestamp(format_string: str = '%Y%m%d_%H%M%S') -> str:
    """
    Generate a timestamp string.

    Args:
        format_string: Datetime format string

    Returns:
        Formatted timestamp string

    Example:
        >>> timestamp = generate_timestamp()
        >>> print(timestamp)  # e.g., "20240113_153045"
    """
    return datetime.now().strftime(format_string)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string

    Example:
        >>> format_file_size(1024)
        '1.00 KB'
        >>> format_file_size(1048576)
        '1.00 MB'
    """
    size: float = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

    return f"{size:.2f} TB"


def format_error_message(error_type: str, details: str, line_number: Optional[int] = None) -> str:
    """
    Format an error message in a consistent way.

    Args:
        error_type: Type of error (e.g., "ParseError", "ValidationError")
        details: Error details
        line_number: Optional line number where error occurred

    Returns:
        Formatted error message

    Example:
        >>> msg = format_error_message("ValidationError", "Invalid XML", 42)
        >>> print(msg)
        '[ValidationError] Line 42: Invalid XML'
    """
    if line_number:
        return f"[{error_type}] Line {line_number}: {details}"
    else:
        return f"[{error_type}] {details}"


def format_warning_message(warning_type: str, details: str) -> str:
    """
    Format a warning message in a consistent way.

    Args:
        warning_type: Type of warning
        details: Warning details

    Returns:
        Formatted warning message

    Example:
        >>> msg = format_warning_message("ConversionWarning", "Unsupported element ignored")
        >>> print(msg)
    """
    return f"[Warning:{warning_type}] {details}"


def format_success_message(operation: str, details: str = "") -> str:
    """
    Format a success message in a consistent way.

    Args:
        operation: Operation that succeeded
        details: Optional details

    Returns:
        Formatted success message

    Example:
        >>> msg = format_success_message("Conversion", "10 samplers converted")
        >>> print(msg)
    """
    if details:
        return f"[Success] {operation}: {details}"
    else:
        return f"[Success] {operation}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename

    Example:
        >>> sanitize_filename("test<file>.txt")
        'test_file_.txt'
    """
    # Replace invalid characters with underscore
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32)

    # Limit length
    max_length = 255
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        name = name[:max_length - len(ext)]
        sanitized = name + ext

    return sanitized


def extract_variable_name(variable_ref: str, style: str = 'jmeter') -> Optional[str]:
    """
    Extract variable name from a variable reference.

    Args:
        variable_ref: Variable reference string
        style: Variable style ('jmeter' for ${var}, 'lr' for {var})

    Returns:
        Variable name or None if not a valid reference

    Example:
        >>> extract_variable_name("${username}", "jmeter")
        'username'
        >>> extract_variable_name("{token}", "lr")
        'token'
    """
    if style == 'jmeter':
        # JMeter style: ${varname}
        match = re.match(r'\$\{([^}]+)\}', variable_ref)
    elif style == 'lr':
        # LoadRunner style: {varname}
        match = re.match(r'\{([^}]+)\}', variable_ref)
    else:
        return None

    if match:
        return match.group(1)
    return None


def convert_variable_reference(var_ref: str, source: str, target: str) -> str:
    """
    Convert variable reference from one format to another.

    Args:
        var_ref: Variable reference string
        source: Source format ('jmeter' or 'lr')
        target: Target format ('jmeter' or 'lr')

    Returns:
        Converted variable reference

    Example:
        >>> convert_variable_reference("${username}", "jmeter", "lr")
        'lr_eval_string("{username}")'
        >>> convert_variable_reference("{token}", "lr", "jmeter")
        '${token}'
    """
    var_name = extract_variable_name(var_ref, source)

    if not var_name:
        return var_ref

    if target == 'lr':
        # Convert to LoadRunner format
        return f'lr_eval_string("{{{var_name}}}")'
    elif target == 'jmeter':
        # Convert to JMeter format
        return f'${{{var_name}}}'
    else:
        return var_ref


def escape_c_string(text: str) -> str:
    """
    Escape a string for use in C code.

    Args:
        text: Text to escape

    Returns:
        Escaped text

    Example:
        >>> escape_c_string('Hello "World"')
        'Hello \\\\"World\\\\"'
    """
    # Escape backslashes first
    text = text.replace('\\', '\\\\')

    # Escape quotes
    text = text.replace('"', '\\"')

    # Escape newlines
    text = text.replace('\n', '\\n')

    # Escape tabs
    text = text.replace('\t', '\\t')

    # Escape carriage returns
    text = text.replace('\r', '\\r')

    return text


def unescape_c_string(text: str) -> str:
    """
    Unescape a C string.

    Args:
        text: Escaped text

    Returns:
        Unescaped text

    Example:
        >>> unescape_c_string('Hello \\\\"World\\\\"')
        'Hello "World"'
    """
    # Unescape in reverse order
    text = text.replace('\\r', '\r')
    text = text.replace('\\t', '\t')
    text = text.replace('\\n', '\n')
    text = text.replace('\\"', '"')
    text = text.replace('\\\\', '\\')

    return text


def split_url(url: str) -> Tuple[str, str, str, str]:
    """
    Split a URL into components.

    Args:
        url: Full URL

    Returns:
        Tuple of (protocol, domain, port, path)

    Example:
        >>> split_url("https://example.com:8080/api/users")
        ('https', 'example.com', '8080', '/api/users')
    """
    # Default values
    protocol = 'http'
    domain = ''
    port = ''
    path = '/'

    # Extract protocol
    if '://' in url:
        protocol, rest = url.split('://', 1)
    else:
        rest = url

    # Extract path
    if '/' in rest:
        host_part, path = rest.split('/', 1)
        path = '/' + path
    else:
        host_part = rest
        path = '/'

    # Extract domain and port
    if ':' in host_part:
        domain, port = host_part.rsplit(':', 1)
    else:
        domain = host_part

    return protocol, domain, port, path


def join_url(protocol: str, domain: str, port: str = '', path: str = '/') -> str:
    """
    Join URL components into a full URL.

    Args:
        protocol: Protocol (http, https)
        domain: Domain name
        port: Port number (optional)
        path: Path (default: /)

    Returns:
        Full URL

    Example:
        >>> join_url("https", "example.com", "8080", "/api/users")
        'https://example.com:8080/api/users'
    """
    url = f"{protocol}://{domain}"

    if port:
        url += f":{port}"

    if not path.startswith('/'):
        path = '/' + path

    url += path

    return url


def parse_key_value_pairs(text: str, delimiter: str = '=', separator: str = '&') -> dict:
    """
    Parse key-value pairs from a string.

    Args:
        text: Text containing key-value pairs
        delimiter: Delimiter between key and value
        separator: Separator between pairs

    Returns:
        Dictionary of key-value pairs

    Example:
        >>> parse_key_value_pairs("name=John&age=30")
        {'name': 'John', 'age': '30'}
    """
    result: dict[str, str] = {}

    if not text:
        return result

    pairs = text.split(separator)

    for pair in pairs:
        if delimiter in pair:
            key, value = pair.split(delimiter, 1)
            result[key.strip()] = value.strip()

    return result


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.

    Args:
        filename: Filename or path

    Returns:
        File extension (lowercase, with dot)

    Example:
        >>> get_file_extension("test.JMX")
        '.jmx'
    """
    return os.path.splitext(filename)[1].lower()


def ensure_directory_exists(file_path: str) -> bool:
    """
    Ensure that the directory for a file path exists.

    Args:
        file_path: Full file path

    Returns:
        True if directory exists or was created successfully

    Example:
        >>> ensure_directory_exists("output/results/test.txt")
        True
    """
    directory = os.path.dirname(file_path)

    if not directory:
        return True

    if os.path.exists(directory):
        return True

    try:
        os.makedirs(directory)
        return True
    except Exception:
        return False
