"""
ETF Data Downloader - Python 3.13 Compatible
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

def download_etf_data(start_date=None, end_date=None):
    """Download adjusted close prices for all ETFs"""
    
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=365*10 + 5)
    
    all_etfs = []
    for category, etfs in ETF_LIST.items():
        all_etfs.extend(etfs)
    
    print(f"Downloading data for {len(all_etfs)} ETFs...")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("This may take a few minutes...\n")
    
    # Store series in a dictionary
    price_series = {}
    successful = 0
    failed = []
    
    for i, ticker in enumerate(all_etfs, 1):
        try:
            print(f"[{i}/{len(all_etfs)}] Downloading {ticker}...", end=" ")
            
            # Download data
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)
            
            if not data.empty and 'Close' in data.columns:
                # Extract the Close series directly
                price_series[ticker] = data['Close'].copy()
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
    print(f"Total days: {len(prices)}")
    print(f"{'='*60}")
    
    return prices

def save_data(prices, filename='etf_prices.csv'):
    """Save price data to CSV file"""
    prices.to_csv(filename)
    size_kb = os.path.getsize(filename) / 1024
    print(f"\n✓ Data saved to {filename} ({size_kb:.2f} KB)")

def main():
    """Main function"""
    print("="*60)
    print("ETF DATA DOWNLOADER")
    print("="*60 + "\n")
    
    prices = download_etf_data()
    save_data(prices)
    
    print("\nSummary by Category:")
    print("-"*60)
    for category, etfs in ETF_LIST.items():
        available = [etf for etf in etfs if etf in prices.columns]
        print(f"{category:20} {len(available)}/{len(etfs)} ETFs")
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()