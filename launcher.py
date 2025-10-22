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


def main():
    """Launch the Streamlit application"""
    # Get the directory where this script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = Path(sys.executable).parent
    else:
        # Running as script
        application_path = Path(__file__).parent

    # Change to application directory
    os.chdir(application_path)

    # Set up environment
    app_file = application_path / "app.py"

    if not app_file.exists():
        print(f"Error: app.py not found at {app_file}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Launch Streamlit
    print("=" * 80)
    print("Performance Test Script Converter (PTSC)")
    print("=" * 80)
    print(f"Application path: {application_path}")
    print(f"Starting Streamlit server...")
    print("=" * 80)

    # Start Streamlit in subprocess
    try:
        # Run streamlit with specific port and headless mode
        cmd = [
            sys.executable,
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
            bufsize=1
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
