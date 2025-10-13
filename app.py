"""
Performance Test Script Converter (PTSC)
Main Streamlit Application

This application provides bidirectional conversion between:
- JMeter JMX files → LoadRunner C scripts
- LoadRunner C scripts → JMeter JMX files
"""

import streamlit as st

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

def main():
    """Main application function"""

    # Header section
    st.markdown('<div class="main-header">🔄 Performance Test Script Converter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">JMeter ↔ LoadRunner Script Converter</div>', unsafe_allow_html=True)

    # Version info in sidebar
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.info("""
        **Version:** 0.1.0

        **Features:**
        - JMeter → LoadRunner conversion
        - LoadRunner → JMeter conversion
        - Code preview with syntax highlighting
        - Conversion logs and statistics
        """)

        st.markdown("---")
        st.markdown("### 📚 Documentation")
        st.markdown("[GitHub Repository](https://github.com/taein2301/PTSC)")

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
                st.warning("⏳ Ready to convert. Click 'Convert' button below.")
            else:
                st.info("💡 Please upload a JMX file to begin")

        # Action buttons
        st.markdown("---")
        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            convert_btn = st.button("🔄 Convert", key="convert_jmx", disabled=not uploaded_file)

        with button_col2:
            download_btn = st.button("⬇️ Download", key="download_lr", disabled=True)

        with button_col3:
            clear_btn = st.button("🗑️ Clear", key="clear_jmx")

        # Preview section
        if uploaded_file:
            st.markdown("---")
            st.markdown("### 👁️ Code Preview")

            preview_col1, preview_col2 = st.columns(2)

            with preview_col1:
                st.markdown("**Original JMX:**")
                try:
                    content = uploaded_file.read().decode('utf-8')
                    st.code(content[:500] + "..." if len(content) > 500 else content, language='xml', line_numbers=True)
                    uploaded_file.seek(0)  # Reset file pointer
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted LoadRunner C:**")
                st.code("// Conversion result will appear here\n// Click 'Convert' button to start", language='c')

        # Conversion log section
        st.markdown("---")
        st.markdown("### 📋 Conversion Log")
        st.text_area(
            "Log messages will appear here",
            value="Ready to convert...",
            height=150,
            disabled=True,
            key="log_jmx"
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
                st.warning("⏳ Ready to convert. Click 'Convert' button below.")
            else:
                st.info("💡 Please upload a C file to begin")

        # Action buttons
        st.markdown("---")
        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            convert_btn_lr = st.button("🔄 Convert", key="convert_lr", disabled=not uploaded_file_lr)

        with button_col2:
            download_btn_lr = st.button("⬇️ Download", key="download_jmx", disabled=True)

        with button_col3:
            clear_btn_lr = st.button("🗑️ Clear", key="clear_lr")

        # Preview section
        if uploaded_file_lr:
            st.markdown("---")
            st.markdown("### 👁️ Code Preview")

            preview_col1, preview_col2 = st.columns(2)

            with preview_col1:
                st.markdown("**Original LoadRunner C:**")
                try:
                    content = uploaded_file_lr.read().decode('utf-8')
                    st.code(content[:500] + "..." if len(content) > 500 else content, language='c', line_numbers=True)
                    uploaded_file_lr.seek(0)  # Reset file pointer
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            with preview_col2:
                st.markdown("**Converted JMX:**")
                st.code("<!-- Conversion result will appear here -->\n<!-- Click 'Convert' button to start -->", language='xml')

        # Conversion log section
        st.markdown("---")
        st.markdown("### 📋 Conversion Log")
        st.text_area(
            "Log messages will appear here",
            value="Ready to convert...",
            height=150,
            disabled=True,
            key="log_lr"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Performance Test Script Converter v0.1.0 | Made with ❤️ using Streamlit</p>
        <p>© 2025 PTSC Team | <a href="https://github.com/taein2301/PTSC">GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
