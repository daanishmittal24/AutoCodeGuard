import subprocess

def check_tool_availability(tool_name):
    #\"\"\"Check if a tool is installed and available in the system PATH.\"\"\"
    try:
        subprocess.run([tool_name, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
