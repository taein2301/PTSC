# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Performance Test Script Converter (PTSC) - Streamlit web app for bidirectional conversion between JMeter JMX and LoadRunner C scripts. Primary: JMeter→LoadRunner (95%+ accuracy), Secondary: LoadRunner→JMeter.

**Stack:** Python 3.9+, Streamlit, lxml/xml.etree.ElementTree

## Development Commands

### Environment Setup (Windows)

```bash
# Activate virtual environment (REQUIRED before any development)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start Streamlit app (opens browser at http://localhost:8501)
streamlit run app.py
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_jmx_parser.py

# Run with coverage report
pytest --cov=. --cov-report=html tests/

# Run single test
pytest tests/test_jmx_parser.py::TestJMXParser::test_parse_http_sampler
```

### Code Quality

```bash
# Format code
python -m black app.py converters/ parsers/ generators/ utils/

# Lint code
python -m flake8 app.py converters/ parsers/ generators/ utils/

# Type checking
python -m mypy utils/comparator.py --ignore-missing-imports
```

## Architecture: 3-Stage Conversion Pipeline

All converters inherit from `BaseConverter` and follow this pattern:

### Stage 1: Validate (`validate_input()`)

- Check file format (XML structure for JMX, C syntax for LoadRunner)
- Verify required elements exist
- Return (is_valid: bool, error_message: Optional[str])

### Stage 2: Convert (`convert()`)

- **Parse** source into intermediate dict structure
- **Transform** data (reorganize, map elements)
- **Track** stats (items_total, items_converted, items_skipped)
- Return dict with {success, data, errors, warnings}

### Stage 3: Generate (`generate_output()`)

- Generate target format from intermediate structure
- Return formatted string (C script or XML)

**Entry Point:** `execute_conversion(content: str)` orchestrates all stages.

## Key Architecture Details

### Intermediate Data Structure

Converters transform source formats into this shared structure:

```python
{
  'test_plan': {
    'name': str,
    'version': str,
    # TestPlan metadata
  },
  'thread_groups': [{
    'name': str,
    'num_threads': int,
    'ramp_time': int,
    'loops': int,
    'samplers': [...],      # HTTP requests
    'headers': [...],       # Header managers
    'extractors': [...],    # Regex/JSON extractors
    'timers': [...],        # Think times
    'assertions': [...],    # Response validations
    'controllers': [...],   # Transaction/Loop/If controllers
    'cookies': [...]        # Cookie managers
  }],
  'variables': {           # User-defined variables
    'var_name': 'value'
  }
}
```

### Component Responsibilities

**Parsers** (parsers/): Parse source format → intermediate dict

- `JMXParser`: Parse JMX XML using ElementTree, handle nested hashTree elements
- `LRParser`: Parse C code, extract function calls and parameters

**Converters** (converters/): Orchestrate pipeline, track metrics

- `JMeterToLRConverter`: Calls JMXParser → reorganizes data → LRGenerator
- `LRToJMeterConverter`: Calls LRParser → transforms → JMXGenerator
- Both inherit from `BaseConverter` (defines 3-stage interface)

**Generators** (generators/): Generate target format from intermediate dict

- `LRGenerator`: Create LoadRunner C code (web_url, web_submit_data, etc.)
- `JMXGenerator`: Create JMeter JMX XML with proper structure

**Utils** (utils/):

- `validators.py`: File validation (size, encoding, format)
- `formatters.py`: Code formatting, truncation for UI
- `helpers.py`: Common utilities (file I/O, output filename generation)
- `constants.py`: Element type constants, error codes
- `comparator.py`: Side-by-side script diff with similarity metrics

### Streamlit App Structure (app.py)

Session state management for:

- Converted content (jmx_converted_content, lr_converted_content)
- Conversion logs (jmx_conversion_log, lr_conversion_log)
- Preview settings (show_full_original, show_full_converted)
- Comparison state (compare_content_left/right, compare_diff_lines)

Three main tabs:

