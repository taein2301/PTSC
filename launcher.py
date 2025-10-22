"""
Performance Test Script Converter (PTSC) Launcher
Launches the Streamlit application
"""
import sys
import os
import subprocess
import webbrowser
import time
from pathlib import Path
import multiprocessing


def find_python_executable():
    """Find the Python interpreter executable"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        # Need to find the bundled Python interpreter
        if sys.platform == 'win32':
            # On Windows, look for python.exe in the bundle
            bundle_dir = Path(sys._MEIPASS)
            python_paths = [
                bundle_dir / 'python.exe',
                bundle_dir / 'python' / 'python.exe',
                Path(sys.executable).parent / 'python.exe',
            ]
            for python_path in python_paths:
                if python_path.exists():
                    return str(python_path)

            # If not found, use pythonw to avoid console window
            # This assumes Python is in PATH
            return 'pythonw'
        else:
            return 'python3'
    else:
        # Running as script, use current interpreter
        return sys.executable


def main():
    """Launch the Streamlit application"""
    # CRITICAL: Prevent infinite recursion when frozen
    if getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()

    # Get the directory where this script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # PyInstaller extracts files to sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
            # Files are in the temporary _MEIPASS folder
            application_path = Path(sys._MEIPASS)
        else:
            # Fallback to executable directory
            application_path = Path(sys.executable).parent
    else:
        # Running as script
        application_path = Path(__file__).parent

    # Set up environment
    app_file = application_path / "app.py"

    print("=" * 80)
    print("Performance Test Script Converter (PTSC)")
    print("=" * 80)
    print(f"Application path: {application_path}")
    print(f"Looking for app.py at: {app_file}")
    print(f"File exists: {app_file.exists()}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")

    if not app_file.exists():
        print(f"\nError: app.py not found!")
        print(f"Searched at: {app_file}")
        print(f"\nDirectory contents:")
        for item in application_path.iterdir():
            print(f"  - {item.name}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Find Python executable
    python_exe = find_python_executable()
    print(f"Python executable: {python_exe}")

    # Launch Streamlit
    print(f"Starting Streamlit server...")
    print("=" * 80)

    # Start Streamlit in subprocess
    try:
        # Run streamlit with specific port and headless mode
        cmd = [
            python_exe,
            "-m", "streamlit", "run",
            str(app_file),
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]

        print(f"Command: {' '.join(cmd)}")
        print("=" * 80)

        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )

        # Wait a bit for server to start
        time.sleep(3)

        # Open browser
        url = "http://localhost:8501"
        print(f"\nOpening browser at {url}")
        webbrowser.open(url)

        print("\n" + "=" * 80)
        print("Application is running!")
        print("Close this window to stop the application.")
        print("=" * 80 + "\n")

        # Keep reading output
        for line in process.stdout:
            print(line.strip())

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
