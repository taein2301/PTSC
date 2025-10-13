"""
Constants and configuration values for PTSC
"""

# File extensions
ALLOWED_EXTENSIONS = {
    'JMX': ['.jmx'],
    'LOADRUNNER': ['.c']
}

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Conversion directions
CONVERSION_DIRECTION = {
    'JMETER_TO_LR': 'jmeter_to_lr',
    'LR_TO_JMETER': 'lr_to_jmeter'
}

# JMeter element types
JMETER_ELEMENTS = {
    'TEST_PLAN': 'TestPlan',
    'THREAD_GROUP': 'ThreadGroup',
    'HTTP_SAMPLER': 'HTTPSamplerProxy',
    'HEADER_MANAGER': 'HeaderManager',
    'COOKIE_MANAGER': 'CookieManager',
    'REGEX_EXTRACTOR': 'RegexExtractor',
    'JSON_EXTRACTOR': 'JSONPostProcessor',
    'CONSTANT_TIMER': 'ConstantTimer',
    'RESPONSE_ASSERTION': 'ResponseAssertion',
    'TRANSACTION_CONTROLLER': 'TransactionController',
    'LOOP_CONTROLLER': 'LoopController',
    'IF_CONTROLLER': 'IfController',
    'WHILE_CONTROLLER': 'WhileController'
}

# LoadRunner function names
LR_FUNCTIONS = {
    'WEB_URL': 'web_url',
    'WEB_SUBMIT_DATA': 'web_submit_data',
    'WEB_CUSTOM_REQUEST': 'web_custom_request',
    'WEB_ADD_HEADER': 'web_add_header',
    'WEB_SET_COOKIE': 'web_set_cookie',
    'WEB_REG_SAVE_PARAM': 'web_reg_save_param',
    'WEB_REG_SAVE_PARAM_JSON': 'web_reg_save_param_json',
    'LR_THINK_TIME': 'lr_think_time',
    'LR_START_TRANSACTION': 'lr_start_transaction',
    'LR_END_TRANSACTION': 'lr_end_transaction',
    'LR_ERROR_MESSAGE': 'lr_error_message',
    'LR_ABORT': 'lr_abort',
    'LR_SAVE_STRING': 'lr_save_string',
    'LR_EVAL_STRING': 'lr_eval_string',
    'VUSER_INIT': 'vuser_init',
    'ACTION': 'Action',
    'VUSER_END': 'vuser_end'
}

# Error codes
ERROR_CODES = {
    'INVALID_FILE_TYPE': 'E001',
    'FILE_TOO_LARGE': 'E002',
    'INVALID_XML': 'E003',
    'INVALID_C_SYNTAX': 'E004',
    'PARSING_ERROR': 'E005',
    'CONVERSION_ERROR': 'E006',
    'UNSUPPORTED_ELEMENT': 'E007',
    'MISSING_REQUIRED_FIELD': 'E008'
}

# MIME types
MIME_TYPES = {
    'XML': ['text/xml', 'application/xml'],
    'TEXT': ['text/plain', 'text/x-c']
}

# Encoding
DEFAULT_ENCODING = 'utf-8'
SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'euc-kr', 'cp949']

# Conversion settings
CONVERSION_CONFIG = {
    'ACCURACY_TARGET': 0.95,  # 95% accuracy target
    'MAX_LINE_LENGTH': 2000,
    'INDENT_SIZE': 4,
    'USE_TABS': False
}
