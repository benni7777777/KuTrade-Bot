import subprocess
import time
import datetime

def run_script(script_name):
    """Run a Python script using subprocess."""
    try:
        subprocess.run(['python', script_name], check=True)
        print(f"{script_name} executed successfully.")
    except subprocess.CalledProcessError:
        print(f"Error occurred while executing {script_name}.")

def main():
    while True:
        try:
            print("\nRunning 1.py to generate signals...")
            subprocess.run(['python', '1.py'], check=True)
            
            print("\nWaiting 30 seconds for signals to be written...")
            time.sleep(30)
            
            print("\nRunning 2.py to execute trades...")
            subprocess.run(['python', '2.py'], check=True)
            
            print("\nWaiting 45 minutes before next scan...")
            time.sleep(2700)  # 45 minutes
            
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(300)  # 5 minute cooldown on error

if __name__ == "__main__":
    try:
        print("\nKuCoin Futures Trading Bot")
        print("-------------------------")
        print("This bot will:")
        print("1. Generate and execute trades")
        print("2. Wait 45 minutes for profit development")
        print("3. Manage positions and take profits")
        print("4. Prepare for next cycle\n")
        
        hours = float(input("Enter the number of hours to run (e.g., 24 for one day): "))
        if hours <= 0:
            raise ValueError("Hours must be positive")
            
        print(f"\nStarting trading bot for {hours} hours...")
        print("Note: Each cycle takes 45 minutes to allow trades to develop properly")
        main()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please enter a valid positive number for hours.")
