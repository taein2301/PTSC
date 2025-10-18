"""
Performance Test Script Converter (PTSC)
Main Streamlit Application

This application provides bidirectional conversion between:
- JMeter JMX files → LoadRunner C scripts
- LoadRunner C scripts → JMeter JMX files
"""

import streamlit as st
import os
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
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 1.1rem;
    }
    .upload-section {
        border: 2px dashed #1E88E5;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Enhanced code block styling for better syntax highlighting */
    .stCodeBlock {
        background-color: #1e1e1e !important;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Improve XML/code readability */
    code {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
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

if 'lr_converted_content' not in st.session_state:
    st.session_state.lr_converted_content = None
if 'lr_conversion_log' not in st.session_state:
    st.session_state.lr_conversion_log = "Ready to convert..."
if 'lr_output_filename' not in st.session_state:
    st.session_state.lr_output_filename = None
if 'lr_sample_file' not in st.session_state:
    st.session_state.lr_sample_file = None

# Conversion settings (for future enhancements)
if 'indent_size' not in st.session_state:
    st.session_state.indent_size = 4
if 'include_comments' not in st.session_state:
    st.session_state.include_comments = True
if 'error_handling_level' not in st.session_state:
    st.session_state.error_handling_level = 'Standard'

# Preview settings (lines to show)
if 'jmx_preview_lines_original' not in st.session_state:
    st.session_state.jmx_preview_lines_original = 30
if 'jmx_preview_lines_converted' not in st.session_state:
    st.session_state.jmx_preview_lines_converted = 30
if 'lr_preview_lines_original' not in st.session_state:
    st.session_state.lr_preview_lines_original = 30
if 'lr_preview_lines_converted' not in st.session_state:
    st.session_state.lr_preview_lines_converted = 30

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

    Args:
        c_content: Raw C code string

    Returns:
        Formatted C code string with improved indentation and spacing
    """
    try:
        lines = c_content.split('\n')
        formatted_lines = []
        indent_level = 0
        prev_line_was_blank = False

        for line in lines:
            stripped = line.strip()

            # Skip multiple consecutive blank lines
            if not stripped:
                if not prev_line_was_blank:
                    formatted_lines.append('')
                    prev_line_was_blank = True
                continue

            prev_line_was_blank = False

            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)

            # Apply indentation (4 spaces per level)
            if stripped:
                formatted_line = '    ' * indent_level + stripped
                formatted_lines.append(formatted_line)

            # Increase indent after opening braces
            if stripped.endswith('{'):
                indent_level += 1

        # Remove trailing empty lines
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()

        return '\n'.join(formatted_lines)
    except Exception:
        # If formatting fails, return original content
        return c_content


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
        - Script comparison (side-by-side diff)
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
    tab1, tab2, tab3 = st.tabs(["🔵 JMeter → LoadRunner", "🟢 LoadRunner → JMeter", "🔍 Compare Scripts"])

    with tab1:
        st.markdown("### Convert JMeter JMX to LoadRunner C Script")
        st.info("📌 Upload a JMeter .jmx file to convert it to LoadRunner C script")

        # File upload section
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📤 Upload JMX File")
            uploaded_file = st.file_uploader(
                "Choose a JMeter JMX file",
                type=['jmx'],
                key="jmx_uploader",
                help="Upload a valid JMeter JMX file (max 10MB)"
            )

            if uploaded_file:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.text(f"Size: {uploaded_file.size / 1024:.2f} KB")

        with col2:
            st.markdown("#### 📊 Conversion Status")
            if st.session_state.jmx_converted_content:
                st.success("✅ Conversion completed!")
            elif uploaded_file or st.session_state.jmx_sample_file:
                st.info("🔄 Converting...")
            else:
                st.info("💡 Please upload a JMX file to begin")

        # Auto-convert on file upload
        if uploaded_file:
            # Check if we need to convert (file changed)
            current_file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if 'jmx_last_file_key' not in st.session_state or st.session_state.jmx_last_file_key != current_file_key:
                with st.spinner("Converting..."):
                    uploaded_file.seek(0)  # Reset file pointer
                    success, output, log_msg = convert_jmx_to_lr(uploaded_file=uploaded_file)

                    # Update session state
                    st.session_state.jmx_converted_content = output if success else None
                    st.session_state.jmx_conversion_log = log_msg
                    st.session_state.jmx_last_file_key = current_file_key

                    # Add to history
                    add_to_history("JMeter → LoadRunner", uploaded_file.name, success, log_msg)

                    # Show message
                    if success:
                        st.success("Conversion completed successfully!")
                    else:
                        st.error("Conversion failed. Check logs for details.")
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
                st.session_state.jmx_preview_lines_original = 30
                st.session_state.jmx_preview_lines_converted = 30
                if 'jmx_last_file_key' in st.session_state:
                    del st.session_state.jmx_last_file_key
                st.rerun()

        # Preview section
        has_input = uploaded_file or st.session_state.jmx_sample_file
        if has_input:
            st.markdown("---")
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

                    formatter = CodeFormatter()
                    total_lines = len(content.split('\n'))
                    preview_lines = st.session_state.jmx_preview_lines_original

                    # Show preview or full content
                    if preview_lines >= total_lines:
                        st.code(content, language='xml', line_numbers=True)
                    else:
                        truncated = formatter.truncate_code(content, max_lines=preview_lines)
                        st.code(truncated, language='xml', line_numbers=True)

                    # Show More/Less/Reset buttons
                    if total_lines > 30:
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        with btn_col1:
                            if preview_lines < total_lines:
                                next_lines = min(preview_lines + 50, total_lines)
                                if st.button("📄 Show More (+50)", key="show_more_jmx_original"):
                                    st.session_state.jmx_preview_lines_original = next_lines
                                    st.rerun()
                        with btn_col2:
                            if preview_lines > 30:
                                prev_lines = max(preview_lines - 50, 30)
                                if st.button("📄 Show Less (-50)", key="show_less_jmx_original"):
                                    st.session_state.jmx_preview_lines_original = prev_lines
                                    st.rerun()
                        with btn_col3:
                            if preview_lines != 30:
                                if st.button("🔄 Reset", key="reset_jmx_original"):
                                    st.session_state.jmx_preview_lines_original = 30
                                    st.rerun()
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted LoadRunner C:**")
                if st.session_state.jmx_converted_content:
                    formatter = CodeFormatter()
                    total_lines = len(st.session_state.jmx_converted_content.split('\n'))
                    preview_lines = st.session_state.jmx_preview_lines_converted

                    # Show preview or full content
                    if preview_lines >= total_lines:
                        st.code(st.session_state.jmx_converted_content, language='c', line_numbers=True)
                    else:
                        truncated = formatter.truncate_code(st.session_state.jmx_converted_content, max_lines=preview_lines)
                        st.code(truncated, language='c', line_numbers=True)

                    # Show More/Less/Reset buttons
                    if total_lines > 30:
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        with btn_col1:
                            if preview_lines < total_lines:
                                next_lines = min(preview_lines + 50, total_lines)
                                if st.button("📄 Show More (+50)", key="show_more_jmx_converted"):
                                    st.session_state.jmx_preview_lines_converted = next_lines
                                    st.rerun()
                        with btn_col2:
                            if preview_lines > 30:
                                prev_lines = max(preview_lines - 50, 30)
                                if st.button("📄 Show Less (-50)", key="show_less_jmx_converted"):
                                    st.session_state.jmx_preview_lines_converted = prev_lines
                                    st.rerun()
                        with btn_col3:
                            if preview_lines != 30:
                                if st.button("🔄 Reset", key="reset_jmx_converted"):
                                    st.session_state.jmx_preview_lines_converted = 30
                                    st.rerun()
                else:
                    st.code("// Conversion result will appear here\n// Upload a file to start", language='c')

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
        st.info("📌 Upload a LoadRunner .c file to convert it to JMeter JMX format")

        # File upload section
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📤 Upload C File")
            uploaded_file_lr = st.file_uploader(
                "Choose a LoadRunner C script file",
                type=['c'],
                key="lr_uploader",
                help="Upload a valid LoadRunner C script file (max 10MB)"
            )

            if uploaded_file_lr:
                st.success(f"✅ File uploaded: {uploaded_file_lr.name}")
                st.text(f"Size: {uploaded_file_lr.size / 1024:.2f} KB")

        with col2:
            st.markdown("#### 📊 Conversion Status")
            if st.session_state.lr_converted_content:
                st.success("✅ Conversion completed!")
            elif uploaded_file_lr or st.session_state.lr_sample_file:
                st.info("🔄 Converting...")
            else:
                st.info("💡 Please upload a C file to begin")

        # Auto-convert on file upload
        if uploaded_file_lr:
            # Check if we need to convert (file changed)
            current_file_key = f"{uploaded_file_lr.name}_{uploaded_file_lr.size}"
            if 'lr_last_file_key' not in st.session_state or st.session_state.lr_last_file_key != current_file_key:
                with st.spinner("Converting..."):
                    uploaded_file_lr.seek(0)  # Reset file pointer
                    success, output, log_msg = convert_lr_to_jmx(uploaded_file=uploaded_file_lr)

                    # Update session state
                    st.session_state.lr_converted_content = output if success else None
                    st.session_state.lr_conversion_log = log_msg
                    st.session_state.lr_last_file_key = current_file_key

                    # Add to history
                    add_to_history("LoadRunner → JMeter", uploaded_file_lr.name, success, log_msg)

                    # Show message
                    if success:
                        st.success("Conversion completed successfully!")
                    else:
                        st.error("Conversion failed. Check logs for details.")
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
                st.session_state.lr_preview_lines_original = 30
                st.session_state.lr_preview_lines_converted = 30
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

                    formatter = CodeFormatter()
                    total_lines = len(content.split('\n'))
                    preview_lines = st.session_state.lr_preview_lines_original

                    # Show preview or full content
                    if preview_lines >= total_lines:
                        st.code(content, language='c', line_numbers=True)
                    else:
                        truncated = formatter.truncate_code(content, max_lines=preview_lines)
                        st.code(truncated, language='c', line_numbers=True)

                    # Show More/Less/Reset buttons
                    if total_lines > 30:
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        with btn_col1:
                            if preview_lines < total_lines:
                                next_lines = min(preview_lines + 50, total_lines)
                                if st.button("📄 Show More (+50)", key="show_more_lr_original"):
                                    st.session_state.lr_preview_lines_original = next_lines
                                    st.rerun()
                        with btn_col2:
                            if preview_lines > 30:
                                prev_lines = max(preview_lines - 50, 30)
                                if st.button("📄 Show Less (-50)", key="show_less_lr_original"):
                                    st.session_state.lr_preview_lines_original = prev_lines
                                    st.rerun()
                        with btn_col3:
                            if preview_lines != 30:
                                if st.button("🔄 Reset", key="reset_lr_original"):
                                    st.session_state.lr_preview_lines_original = 30
                                    st.rerun()
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted JMX:**")
                if st.session_state.lr_converted_content:
                    formatter = CodeFormatter()
                    total_lines = len(st.session_state.lr_converted_content.split('\n'))
                    preview_lines = st.session_state.lr_preview_lines_converted

                    # Show preview or full content
                    if preview_lines >= total_lines:
                        st.code(st.session_state.lr_converted_content, language='xml', line_numbers=True)
                    else:
                        truncated = formatter.truncate_code(
                            st.session_state.lr_converted_content, max_lines=preview_lines
                        )
                        st.code(truncated, language='xml', line_numbers=True)

                    # Show More/Less/Reset buttons
                    if total_lines > 30:
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        with btn_col1:
                            if preview_lines < total_lines:
                                next_lines = min(preview_lines + 50, total_lines)
                                if st.button("📄 Show More (+50)", key="show_more_lr_converted"):
                                    st.session_state.lr_preview_lines_converted = next_lines
                                    st.rerun()
                        with btn_col2:
                            if preview_lines > 30:
                                prev_lines = max(preview_lines - 50, 30)
                                if st.button("📄 Show Less (-50)", key="show_less_lr_converted"):
                                    st.session_state.lr_preview_lines_converted = prev_lines
                                    st.rerun()
                        with btn_col3:
                            if preview_lines != 30:
                                if st.button("🔄 Reset", key="reset_lr_converted"):
                                    st.session_state.lr_preview_lines_converted = 30
                                    st.rerun()
                else:
                    st.code(
                        "<!-- Conversion result will appear here -->\n"
                        "<!-- Upload a file to start -->",
                        language='xml'
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

    with tab3:
        st.markdown("### Compare Two Scripts Side-by-Side")
        st.info("📌 Compare original and converted scripts to see differences")

        # File upload section
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📄 Original Script")
            compare_file_left = st.file_uploader(
                "Choose original script",
                type=['jmx', 'c'],
                key="compare_uploader_left",
                help="Upload the original script file"
            )

            if compare_file_left:
                st.success(f"✅ File loaded: {compare_file_left.name}")
                st.text(f"Size: {compare_file_left.size / 1024:.2f} KB")
                # Store content
                compare_file_left.seek(0)
                st.session_state.compare_content_left = compare_file_left.read().decode('utf-8')
                st.session_state.compare_filename_left = compare_file_left.name

        with col2:
            st.markdown("#### 📄 Converted Script")
            compare_file_right = st.file_uploader(
                "Choose converted script",
                type=['jmx', 'c'],
                key="compare_uploader_right",
                help="Upload the converted script file"
            )

            if compare_file_right:
                st.success(f"✅ File loaded: {compare_file_right.name}")
                st.text(f"Size: {compare_file_right.size / 1024:.2f} KB")
                # Store content
                compare_file_right.seek(0)
                st.session_state.compare_content_right = compare_file_right.read().decode('utf-8')
                st.session_state.compare_filename_right = compare_file_right.name

        # Action buttons
        st.markdown("---")
        button_col1, button_col2, button_col3 = st.columns([1, 1, 1])

        with button_col1:
            has_both = st.session_state.compare_content_left and st.session_state.compare_content_right
            compare_btn = st.button("🔍 Compare", key="compare_scripts", disabled=not has_both)
            if compare_btn and has_both:
                with st.spinner("Comparing..."):
                    comparator = ScriptComparator()
                    diff_lines, stats = comparator.compare(
                        st.session_state.compare_content_left,
                        st.session_state.compare_content_right,
                        label_left=st.session_state.compare_filename_left or "Original",
                        label_right=st.session_state.compare_filename_right or "Converted"
                    )
                    st.session_state.compare_diff_lines = diff_lines
                    st.session_state.compare_stats = stats
                    st.success("Comparison completed!")
                    st.rerun()

        with button_col2:
            if st.session_state.compare_diff_lines:
                comparator = ScriptComparator()
                unified_diff = comparator.generate_unified_diff(
                    st.session_state.compare_content_left,
                    st.session_state.compare_content_right,
                    label_left=st.session_state.compare_filename_left or "Original",
                    label_right=st.session_state.compare_filename_right or "Converted"
                )
                st.download_button(
                    label="⬇️ Download Diff",
                    data=unified_diff,
                    file_name="comparison_diff.patch",
                    mime="text/plain",
                    key="download_diff"
                )

        with button_col3:
            clear_compare_btn = st.button("🗑️ Clear", key="clear_compare")
            if clear_compare_btn:
                st.session_state.compare_content_left = None
                st.session_state.compare_content_right = None
                st.session_state.compare_filename_left = None
                st.session_state.compare_filename_right = None
                st.session_state.compare_diff_lines = None
                st.session_state.compare_stats = None
                st.rerun()

        # Show comparison results
        if st.session_state.compare_stats:
            st.markdown("---")
            st.markdown("### 📊 Comparison Statistics")

            # Display statistics in columns
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                st.metric(
                    "Similarity",
                    f"{st.session_state.compare_stats.similarity_ratio:.1%}"
                )

            with stat_col2:
                st.metric(
                    "Lines Added",
                    st.session_state.compare_stats.lines_added,
                    delta=None
                )

            with stat_col3:
                st.metric(
                    "Lines Removed",
                    st.session_state.compare_stats.lines_removed,
                    delta=None
                )

            with stat_col4:
                st.metric(
                    "Lines Modified",
                    st.session_state.compare_stats.lines_modified,
                    delta=None
                )

        # Display diff view
        if st.session_state.compare_diff_lines:
            st.markdown("---")
            st.markdown("### 🔍 Detailed Comparison")

            # Filter options
            filter_col1, filter_col2 = st.columns([3, 1])
            with filter_col1:
                st.session_state.compare_show_unchanged = st.checkbox(
                    "Show unchanged lines",
                    value=st.session_state.compare_show_unchanged,
                    key="show_unchanged_lines"
                )

            # Filter diff lines
            comparator = ScriptComparator()
            filtered_lines = comparator.filter_diff_lines(
                st.session_state.compare_diff_lines,
                show_unchanged=st.session_state.compare_show_unchanged
            )

            # Display diff in a styled format
            st.markdown("#### Side-by-Side Comparison")

            # Create custom CSS for diff view
            st.markdown("""
            <style>
            .diff-line {
                font-family: 'Courier New', monospace;
                font-size: 0.85rem;
                padding: 2px 5px;
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .diff-line-num {
                display: inline-block;
                width: 50px;
                text-align: right;
                padding-right: 10px;
                color: #666;
                user-select: none;
            }
            .diff-unchanged {
                background-color: #f8f9fa;
            }
            .diff-added {
                background-color: #d4edda;
            }
            .diff-removed {
                background-color: #f8d7da;
            }
            .diff-modified {
                background-color: #fff3cd;
            }
            .diff-container {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                overflow: hidden;
                margin-bottom: 1rem;
            }
            .diff-header {
                background-color: #e9ecef;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 0.9rem;
            }
            </style>
            """, unsafe_allow_html=True)

            # Create two-column layout for side-by-side diff
            diff_col1, diff_col2 = st.columns(2)

            with diff_col1:
                st.markdown(f'<div class="diff-container"><div class="diff-header">📄 {st.session_state.compare_filename_left or "Original"}</div></div>', unsafe_allow_html=True)

            with diff_col2:
                st.markdown(f'<div class="diff-container"><div class="diff-header">📄 {st.session_state.compare_filename_right or "Converted"}</div></div>', unsafe_allow_html=True)

            # Display lines (limit to first 500 for performance)
            max_display_lines = 500
            display_lines = filtered_lines[:max_display_lines]

            if len(filtered_lines) > max_display_lines:
                st.warning(f"⚠️ Showing first {max_display_lines} of {len(filtered_lines)} lines. Download the diff for complete comparison.")

            # Build HTML for both columns
            left_html = []
            right_html = []

            for line in display_lines:
                # Determine CSS class
                if line.change_type == ChangeType.UNCHANGED:
                    css_class = "diff-unchanged"
                elif line.change_type == ChangeType.ADDED:
                    css_class = "diff-added"
                elif line.change_type == ChangeType.REMOVED:
                    css_class = "diff-removed"
                elif line.change_type == ChangeType.MODIFIED:
                    css_class = "diff-modified"
                else:
                    css_class = ""

                # Left column
                line_num_left = str(line.line_num_left) if line.line_num_left else ""
                content_left = line.content_left.replace('<', '&lt;').replace('>', '&gt;')
                left_html.append(
                    f'<div class="diff-line {css_class}">'
                    f'<span class="diff-line-num">{line_num_left}</span>'
                    f'{content_left}</div>'
                )

                # Right column
                line_num_right = str(line.line_num_right) if line.line_num_right else ""
                content_right = line.content_right.replace('<', '&lt;').replace('>', '&gt;')
                right_html.append(
                    f'<div class="diff-line {css_class}">'
                    f'<span class="diff-line-num">{line_num_right}</span>'
                    f'{content_right}</div>'
                )

            # Display in columns
            with diff_col1:
                st.markdown(f'<div class="diff-container">{"".join(left_html)}</div>', unsafe_allow_html=True)

            with diff_col2:
                st.markdown(f'<div class="diff-container">{"".join(right_html)}</div>', unsafe_allow_html=True)

            # Legend
            st.markdown("---")
            st.markdown("#### 🎨 Legend")
            legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
            with legend_col1:
                st.markdown('<div class="diff-line diff-unchanged" style="padding: 5px;">Unchanged</div>', unsafe_allow_html=True)
            with legend_col2:
                st.markdown('<div class="diff-line diff-added" style="padding: 5px;">Added</div>', unsafe_allow_html=True)
            with legend_col3:
                st.markdown('<div class="diff-line diff-removed" style="padding: 5px;">Removed</div>', unsafe_allow_html=True)
            with legend_col4:
                st.markdown('<div class="diff-line diff-modified" style="padding: 5px;">Modified</div>', unsafe_allow_html=True)

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
