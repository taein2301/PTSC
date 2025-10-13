"""
Project Constants

This module defines constants used throughout the application:
- JMeter element types
- LoadRunner function names
- File extensions
- Configuration values
- Error codes
"""

# Application Information
APP_NAME = "Performance Test Script Converter"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Bidirectional converter between JMeter JMX and LoadRunner C scripts"

# File Settings
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported File Extensions
EXTENSION_JMX = '.jmx'
EXTENSION_C = '.c'
EXTENSION_H = '.h'

FILE_EXTENSIONS = {
    'jmeter': [EXTENSION_JMX],
    'loadrunner': [EXTENSION_C, EXTENSION_H],
    'all': [EXTENSION_JMX, EXTENSION_C, EXTENSION_H]
}

# Encoding
DEFAULT_ENCODING = 'utf-8'
SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'euc-kr', 'cp949', 'latin-1', 'ascii']

# JMeter Element Types
JMETER_TEST_PLAN = 'TestPlan'
JMETER_THREAD_GROUP = 'ThreadGroup'
JMETER_HASH_TREE = 'hashTree'

# JMeter Samplers
JMETER_HTTP_SAMPLER = 'HTTPSamplerProxy'
JMETER_HTTP_SAMPLER_OLD = 'HTTPSampler'
JMETER_JAVA_SAMPLER = 'JavaSampler'
JMETER_DEBUG_SAMPLER = 'DebugSampler'

# JMeter Config Elements
JMETER_HEADER_MANAGER = 'HeaderManager'
JMETER_COOKIE_MANAGER = 'CookieManager'
JMETER_CACHE_MANAGER = 'CacheManager'
JMETER_DNS_CACHE_MANAGER = 'DNSCacheManager'
JMETER_USER_DEFINED_VARIABLES = 'Arguments'
JMETER_CSV_DATA_SET = 'CSVDataSet'

# JMeter Post Processors
JMETER_REGEX_EXTRACTOR = 'RegexExtractor'
JMETER_JSON_EXTRACTOR = 'JSONPostProcessor'
JMETER_XPATH_EXTRACTOR = 'XPathExtractor'
JMETER_BOUNDARY_EXTRACTOR = 'BoundaryExtractor'

# JMeter Assertions
JMETER_RESPONSE_ASSERTION = 'ResponseAssertion'
JMETER_DURATION_ASSERTION = 'DurationAssertion'
JMETER_SIZE_ASSERTION = 'SizeAssertion'
JMETER_JSON_ASSERTION = 'JSONAssertion'

# JMeter Timers
JMETER_CONSTANT_TIMER = 'ConstantTimer'
JMETER_UNIFORM_RANDOM_TIMER = 'UniformRandomTimer'
JMETER_GAUSSIAN_RANDOM_TIMER = 'GaussianRandomTimer'
JMETER_POISSON_RANDOM_TIMER = 'PoissonRandomTimer'

# JMeter Controllers
JMETER_LOOP_CONTROLLER = 'LoopController'
JMETER_IF_CONTROLLER = 'IfController'
JMETER_WHILE_CONTROLLER = 'WhileController'
JMETER_FOREACH_CONTROLLER = 'ForeachController'
JMETER_TRANSACTION_CONTROLLER = 'TransactionController'
JMETER_SIMPLE_CONTROLLER = 'GenericController'

# JMeter Listeners
JMETER_VIEW_RESULTS_TREE = 'ResultCollector'
JMETER_AGGREGATE_REPORT = 'SummaryReport'

# HTTP Methods
HTTP_METHOD_GET = 'GET'
HTTP_METHOD_POST = 'POST'
HTTP_METHOD_PUT = 'PUT'
HTTP_METHOD_DELETE = 'DELETE'
HTTP_METHOD_PATCH = 'PATCH'
HTTP_METHOD_HEAD = 'HEAD'
HTTP_METHOD_OPTIONS = 'OPTIONS'

HTTP_METHODS = [
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
    HTTP_METHOD_DELETE,
    HTTP_METHOD_PATCH,
    HTTP_METHOD_HEAD,
    HTTP_METHOD_OPTIONS
]

# LoadRunner Function Names
LR_WEB_URL = 'web_url'
LR_WEB_SUBMIT_DATA = 'web_submit_data'
LR_WEB_CUSTOM_REQUEST = 'web_custom_request'
LR_WEB_ADD_HEADER = 'web_add_header'
LR_WEB_ADD_COOKIE = 'web_add_cookie'
LR_WEB_SET_COOKIE = 'web_set_cookie'
LR_WEB_REG_SAVE_PARAM = 'web_reg_save_param'
LR_WEB_REG_SAVE_PARAM_JSON = 'web_reg_save_param_json'
LR_WEB_REG_SAVE_PARAM_XPATH = 'web_reg_save_param_xpath'
LR_WEB_REG_FIND = 'web_reg_find'
LR_THINK_TIME = 'lr_think_time'
LR_START_TRANSACTION = 'lr_start_transaction'
LR_END_TRANSACTION = 'lr_end_transaction'
LR_SAVE_STRING = 'lr_save_string'
LR_EVAL_STRING = 'lr_eval_string'
LR_ERROR_MESSAGE = 'lr_error_message'
LR_OUTPUT_MESSAGE = 'lr_output_message'
LR_ABORT = 'lr_abort'

