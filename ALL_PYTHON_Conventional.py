#!/usr/bin/env python3
"""
SATID Master Script Runner
Executes all SATID generation scripts in the correct sequence
"""

import subprocess
import sys
from datetime import datetime

# Define scripts in execution order
SCRIPTS = [
    ('download_data.py', 'Downloading daily ETF data'),
    ('calculate_portfolios.py', 'Calculating daily portfolio statistics'),
    ('download_data_monthly.py', 'Downloading monthly ETF data'),
    ('calculate_portfolios_monthly.py', 'Calculating monthly portfolio statistics'),
    ('generate_dashboard_monthly.py', 'Generating portfolio dashboard'),
    ('generate_model_portfolios.py', 'Generating model portfolios page'),
    ('generate_portfolio_stats_monthly.py', 'Generating portfolio statistics'),
    ('generate_annual_returns_chart.py', 'Generating annual returns chart'),
]

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70)

def print_step(step_num, total_steps, message):
    """Print a step indicator"""
    print(f"\n[{step_num}/{total_steps}] {message}...")

def run_script(script_name):
    """Run a Python script and return success status"""
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"\n❌ ERROR: {script_name} not found in current directory")
        return False

def main():
    """Main execution function"""
    start_time = datetime.now()
    
    print_header("SATID MASTER SCRIPT RUNNER")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total scripts to run: {len(SCRIPTS)}")
    
    successful = 0
    failed = 0
    
    for i, (script, description) in enumerate(SCRIPTS, 1):
        print_step(i, len(SCRIPTS), description)
        
        if run_script(script):
            successful += 1
            print(f"✓ {script} completed successfully")
        else:
            failed += 1
            print(f"✗ {script} failed")
            
            # Ask user if they want to continue
            response = input("\nContinue with remaining scripts? (y/n): ").lower()
            if response != 'y':
                print("\nStopping execution as requested.")
                break
    
    # Print summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("EXECUTION SUMMARY")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print(f"\nResults:")
    print(f"  ✓ Successful: {successful}/{len(SCRIPTS)}")
    print(f"  ✗ Failed: {failed}/{len(SCRIPTS)}")
    
    if failed == 0:
        print("\n🎉 All scripts completed successfully!")
    else:
        print(f"\n⚠️  {failed} script(s) failed. Please check errors above.")
    
    print("=" * 70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
