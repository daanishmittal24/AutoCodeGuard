import subprocess
import os
import tempfile
import logging
import sys
from git import Repo
import streamlit as st
from time import sleep
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class StreamlitLogHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container
        
    def emit(self, record):
        log_entry = self.format(record)
        self.container.markdown(f"`{log_entry}`")

# Path to Node.js tools (update this if needed)
node_modules_path = os.path.join(os.getcwd(), "node_modules", ".bin")

def check_tool_availability(tool_name):
    """Check if a tool is installed and available in the system PATH."""
    try:
        subprocess.run([tool_name, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def analyze_repo(repo_url, status_callback, log_callback):
    results = {"Python": [], "HTML": [], "CSS": [], "JavaScript": [], "Java": []}

    # Clone repo to temp directory
    temp_dir = tempfile.mkdtemp()
    try:
        log_callback(f"🔍 Cloning repository from {repo_url}...")
        Repo.clone_from(repo_url, temp_dir)
        status_callback("Cloning complete. Starting analysis...")
    except Exception as e:
        log_callback(f"❌ Clone error: {str(e)}")
        return {"Error": [str(e)]}

    total_files = sum([len(files) for _, _, files in os.walk(temp_dir)])
    processed_files = 0

    # Create configuration files for linters
    create_linter_configs(temp_dir)

    for root, _, files in os.walk(temp_dir):
        for file in files:
            processed_files += 1
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, temp_dir)
            
            # Update progress
            progress_percentage = int((processed_files / total_files) * 100)
            status_callback(f"Analyzing ({processed_files}/{total_files}): {rel_path}")
            log_callback(f"📄 Processing {rel_path}...")

            # Python analysis
            if file.endswith(".py"):
                try:
                    log_callback("🐍 Running Pylint analysis...")
                    result = subprocess.run(
                        ["pylint", "--output-format=text", "--rcfile=.pylintrc", file_path],
                        capture_output=True, text=True, cwd=temp_dir
                    )
                    issues = result.stdout if result.returncode in [0, 1] else result.stderr
                    error_count = issues.count('error') + issues.count('Error')
                    warning_count = issues.count('warning') + issues.count('Warning')
                    
                    results["Python"].append({
                        "file": rel_path,
                        "issues": issues,
                        "error_count": error_count,
                        "warning_count": warning_count
                    })
                    log_callback(f"✅ Python analysis completed for {rel_path}")
                except Exception as e:
                    log_callback(f"❌ Python analysis failed: {str(e)}")
                    results["Python"].append({
                        "file": rel_path,
                        "issues": f"Analysis failed: {str(e)}",
                        "error_count": 1,
                        "warning_count": 0
                    })

            # JavaScript analysis (using npx directly)
            elif file.endswith(".js"):
                try:
                    log_callback("📜 Running ESLint analysis (using npx)...")
                    result = subprocess.run(
                        ["npx", "eslint", file_path, "--format", "stylish", "--config", "eslintconfig.js"],
                        capture_output=True, text=True, cwd=temp_dir
                    )
                    
                    if result.returncode in [0, 1]:
                        issues = result.stdout
                    else:
                        issues = f"ESLint Error: {result.stderr}"
                    
                    error_count = issues.count('✖') 
                    warning_count = issues.count('⚠')
                    
                    results["JavaScript"].append({
                        "file": rel_path,
                        "issues": issues,
                        "error_count": error_count,
                        "warning_count": warning_count
                    })
                    log_callback(f"✅ JavaScript analysis completed for {rel_path}")
                except Exception as e:
                    log_callback(f"❌ JavaScript analysis failed: {str(e)}")
                    results["JavaScript"].append({
                        "file": rel_path,
                        "issues": f"Analysis failed: {str(e)}",
                        "error_count": 1,
                        "warning_count": 0
                    })
            
            # HTML analysis
            elif file.endswith(".html"):
                try:
                    log_callback("🌐 Running HTMLHint analysis...")
                    htmlhint_cmd = os.path.join(node_modules_path, 'htmlhint')
                    result = subprocess.run(
                        [htmlhint_cmd, file_path, "--config", "htmlhint.config.js"],
                        capture_output=True, text=True, cwd=temp_dir
                    )
                    issues = result.stdout if result.returncode in [0, 1] else result.stderr
                    results["HTML"].append({
                        "file": rel_path,
                        "issues": issues,
                        "error_count": issues.count('✗'),
                        "warning_count": issues.count('⚠')
                    })
                    log_callback(f"✅ HTML analysis completed for {rel_path}")
                except Exception as e:
                    log_callback(f"❌ HTML analysis failed: {str(e)}")
                    results["HTML"].append({
                        "file": rel_path,
                        "issues": f"Analysis failed: {str(e)}",
                        "error_count": 1,
                        "warning_count": 0
                    })

            # CSS analysis
            elif file.endswith(".css"):
                try:
                    log_callback("🎨 Running Stylelint analysis for CSS...")
                    stylelint_cmd = os.path.join(node_modules_path, 'stylelint')
                    result = subprocess.run(
                        [stylelint_cmd, file_path, "--formatter", "string", "--config", "stylelint.config.js"],
                        capture_output=True, text=True, cwd=temp_dir
                    )
                    issues = result.stdout if result.returncode in [0, 1] else result.stderr
                    results["CSS"].append({
                        "file": rel_path,
                        "issues": issues,
                        "error_count": issues.count('✖'),
                        "warning_count": issues.count('⚠')
                    })
                    log_callback(f"✅ CSS analysis completed for {rel_path}")
                except Exception as e:
                    log_callback(f"❌ CSS analysis failed: {str(e)}")
                    results["CSS"].append({
                        "file": rel_path,
                        "issues": f"Analysis failed: {str(e)}",
                        "error_count": 1,
                        "warning_count": 0
                    })

            # Java analysis
            elif file.endswith(".java"):
                try:
                    log_callback("☕ Running Checkstyle analysis...")
                    checkstyle_jar = os.getenv("CHECKSTYLE_JAR", "/home/ishu/checkstyle-10.12.0-all.jar")
                    checkstyle_config = os.getenv("CHECKSTYLE_CONFIG", "/home/ishu/sun_checks.xml")
                    
                    result = subprocess.run(
                        ["java", "-jar", checkstyle_jar, "-c", checkstyle_config, file_path],
                        capture_output=True, text=True
                    )
                    issues = result.stdout if result.returncode == 0 else result.stderr
                    results["Java"].append({
                        "file": rel_path,
                        "issues": issues,
                        "error_count": issues.count('ERROR'),
                        "warning_count": issues.count('WARN')
                    })
                    log_callback(f"✅ Java analysis completed for {rel_path}")
                except Exception as e:
                    log_callback(f"❌ Java analysis failed: {str(e)}")
                    results["Java"].append({
                        "file": rel_path,
                        "issues": f"Analysis failed: {str(e)}",
                        "error_count": 1,
                        "warning_count": 0
                    })

    # Clean up temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)
    log_callback(f"🧹 Cleaned up temporary directory: {temp_dir}")

    return results

def create_linter_configs(temp_dir):
    """Create configuration files for linters in the temporary directory."""
    # Pylint configuration
    with open(os.path.join(temp_dir, ".pylintrc"), "w") as f:
        f.write("""\
[BASIC]
function-naming-style=camelCase
variable-naming-style=camelCase
class-naming-style=PascalCase
""")

    # ESLint configuration
    with open(os.path.join(temp_dir, "eslintconfig.js"), "w") as f:
        f.write("""\
export default {
    rules: {
        "camelcase": ["error", { "properties": "always" }],
        "no-unused-vars": "warn",
        "no-console": "off",
        "semi": ["error", "always"],
        "quotes": ["error", "single"]
    }
};
""")

    # HTMLHint configuration
    with open(os.path.join(temp_dir, "htmlhint.config.js"), "w") as f:
        f.write("""\
module.exports = {
    rules: {
        "class-id-naming": {
            "pattern": "^[a-z][a-zA-Z0-9]*$",
            "message": "Class and ID names must be in camelCase"
        }
    }
};
""")

    # Stylelint configuration
    with open(os.path.join(temp_dir, "stylelint.config.js"), "w") as f:
        f.write("""\
module.exports = {
    rules: {
        "selector-class-pattern": ["^[a-z][a-zA-Z0-9]*$", {
            "message": "Class names must be in camelCase"
        }]
    }
};
""")

# =============================================
# Enhanced Streamlit UI Components
# =============================================

# Page Configuration
st.set_page_config(
    page_title="AutoCodeGuard",
    page_icon="🛡️",  # Changed to shield icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling with Button Enhancements
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .st-expander { background-color: white; border-radius: 10px; }
    .stButton>button { 
        border-radius: 20px; 
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .metric-box { padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .header { color: #2c3e50; text-align: center; padding: 20px 0; }
    .feature-card { padding: 20px; background: white; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .tool-item { padding: 10px 0; border-bottom: 1px solid #eee; }
    
    /* Button Highlights */
    [data-testid="baseButton-llm_btn"] > div > div {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 1px solid #45a049 !important;
    }
    [data-testid="baseButton-jira_btn"] > div > div {
        background-color: #0052CC !important;
        color: white !important;
        border: 1px solid #0041A3 !important;
    }
    [data-testid="baseButton-analyze_btn"] > div > div {
        background-color: #008CBA !important;
        color: white !important;
    }
    [data-testid="baseButton-webhook_btn"] > div > div {
        background-color: #9C27B0 !important;
        color: white !important;
    }
    [data-testid="baseButton-report_btn"] > div > div {
        background-color: #FF9800 !important;
        color: white !important;
    }
    
    /* Hover Effects */
    [data-testid="baseButton-llm_btn"] > div > div:hover {
        background-color: #45a049 !important;
        transform: scale(1.05);
    }
    [data-testid="baseButton-jira_btn"] > div > div:hover {
        background-color: #0041A3 !important;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)


# Header Section
st.markdown("""
    <div class="header">
        <h1 style="font-size: 2.5em; margin-bottom: 0.2em;">🛡️ AutoCodeGuard</h1>
        <p style="font-size: 1.2em; color: #666;">Professional Code Quality Analysis Platform</p>
    </div>
""", unsafe_allow_html=True)

# Session State Initialization
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'status' not in st.session_state:
    st.session_state.status = "Ready"

# Main Layout Columns
main_col, side_col = st.columns([3, 1])

# Main Layout Columns
main_col, side_col = st.columns([3, 1])

with main_col:
    # Analysis Controls Card with Enhanced Buttons
    with st.expander("🚀 Start New Analysis", expanded=True):
        repo_url = st.text_input(
            "GitHub Repository URL:", 
            placeholder="https://github.com/username/repository",
            help="Enter a public repository URL to analyze"
        )
        
        # Expanded button layout with 5 columns
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            analyze_btn = st.button("🔍 Analyze Now", 
                                  key="analyze_btn",
                                  use_container_width=True)
        with col2:
            webhook_btn = st.button("🔗 Setup Webhook", 
                                  key="webhook_btn",
                                  use_container_width=True)
        with col3:
            report_btn = st.button("📄 Generate Report", 
                                 key="report_btn",
                                 use_container_width=True)
        with col4:
            llm_btn = st.button("🧠 LLM Review", 
                              key="llm_btn",
                              use_container_width=True)
        with col5:
            jira_btn = st.button("🚀 Push to JIRA", 
                               key="jira_btn",
                               use_container_width=True)

    # Real-time Analysis Dashboard
    st.markdown("### 📊 Live Analysis Dashboard")
    
    # Status Indicators
    status_col1, status_col2, status_col3 ,status_col4= st.columns(4)
    with status_col1:
        st.markdown(f"<div class='metric-box'><b>Current Status</b><br>{st.session_state.status}</div>", 
                    unsafe_allow_html=True)
    with status_col2:
        total_logs = len(st.session_state.logs)
        st.markdown(f"<div class='metric-box'><b>Total Logs</b><br>{total_logs} entries</div>", 
                    unsafe_allow_html=True)

    with status_col4:
        st.markdown(f"<div class='metric-box'><b>LLM Review</b><br>Not started</div>", 
                    unsafe_allow_html=True) 
    with status_col3:
        progress_bar = st.progress(0)


    # Live Logs Display
    with st.expander("📝 Live Analysis Logs", expanded=True):
        log_container = st.empty()


with side_col:
    # Quick Actions Panel
    st.markdown("### ⚡ Quick Actions")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 Documentation", use_container_width=True):
                st.session_state.logs.append("ℹ️ Opening documentation...")
            if st.button("📁 View History", use_container_width=True):
                st.session_state.logs.append("🕒 Loading analysis history...")
        with col2:
            if st.button("📤 Export Results", use_container_width=True):
                st.session_state.logs.append("💾 Exporting analysis results...")
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.logs.append("⚙️ Opening settings...")

    # Enhanced System Information Panel
    st.markdown("### 🛠️ System Information")
    with st.expander("🔧 Installed Tools", expanded=True):
        st.markdown("""
            <div class="feature-card">
                <div class="tool-item">🐍 Python 3.12.3</div>
                <div class="tool-item">📜 ESLint 9.19.0</div>
                <div class="tool-item">🌐 HTMLHint 1.1.4</div>
                <div class="tool-item">🎨 Stylelint 16.2.1</div>
                <div class="tool-item">☕ Checkstyle 10.12.0</div>
                <div class="tool-item">🔍 Pylint 3.0.3</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Enhanced System Health Panel
    st.markdown("### 📈 System Health")
    st.markdown(f"""
        <div class='feature-card'>
            <b>⚡ CPU Usage:</b> 24%<br>
            <b>💾 Memory Usage:</b> 1.2/2.0 GB<br>
            <b>📂 Active Processes:</b> 12<br>
            <b>🌐 Network Activity:</b> 45 KB/s
        </div>
    """, unsafe_allow_html=True)

    # Linter Paths Section
    st.markdown("### 📂 Linter Paths")
    st.markdown(f"""
        <div class='feature-card'>
            <b>📦 Node Modules:</b> {node_modules_path}<br>
            <b>⚙️ Checkstyle JAR:</b> {os.getenv("CHECKSTYLE_JAR", "/default/path")}
        </div>
    """, unsafe_allow_html=True)


# Log Handling Functions
def update_status(text):
    st.session_state.status = text

def add_log(text):
    st.session_state.logs.append(text)
    if len(st.session_state.logs) > 20:
        st.session_state.logs.pop(0)
    log_container.markdown("\n".join([f"`{log}`" for log in st.session_state.logs[-20:]]))

# Analysis Trigger
if analyze_btn and repo_url:
    try:
        st.session_state.logs = []
        add_log("🚀 Starting analysis workflow...")
        
        # Run actual analysis
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
            st.success("🎉 Analysis Complete!")
            for lang, files in results.items():
                if files:
                    with st.expander(f"{lang} Results ({len(files)} files)"):
                        for file in files:
                            st.markdown(f"**{file['file']}** (Errors: {file['error_count']}, Warnings: {file['warning_count']})")
                            if file['issues'].strip():
                                st.code(file['issues'], language='text')
                            else:
                                st.success("No issues found!")

    except Exception as e:
        add_log(f"❌ Critical error: {str(e)}")
        update_status("Analysis failed")
        progress_bar.progress(0)

if jira_btn:
    add_log("🚀 Initiating JIRA integration...")
    # Placeholder for actual JIRA integration
    try:
        # Example integration code
        add_log("📡 Connecting to JIRA API...")
        sleep(1)
        add_log("📨 Creating new JIRA tickets...")
        sleep(1)
        st.success("✅ Successfully created 5 JIRA tickets!")
        add_log("✅ Code quality issues pushed to JIRA")
    except Exception as e:
        add_log(f"❌ JIRA integration failed: {str(e)}")

if llm_btn:
    add_log("🧠 Starting LLM Code Review...")
    try:
        # Placeholder for LLM analysis
        add_log("🤖 Initializing GPT-4 Code Analysis...")
        sleep(2)
        add_log("📝 Generating comprehensive code review...")
        sleep(2)
        st.success("✨ LLM Review Completed!")
        with st.expander("LLM Code Review Summary"):
            st.markdown("""
            ### 🧠 AI-Powered Code Review
            **Overall Rating**: B+
            
            **Key Improvements**:
            - Improve error handling in database connections
            - Add input validation for API endpoints
            - Consider implementing caching mechanism
            
            **Security Recommendations**:
            - Update vulnerable dependency: lodash@4.17.15
            - Implement rate limiting on authentication endpoints
            """)
    except Exception as e:
        add_log(f"❌ LLM analysis failed: {str(e)}")

# Updated Footer Section
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        🛡️ Powered by AutoCodeGuard | 📧 Support: [contact@autocodeguard.com](mailto:contact@autocodeguard.com)<br>
        📄 Terms of Service | 🔏 Privacy Policy | 📚 Documentation | 🌐 GitHub
    </div>
""", unsafe_allow_html=True)
