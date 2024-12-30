import subprocess
import time
import os

def run_script(script_name):
    """ Run a Python script and wait for it to complete. """
    try:
        subprocess.run(['python', script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

def main():
    print("Starting the trading signal generation script (1.py)...")
    run_script('1.py')  # This will generate signals.json

    print("Waiting for the signal file to be ready...")
    time.sleep(10)  # Wait for a few seconds to ensure the file is written

    # Check if the file exists and has content before running the second script
    if os.path.exists('signals.json') and os.path.getsize('signals.json') > 0:
        print("Starting the trading execution script (2.py)...")
        run_script('2.py')  # This will read signals.json and execute trades
    else:
        print("Signal file is not ready or empty.")

if __name__ == "__main__":
    main()
