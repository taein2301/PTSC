"""
File validation utilities for PTSC
"""

import os
from typing import Tuple, Optional
from pathlib import Path
import xml.etree.ElementTree as ET

from .constants import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    ERROR_CODES,
    SUPPORTED_ENCODINGS
)


class FileValidator:
    """Validates uploaded files for conversion"""

    @staticmethod
    def validate_file_extension(filename: str, file_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if file has correct extension

        Args:
            filename: Name of the file
            file_type: Type of file ('JMX' or 'LOADRUNNER')

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is empty"

        file_ext = Path(filename).suffix.lower()

        if file_type.upper() not in ALLOWED_EXTENSIONS:
            return False, f"Unknown file type: {file_type}"

        allowed_exts = ALLOWED_EXTENSIONS[file_type.upper()]

        if file_ext not in allowed_exts:
            expected = ", ".join(allowed_exts)
            return False, f"{ERROR_CODES['INVALID_FILE_TYPE']}: Expected {expected}, got {file_ext}"

        return True, None

    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if file size is within limits

        Args:
            file_size: Size of file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size <= 0:
            return False, "File is empty"

        if file_size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            return False, f"{ERROR_CODES['FILE_TOO_LARGE']}: File size {actual_mb:.2f}MB exceeds maximum {max_mb}MB"

        return True, None

    @staticmethod
    def validate_xml_structure(content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate if content is valid XML

        Args:
            content: File content as bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Try different encodings
        for encoding in SUPPORTED_ENCODINGS:
            try:
                text = content.decode(encoding)
                ET.fromstring(text)
                return True, None
            except UnicodeDecodeError:
                continue
            except ET.ParseError as e:
                return False, f"{ERROR_CODES['INVALID_XML']}: XML parsing error - {str(e)}"
            except Exception as e:
                return False, f"{ERROR_CODES['INVALID_XML']}: Unexpected error - {str(e)}"

        return False, f"{ERROR_CODES['INVALID_XML']}: Unable to decode file with supported encodings"

    @staticmethod
    def validate_jmx_file(filename: str, content: bytes, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive validation for JMX files

        Args:
            filename: Name of the file
            content: File content as bytes
            file_size: Size of file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        is_valid, error = FileValidator.validate_file_extension(filename, 'JMX')
        if not is_valid:
            return False, error

        # Check size
        is_valid, error = FileValidator.validate_file_size(file_size)
        if not is_valid:
            return False, error

        # Check XML structure
        is_valid, error = FileValidator.validate_xml_structure(content)
        if not is_valid:
            return False, error

        # Check if it's a JMeter test plan
        try:
            for encoding in SUPPORTED_ENCODINGS:
                try:
                    text = content.decode(encoding)
                    root = ET.fromstring(text)

                    # Check if root element is jmeterTestPlan
                    if root.tag != 'jmeterTestPlan':
                        return False, f"{ERROR_CODES['INVALID_XML']}: Root element must be 'jmeterTestPlan', found '{root.tag}'"

                    # Check for TestPlan element
                    test_plan = root.find('.//TestPlan')
                    if test_plan is None:
                        return False, f"{ERROR_CODES['MISSING_REQUIRED_FIELD']}: No TestPlan element found"

                    return True, None

                except UnicodeDecodeError:
                    continue

            return False, f"{ERROR_CODES['INVALID_XML']}: Unable to decode JMX file"

        except Exception as e:
            return False, f"{ERROR_CODES['PARSING_ERROR']}: Error validating JMX structure - {str(e)}"

    @staticmethod
    def validate_c_file(filename: str, content: bytes, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive validation for LoadRunner C files

        Args:
            filename: Name of the file
            content: File content as bytes
            file_size: Size of file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        is_valid, error = FileValidator.validate_file_extension(filename, 'LOADRUNNER')
        if not is_valid:
            return False, error

        # Check size
        is_valid, error = FileValidator.validate_file_size(file_size)
        if not is_valid:
            return False, error

        # Try to decode content
        text = None
        for encoding in SUPPORTED_ENCODINGS:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            return False, f"{ERROR_CODES['INVALID_C_SYNTAX']}: Unable to decode C file with supported encodings"

        # Check for basic LoadRunner structure
        has_includes = '#include' in text
        has_vuser_init = 'vuser_init' in text or 'Action' in text
        has_web_functions = any(func in text for func in ['web_url', 'web_submit_data', 'web_custom_request'])

        if not (has_includes or has_vuser_init or has_web_functions):
            return False, f"{ERROR_CODES['INVALID_C_SYNTAX']}: File does not appear to be a valid LoadRunner script"

        return True, None

    @staticmethod
    def detect_encoding(content: bytes) -> str:
        """
        Detect the encoding of file content

        Args:
            content: File content as bytes

        Returns:
            Detected encoding string
        """
        for encoding in SUPPORTED_ENCODINGS:
            try:
                content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue

        # Default to utf-8 if detection fails
        return 'utf-8'
