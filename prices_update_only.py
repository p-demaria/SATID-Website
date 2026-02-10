"""
SATID PRICE UPDATE ONLY - COMPLETE WORKFLOW
============================================
Updates ETF prices and regenerates all reports/dashboards
WITHOUT re-optimizing FBIS parameters.

Use this script when:
- You want fresh price data in all outputs
- You've manually adjusted FBIS parameters and want to keep them
- You want routine daily/weekly updates

Execution sequence:
1. Download latest ETF prices → CSV
2. Generate Support Levels Interactive → HTML (uses existing JSON params)
3. Generate Portfolio Risk Exposure → HTML
4. Generate SATID Risk Score → HTML + Excel dashboard
5. Generate Portfolio Risk Dashboard → HTML

All outputs use existing FBIS parameters from JSON file.

Author: SATID Risk Management System
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Scripts to run in sequence (FBIS optimizer NOT included)
SCRIPTS = [
    {
        'name': 'ETF Price Download',
        'file': 'download_satid_data.py',
        'output': 'SATID_portfolio_etf_data_weekly_ohlc.csv'
    },
    {
        'name': 'Support Levels Interactive (No Optimization)',
        'file': 'generate_Fbis_Levels_Interactive_NO_OPTIMIZATION.py',
        'output': 'Support_Levels_Interactive.html'
    },
    {
        'name': 'Portfolio Risk Exposure',
        'file': 'Portfolio_Risk_Exposure.py',
        'output': 'Portfolio_Risk_Exposure.html'
    },
    {
        'name': 'SATID Risk Score',
        'file': 'SATID_Risk_Score.py',
        'output': 'SATID_Risk_Score.html'
    },
    {
        'name': 'Portfolio Risk Dashboard',
        'file': 'Portfolio_Risk_Dashboard.py',
        'output': 'Portfolio_Risk_Dashboard.html'
    }
]


def print_header():
    """Print script header"""
    print("=" * 80)
    print("SATID PRICE UPDATE ONLY - COMPLETE WORKFLOW")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🔒 FBIS parameters will NOT be modified")
    print("   (Uses existing SATID_Fbis_Optimized_Parameters.json)")
    print("=" * 80)
    print()


def run_script(script_info):
    """
    Run a Python script and capture output
    
    Returns:
        tuple: (success: bool, duration: float)
    """
    script_name = script_info['name']
    script_file = script_info['file']
    expected_output = script_info['output']
    
    print(f"\n{'─' * 80}")
    print(f"▶ Running: {script_name}")
    print(f"  Script: {script_file}")
    print(f"{'─' * 80}")
    
    start_time = datetime.now()
    
    try:
        # Check if script exists
        if not Path(script_file).exists():
            print(f"  ✗ ERROR: Script not found: {script_file}")
            return False, 0
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Print script output
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"  {line}")
        
        # Check for errors
        if result.returncode != 0:
            print(f"\n  ✗ FAILED (exit code {result.returncode})")
            if result.stderr:
                print(f"  Error output:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"    {line}")
            return False, duration
        
        # Verify output file was created
        if expected_output and not Path(expected_output).exists():
            print(f"  ⚠ WARNING: Expected output not found: {expected_output}")
            return False, duration
        
        print(f"\n  ✓ SUCCESS ({duration:.1f}s)")
        if expected_output:
            print(f"  ✓ Generated: {expected_output}")
        
        return True, duration
        
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n  ✗ TIMEOUT after {duration:.1f}s")
        return False, duration
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n  ✗ ERROR: {str(e)}")
        return False, duration


def print_summary(results):
    """Print execution summary"""
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    
    total_time = sum(r['duration'] for r in results)
    successful = sum(1 for r in results if r['success'])
    
    print(f"Total time: {total_time:.1f}s")
    print(f"Success: {successful}/{len(results)} scripts")
    print()
    
    # Detailed results
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['name']:<50} ({result['duration']:.1f}s)")
    
    print("\n" + "=" * 80)
    
    if successful == len(results):
        print("✓ ALL UPDATES COMPLETE!")
        print("\n📊 Generated outputs:")
        print("  • Support_Levels_Interactive.html")
        print("  • Portfolio_Risk_Exposure.html")
        print("  • SATID_Risk_Score.html")
        print("  • Portfolio_Risk_Dashboard.html")
        print("  • SATID_Risk_Dashboard.xlsx")
        print("\n💾 FBIS parameters unchanged (using existing JSON file)")
        print("\n🌐 Website ready files:")
        print("  All HTML dashboards have been updated with latest prices")
        print("  Support levels use your previously optimized/adjusted parameters")
    else:
        print("⚠ SOME SCRIPTS FAILED")
        print("Check error messages above for details")
    
    print("=" * 80)


def main():
    """Main execution flow"""
    print_header()
    
    results = []
    
    # Run each script in sequence
    for script_info in SCRIPTS:
        success, duration = run_script(script_info)
        results.append({
            'name': script_info['name'],
            'success': success,
            'duration': duration
        })
        
        # Stop on failure
        if not success:
            print(f"\n⚠ Stopping execution due to failure in: {script_info['name']}")
            break
    
    # Print final summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all(r['success'] for r in results) else 1)


if __name__ == "__main__":
    main()
