import subprocess
import os

def analyze_java(file_path, rel_path, log_callback):
    try:
        log_callback("☕ Running Checkstyle analysis...")
        checkstyle_jar = os.getenv("CHECKSTYLE_JAR", "/home/ishu/checkstyle-10.12.0-all.jar")
        checkstyle_config = os.getenv("CHECKSTYLE_CONFIG", "/home/ishu/sun_checks.xml")
        
        result = subprocess.run(
            ["java", "-jar", checkstyle_jar, "-c", checkstyle_config, file_path],
            capture_output=True, text=True
        )
        issues = result.stdout if result.returncode == 0 else result.stderr
        log_callback(f"✅ Java analysis completed for {rel_path}")
        return {
            "file": rel_path,
            "issues": issues,
            "error_count": issues.count('ERROR'),
            "warning_count": issues.count('WARN')
        }
    except Exception as e:
        log_callback(f"❌ Java analysis failed: {str(e)}")
        return {
            "file": rel_path,
            "issues": f"Analysis failed: {str(e)}",
            "error_count": 1,
            "warning_count": 0
        }
