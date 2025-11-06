"""
Performance Test Script Converter (PTSC) Launcher
Launches the Streamlit application
"""
import sys
import os
import webbrowser
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
import multiprocessing
import threading


def main():
    """Launch the Streamlit application"""
    # CRITICAL: Prevent infinite recursion when frozen
    multiprocessing.freeze_support()

    # Get the directory where this script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # In onedir mode, sys._MEIPASS points to _internal folder
        # In onefile mode, sys._MEIPASS points to temp extraction folder
        if hasattr(sys, '_MEIPASS'):
            application_path = Path(sys._MEIPASS)
        else:
            # Fallback: check _internal folder relative to executable
            exe_dir = Path(sys.executable).parent
            internal_dir = exe_dir / "_internal"
            if internal_dir.exists():
                application_path = internal_dir
            else:
                application_path = exe_dir
    else:
        # Running as script
        application_path = Path(__file__).parent

    # Set up environment
    app_file = application_path / "app.py"

    print("=" * 80)
    print("Performance Test Script Converter (PTSC)")
    print("=" * 80)
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Has _MEIPASS: {hasattr(sys, '_MEIPASS')}")
    if hasattr(sys, '_MEIPASS'):
        print(f"_MEIPASS: {sys._MEIPASS}")
    print(f"sys.executable: {sys.executable}")
    print(f"Executable parent: {Path(sys.executable).parent}")
    print(f"Application path: {application_path}")
    print(f"Looking for app.py at: {app_file}")
    print(f"File exists: {app_file.exists()}")

    if not app_file.exists():
        print(f"\nError: app.py not found!")
        print(f"Searched at: {app_file}")
        print(f"\nDirectory contents:")
        for item in application_path.iterdir():
            print(f"  - {item.name}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Launch Streamlit
    print(f"Starting Streamlit server...")
    print("=" * 80)

    try:
        # Import streamlit CLI
        from streamlit.web import cli as stcli

        # Set environment variables to configure Streamlit
        os.environ['STREAMLIT_SERVER_PORT'] = '8501'
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'

        # Prepare arguments (simpler, let environment vars handle config)
        sys.argv = [
            "streamlit",
            "run",
            str(app_file),
        ]

        print(f"Arguments: {' '.join(sys.argv)}")
        print("=" * 80)

        # Shared variables to track browser process
        chrome_process = None
        chrome_user_data_dir = None
        should_exit = threading.Event()

        # Open browser in a separate thread after a delay
        def open_browser():
            nonlocal chrome_process, chrome_user_data_dir
            time.sleep(3)
            url = "http://localhost:8501"
            print(f"\nOpening browser at {url}")

            # Try to open Chrome in a new window explicitly
            try:
                # Chrome with --app mode for standalone window and separate profile
                chrome_path = None
                possible_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break

                if chrome_path:
                    # Create temporary user-data-dir for isolated Chrome instance
                    chrome_user_data_dir = tempfile.mkdtemp(prefix="ptsc_chrome_")

                    # Open in app mode with isolated profile to ensure separate process
                    chrome_process = subprocess.Popen(
                        [
                            chrome_path,
                            f"--user-data-dir={chrome_user_data_dir}",
                            f"--app={url}",
                            "--new-window"
                        ]
                    )
                    print("Chrome opened in app mode. Monitoring browser...")
                else:
                    # Fallback to default browser
                    webbrowser.open(url, new=1)
            except Exception as e:
                print(f"Failed to open Chrome, using default browser: {e}")
                webbrowser.open(url, new=1)

        # Monitor Chrome process - exit when Chrome closes
        def monitor_browser():
            nonlocal chrome_process, chrome_user_data_dir
            if chrome_process:
                try:
                    # Wait for Chrome process to exit
                    chrome_process.wait()
                    print("\n\nBrowser closed. Shutting down application...")
                    should_exit.set()

                    # Cleanup temporary Chrome profile directory
                    if chrome_user_data_dir and os.path.exists(chrome_user_data_dir):
                        try:
                            shutil.rmtree(chrome_user_data_dir, ignore_errors=True)
                            print(f"Cleaned up Chrome profile: {chrome_user_data_dir}")
                        except Exception as cleanup_err:
                            print(f"Warning: Cleanup failed: {cleanup_err}")

                    # Force exit
                    os._exit(0)
                except Exception as e:
                    print(f"Browser monitoring error: {e}")

        # Run Streamlit in a separate thread
        def run_streamlit():
            try:
                stcli.main()
            except SystemExit:
                pass

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Wait a bit for browser to start
        time.sleep(5)

        # Start browser monitoring if Chrome was opened
        if chrome_process:
            monitor_thread = threading.Thread(target=monitor_browser, daemon=False)
            monitor_thread.start()

        print("\n" + "=" * 80)
        print("Application is running!")
        print("Close the browser window to stop the application.")
        print("=" * 80 + "\n")

        # Run Streamlit in main thread
        run_streamlit()

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
