import os
import tempfile
import shutil
import subprocess
from git import Repo
from src.analyzers.python_analyzer import analyze_python
from src.analyzers.javascript_analyzer import analyze_javascript
from src.analyzers.html_analyzer import analyze_html
from src.analyzers.css_analyzer import analyze_css
from src.analyzers.java_analyzer import analyze_java

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

    # Copy configuration files for linters
    create_linter_configs(temp_dir)

    for root, _, files in os.walk(temp_dir):
        for file in files:
            # Skip linter configuration files
            if file in {".pylintrc", "eslintconfig.js", "htmlhint.config.js", "stylelint.config.js"}:
                log_callback(f"⚠️ Skipping linter config file: {file}")
                continue

            processed_files += 1
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, temp_dir)
            
            # Update progress
            status_callback(f"Analyzing ({processed_files}/{total_files}): {rel_path}")
            log_callback(f"📄 Processing {rel_path}...")

            # Python analysis
            if file.endswith(".py"):
                res = analyze_python(file_path, rel_path, log_callback, temp_dir)
                results["Python"].append(res)

            # JavaScript analysis
            elif file.endswith(".js"):
                if file.endswith(".min.js"):
                    log_callback(f"⚠️ Skipping minified file: {rel_path}")
                    continue

                res = analyze_javascript(file_path, rel_path, log_callback, temp_dir)
                results["JavaScript"].append(res)

            # HTML analysis
            elif file.endswith(".html"):
                res = analyze_html(file_path, rel_path, log_callback, temp_dir)
                results["HTML"].append(res)

            # CSS analysis
            elif file.endswith(".css"):
                res = analyze_css(file_path, rel_path, log_callback, temp_dir)
                results["CSS"].append(res)

            # Java analysis
            elif file.endswith(".java"):
                res = analyze_java(file_path, rel_path, log_callback)
                results["Java"].append(res)

    # Clean up temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)
    log_callback(f"🧹 Cleaned up temporary directory: {temp_dir}")

    return results


def create_linter_configs(temp_dir):
    """Copy existing linter configuration files to the cloned repo."""
    config_dir = os.path.join(os.path.dirname(__file__), "config")  # Path to config directory

    for config_file in [".pylintrc", "eslintconfig.js", "htmlhint.config.js", "stylelint.config.js"]:
        src_path = os.path.join(config_dir, config_file)
        dest_path = os.path.join(temp_dir, config_file)

        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)  # Copy linter config to cloned repo


def analyze_javascript(file_path, rel_path, log_callback, temp_dir):
    """Run ESLint analysis on a JavaScript file."""
    if file_path.endswith('.min.js'):
        log_callback(f"⚠️ Skipping minified file: {file_path}")
        return {
            "file": rel_path,
            "issues": "Minified files are skipped.",
            "error_count": 0,
            "warning_count": 0,
            "rating": "Good"
        }

    # Run ESLint analysis
    eslint_result = subprocess.run(
        ["npx", "eslint", "--config", "eslintconfig.js", "--format=stylish", file_path],
        capture_output=True, text=True, cwd=temp_dir
    )
    eslint_issues = eslint_result.stdout.strip()
    error_count = len(eslint_issues.splitlines()) if eslint_issues else 0
    warning_count = 0  # Adjust depending on ESLint config

    rating = "Good" if error_count == 0 else "Needs Improvement"
    if error_count > 5:
        rating = "Poor"

    log_callback(f"✅ JavaScript analysis completed for {rel_path}")
    return {
        "file": rel_path,
        "issues": eslint_issues,
        "error_count": error_count,
        "warning_count": warning_count,
        "rating": rating
    }
