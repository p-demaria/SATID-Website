"""
ETF Data Downloader - Monthly Adjusted Data - IMPROVED VERSION
Downloads monthly ADJUSTED close prices for accurate total return analysis
Adjusted close includes dividends and splits for true performance measurement
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import time

ETF_LIST = {
    "CASH": ["BIL"],
    "FIXED_INCOME": ["SHY", "IGSB", "IGIB", "LQD", "SHYG", "HYG", "EMB", "CEMB"],
    "EQUITY": ["SPY", "QQQ", "IJK", "IWM", "VGK", "EWU", "EWJ", "EEM", "AAXJ", "MCHI", "INDA"],
    "ALTERNATIVES": ["GLD", "FTLS", "QAI", "WTMF"]
}

# Known benchmark returns for validation (SPY annual returns)
SPY_BENCHMARK_RETURNS = {
    2024: 0.2489,  # 24.89% (YTD as of data)
    2023: 0.2619,  # 26.19%
    2022: -0.1817, # -18.17%
    2021: 0.2875,  # 28.75%
    2020: 0.1837,  # 18.37%
    2019: 0.3122,  # 31.22%
    2018: -0.0456, # -4.56%
    2017: 0.2170,  # 21.70%
}

def download_etf_data_monthly(start_date=None, end_date=None):
    """
    Download monthly adjusted close prices for all ETFs
    
    IMPORTANT: Uses Adjusted Close which includes:
    - Dividend adjustments
    - Stock split adjustments
    - Total return calculation (not just price return)
    """
    
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        # Download 10 years + 2 months buffer to ensure 121+ data points
        start_date = end_date - timedelta(days=365*10 + 60)
    
    all_etfs = []
    for category, etfs in ETF_LIST.items():
        all_etfs.extend(etfs)
    
    print(f"Downloading MONTHLY ADJUSTED CLOSE data for {len(all_etfs)} ETFs...")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Data includes: Dividends + Splits (Total Return)")
    print("This may take a few minutes...\n")
    
    # Store series in a dictionary
    price_series = {}
    successful = 0
    failed = []
    
    for i, ticker in enumerate(all_etfs, 1):
        try:
            print(f"[{i}/{len(all_etfs)}] Downloading {ticker}...", end=" ")
            
            # Download data with monthly interval
            ticker_obj = yf.Ticker(ticker)
            # CRITICAL: Do NOT use auto_adjust=True, instead get 'Adj Close' explicitly
            # This ensures we get dividend-adjusted total return data
            data = ticker_obj.history(start=start_date, end=end_date, interval="1mo", auto_adjust=False)
            
            if not data.empty and 'Adj Close' in data.columns:
                # Use Adj Close for total return (includes dividends)
                price_series[ticker] = data['Adj Close'].copy()
                successful += 1
                print("✓")
            else:
                print("✗ (no data)")
                failed.append(ticker)
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"✗ (error: {str(e)[:50]})")
            failed.append(ticker)
    
    # Create DataFrame from the series dictionary
    if price_series:
        prices = pd.DataFrame(price_series)
        prices = prices.ffill()
    else:
        raise ValueError("No data downloaded successfully")
    
    print(f"\n{'='*60}")
    print(f"Successfully downloaded: {successful}/{len(all_etfs)} ETFs")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"Date range: {prices.index[0].strftime('%Y-%m-%d')} to {prices.index[-1].strftime('%Y-%m-%d')}")
    print(f"Total months: {len(prices)}")
    print(f"{'='*60}")
    
    return prices

def validate_spy_returns(prices):
    """
    Validate SPY returns against known benchmark returns
    This helps verify data quality and calculation accuracy
    """
    if 'SPY' not in prices.columns:
        print("\n⚠ SPY not in dataset - skipping validation")
        return
    
    print("\n" + "="*60)
    print("VALIDATING SPY RETURNS AGAINST OFFICIAL DATA")
    print("="*60)
    
    spy_prices = prices['SPY'].dropna()
    dates = spy_prices.index
    
    print(f"\n{'Year':<8} {'Calculated':<12} {'Official':<12} {'Difference':<12}")
    print("-" * 60)
    
    max_diff = 0
    total_diff = 0
    count = 0
    
    for year in sorted(SPY_BENCHMARK_RETURNS.keys()):
        year_data = spy_prices[dates.year == year]
        
        if len(year_data) >= 2:
            # Calculate using SIMPLE returns (standard for ETF reporting)
            calculated_return = (year_data.iloc[-1] / year_data.iloc[0]) - 1
            official_return = SPY_BENCHMARK_RETURNS[year]
            difference = calculated_return - official_return
            
            max_diff = max(max_diff, abs(difference))
            total_diff += abs(difference)
            count += 1
            
            status = "✓" if abs(difference) < 0.02 else "⚠"  # Flag if >2% difference
            
            print(f"{year:<8} {calculated_return*100:>10.2f}% {official_return*100:>10.2f}% "
                  f"{difference*100:>10.2f}% {status}")
    
    avg_diff = total_diff / count if count > 0 else 0
    
    print("-" * 60)
    print(f"Average absolute difference: {avg_diff*100:.2f}%")
    print(f"Maximum absolute difference: {max_diff*100:.2f}%")
    
    if avg_diff < 0.01:
        print("\n✓ EXCELLENT: Returns match official data within 1%")
    elif avg_diff < 0.02:
        print("\n✓ GOOD: Returns match official data within 2%")
    elif avg_diff < 0.05:
        print("\n⚠ ACCEPTABLE: Returns within 5% (may be due to monthly sampling)")
    else:
        print("\n⚠ WARNING: Large differences detected - verify data source")
        print("  Possible causes:")
        print("  - Monthly data uses end-of-month vs exact year-end dates")
        print("  - yfinance data quality issues")
        print("  - Timing differences in dividend adjustments")
    
    print("\nNOTE: Small differences (<2%) are normal due to:")
    print("  - Monthly data sampling vs daily exact dates")
    print("  - Timing of dividend reinvestment")
    print("  - Data provider calculation methods")
    print("="*60)

def save_data(prices, filename='etf_prices_monthly.csv'):
    """Save price data to CSV file"""
    prices.to_csv(filename)
    size_kb = os.path.getsize(filename) / 1024
    print(f"\n✓ Data saved to {filename} ({size_kb:.2f} KB)")

def main():
    """Main function"""
    print("="*60)
    print("ETF DATA DOWNLOADER - MONTHLY ADJUSTED CLOSE")
    print("="*60 + "\n")
    
    prices = download_etf_data_monthly()
    
    # Validate SPY returns against known benchmarks
    validate_spy_returns(prices)
    
    save_data(prices)
    
    print("\nSummary by Category:")
    print("-"*60)
    for category, etfs in ETF_LIST.items():
        available = [etf for etf in etfs if etf in prices.columns]
        print(f"{category:20} {len(available)}/{len(etfs)} ETFs")
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    print("\n✓ Data Type: Monthly Adjusted Close (includes dividends)")
    print("✓ Use for: Total Return calculations")
    print("✓ Calculation: Simple returns (standard for ETF reporting)")

if __name__ == "__main__":
    main()