# LoadRunner Standard Functions
LR_VUSER_INIT = 'vuser_init'
LR_ACTION = 'Action'
LR_VUSER_END = 'vuser_end'

LR_STANDARD_FUNCTIONS = [
    LR_VUSER_INIT,
    LR_ACTION,
    LR_VUSER_END
]

# LoadRunner Web Functions
LR_WEB_FUNCTIONS = [
    LR_WEB_URL,
    LR_WEB_SUBMIT_DATA,
    LR_WEB_CUSTOM_REQUEST,
    LR_WEB_ADD_HEADER,
    LR_WEB_ADD_COOKIE,
    LR_WEB_SET_COOKIE,
    LR_WEB_REG_SAVE_PARAM,
    LR_WEB_REG_SAVE_PARAM_JSON,
    LR_WEB_REG_SAVE_PARAM_XPATH,
    LR_WEB_REG_FIND
]

# LoadRunner Utility Functions
LR_UTILITY_FUNCTIONS = [
    LR_THINK_TIME,
    LR_START_TRANSACTION,
    LR_END_TRANSACTION,
    LR_SAVE_STRING,
    LR_EVAL_STRING,
    LR_ERROR_MESSAGE,
    LR_OUTPUT_MESSAGE,
    LR_ABORT
]

# LoadRunner Include Files
LR_INCLUDE_WEB_API = '#include "web_api.h"'
LR_INCLUDE_LR = '#include "lrun.h"'
LR_INCLUDE_LR_WEB = '#include "web_utils.h"'

# LoadRunner Parameter Keywords
LR_PARAM_LAST = 'LAST'
LR_PARAM_EXTRARES = 'EXTRARES'
LR_PARAM_ENDITEM = 'ENDITEM'

# Conversion Direction
DIRECTION_JMETER_TO_LR = 'jmeter_to_lr'
DIRECTION_LR_TO_JMETER = 'lr_to_jmeter'

# Conversion Status
STATUS_SUCCESS = 'success'
STATUS_PARTIAL = 'partial'
STATUS_FAILED = 'failed'
STATUS_PENDING = 'pending'

# Message Types
MSG_TYPE_INFO = 'info'
MSG_TYPE_SUCCESS = 'success'
MSG_TYPE_WARNING = 'warning'
MSG_TYPE_ERROR = 'error'

# Error Codes
ERROR_INVALID_FILE = 1001
ERROR_FILE_TOO_LARGE = 1002
ERROR_INVALID_FORMAT = 1003
ERROR_PARSING_FAILED = 1004
ERROR_CONVERSION_FAILED = 1005
ERROR_GENERATION_FAILED = 1006
ERROR_UNSUPPORTED_ELEMENT = 1007
ERROR_VALIDATION_FAILED = 1008

ERROR_MESSAGES = {
    ERROR_INVALID_FILE: "Invalid file format",
    ERROR_FILE_TOO_LARGE: "File size exceeds maximum limit",
    ERROR_INVALID_FORMAT: "Invalid file format",
    ERROR_PARSING_FAILED: "Failed to parse input file",
    ERROR_CONVERSION_FAILED: "Conversion failed",
    ERROR_GENERATION_FAILED: "Failed to generate output",
    ERROR_UNSUPPORTED_ELEMENT: "Unsupported element encountered",
    ERROR_VALIDATION_FAILED: "Validation failed"
}

# Regex Patterns
PATTERN_VARIABLE_JMETER = r'\$\{([^}]+)\}'  # ${varname}
PATTERN_VARIABLE_LR = r'\{([^}]+)\}'  # {varname}
PATTERN_FUNCTION_CALL = r'(\w+)\s*\('  # function_name(
PATTERN_C_COMMENT_SINGLE = r'//.*?$'
PATTERN_C_COMMENT_MULTI = r'/\*.*?\*/'

# Code Formatting
INDENT_SIZE_C = 4  # spaces
INDENT_SIZE_XML = 2  # spaces
MAX_LINE_LENGTH = 120
COMMENT_ALIGN_COLUMN = 40

# UI Settings
UI_TITLE = "Performance Test Script Converter"
UI_ICON = "🔄"
UI_LAYOUT = "wide"
UI_SIDEBAR_STATE = "expanded"

