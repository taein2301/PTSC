"""
Performance Test Script Converter (PTSC) Launcher
Launches the Streamlit application
"""
import sys
import os
import webbrowser
import time
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

        # Open browser in a separate thread after a delay
        def open_browser():
            time.sleep(3)
            url = "http://localhost:8501"
            print(f"\nOpening browser at {url}")
            webbrowser.open(url)

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        print("\n" + "=" * 80)
        print("Application is running!")
        print("Press Ctrl+C to stop the application.")
        print("=" * 80 + "\n")

        # Run Streamlit
        sys.exit(stcli.main())

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