1. **JMeter → LoadRunner**: Upload JMX → Convert → Preview/Download C script
2. **LoadRunner → JMeter**: Upload C → Convert → Preview/Download JMX
3. **Compare Scripts**: Side-by-side diff with change highlighting

## Critical Implementation Details

### JMX Parsing (JMeter Structure)

- JMeter uses `<hashTree>` elements for hierarchy: each element followed by hashTree containing children
- Parse flow: Root jmeterTestPlan → TestPlan → hashTree → ThreadGroup → hashTree → Samplers/Timers/etc.
- Method: `_parse_hash_tree()` recursively processes element + next sibling hashTree
- Variable syntax: `${varname}` in JMeter → `lr_eval_string("{varname}")` in LoadRunner

### LoadRunner Code Generation Rules

- **ALL web functions MUST end with `LAST` parameter** (required by LoadRunner API)
- Correlation placement: `web_reg_save_param()` must appear BEFORE the request it applies to
- Thread settings: Converted as comments (Runtime Settings configured in GUI)
- String escaping: Use C-style escaping for quotes and special chars
- Transaction structure: `lr_start_transaction()` before requests, `lr_end_transaction()` after

### Correlation Conversion

**JMeter RegexExtractor → LoadRunner web_reg_save_param:**

- Extract Left Boundary (LB) and Right Boundary (RB) from regex
- Example: `token":"([^"]+)` → LB=`token":"`, RB=`"`, Ordinal=1

**LoadRunner web_reg_save_param → JMeter RegexExtractor:**

- Escape special regex chars in LB/RB
- Construct pattern: `LB + ([^RB]+) + RB`
- Set match_number from Ordinal (1=first, -1=last, 0=random)

## Element Mapping Reference

### JMeter → LoadRunner

| JMeter Element | LoadRunner Function | Notes |
|----------------|---------------------|-------|
| HTTPSamplerProxy (GET) | `web_url()` | Simple GET requests |
| HTTPSamplerProxy (POST) | `web_submit_data()` | Form submissions |
| HTTPSamplerProxy (PUT/DELETE) | `web_custom_request()` | Custom HTTP methods |
| ThreadGroup | vuser_init/Action/vuser_end | Structure only, thread count → comments |
| HeaderManager | `web_add_header()` | Per-request headers |
| RegexExtractor | `web_reg_save_param()` | LB/RB extraction |
| JSONExtractor | `web_reg_save_param_json()` | JSONPath extraction |
| ConstantTimer | `lr_think_time()` | Delays in milliseconds→seconds |
| TransactionController | `lr_start/end_transaction()` | Named transactions |

### LoadRunner → JMeter

| LoadRunner Function | JMeter Element | Notes |
|---------------------|----------------|-------|
| `web_url()` | HTTPSamplerProxy (GET) | Parse URL parameter |
| `web_submit_data()` | HTTPSamplerProxy (POST) | Parse ITEMDATA array |
| `web_custom_request()` | HTTPSamplerProxy | Method from Method parameter |
| `web_add_header()` | HeaderManager | Header name/value pairs |
| `web_reg_save_param()` | RegexExtractor | LB/RB → regex pattern |
| `lr_think_time()` | ConstantTimer | Seconds→milliseconds |

## Sample Files

Located in `samples/` directory:

- `01_simple_get.jmx` / `.c` - Basic GET request
- `02_post_with_params.jmx` / `.c` - POST with form data
- `03_with_headers.jmx` / `.c` - Custom headers
- `04_with_regex_extractor.jmx` / `04_with_correlation.c` - Correlation examples
- `05_with_json_extractor.jmx` / `05_with_transaction.c` - JSON/transactions
- Additional complex scenarios (06-10.jmx)

Use these for testing changes to parsers/generators.

## Known Constraints

- JMeter plugins not supported (standard elements only)
- HTTP protocol only (no WebSocket, FTP, etc.)
- Complex custom functions require manual adjustment
- LoadRunner GUI settings (Runtime Settings) documented as comments
- Assertions converted with warnings (manual lr_error_message implementation needed)
