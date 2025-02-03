import os
import sys
import logging
from time import sleep
import streamlit as st
from src.repo_analyzer import analyze_repo

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit page configuration
st.set_page_config(page_title="AutoCodeGuard", page_icon="🔍", layout="wide")

# Streamlit title and description
st.title("🔍 AutoCodeGuard - Real-Time Code Analysis")
st.markdown("""
    ### Comprehensive Static Analysis with Live Feedback
    Analyze your code quality in real-time with detailed error, warning, and performance reports.
""")

# Session state initialization
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'status' not in st.session_state:
    st.session_state.status = "Ready"

# Layout columns for input and status
col1, col2 = st.columns([3, 1])

with col1:
    repo_url = st.text_input(
        "**GitHub Repository URL:**", 
        placeholder="https://github.com/username/repository",
        help="Enter a public repository URL to analyze"
    )

with col2:
    st.markdown("## Current Status", unsafe_allow_html=True)
    status_display = st.empty()
    progress_bar = st.progress(0)

# Live logs container
logs_container = st.expander("Live Analysis Logs", expanded=True)
with logs_container:
    log_display = st.empty()

# Helper functions for status updates and logs
def update_status(text):
    st.session_state.status = text
    status_display.markdown(f"**Status:** {text}")

def add_log(text):
    st.session_state.logs.append(text)
    log_display.markdown("\n".join(st.session_state.logs[-20:]))

# Analysis trigger
if repo_url:
    st.session_state.logs = []  # Clear previous logs
    st.session_state.status = "Starting analysis..."
    
    try:
        # Call the analysis function
        results = analyze_repo(
            repo_url,
            status_callback=update_status,
            log_callback=add_log
        )
        
        if "Error" in results:
            add_log(f"❌ Final status: Analysis failed - {results['Error'][0]}")
            update_status("Analysis failed")
            progress_bar.progress(0)
        else:
            add_log("✅ Analysis completed successfully!")
            update_status("Analysis complete")
            progress_bar.progress(100)
            sleep(0.5)
            progress_bar.empty()

            # Display analysis results
            st.success("Analysis Complete!")
            for lang, files in results.items():
                if files:
                    with st.expander(f"{lang} Results ({len(files)} files)"):
                        for file in files:
                            # Ensure 'rating' is handled correctly
                            rating = file.get("rating", "No rating available")
                            st.markdown(f"**{file['file']}** (Errors: {file['error_count']}, Warnings: {file['warning_count']}, Rating: {rating})")
                            if file['issues'].strip():
                                st.code(file['issues'], language='text')
                            else:
                                st.success("No issues found!")
                                
    except Exception as e:
        add_log(f"❌ Critical error: {str(e)}")
        update_status("Analysis failed")
        progress_bar.progress(0)

# Buttons for additional actions (Main page)
st.markdown("## Additional Actions", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    generate_report_button = st.button("Generate Report for Analysis", key="report", use_container_width=True)
with col2:
    upload_linter_button = st.button("Upload Custom Linter Profiles", key="linter", use_container_width=True)
with col3:
    use_llm_button = st.button("Use LLM for Code Review (Testing Phase)", key="llm", use_container_width=True)

if generate_report_button:
    # Placeholder for generating report functionality
    st.info("Report generation is currently under development.")
    
if upload_linter_button:
    # Placeholder for uploading custom linter profiles functionality
    st.info("Upload custom linter profiles feature is under development.")
    
if use_llm_button:
    # Placeholder for LLM-based code review functionality
    st.info("LLM-based code review is in the testing phase.")

# Sidebar with system info and icons
with st.sidebar:
    st.markdown("## 🚀 AutoCodeGuard Features")
    st.markdown("""
        - **Real-time code quality analysis** for multiple languages
        - **Error and warning reports** with detailed feedback
        - **Custom linter profiles** support for personalized checks
    """)
    st.markdown("## 🛠️ System Information")
    st.markdown(f"**Python Version:** {sys.version.split()[0]}")
    st.markdown("**Installed Tools:**")
    st.markdown("- Pylint 3.0.3\n- ESLint 9.19.0\n- HTMLHint 1.1.4\n- Stylelint (for CSS analysis)\n- Checkstyle 10.12.0")
    st.markdown("**Linter Paths:**")
    node_modules_path = os.path.join(os.getcwd(), "node_modules", ".bin")
    st.markdown(f"- Node Modules: `{node_modules_path}`")
    st.markdown("---")
    st.markdown("## 📊 Live Logs Summary")
    if st.session_state.logs:
        st.metric("Total Log Entries", len(st.session_state.logs))
        st.metric("Last Log Entry", st.session_state.logs[-1][:50] + "...")
    else:
        st.info("No logs generated yet")

# Footer for additional details
st.markdown("---")
st.markdown("""
    🛠️ Professional Code Quality Analysis System | 📧 Support: [contact@autocodeguard.com](mailto:contact@autocodeguard.com)
""")

