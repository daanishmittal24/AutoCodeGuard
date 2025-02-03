import subprocess
import os

def analyze_css(file_path, rel_path, log_callback, temp_dir):
    try:
        log_callback("🎨 Running Stylelint analysis for CSS...")
        node_modules_path = os.path.join(os.getcwd(), "node_modules", ".bin")
        stylelint_cmd = os.path.join(node_modules_path, 'stylelint')
        result = subprocess.run(
            [stylelint_cmd, file_path, "--formatter", "string", "--config", "stylelint.config.js"],
            capture_output=True, text=True, cwd=temp_dir
        )
        issues = result.stdout if result.returncode in [0, 1] else result.stderr
        log_callback(f"✅ CSS analysis completed for {rel_path}")
        return {
            "file": rel_path,
            "issues": issues,
            "error_count": issues.count('✖'),
            "warning_count": issues.count('⚠')
        }
    except Exception as e:
        log_callback(f"❌ CSS analysis failed: {str(e)}")
        return {
            "file": rel_path,
            "issues": f"Analysis failed: {str(e)}",
            "error_count": 1,
            "warning_count": 0
        }
