"""
Test script to run PTSC.exe and capture output
"""
import subprocess
import time

print("Starting PTSC.exe...")
print("=" * 80)

# Run PTSC.exe and capture output
process = subprocess.Popen(
    [r"dist\PTSC\PTSC.exe"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    universal_newlines=True
)

# Read output for 10 seconds
start_time = time.time()
timeout = 10

try:
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if line:
            print(line.rstrip())

        # Check if process has ended
        if process.poll() is not None:
            # Read remaining output
            remaining = process.stdout.read()
            if remaining:
                print(remaining)
            break

        time.sleep(0.1)

    # Terminate if still running
    if process.poll() is None:
        print("\n" + "=" * 80)
        print("Process is still running. Killing it...")
        process.terminate()
        time.sleep(2)
        if process.poll() is None:
            process.kill()

        # Get any remaining output
        stdout, stderr = process.communicate()
        if stdout:
            print("Remaining stdout:", stdout)
        if stderr:
            print("Stderr:", stderr)

    print("\n" + "=" * 80)
    print(f"Process exit code: {process.returncode}")

except KeyboardInterrupt:
    print("\nInterrupted by user")
    process.terminate()
