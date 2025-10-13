"""
Utils module for Performance Test Script Converter.
Contains utility functions for validation, formatting, and helpers.
"""

# Import constants
from .constants import (
    APP_NAME,
    APP_VERSION,
    MAX_FILE_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
    FILE_EXTENSIONS,
    DEFAULT_ENCODING,
    SUPPORTED_ENCODINGS,
    ERROR_MESSAGES,
    ERROR_INVALID_FILE,
    ERROR_FILE_TOO_LARGE,
    ERROR_PARSING_FAILED,
    HTTP_METHODS,
    CONTENT_TYPES,
    JMETER_HTTP_SAMPLER,
    JMETER_THREAD_GROUP,
    JMETER_HEADER_MANAGER,
    JMETER_REGEX_EXTRACTOR,
    JMETER_JSON_EXTRACTOR,
    JMETER_CONSTANT_TIMER,
    JMETER_TRANSACTION_CONTROLLER,
    JMETER_HASH_TREE,
    LR_WEB_URL,
    LR_WEB_SUBMIT_DATA,
    LR_WEB_CUSTOM_REQUEST,
    LR_WEB_ADD_HEADER,
    LR_WEB_REG_SAVE_PARAM,
    LR_WEB_REG_SAVE_PARAM_JSON,
    LR_THINK_TIME,
    LR_START_TRANSACTION,
    LR_END_TRANSACTION,
    DIRECTION_JMETER_TO_LR,
    DIRECTION_LR_TO_JMETER
)

# Import validation functions
from .validators import (
    validate_file_extension,
    validate_file_size,
    validate_xml_format,
    validate_jmx_format,
    validate_c_file_syntax,
    detect_encoding,
    check_malicious_patterns,
    validate_file
)

# Import formatting functions
from .formatters import (
    format_c_code,
    format_xml_code,
    format_jmx_code,
    align_code_comments,
    remove_extra_blank_lines,
    beautify_c_code,
    beautify_xml_code,
    strip_comments,
    add_header_comment
)

# Import helper functions
from .helpers import (
    read_file,
    write_file,
    generate_output_filename,
    generate_timestamp,
    format_file_size,
    format_error_message,
    format_warning_message,
    format_success_message,
    sanitize_filename,
    extract_variable_name,
    convert_variable_reference,
    escape_c_string,
    unescape_c_string,
    split_url,
    join_url,
    parse_key_value_pairs,
    get_file_extension,
    ensure_directory_exists
)

__all__ = [
    # Constants
    'APP_NAME',
    'APP_VERSION',
    'MAX_FILE_SIZE_MB',
    'MAX_FILE_SIZE_BYTES',
    'FILE_EXTENSIONS',
    'DEFAULT_ENCODING',
    'SUPPORTED_ENCODINGS',
    'ERROR_MESSAGES',
    'ERROR_INVALID_FILE',
    'ERROR_FILE_TOO_LARGE',
    'ERROR_PARSING_FAILED',
    'HTTP_METHODS',
    'CONTENT_TYPES',
    'JMETER_HTTP_SAMPLER',
    'JMETER_THREAD_GROUP',
    'JMETER_HEADER_MANAGER',
    'JMETER_REGEX_EXTRACTOR',
    'JMETER_JSON_EXTRACTOR',
    'JMETER_CONSTANT_TIMER',
    'JMETER_TRANSACTION_CONTROLLER',
    'JMETER_HASH_TREE',
    'LR_WEB_URL',
    'LR_WEB_SUBMIT_DATA',
    'LR_WEB_CUSTOM_REQUEST',
    'LR_WEB_ADD_HEADER',
    'LR_WEB_REG_SAVE_PARAM',
    'LR_WEB_REG_SAVE_PARAM_JSON',
    'LR_THINK_TIME',
    'LR_START_TRANSACTION',
    'LR_END_TRANSACTION',
    'DIRECTION_JMETER_TO_LR',
    'DIRECTION_LR_TO_JMETER',
    # Validators
    'validate_file_extension',
    'validate_file_size',
    'validate_xml_format',
    'validate_jmx_format',
    'validate_c_file_syntax',
    'detect_encoding',
    'check_malicious_patterns',
    'validate_file',
    # Formatters
    'format_c_code',
    'format_xml_code',
    'format_jmx_code',
    'align_code_comments',
    'remove_extra_blank_lines',
    'beautify_c_code',
    'beautify_xml_code',
    'strip_comments',
    'add_header_comment',
    # Helpers
    'read_file',
    'write_file',
    'generate_output_filename',
    'generate_timestamp',
    'format_file_size',
    'format_error_message',
    'format_warning_message',
    'format_success_message',
    'sanitize_filename',
    'extract_variable_name',
    'convert_variable_reference',
    'escape_c_string',
    'unescape_c_string',
    'split_url',
    'join_url',
    'parse_key_value_pairs',
    'get_file_extension',
    'ensure_directory_exists'
]
