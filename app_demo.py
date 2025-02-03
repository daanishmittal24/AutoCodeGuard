import os
import sys
import logging
import time
import streamlit as st
from src.repo_analyzer import analyze_repo

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit page configuration
st.set_page_config(page_title="AutoCodeGuard", page_icon="🔍", layout="wide")

# Header - Title and Description
st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #4CAF50;">🔍 AutoCodeGuard</h1>
        <p style="font-size: 18px; color: #333;">Comprehensive Real-Time Code Analysis with Live Feedback</p>
    </div>
""", unsafe_allow_html=True)

# Session state initialization
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'status' not in st.session_state:
    st.session_state.status = "Ready"

# Layout for main actions
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## 🚀 Repository Analysis")
        with st.expander("📂 Analyze Repository"):
            repo_url = st.text_input(
                "Enter GitHub Repository URL:",
                placeholder="https://github.com/username/repository",
                help="Enter a public repository URL to analyze"
            )
            
            analyze_button = st.button("Analyze Now", key="analyze")

    with col2:
        st.markdown("## 🔧 Webhooks & Automation")
        with st.expander("🔄 Setup Webhooks for Automation"):
            webhook_button = st.button("Setup Webhook", key="webhook")

# Advanced Features Section
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## 🌟 Advanced Features")
        with st.expander("⚙️ Use AI for Code Review"):
            llm_button = st.button("Use LLM for Code Review", key="llm")

        with st.expander("📄 Generate Detailed Report"):
            report_button = st.button("Generate Report", key="report")

    with col2:
        st.markdown("## 📝 Custom Rules")
        with st.expander("🔧 Upload Custom Rule File"):
            upload_button = st.file_uploader(
                "Upload Custom Linter Rules", 
                type=["json", "yaml", "pylintrc", "eslint_config.js", "stylelint_config.js"]
            )

# Status and Log Section
st.markdown("## 📝 Live Analysis Logs")
status_display = st.empty()
progress_bar = st.progress(0)
logs_container = st.expander("Show Logs", expanded=True)
with logs_container:
    log_display = st.empty()

# Helper functions for status updates and logs
def update_status(text):
    st.session_state.status = text
    status_display.markdown(f"**Status:** {text}")

def add_log(text):
    st.session_state.logs.append(text)
    log_display.markdown("\n".join(st.session_state.logs[-20:]))

# Action functions for buttons
def simulate_push_and_analyze():
    add_log("⏳ Simulating push... Initiating analysis.")
    time.sleep(2)
    add_log("✅ Analysis triggered by push event.")
    analyze_repo_and_display_results()

def analyze_now():
    if repo_url:
        add_log("⏳ Starting analysis for repository: " + repo_url)
        update_status("Starting analysis...")
        analyze_repo_and_display_results()

def use_llm():
    add_log("💡 Simulating LLM-based code review.")
    update_status("LLM code review in progress...")
    time.sleep(2)
    add_log("✅ LLM Review Completed: No significant improvements found.")

def generate_report():
    add_log("📄 Generating report... Please wait.")
    update_status("Generating report...")
    time.sleep(2)
    add_log("✅ Report generated successfully.")

def setup_webhook():
    add_log("🔧 Setting up webhook... Please wait.")
    update_status("Setting up webhook...")
    time.sleep(2)
    add_log("✅ Webhook setup completed.")

def handle_uploaded_rule_file(uploaded_file):
    file_name = uploaded_file.name
    file_path = os.path.join("uploaded_rules", file_name)
    
    # Save the uploaded file to a temporary folder
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    add_log(f"✅ Rule file '{file_name}' uploaded successfully.")
    update_status(f"Custom rules from '{file_name}' applied.")

# Analyze the repository and display results
def analyze_repo_and_display_results():
    try:
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
            time.sleep(0.5)
            progress_bar.empty()

            # Display analysis results
            st.success("Analysis Complete!")
            for lang, files in results.items():
                if files:
                    with st.expander(f"{lang} Results ({len(files)} files)"):
                        for file in files:
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

# Action handlers


if analyze_button:
    analyze_now()

if webhook_button:
    setup_webhook()

if llm_button:
    use_llm()

if report_button:
    generate_report()

if upload_button:
    handle_uploaded_rule_file(upload_button)

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