# UI Messages
UI_MSG_UPLOAD_FILE = "Upload your file to convert"
UI_MSG_SELECT_DIRECTION = "Select conversion direction"
UI_MSG_PROCESSING = "Processing your file..."
UI_MSG_SUCCESS = "Conversion completed successfully!"
UI_MSG_PARTIAL_SUCCESS = "Conversion completed with warnings"
UI_MSG_FAILED = "Conversion failed"

# Conversion Targets
TARGET_ACCURACY = 0.95  # 95% conversion accuracy target

# JMeter Property Types
JMETER_PROP_STRING = 'stringProp'
JMETER_PROP_BOOL = 'boolProp'
JMETER_PROP_INT = 'intProp'
JMETER_PROP_LONG = 'longProp'
JMETER_PROP_ELEMENT = 'elementProp'
JMETER_PROP_COLLECTION = 'collectionProp'
JMETER_PROP_OBJECT = 'objProp'

# Default Values
DEFAULT_THREAD_COUNT = 1
DEFAULT_RAMP_UP_TIME = 1
DEFAULT_LOOP_COUNT = 1
DEFAULT_THINK_TIME = 0
DEFAULT_HTTP_PORT = 80
DEFAULT_HTTPS_PORT = 443

# Timeout Values (in seconds)
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_RESPONSE_TIMEOUT = 60

# Content Types
CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'
CONTENT_TYPE_FORM = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTIPART = 'multipart/form-data'
CONTENT_TYPE_TEXT = 'text/plain'
CONTENT_TYPE_HTML = 'text/html'

CONTENT_TYPES = [
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_XML,
    CONTENT_TYPE_FORM,
    CONTENT_TYPE_MULTIPART,
    CONTENT_TYPE_TEXT,
    CONTENT_TYPE_HTML
]

# Protocols
PROTOCOL_HTTP = 'http'
PROTOCOL_HTTPS = 'https'

PROTOCOLS = [PROTOCOL_HTTP, PROTOCOL_HTTPS]

# Transaction Status
TRANSACTION_AUTO = 'AUTO'
TRANSACTION_PASS = 'PASS'
TRANSACTION_FAIL = 'FAIL'
TRANSACTION_STOP = 'STOP'

# Ordinal Values (for correlation)
ORDINAL_ALL = 'All'
ORDINAL_FIRST = '1'
ORDINAL_LAST = '-1'

# Template Values
TEMPLATE_VAR_PREFIX = '$'
TEMPLATE_GROUP_PREFIX = '$'

# File Generation Templates
TEMPLATE_LR_HEADER = """/*
 * {title}
 *
 * Generated by Performance Test Script Converter
 * Date: {date}
 * Source: {source_file}
 *
 * WARNING: This is an auto-generated script.
 * Review and test thoroughly before use.
 */

#include "web_api.h"
"""

TEMPLATE_LR_VUSER_INIT = """
{func_name}()
{{
    // Initialize virtual user
    lr_output_message("Starting {func_name}");

    return 0;
}}
"""

TEMPLATE_LR_ACTION = """
{func_name}()
{{
    // Main action
    lr_output_message("Starting {func_name}");

{body}

    return 0;
}}
"""

TEMPLATE_LR_VUSER_END = """
{func_name}()
{{
    // Cleanup
    lr_output_message("Ending {func_name}");

    return 0;
}}
"""

# XML Declaration
XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'

# JMeter XML Namespaces
JMETER_NAMESPACE = 'http://jakarta.apache.org/jmeter/save'
JMETER_TESTPLAN_VERSION = '1.2'
JMETER_PROPERTIES = '5.0'
JMETER_JMETER_VERSION = '5.5'

# Conversion Mappings
JMETER_TO_LR_MAPPING = {
    JMETER_HTTP_SAMPLER: {
        HTTP_METHOD_GET: LR_WEB_URL,
        HTTP_METHOD_POST: LR_WEB_SUBMIT_DATA,
        HTTP_METHOD_PUT: LR_WEB_CUSTOM_REQUEST,
        HTTP_METHOD_DELETE: LR_WEB_CUSTOM_REQUEST,
        HTTP_METHOD_PATCH: LR_WEB_CUSTOM_REQUEST
    },
    JMETER_HEADER_MANAGER: LR_WEB_ADD_HEADER,
    JMETER_REGEX_EXTRACTOR: LR_WEB_REG_SAVE_PARAM,
    JMETER_JSON_EXTRACTOR: LR_WEB_REG_SAVE_PARAM_JSON,
    JMETER_CONSTANT_TIMER: LR_THINK_TIME,
    JMETER_TRANSACTION_CONTROLLER: (LR_START_TRANSACTION, LR_END_TRANSACTION)
}

# Feature Support Status
FEATURE_FULLY_SUPPORTED = 'fully_supported'
FEATURE_PARTIALLY_SUPPORTED = 'partially_supported'
FEATURE_NOT_SUPPORTED = 'not_supported'

# Log Levels
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_CRITICAL = 'CRITICAL'
