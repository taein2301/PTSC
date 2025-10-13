"""
Performance Test Script Converter (PTSC)
Main Streamlit Application

This application provides bidirectional conversion between:
- JMeter JMX files → LoadRunner C scripts
- LoadRunner C scripts → JMeter JMX files
"""

import streamlit as st
import io
from converters.jmeter_to_lr import JMeterToLRConverter
from converters.lr_to_jmeter import LRToJMeterConverter
from utils.validators import FileValidator
from utils.formatters import CodeFormatter
from utils.helpers import FileHelper, LogHelper

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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'jmx_converted_content' not in st.session_state:
    st.session_state.jmx_converted_content = None
if 'jmx_conversion_log' not in st.session_state:
    st.session_state.jmx_conversion_log = "Ready to convert..."
if 'jmx_output_filename' not in st.session_state:
    st.session_state.jmx_output_filename = None

if 'lr_converted_content' not in st.session_state:
    st.session_state.lr_converted_content = None
if 'lr_conversion_log' not in st.session_state:
    st.session_state.lr_conversion_log = "Ready to convert..."
if 'lr_output_filename' not in st.session_state:
    st.session_state.lr_output_filename = None


def convert_jmx_to_lr(uploaded_file):
    """
    Convert JMeter JMX file to LoadRunner C script

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Tuple of (success, output_content, log_message)
    """
    try:
        # Read file content
        file_content = uploaded_file.read()
        file_size = len(file_content)

        # Validate file
        validator = FileValidator()
        is_valid, error_msg = validator.validate_jmx_file(
            uploaded_file.name,
            file_content,
            file_size
        )

        if not is_valid:
            return False, None, f"Validation Error:\n{error_msg}"

        # Decode content
        encoding = validator.detect_encoding(file_content)
        content_str = file_content.decode(encoding)

        # Perform conversion
        converter = JMeterToLRConverter()
        success, output_content, stats = converter.execute_conversion(content_str)

        # Generate log message
        if success:
            summary = converter.get_conversion_summary()
            log_msg = f"Conversion Successful!\n\n{summary}"

            # Generate output filename
            output_filename = FileHelper.generate_output_filename(uploaded_file.name, '.c')
            st.session_state.jmx_output_filename = output_filename

            return True, output_content, log_msg
        else:
            errors = "\n".join([f"  - {e}" for e in stats.get('errors', [])])
            log_msg = f"Conversion Failed!\n\nErrors:\n{errors}"
            return False, None, log_msg

    except Exception as e:
        return False, None, f"Unexpected Error:\n{str(e)}"


