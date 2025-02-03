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
    results = {"Python": [], "JavaScript": [], "HTML": [], "CSS": [], "Java": []}

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

# Streamlit UI
st.set_page_config(page_title="AutoCodeGuard", page_icon="🔍", layout="wide")

st.title("🔍 AutoCodeGuard - Real-Time Code Analysis")
st.markdown("### Comprehensive Static Analysis with Live Feedback")

# Session state initialization
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'status' not in st.session_state:
    st.session_state.status = "Ready"

# Layout columns
col1, col2 = st.columns([3, 1])

with col1:
    repo_url = st.text_input("**GitHub Repository URL:**", 
                           placeholder="https://github.com/username/repository",
                           help="Enter a public repository URL to analyze")

with col2:
    st.markdown("## Current Status")
    status_display = st.empty()
    progress_bar = st.progress(0)

# Logs container
logs_container = st.expander("Live Analysis Logs", expanded=True)
with logs_container:
    log_display = st.empty()

def update_status(text):
    st.session_state.status = text
    status_display.markdown(f"**Status:** {text}")

def add_log(text):
    st.session_state.logs.append(text)
    log_display.markdown("\n".join(st.session_state.logs[-20:]))

# Analysis trigger
if repo_url:
    st.session_state.logs = []
    st.session_state.status = "Starting analysis..."
    
    try:
        results = analyze_repo(
            repo_url,
            status_callback=update_status,
            log_callback=add_log
        )
        
        if "Error" in results:
            add_log(f"❌ Final status: Analysis failed - {results['Error'][0]}")
        else:
            add_log("✅ Analysis completed successfully!")
            update_status("Analysis complete")
            progress_bar.progress(100)
            sleep(0.5)
            progress_bar.empty()

            # Display results
            st.success("Analysis Complete!")
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

# Sidebar with system info
with st.sidebar:
    st.markdown("## System Information")
    st.markdown(f"**Python Version:** {sys.version.split()[0]}")
    st.markdown("**Installed Tools:**")
    st.markdown("- Pylint 3.0.3\n- ESLint 9.19.0\n- HTMLHint 1.1.4\n- Stylelint (for CSS analysis)\n- Checkstyle 10.12.0")
    st.markdown("**Linter Paths:**")
    st.markdown(f"- Node Modules: `{node_modules_path}`")
    st.markdown("---")
    st.markdown("**Live Logs Summary**")
    if st.session_state.logs:
        st.metric("Total Log Entries", len(st.session_state.logs))
        st.metric("Last Log Entry", st.session_state.logs[-1][:50] + "...")
    else:
        st.info("No logs generated yet")

st.markdown("---")
st.caption("🛠️ Professional Code Quality Analysis System | 📧 Support: contact@autocodeguard.com")