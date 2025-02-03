import subprocess

def analyze_python(file_path, rel_path, log_callback, temp_dir):
    try:
        log_callback("🐍 Running Pylint and Flake8 analysis...")
        
        # Run Pylint analysis
        pylint_result = subprocess.run(
            ["pylint", "--output-format=text", "--rcfile=.pylintrc", file_path],
            capture_output=True, text=True, cwd=temp_dir
        )
        pylint_issues = pylint_result.stdout if pylint_result.returncode in [0, 1] else pylint_result.stderr
        pylint_error_count = pylint_issues.count('error') + pylint_issues.count('Error')
        pylint_warning_count = pylint_issues.count('warning') + pylint_issues.count('Warning')
        
        # Run Flake8 analysis
        flake8_result = subprocess.run(
            ["flake8", "--max-line-length=79", file_path],
            capture_output=True, text=True, cwd=temp_dir
        )
        flake8_issues = flake8_result.stdout.strip()
        flake8_error_count = len(flake8_issues.splitlines()) if flake8_issues else 0
        flake8_warning_count = 0  # Flake8 doesn't distinguish between errors and warnings

        # Combine results
        total_error_count = pylint_error_count + flake8_error_count
        total_warning_count = pylint_warning_count + flake8_warning_count
        
        # Code rating based on the number of issues
        rating = "Good" if total_error_count == 0 and total_warning_count == 0 else "Needs Improvement"
        if total_error_count > 5:
            rating = "Poor"

        log_callback(f"✅ Python analysis completed for {rel_path}")
        return {
            "file": rel_path,
            "issues": f"Pylint Issues:\n{pylint_issues}\n\nFlake8 Issues:\n{flake8_issues}",
            "error_count": total_error_count,
            "warning_count": total_warning_count,
            "rating": rating  # Make sure this is included
        }
    except Exception as e:
        log_callback(f"❌ Python analysis failed: {str(e)}")
        return {
            "file": rel_path,
            "issues": f"Analysis failed: {str(e)}",
            "error_count": 1,
            "warning_count": 0,
            "rating": "Error"  # Include rating here as well in case of error
        }