def convert_lr_to_jmx(uploaded_file):
    """
    Convert LoadRunner C script to JMeter JMX file

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Tuple of (success, output_content, log_message)
    """
    try:
        # Read file content
        file_content = uploaded_file.read()
        file_size = len(file_content)

        # Validate file
        validator = FileValidator()
        is_valid, error_msg = validator.validate_c_file(
            uploaded_file.name,
            file_content,
            file_size
        )

        if not is_valid:
            return False, None, f"Validation Error:\n{error_msg}"

        # Decode content
        encoding = validator.detect_encoding(file_content)
        content_str = file_content.decode(encoding)

        # Perform conversion
        converter = LRToJMeterConverter()
        success, output_content, stats = converter.execute_conversion(content_str)

        # Generate log message
        if success:
            summary = converter.get_conversion_summary()
            log_msg = f"Conversion Successful!\n\n{summary}"

            # Generate output filename
            output_filename = FileHelper.generate_output_filename(uploaded_file.name, '.jmx')
            st.session_state.lr_output_filename = output_filename

            return True, output_content, log_msg
        else:
            errors = "\n".join([f"  - {e}" for e in stats.get('errors', [])])
            log_msg = f"Conversion Failed!\n\nErrors:\n{errors}"
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
        st.markdown("### ℹ️ About")
        st.info("""
        **Version:** 0.2.0

        **Features:**
        - JMeter → LoadRunner conversion
        - LoadRunner → JMeter conversion
        - Code preview with syntax highlighting
        - Conversion logs and statistics
        - File validation
        """)

        st.markdown("---")
        st.markdown("### 📚 Documentation")
        st.markdown("[GitHub Repository](https://github.com/taein2301/PTSC)")
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
            if uploaded_file:
                if st.session_state.jmx_converted_content:
                    st.success("✅ Conversion completed!")
                else:
                    st.warning("⏳ Ready to convert. Click 'Convert' button below.")
            else:
                st.info("💡 Please upload a JMX file to begin")

        # Action buttons
        st.markdown("---")
        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            convert_btn = st.button("🔄 Convert", key="convert_jmx", disabled=not uploaded_file)
            if convert_btn and uploaded_file:
                with st.spinner("Converting..."):
                    uploaded_file.seek(0)  # Reset file pointer
                    success, output, log_msg = convert_jmx_to_lr(uploaded_file)

                    st.session_state.jmx_converted_content = output if success else None
                    st.session_state.jmx_conversion_log = log_msg

                    if success:
                        st.success("Conversion completed successfully!")
                    else:
                        st.error("Conversion failed. Check logs for details.")
                    st.rerun()

        with button_col2:
            if st.session_state.jmx_converted_content:
                st.download_button(
                    label="⬇️ Download",
                    data=st.session_state.jmx_converted_content,
                    file_name=st.session_state.jmx_output_filename or "converted_script.c",
                    mime="text/plain",
                    key="download_lr"
                )

        with button_col3:
            clear_btn = st.button("🗑️ Clear", key="clear_jmx")
            if clear_btn:
                st.session_state.jmx_converted_content = None
                st.session_state.jmx_conversion_log = "Ready to convert..."
                st.session_state.jmx_output_filename = None
                st.rerun()

        # Preview section
        if uploaded_file:
            st.markdown("---")
            st.markdown("### 👁️ Code Preview")

            preview_col1, preview_col2 = st.columns(2)

            with preview_col1:
                st.markdown("**Original JMX:**")
                try:
                    uploaded_file.seek(0)
                    content = uploaded_file.read().decode('utf-8')
                    formatter = CodeFormatter()
                    truncated = formatter.truncate_code(content, max_lines=30)
                    st.code(truncated, language='xml', line_numbers=True)
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted LoadRunner C:**")
                if st.session_state.jmx_converted_content:
                    formatter = CodeFormatter()
                    truncated = formatter.truncate_code(st.session_state.jmx_converted_content, max_lines=30)
                    st.code(truncated, language='c', line_numbers=True)
                else:
                    st.code("// Conversion result will appear here\n// Click 'Convert' button to start", language='c')

        # Conversion log section
        st.markdown("---")
        st.markdown("### 📋 Conversion Log")
        st.text_area(
            "Log messages",
            value=st.session_state.jmx_conversion_log,
            height=200,
            disabled=True,
            key="log_jmx_display"
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
            if uploaded_file_lr:
                if st.session_state.lr_converted_content:
                    st.success("✅ Conversion completed!")
                else:
                    st.warning("⏳ Ready to convert. Click 'Convert' button below.")
            else:
                st.info("💡 Please upload a C file to begin")

        # Action buttons
        st.markdown("---")
        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            convert_btn_lr = st.button("🔄 Convert", key="convert_lr", disabled=not uploaded_file_lr)
            if convert_btn_lr and uploaded_file_lr:
                with st.spinner("Converting..."):
                    uploaded_file_lr.seek(0)  # Reset file pointer
                    success, output, log_msg = convert_lr_to_jmx(uploaded_file_lr)

                    st.session_state.lr_converted_content = output if success else None
                    st.session_state.lr_conversion_log = log_msg

                    if success:
                        st.success("Conversion completed successfully!")
                    else:
                        st.error("Conversion failed. Check logs for details.")
                    st.rerun()

        with button_col2:
            if st.session_state.lr_converted_content:
                st.download_button(
                    label="⬇️ Download",
                    data=st.session_state.lr_converted_content,
                    file_name=st.session_state.lr_output_filename or "converted_testplan.jmx",
                    mime="application/xml",
                    key="download_jmx"
                )

        with button_col3:
            clear_btn_lr = st.button("🗑️ Clear", key="clear_lr")
            if clear_btn_lr:
                st.session_state.lr_converted_content = None
                st.session_state.lr_conversion_log = "Ready to convert..."
                st.session_state.lr_output_filename = None
                st.rerun()

        # Preview section
        if uploaded_file_lr:
            st.markdown("---")
            st.markdown("### 👁️ Code Preview")

            preview_col1, preview_col2 = st.columns(2)

            with preview_col1:
                st.markdown("**Original LoadRunner C:**")
                try:
                    uploaded_file_lr.seek(0)
                    content = uploaded_file_lr.read().decode('utf-8')
                    formatter = CodeFormatter()
                    truncated = formatter.truncate_code(content, max_lines=30)
                    st.code(truncated, language='c', line_numbers=True)
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted JMX:**")
                if st.session_state.lr_converted_content:
                    formatter = CodeFormatter()
                    truncated = formatter.truncate_code(st.session_state.lr_converted_content, max_lines=30)
                    st.code(truncated, language='xml', line_numbers=True)
                else:
                    st.code("<!-- Conversion result will appear here -->\n<!-- Click 'Convert' button to start -->", language='xml')

        # Conversion log section
        st.markdown("---")
        st.markdown("### 📋 Conversion Log")
        st.text_area(
            "Log messages",
            value=st.session_state.lr_conversion_log,
            height=200,
            disabled=True,
            key="log_lr_display"
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
