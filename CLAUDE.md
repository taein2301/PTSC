# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Performance Test Script Converter (PTSC) is a Streamlit-based web application for bidirectional conversion between JMeter JMX files and LoadRunner C scripts. The primary focus is JMeter → LoadRunner conversion, with LoadRunner → JMeter as secondary priority.

**Tech Stack:**
- Python 3.9+
- Streamlit (web GUI framework)
- lxml + xml.etree.ElementTree (XML parsing)
- Target accuracy: 95%+ conversion rate

## Project Structure

```
performance-script-converter/
├── app.py                      # Streamlit main application
├── requirements.txt            # Python dependencies
├── converters/
│   ├── base_converter.py      # Abstract base class for converters
│   ├── jmeter_to_lr.py        # JMeter → LoadRunner converter
│   └── lr_to_jmeter.py        # LoadRunner → JMeter converter
├── parsers/
│   ├── jmx_parser.py          # JMX file parser
│   └── lr_parser.py           # LoadRunner C script parser
├── generators/
│   ├── lr_generator.py        # LoadRunner C code generator
│   └── jmx_generator.py       # JMX file generator
├── utils/
│   ├── validators.py          # File validation utilities
│   ├── formatters.py          # Code formatting utilities
│   ├── helpers.py             # Common helper functions
│   └── constants.py           # Project constants
├── tests/                      # Unit and integration tests
└── samples/                    # Sample conversion files
```

## Development Setup

### Virtual Environment (.venv)

This project uses Python virtual environments. Always activate the virtual environment before development:

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. --cov-report=html tests/
```

## Architecture

### Conversion Pipeline

**JMeter → LoadRunner:**
1. Validate input JMX file
2. Parse JMX using `JMXParser` (extract TestPlan, ThreadGroups, Samplers, etc.)
3. Convert parsed data using `JMeterToLRConverter`
4. Generate LoadRunner C code using `LRGenerator`
5. Return formatted C script

**LoadRunner → JMeter:**
1. Validate input C file
2. Parse LoadRunner script using `LRParser` (extract functions, parameters)
3. Convert parsed data using `LRToJMeterConverter`
4. Generate JMX using `JMXGenerator`
5. Return formatted JMX file

### Key Conversion Mappings

**JMeter → LoadRunner:**
- HTTPSamplerProxy (GET) → `web_url()`
- HTTPSamplerProxy (POST) → `web_submit_data()`
- HTTPSamplerProxy (PUT/DELETE) → `web_custom_request()`
- ThreadGroup → `vuser_init()` / `Action()` / `vuser_end()` structure
- HeaderManager → `web_add_header()`
- RegexExtractor → `web_reg_save_param()` with LB/RB
- JSONExtractor → `web_reg_save_param_json()`
- ConstantTimer → `lr_think_time()`
- ResponseAssertion → conditional `lr_error_message()` + `lr_abort()`
- Variables `${var}` → `lr_eval_string("{var}")`

**LoadRunner → JMeter:**
- `web_url()` → HTTPSamplerProxy (GET)
- `web_submit_data()` → HTTPSamplerProxy (POST)
- `web_custom_request()` → HTTPSamplerProxy (method-specific)
- `web_add_header()` → HeaderManager
- `web_reg_save_param()` → RegexExtractor (LB/RB → regex pattern)
- `lr_think_time()` → ConstantTimer
- `lr_start/end_transaction()` → TransactionController
- vuser_init/Action/vuser_end → ThreadGroups

## Core Classes

### BaseConverter (abstract)
Base class defining the conversion interface:
- `validate_input()` - validates input file format
- `convert()` - performs conversion logic
- `generate_output()` - generates output file

### JMXParser
Parses JMeter JMX files and extracts:
- TestPlan elements and global variables
- ThreadGroup configurations (threads, ramp-up, loops)
- HTTP Samplers (method, domain, path, parameters, body)
- Headers, cookies, assertions, timers
- Correlation extractors (regex, JSON)
- Controllers (Loop, If, While, Transaction)

### LRGenerator
Generates LoadRunner C code with:
- Proper script structure (includes, vuser functions)
- HTTP request functions (web_url, web_submit_data, web_custom_request)
- Correlation functions (web_reg_save_param)
- Transaction management
- Think time and error handling
- Proper indentation and formatting

### LRParser
Parses LoadRunner C scripts to extract:
- Function boundaries (vuser_init, Action, vuser_end)
- HTTP function calls and parameters
- Transaction markers
- Variable declarations and usage
- Control flow structures

### JMXGenerator
Generates valid JMX files with:
- Proper XML structure and namespaces
- TestPlan and ThreadGroup elements
- HTTPSamplerProxy configurations
- Header/Cookie managers
- Extractors and assertions
- UTF-8 encoding

## Important Implementation Notes

### JMX Parsing
- Handle nested hashTree elements correctly - JMeter uses hashTree for hierarchy
- ThreadGroup settings include: num_threads, ramp_time, loops, scheduler settings
- HTTPSamplerProxy parameters are stored as stringProp/boolProp elements
- Variable references use `${varname}` format
- Support both raw body (postBodyRaw) and argument-based body data

### LoadRunner Code Generation
- All web functions must end with `LAST` parameter
- Use proper C string escaping for quotes and special characters
- web_reg_save_param must be placed BEFORE the request it applies to
- Transaction names should be meaningful and match JMeter transaction controllers
- Include comments for settings that cannot be scripted (e.g., Runtime Settings for thread count)

### Correlation Conversion
**Regex → LB/RB:**
- Extract left boundary and right boundary from regex patterns
- Handle capture groups correctly
- Set Ordinal (1=first occurrence, -1=last, All=all)

**LB/RB → Regex:**
- Escape special regex characters in boundaries
- Create proper capture group syntax
- Handle greedy vs non-greedy matching

### Error Handling
- Validate file extensions (.jmx, .c)
- Check file size limits (max 10MB)
- Handle encoding issues (UTF-8, EUC-KR)
- Provide clear error messages for unsupported elements
- Log warnings for partial conversions

### Variable Handling
- JMeter variables `${var}` convert to LoadRunner `lr_eval_string("{var}")`
- lr_save_string creates new variables in LoadRunner
- Track variable scope and usage across the script

## Testing Requirements

- Write unit tests for each parser, generator, and converter class
- Include integration tests for full conversion workflows
- Test with real JMeter and LoadRunner scripts
- Validate generated scripts can load in target tools
- Target: 80%+ code coverage

## Code Style

- Use Python type hints for function signatures
- Write docstrings for all classes and public methods
- Follow PEP 8 style guidelines
- Use meaningful variable names (avoid abbreviations)
- Keep functions focused and small (< 50 lines preferred)

## Known Limitations

- Complex custom functions require manual adjustment
- LoadRunner GUI-based settings documented as comments
- JMeter plugins not supported
- Only standard HTTP protocol supported
- Some advanced LoadRunner functions may not have JMeter equivalents
