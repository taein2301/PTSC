"""
Performance Test Script Converter (PTSC)
Main Streamlit Application

This application provides bidirectional conversion between:
- JMeter JMX files → LoadRunner C scripts
- LoadRunner C scripts → JMeter JMX files
"""

import streamlit as st
import os
from code_editor import code_editor
from converters.jmeter_to_lr import JMeterToLRConverter
from converters.lr_to_jmeter import LRToJMeterConverter
from utils.validators import FileValidator
from utils.formatters import CodeFormatter
from utils.helpers import FileHelper
from utils.comparator import ScriptComparator, ChangeType

# Page configuration
st.set_page_config(
    page_title="Performance Test Script Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling - LG CNS Brand Colors
st.markdown("""
<style>
    /* LG CNS Color Palette:
       Primary: #A50034 (LG Red)
       Secondary: #000000 (Black)
       Accent: #666666 (Gray)
       Background: #F5F5F5 (Light Gray)
       Success: #00A651 (Green)
    */

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #A50034;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #F5F5F5;
        padding: 0.5rem;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 1.1rem;
        color: #666666;
        background-color: transparent;
        border-radius: 6px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #A50034;
        color: white;
    }
    .upload-section {
        border: 2px dashed #A50034;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
        background-color: #FAFAFA;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        background-color: #A50034;
        color: white;
        border: none;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #8B002C;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #00A651;
        color: white;
        border: none;
    }
    .stDownloadButton>button:hover {
        background-color: #008A43;
    }
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: #A50034;
    }
    /* Success/Info boxes */
    .stSuccess {
        background-color: #E8F5E9;
        border-left: 4px solid #00A651;
    }
    .stInfo {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-left: 4px solid #A50034;
    }
    /* Main content background */
    .main {
        background-color: #FFFFFF;
    }
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #F5F5F5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'jmx_converted_content' not in st.session_state:
    st.session_state.jmx_converted_content = None
if 'jmx_conversion_log' not in st.session_state:
    st.session_state.jmx_conversion_log = "Ready to convert..."
if 'jmx_output_filename' not in st.session_state:
    st.session_state.jmx_output_filename = None
if 'jmx_sample_file' not in st.session_state:
    st.session_state.jmx_sample_file = None
if 'jmx_uploader_key' not in st.session_state:
    st.session_state.jmx_uploader_key = 0

if 'lr_converted_content' not in st.session_state:
    st.session_state.lr_converted_content = None
if 'lr_conversion_log' not in st.session_state:
    st.session_state.lr_conversion_log = "Ready to convert..."
if 'lr_output_filename' not in st.session_state:
    st.session_state.lr_output_filename = None
if 'lr_sample_file' not in st.session_state:
    st.session_state.lr_sample_file = None
if 'lr_uploader_key' not in st.session_state:
    st.session_state.lr_uploader_key = 0

# Conversion settings (for future enhancements)
if 'indent_size' not in st.session_state:
    st.session_state.indent_size = 4
if 'include_comments' not in st.session_state:
    st.session_state.include_comments = True
if 'error_handling_level' not in st.session_state:
    st.session_state.error_handling_level = 'Standard'


# Conversion history
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

# Comparison mode state
if 'compare_content_left' not in st.session_state:
    st.session_state.compare_content_left = None
if 'compare_content_right' not in st.session_state:
    st.session_state.compare_content_right = None
if 'compare_filename_left' not in st.session_state:
    st.session_state.compare_filename_left = None
if 'compare_filename_right' not in st.session_state:
    st.session_state.compare_filename_right = None
if 'compare_show_unchanged' not in st.session_state:
    st.session_state.compare_show_unchanged = True
if 'compare_diff_lines' not in st.session_state:
    st.session_state.compare_diff_lines = None
if 'compare_stats' not in st.session_state:
    st.session_state.compare_stats = None


# Sample file configurations
SAMPLE_JMX_FILES = {
    "Simple GET Request": "samples/01_simple_get.jmx",
    "POST with Parameters": "samples/02_post_with_params.jmx",
    "Request with Headers": "samples/03_with_headers.jmx",
    "Regex Extractor (Correlation)": "samples/04_with_regex_extractor.jmx",
    "JSON Extractor": "samples/05_with_json_extractor.jmx",
}

SAMPLE_LR_FILES = {
    "Simple GET Request": "samples/01_simple_get.c",
    "POST with Parameters": "samples/02_post_with_params.c",
    "Request with Headers": "samples/03_with_headers.c",
    "Correlation Example": "samples/04_with_correlation.c",
    "Transaction with Think Time": "samples/05_with_transaction.c",
}


def format_xml_for_display(xml_content):
    """
    Format XML content for better display readability

    Args:
        xml_content: Raw XML string

    Returns:
        Formatted XML string with proper indentation
    """
    try:
        import xml.dom.minidom as minidom

        # Parse and prettify
        dom = minidom.parseString(xml_content)
        pretty_xml = dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

        # Remove extra blank lines
        lines = []
        for line in pretty_xml.split('\n'):
            if not line.strip():
                continue
            if line.strip().startswith('<?xml') and 'version="1.0"' in line:
                continue
            lines.append(line)

        # Add proper XML declaration
        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>'
        result = [xml_declaration] + lines

        return '\n'.join(result)
    except Exception:
        # If formatting fails, return original content
        return xml_content


def format_c_for_display(c_content):
    """
    Format C code content for better display readability
    Only cleans up excessive blank lines, preserves existing indentation

    Args:
        c_content: Raw C code string

    Returns:
        Formatted C code string with cleaned spacing
    """
    try:
        lines = c_content.split('\n')
        formatted_lines = []
        prev_line_was_blank = False

        for line in lines:
            # Skip multiple consecutive blank lines
            if not line.strip():
                if not prev_line_was_blank:
                    formatted_lines.append('')
                    prev_line_was_blank = True
                continue

            prev_line_was_blank = False
            formatted_lines.append(line)

        # Remove trailing empty lines
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()

        return '\n'.join(formatted_lines)
    except Exception:
        # If formatting fails, return original content
        return c_content


def extract_jmx_settings(jmx_content):
    """
    Extract ThreadGroup settings and user variables from JMX content for display

    Args:
        jmx_content: JMX XML content string

    Returns:
        Dictionary with test plan, thread group settings, and user variables
    """
    try:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(jmx_content)
        settings = {
            'test_plan_name': 'Unknown',
            'thread_groups': [],
            'variables': {}
        }

        # Extract test plan name
        test_plan = root.find('.//TestPlan')
        if test_plan is not None:
            name_prop = test_plan.get('testname')
            if name_prop:
                settings['test_plan_name'] = name_prop

        # Extract user defined variables
        arguments_elem = root.find(".//elementProp[@name='TestPlan.user_defined_variables']")
        if arguments_elem is not None:
            collection = arguments_elem.find(".//collectionProp[@name='Arguments.arguments']")
            if collection is not None:
                for arg_elem in collection.findall(".//elementProp[@elementType='Argument']"):
                    var_name_prop = arg_elem.find(".//stringProp[@name='Argument.name']")
                    var_value_prop = arg_elem.find(".//stringProp[@name='Argument.value']")

                    if var_name_prop is not None and var_name_prop.text:
                        var_name = var_name_prop.text
                        var_value = var_value_prop.text if var_value_prop is not None and var_value_prop.text else ''
                        settings['variables'][var_name] = var_value

        # Extract thread groups
        thread_groups = root.findall('.//ThreadGroup')
        for tg in thread_groups:
            tg_settings = {
                'name': tg.get('testname', 'Thread Group'),
                'enabled': True,
                'num_threads': 1,
                'ramp_time': 1,
                'loops': 1,
                'duration': 0,
                'delay': 0,
                'scheduler': False,
                'loop_controllers': []  # Store child LoopControllers
            }

            # Extract enabled status
            enabled_prop = tg.find(".//boolProp[@name='TestElement.enabled']")
            if enabled_prop is not None and enabled_prop.text:
                tg_settings['enabled'] = enabled_prop.text.lower() == 'true'

            # Extract num_threads
            num_threads_prop = tg.find(".//stringProp[@name='ThreadGroup.num_threads']")
            if num_threads_prop is not None and num_threads_prop.text:
                try:
                    tg_settings['num_threads'] = int(num_threads_prop.text)
                except ValueError:
                    pass

            # Extract ramp_time
            ramp_time_prop = tg.find(".//stringProp[@name='ThreadGroup.ramp_time']")
            if ramp_time_prop is not None and ramp_time_prop.text:
                try:
                    tg_settings['ramp_time'] = int(ramp_time_prop.text)
                except ValueError:
                    pass

            # Extract loops
            loop_controller = tg.find(".//elementProp[@name='ThreadGroup.main_controller']")
            if loop_controller is not None:
                # Try stringProp first (common format)
                loops_prop = loop_controller.find(".//stringProp[@name='LoopController.loops']")
                if loops_prop is None:
                    # Try intProp (alternative format)
                    loops_prop = loop_controller.find(".//intProp[@name='LoopController.loops']")

                if loops_prop is not None and loops_prop.text:
                    try:
                        tg_settings['loops'] = int(loops_prop.text)
                    except ValueError:
                        pass

            # Extract scheduler settings
            scheduler_prop = tg.find(".//boolProp[@name='ThreadGroup.scheduler']")
            if scheduler_prop is not None and scheduler_prop.text:
                tg_settings['scheduler'] = scheduler_prop.text.lower() == 'true'

            # Extract duration
            duration_prop = tg.find(".//stringProp[@name='ThreadGroup.duration']")
            if duration_prop is not None and duration_prop.text:
                try:
                    tg_settings['duration'] = int(duration_prop.text)
                except ValueError:
                    pass

            # Extract delay
            delay_prop = tg.find(".//stringProp[@name='ThreadGroup.delay']")
            if delay_prop is not None and delay_prop.text:
                try:
                    tg_settings['delay'] = int(delay_prop.text)
                except ValueError:
                    pass

            # Extract child LoopControllers (not the main_controller)
            # Find the hashTree element that follows this ThreadGroup
            # We need to look in the parent context to find sibling hashTree
            parent_map = {c: p for p in root.iter() for c in p}
            parent = parent_map.get(tg)
            if parent is not None:
                # Find index of current ThreadGroup
                children = list(parent)
                tg_index = children.index(tg)
                # The next element should be the hashTree containing children
                if tg_index + 1 < len(children):
                    tg_hashtree = children[tg_index + 1]
                    if tg_hashtree.tag == 'hashTree':
                        # Find LoopController elements in this hashTree
                        loop_controllers = tg_hashtree.findall('.//LoopController[@testclass="LoopController"]')
                        for lc in loop_controllers:
                            lc_name = lc.get('testname', 'Loop Controller')
                            lc_enabled = True
                            lc_loops = 1

                            # Check if enabled
                            lc_enabled_prop = lc.find(".//boolProp[@name='TestElement.enabled']")
                            if lc_enabled_prop is not None and lc_enabled_prop.text:
                                lc_enabled = lc_enabled_prop.text.lower() == 'true'

                            # Get loop count
                            lc_loops_prop = lc.find(".//stringProp[@name='LoopController.loops']")
                            if lc_loops_prop is None:
                                lc_loops_prop = lc.find(".//intProp[@name='LoopController.loops']")

                            if lc_loops_prop is not None and lc_loops_prop.text:
                                try:
                                    lc_loops = int(lc_loops_prop.text)
                                except ValueError:
                                    pass

                            tg_settings['loop_controllers'].append({
                                'name': lc_name,
                                'enabled': lc_enabled,
                                'loops': lc_loops
                            })

            settings['thread_groups'].append(tg_settings)

        return settings

    except Exception as e:
        return None


def load_sample_file(file_path):
    """Load a sample file from the samples directory"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    except Exception as e:
        st.error(f"Error loading sample file: {e}")
        return None


def add_to_history(direction, filename, success, message):
    """Add conversion attempt to history"""
    import datetime
    history_entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'direction': direction,
        'filename': filename,
        'success': success,
        'message': message[:200]  # Truncate long messages
    }
    st.session_state.conversion_history.insert(0, history_entry)
    # Keep only last 50 entries
    if len(st.session_state.conversion_history) > 50:
        st.session_state.conversion_history = st.session_state.conversion_history[:50]


def convert_jmx_to_lr(uploaded_file=None, content_str=None, filename=None):
    """
    Convert JMeter JMX file to LoadRunner C script

    Args:
        uploaded_file: Streamlit UploadedFile object (optional)
        content_str: File content as string (optional)
        filename: Filename for output generation (optional)

    Returns:
        Tuple of (success, output_content, log_message)
    """
    try:
        # Handle uploaded file or direct content
        if uploaded_file:
            file_content = uploaded_file.read()
            file_size = len(file_content)
            file_name = uploaded_file.name
        elif content_str:
            file_content = content_str.encode('utf-8')
            file_size = len(file_content)
            file_name = filename or "sample.jmx"
        else:
            return False, None, "No input provided"

        # Validate file
        validator = FileValidator()
        is_valid, error_msg = validator.validate_jmx_file(
            file_name,
            file_content,
            file_size
        )

        if not is_valid:
            return False, None, f"Validation Error:\n{error_msg}"

        # Decode content
        encoding = validator.detect_encoding(file_content)
        content_string = file_content.decode(encoding)

        # Perform conversion
        converter = JMeterToLRConverter()
        success, output_content, stats = converter.execute_conversion(content_string)

        # Generate log message
        if success:
            summary = converter.get_conversion_summary()
            log_msg = f"Conversion Successful!\n\n{summary}"

            # Generate output filename
            output_filename = FileHelper.generate_output_filename(file_name, '.c')
            st.session_state.jmx_output_filename = output_filename

            return True, output_content, log_msg
        else:
            errors = stats.get('errors', [])
            warnings = stats.get('warnings', [])

            log_parts = ["Conversion Failed!\n"]
            log_parts.append("=" * 60)

            # Show conversion statistics
            conv_stats = stats.get('stats', {})
            log_parts.append("\nStatistics:")
            log_parts.append(f"  Total Items: {conv_stats.get('items_total', 0)}")
            log_parts.append(f"  Converted: {conv_stats.get('items_converted', 0)}")
            log_parts.append(f"  Skipped: {conv_stats.get('items_skipped', 0)}")
            log_parts.append(f"  Accuracy: {stats.get('accuracy', 0):.1f}%\n")

            # Show errors with detailed information
            if errors:
                log_parts.append(f"Errors ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    log_parts.append(f"  [{i}] {error}")
                log_parts.append("")

            # Show warnings
            if warnings:
                log_parts.append(f"Warnings ({len(warnings)}):")
                for warning in warnings[:5]:  # Show first 5 warnings
                    log_parts.append(f"  ⚠ {warning}")
                if len(warnings) > 5:
                    log_parts.append(f"  ... and {len(warnings) - 5} more warnings")
                log_parts.append("")

            log_parts.append("=" * 60)
            log_parts.append("\nPlease check the errors above and fix the issues.")

            log_msg = "\n".join(log_parts)
            return False, None, log_msg

    except Exception as e:
        return False, None, f"Unexpected Error:\n{str(e)}"


def convert_lr_to_jmx(uploaded_file=None, content_str=None, filename=None):
    """
    Convert LoadRunner C script to JMeter JMX file

    Args:
        uploaded_file: Streamlit UploadedFile object (optional)
        content_str: File content as string (optional)
        filename: Filename for output generation (optional)

    Returns:
        Tuple of (success, output_content, log_message)
    """
    try:
        # Handle uploaded file or direct content
        if uploaded_file:
            file_content = uploaded_file.read()
            file_size = len(file_content)
            file_name = uploaded_file.name
        elif content_str:
            file_content = content_str.encode('utf-8')
            file_size = len(file_content)
            file_name = filename or "sample.c"
        else:
            return False, None, "No input provided"

        # Validate file
        validator = FileValidator()
        is_valid, error_msg = validator.validate_c_file(
            file_name,
            file_content,
            file_size
        )

        if not is_valid:
            return False, None, f"Validation Error:\n{error_msg}"

        # Decode content
        encoding = validator.detect_encoding(file_content)
        content_string = file_content.decode(encoding)

        # Perform conversion
        converter = LRToJMeterConverter()
        success, output_content, stats = converter.execute_conversion(content_string)

        # Generate log message
        if success:
            summary = converter.get_conversion_summary()
            log_msg = f"Conversion Successful!\n\n{summary}"

            # Generate output filename
            output_filename = FileHelper.generate_output_filename(file_name, '.jmx')
            st.session_state.lr_output_filename = output_filename

            return True, output_content, log_msg
        else:
            errors = stats.get('errors', [])
            warnings = stats.get('warnings', [])

            log_parts = ["Conversion Failed!\n"]
            log_parts.append("=" * 60)

            # Show conversion statistics
            conv_stats = stats.get('stats', {})
            log_parts.append("\nStatistics:")
            log_parts.append(f"  Total Items: {conv_stats.get('items_total', 0)}")
            log_parts.append(f"  Converted: {conv_stats.get('items_converted', 0)}")
            log_parts.append(f"  Skipped: {conv_stats.get('items_skipped', 0)}")
            log_parts.append(f"  Accuracy: {stats.get('accuracy', 0):.1f}%\n")

            # Show errors with detailed information
            if errors:
                log_parts.append(f"Errors ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    log_parts.append(f"  [{i}] {error}")
                log_parts.append("")

            # Show warnings
            if warnings:
                log_parts.append(f"Warnings ({len(warnings)}):")
                for warning in warnings[:5]:  # Show first 5 warnings
                    log_parts.append(f"  ⚠ {warning}")
                if len(warnings) > 5:
                    log_parts.append(f"  ... and {len(warnings) - 5} more warnings")
                log_parts.append("")

            log_parts.append("=" * 60)
            log_parts.append("\nPlease check the errors above and fix the issues.")

            log_msg = "\n".join(log_parts)
            return False, None, log_msg

    except Exception as e:
        return False, None, f"Unexpected Error:\n{str(e)}"


def main():
    """Main application function"""

    # Header section
    st.markdown('<div class="main-header">🔄 Performance Test Script Converter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">JMeter ↔ LoadRunner Script Converter</div>', unsafe_allow_html=True)

    # Version info in sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Conversion Settings")
        with st.expander("Code Formatting", expanded=False):
            st.session_state.indent_size = st.select_slider(
                "Indentation Size",
                options=[2, 4, 8],
                value=st.session_state.indent_size,
                help="Number of spaces for indentation (currently informational)"
            )

            st.session_state.include_comments = st.checkbox(
                "Include Descriptive Comments",
                value=st.session_state.include_comments,
                help="Add explanatory comments in generated code (currently informational)"
            )

        with st.expander("Error Handling", expanded=False):
            st.session_state.error_handling_level = st.selectbox(
                "Error Handling Level",
                options=['Minimal', 'Standard', 'Verbose'],
                index=['Minimal', 'Standard', 'Verbose'].index(st.session_state.error_handling_level),
                help="Level of error handling in converted scripts (currently informational)"
            )

        st.info("💡 **Note:** Settings are ready for future implementation. Current conversions use default values.")

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        **Version:** 0.2.2

        **Features:**
        - JMeter → LoadRunner conversion
        - LoadRunner → JMeter conversion
        - Sample file loading
        - Code preview with syntax highlighting
        - Conversion logs and statistics
        - File validation
        """)

        st.markdown("---")
        st.markdown("### 📚 Documentation")
        st.markdown("[GitHub Repository](https://github.com/taein2301/PTSC)")

        # Conversion History
        st.markdown("---")
        st.markdown("### 📜 Conversion History")

        if st.session_state.conversion_history:
            # Filter options
            filter_direction = st.selectbox(
                "Filter by direction:",
                options=["All", "JMeter → LoadRunner", "LoadRunner → JMeter"],
                key="history_filter"
            )

            # Filter history
            filtered_history = st.session_state.conversion_history
            if filter_direction != "All":
                filtered_history = [h for h in st.session_state.conversion_history if h['direction'] == filter_direction]

            # Display history (max 10 recent items)
            display_count = min(10, len(filtered_history))

            for i, entry in enumerate(filtered_history[:display_count]):
                status_icon = "✅" if entry['success'] else "❌"
                direction_icon = "🔵" if "JMeter" in entry['direction'].split()[0] else "🟢"

                with st.expander(f"{status_icon} {direction_icon} {entry['filename']} - {entry['timestamp']}", expanded=False):
                    st.text(f"Direction: {entry['direction']}")
                    st.text(f"Status: {'Success' if entry['success'] else 'Failed'}")
                    st.text(f"Time: {entry['timestamp']}")

                    # Show message preview
                    message_preview = entry['message'][:150] + "..." if len(entry['message']) > 150 else entry['message']
                    st.text_area("Log Preview:", message_preview, height=80, disabled=True, key=f"history_msg_{i}")

            if len(filtered_history) > display_count:
                st.info(f"Showing {display_count} of {len(filtered_history)} entries")

            # Clear history button
            if st.button("🗑️ Clear History", key="clear_history"):
                st.session_state.conversion_history = []
                st.rerun()
        else:
            st.info("No conversion history yet. Start converting files to see history here.")

        st.markdown("---")
        st.markdown("### 🔧 Supported Elements")
        with st.expander("JMeter Elements"):
            st.markdown("""
            - HTTP Samplers (GET, POST, PUT, DELETE)
            - Thread Groups
            - Header Manager
            - Cookie Manager
            - RegexExtractor
            - JSON Extractor
            - Constant Timer
            - Transaction Controller
            """)
        with st.expander("LoadRunner Functions"):
            st.markdown("""
            - web_url()
            - web_submit_data()
            - web_custom_request()
            - web_reg_save_param()
            - web_reg_save_param_json()
            - lr_think_time()
            - lr_start/end_transaction()
            """)

    # Main conversion tabs
    tab1, tab2 = st.tabs(["🔵 JMeter → LoadRunner", "🟢 LoadRunner → JMeter"])

    with tab1:
        st.markdown("### Convert JMeter JMX to LoadRunner C Script")

        # File upload section
        st.markdown("#### 📤 Upload JMX File")
        uploaded_file = st.file_uploader(
            "Upload JMX File",
            type=['jmx'],
            key=f"jmx_uploader_{st.session_state.jmx_uploader_key}",
            help="Upload a valid JMeter JMX file (max 10MB)",
            label_visibility="collapsed"
        )

        # Clear previous results if no file is uploaded and no sample is selected
        if not uploaded_file and not st.session_state.jmx_sample_file:
            if st.session_state.jmx_converted_content or 'jmx_last_file_key' in st.session_state:
                st.session_state.jmx_converted_content = None
                st.session_state.jmx_conversion_log = "Ready to convert..."
                st.session_state.jmx_output_filename = None
                if 'jmx_last_file_key' in st.session_state:
                    del st.session_state.jmx_last_file_key

        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name} | Size: {uploaded_file.size / 1024:.2f} KB")

        # Conversion Status in one line
        if st.session_state.jmx_converted_content:
            st.success("📊 Conversion Status: ✅ Conversion completed!")
        elif uploaded_file or st.session_state.jmx_sample_file:
            st.info("📊 Conversion Status: 🔄 Converting...")
        else:
            st.info("📊 Conversion Status: 💡 Please upload a JMX file to begin")

        # Auto-convert on file upload or sample file selection
        if uploaded_file or st.session_state.jmx_sample_file:
            # Generate unique file key based on content hash
            if uploaded_file:
                uploaded_file.seek(0)
                import hashlib
                file_content = uploaded_file.read()
                file_hash = hashlib.md5(file_content).hexdigest()
                current_file_key = f"{uploaded_file.name}_{uploaded_file.size}_{file_hash}"
                uploaded_file.seek(0)  # Reset for later use
            else:
                current_file_key = f"sample_{st.session_state.jmx_sample_file.get('name', 'unknown')}"

            # Check if file has changed
            needs_conversion = (
                'jmx_last_file_key' not in st.session_state or
                st.session_state.jmx_last_file_key != current_file_key
            )

            # Clear previous results immediately when file changes
            if needs_conversion:
                st.session_state.jmx_converted_content = None
                st.session_state.jmx_conversion_log = "Converting..."
                st.session_state.jmx_output_filename = None

            if needs_conversion:
                with st.spinner("Converting..."):
                    if uploaded_file:
                        uploaded_file.seek(0)  # Reset file pointer
                        success, output, log_msg = convert_jmx_to_lr(uploaded_file=uploaded_file)
                        file_name = uploaded_file.name
                    else:
                        success, output, log_msg = convert_jmx_to_lr(sample_file=st.session_state.jmx_sample_file)
                        file_name = st.session_state.jmx_sample_file.get('name', 'sample.jmx')

                    # Update session state
                    st.session_state.jmx_converted_content = output if success else None
                    st.session_state.jmx_conversion_log = log_msg
                    st.session_state.jmx_last_file_key = current_file_key

                    # Add to history
                    add_to_history("JMeter → LoadRunner", file_name, success, log_msg)

                    # Show message
                    if success:
                        st.success("✅ Conversion completed successfully!")
                    else:
                        st.error("❌ Conversion failed. Check logs for details.")
                    st.rerun()

        # Action buttons
        st.markdown("---")
        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.session_state.jmx_converted_content:
                st.download_button(
                    label="⬇️ Download Converted Script",
                    data=st.session_state.jmx_converted_content,
                    file_name=st.session_state.jmx_output_filename or "converted_script.c",
                    mime="text/plain",
                    key="download_lr"
                )

        with button_col2:
            clear_btn = st.button("🗑️ Clear All", key="clear_jmx")
            if clear_btn:
                st.session_state.jmx_converted_content = None
                st.session_state.jmx_conversion_log = "Ready to convert..."
                st.session_state.jmx_output_filename = None
                st.session_state.jmx_sample_file = None
                st.session_state.jmx_uploader_key += 1  # Increment to reset file uploader
                if 'jmx_last_file_key' in st.session_state:
                    del st.session_state.jmx_last_file_key
                st.rerun()

        # Preview section
        has_input = uploaded_file or st.session_state.jmx_sample_file
        if has_input:
            st.markdown("---")

            # Extract and display JMX settings
            try:
                if uploaded_file:
                    uploaded_file.seek(0)
                    jmx_content = uploaded_file.read().decode('utf-8')
                else:
                    jmx_content = st.session_state.jmx_sample_file['content']

                settings = extract_jmx_settings(jmx_content)

                if settings and settings['thread_groups']:
                    st.markdown("### ⚙️ LoadRunner Runtime Settings Guide")

                    # Display user variables if present
                    if settings.get('variables'):
                        st.markdown("#### 📝 JMeter User Defined Variables")
                        st.info("다음 변수들을 LoadRunner의 Runtime Settings > Parameters에서 설정하세요:")

                        # Create a table for variables
                        var_data = []
                        for var_name, var_value in settings['variables'].items():
                            var_data.append({"Variable Name": var_name, "Value": var_value})

                        if var_data:
                            import pandas as pd
                            df = pd.DataFrame(var_data)
                            st.dataframe(df, use_container_width=True, hide_index=True)

                        st.markdown("---")

                    # Display settings in an info box
                    for idx, tg in enumerate(settings['thread_groups'], 1):
                        with st.expander(f"📊 {tg['name']}" + (" (Disabled)" if not tg['enabled'] else ""), expanded=True):
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("Virtual Users", tg['num_threads'])
                                if tg['scheduler'] and tg['duration'] > 0:
                                    st.metric("Duration", f"{tg['duration']}s")

                            with col2:
                                st.metric("Ramp-Up Time", f"{tg['ramp_time']}s")
                                if tg['scheduler'] and tg['delay'] > 0:
                                    st.metric("Start Delay", f"{tg['delay']}s")

                            with col3:
                                loop_text = "Infinite" if tg['loops'] == -1 else str(tg['loops'])
                                st.metric("Loop Count", loop_text)
                                if tg['scheduler']:
                                    st.info("⏰ Scheduler Enabled")

                            # Display child LoopControllers if present
                            if tg.get('loop_controllers'):
                                st.markdown("**🔄 Loop Controllers (Action 내부 루프):**")
                                for lc in tg['loop_controllers']:
                                    status = "✅" if lc['enabled'] else "❌"
                                    st.info(f"{status} **{lc['name']}**: {lc['loops']}회 반복")

                            # LoadRunner configuration guidance
                            st.markdown("**LoadRunner Configuration:**")
                            config_text = f"""Runtime Settings > Run Logic:
  - Number of Vusers: {tg['num_threads']}
  - Start: All Vusers simultaneously
    OR Gradually: {tg['num_threads']} Vusers every {tg['ramp_time']} seconds

Runtime Settings > Run Logic > Run:
  - Iterations: {loop_text}"""

                            if tg['scheduler'] and tg['duration'] > 0:
                                config_text += f"\n  - Duration: {tg['duration']} seconds"
                            if tg['scheduler'] and tg['delay'] > 0:
                                config_text += f"\n  - Start after: {tg['delay']} seconds"

                            # Add Loop Controller information
                            if tg.get('loop_controllers'):
                                config_text += "\n\nAction 내부 Loop Controllers:"
                                for lc in tg['loop_controllers']:
                                    config_text += f"\n  - {lc['name']}: for 루프 {lc['loops']}회 반복"

                            st.code(config_text, language="text")

                    st.markdown("---")
            except Exception as e:
                # If extraction fails, just skip the settings display
                pass

            st.markdown("### 👁️ Code Preview")

            preview_col1, preview_col2 = st.columns(2)

            with preview_col1:
                st.markdown("**Original JMX:**")
                try:
                    if uploaded_file:
                        uploaded_file.seek(0)
                        content = uploaded_file.read().decode('utf-8')
                    else:
                        content = st.session_state.jmx_sample_file['content']

                    # Format XML for better readability
                    content = format_xml_for_display(content)

                    # Use code_editor for enhanced display with full content
                    code_editor(
                        content,
                        lang="xml",
                        theme="monokai",
                        height=[20, 30],
                        options={"wrap": True},
                        buttons=[{
                            "name": "Copy",
                            "feather": "Copy",
                            "hasText": True,
                            "alwaysOn": True,
                            "commands": ["copyAll"],
                            "style": {"top": "0.46rem", "right": "0.4rem"}
                        }],
                        key="jmx_original_editor"
                    )
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted LoadRunner C:**")
                if st.session_state.jmx_converted_content:
                    # Use code_editor for enhanced display with full content
                    code_editor(
                        st.session_state.jmx_converted_content,
                        lang="c_cpp",
                        theme="dracula",
                        height=[20, 30],
                        options={
                            "wrap": True,
                            "showGutter": True,
                            "highlightActiveLine": True,
                            "showPrintMargin": False,
                            "fontSize": 14,
                            "enableBasicAutocompletion": False,
                            "enableLiveAutocompletion": False,
                            "useSoftTabs": False,
                            "tabSize": 4
                        },
                        buttons=[{
                            "name": "Copy",
                            "feather": "Copy",
                            "hasText": True,
                            "alwaysOn": True,
                            "commands": ["copyAll"],
                            "style": {"top": "0.46rem", "right": "0.4rem"}
                        }],
                        key="jmx_converted_editor"
                    )
                else:
                    code_editor(
                        "// Conversion result will appear here\n// Upload a file to start",
                        lang="c_cpp",
                        theme="dracula",
                        height=[10, 15],
                        key="jmx_converted_placeholder"
                    )

        # Conversion log section
        st.markdown("---")
        st.markdown("### 📋 Conversion Log")
        st.text_area(
            "JMeter to LoadRunner conversion log",
            value=st.session_state.jmx_conversion_log,
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )

    with tab2:
        st.markdown("### Convert LoadRunner C Script to JMeter JMX")

        # File upload section
        st.markdown("#### 📤 Upload C File")
        uploaded_file_lr = st.file_uploader(
            "Upload C File",
            type=['c'],
            key=f"lr_uploader_{st.session_state.lr_uploader_key}",
            help="Upload a valid LoadRunner C script file (max 10MB)",
            label_visibility="collapsed"
        )

        # Clear previous results if no file is uploaded and no sample is selected
        if not uploaded_file_lr and not st.session_state.lr_sample_file:
            if st.session_state.lr_converted_content or 'lr_last_file_key' in st.session_state:
                st.session_state.lr_converted_content = None
                st.session_state.lr_conversion_log = "Ready to convert..."
                st.session_state.lr_output_filename = None
                if 'lr_last_file_key' in st.session_state:
                    del st.session_state.lr_last_file_key

        if uploaded_file_lr:
            st.success(f"✅ File uploaded: {uploaded_file_lr.name} | Size: {uploaded_file_lr.size / 1024:.2f} KB")

        # Conversion Status in one line
        if st.session_state.lr_converted_content:
            st.success("📊 Conversion Status: ✅ Conversion completed!")
        elif uploaded_file_lr or st.session_state.lr_sample_file:
            st.info("📊 Conversion Status: 🔄 Converting...")
        else:
            st.info("📊 Conversion Status: 💡 Please upload a C file to begin")

        # Auto-convert on file upload or sample file selection
        if uploaded_file_lr or st.session_state.lr_sample_file:
            # Generate unique file key based on content hash
            if uploaded_file_lr:
                uploaded_file_lr.seek(0)
                import hashlib
                file_content = uploaded_file_lr.read()
                file_hash = hashlib.md5(file_content).hexdigest()
                current_file_key = f"{uploaded_file_lr.name}_{uploaded_file_lr.size}_{file_hash}"
                uploaded_file_lr.seek(0)  # Reset for later use
            else:
                current_file_key = f"sample_{st.session_state.lr_sample_file.get('name', 'unknown')}"

            # Check if file has changed
            needs_conversion = (
                'lr_last_file_key' not in st.session_state or
                st.session_state.lr_last_file_key != current_file_key
            )

            # Clear previous results immediately when file changes
            if needs_conversion:
                st.session_state.lr_converted_content = None
                st.session_state.lr_conversion_log = "Converting..."
                st.session_state.lr_output_filename = None

            if needs_conversion:
                with st.spinner("Converting..."):
                    if uploaded_file_lr:
                        uploaded_file_lr.seek(0)  # Reset file pointer
                        success, output, log_msg = convert_lr_to_jmx(uploaded_file=uploaded_file_lr)
                        file_name = uploaded_file_lr.name
                    else:
                        success, output, log_msg = convert_lr_to_jmx(sample_file=st.session_state.lr_sample_file)
                        file_name = st.session_state.lr_sample_file.get('name', 'sample.c')

                    # Update session state
                    st.session_state.lr_converted_content = output if success else None
                    st.session_state.lr_conversion_log = log_msg
                    st.session_state.lr_last_file_key = current_file_key

                    # Add to history
                    add_to_history("LoadRunner → JMeter", file_name, success, log_msg)

                    # Show message
                    if success:
                        st.success("✅ Conversion completed successfully!")
                    else:
                        st.error("❌ Conversion failed. Check logs for details.")
                    st.rerun()

        # Action buttons
        st.markdown("---")
        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.session_state.lr_converted_content:
                st.download_button(
                    label="⬇️ Download Converted Script",
                    data=st.session_state.lr_converted_content,
                    file_name=st.session_state.lr_output_filename or "converted_testplan.jmx",
                    mime="application/xml",
                    key="download_jmx"
                )

        with button_col2:
            clear_btn_lr = st.button("🗑️ Clear All", key="clear_lr")
            if clear_btn_lr:
                st.session_state.lr_converted_content = None
                st.session_state.lr_conversion_log = "Ready to convert..."
                st.session_state.lr_output_filename = None
                st.session_state.lr_sample_file = None
                st.session_state.lr_uploader_key += 1  # Increment to reset file uploader
                if 'lr_last_file_key' in st.session_state:
                    del st.session_state.lr_last_file_key
                st.rerun()

        # Preview section
        has_input_lr = uploaded_file_lr or st.session_state.lr_sample_file
        if has_input_lr:
            st.markdown("---")
            st.markdown("### 👁️ Code Preview")

            preview_col1, preview_col2 = st.columns(2)

            with preview_col1:
                st.markdown("**Original LoadRunner C:**")
                try:
                    if uploaded_file_lr:
                        uploaded_file_lr.seek(0)
                        content = uploaded_file_lr.read().decode('utf-8')
                    else:
                        content = st.session_state.lr_sample_file['content']

                    # Format C code for better readability
                    content = format_c_for_display(content)

                    # Use code_editor for enhanced display with full content
                    code_editor(
                        content,
                        lang="c_cpp",
                        theme="dracula",
                        height=[20, 30],
                        options={
                            "wrap": True,
                            "showGutter": True,
                            "highlightActiveLine": True,
                            "showPrintMargin": False,
                            "fontSize": 14,
                            "enableBasicAutocompletion": False,
                            "enableLiveAutocompletion": False
                        },
                        buttons=[{
                            "name": "Copy",
                            "feather": "Copy",
                            "hasText": True,
                            "alwaysOn": True,
                            "commands": ["copyAll"],
                            "style": {"top": "0.46rem", "right": "0.4rem"}
                        }],
                        key="lr_original_editor"
                    )
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted JMX:**")
                if st.session_state.lr_converted_content:
                    # Use code_editor for enhanced display with full content
                    code_editor(
                        st.session_state.lr_converted_content,
                        lang="xml",
                        theme="monokai",
                        height=[20, 30],
                        options={"wrap": True},
                        buttons=[{
                            "name": "Copy",
                            "feather": "Copy",
                            "hasText": True,
                            "alwaysOn": True,
                            "commands": ["copyAll"],
                            "style": {"top": "0.46rem", "right": "0.4rem"}
                        }],
                        key="lr_converted_editor"
                    )
                else:
                    code_editor(
                        "<!-- Conversion result will appear here -->\n<!-- Upload a file to start -->",
                        lang="xml",
                        theme="monokai",
                        height=[10, 15],
                        key="lr_converted_placeholder"
                    )

        # Conversion log section
        st.markdown("---")
        st.markdown("### 📋 Conversion Log")
        st.text_area(
            "LoadRunner to JMeter conversion log",
            value=st.session_state.lr_conversion_log,
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Performance Test Script Converter v0.2.0 | Made with Streamlit</p>
        <p>© 2025 PTSC Team | <a href="https://github.com/taein2301/PTSC">GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
