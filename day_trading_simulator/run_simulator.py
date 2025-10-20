"""
Simple script to run the day trading simulator
"""

import sys
import os
from main_simulator import DayTradingSimulator

def main():
    """Simple entry point for the simulator"""
    try:
        print("=" * 50)
        print("Day Trading Simulator")
        print("=" * 50)
        print()
        print("This simulator will:")
        print("- Test 5 different trading strategies")
        print("- Make 2 trades per strategy per day")
        print("- Use real market data")
        print("- Track all trades in Excel")
        print("- Start with $100,000 virtual capital")
        print()
        print("Press Ctrl+C at any time to stop the simulation")
        print("=" * 50)
        print()
        
        # Create simulator
        simulator = DayTradingSimulator()
        
        # Start simulation
        simulator.start_simulation()
        
        print("Simulation is now running...")
        print("Check the Excel file 'trading_log.xlsx' for trade data")
        print("Check the 'logs' folder for detailed logs")
        print()
        
        # Keep running until interrupted
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping simulation...")
            simulator.stop_simulation()
            print("Simulation stopped.")
            print("Thank you for using the Day Trading Simulator!")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
