import subprocess
import os

def analyze_javascript(file_path, rel_path, log_callback, temp_dir):
    if file_path.endswith('.min.js'):
        log_callback(f"⚠️ Skipping minified file: {file_path}")
        return {
            "file": rel_path,
            "issues": "Minified files are skipped.",
            "error_count": 0,
            "warning_count": 0,
            "rating": "Good"
        }

    # Run ESLint analysis using the correct config
    eslint_result = subprocess.run(
        ["eslint", "--config", os.path.join(temp_dir, "eslintconfig.js"), "--format=stylish", file_path],
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
