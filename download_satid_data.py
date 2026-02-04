"""
SATID ETF Weekly OHLC Downloader
→ Reads Model Portfolio.xlsx
→ Only ETFs with allocation > 0
→ Weekly OHLC (Friday close)
→ Saves: SATID_portfolio_etf_data_weekly_ohlc.csv
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import time

# === CONFIGURATION ===
PORTFOLIO_PATH = os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/Documents/Portfolio Management/Python/SATID/Model Portfolio.xlsx"
)
OUTPUT_CSV = "SATID_portfolio_etf_data_weekly_ohlc.csv"
START_DATE = datetime.now() - timedelta(days=365 * 10)  # 10 years
END_DATE = datetime.now()

# === STEP 1: READ PORTFOLIO & EXTRACT ACTIVE ETFS ===
def get_active_etfs():
    print(f"Reading portfolio: {PORTFOLIO_PATH}")
    if not os.path.exists(PORTFOLIO_PATH):
        raise FileNotFoundError(f"Portfolio not found: {PORTFOLIO_PATH}")

    df = pd.read_excel(PORTFOLIO_PATH, sheet_name="Portfolio", header=None)
    active = []

    for idx, row in df.iterrows():
        if len(row) < 6:
            continue
        ticker_cell = row.iloc[2] if len(row) > 2 else None
        alloc_pct = row.iloc[4] if len(row) > 4 else 0
        usd_amount = row.iloc[5] if len(row) > 5 else 0

        if pd.notna(ticker_cell) and isinstance(ticker_cell, str):
            ticker = ticker_cell.strip().upper()
            if alloc_pct > 0 or usd_amount > 0:
                if ticker not in active:
                    active.append(ticker)

    print(f"Found {len(active)} active ETFs: {', '.join(sorted(active))}")
    return active

# === STEP 2: DOWNLOAD WEEKLY OHLC ===
def download_weekly_ohlc(tickers):
    print(f"\nDownloading weekly OHLC for {len(tickers)} ETFs...")
    data = {}
    failed = []

    for i, ticker in enumerate(tickers, 1):
        try:
            print(f"[{i:2d}/{len(tickers)}] {ticker:<6}", end=" ")
            t = yf.Ticker(ticker)

            hist = t.history(start=START_DATE, end=END_DATE, interval="1d", auto_adjust=True)

            if hist.empty or len(hist) < 50:
                print("No data")
                failed.append(ticker)
                continue

            weekly = hist.resample('W-FRI').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })

            weekly = weekly[weekly.index.weekday == 4]
            weekly = weekly.dropna()

            if len(weekly) < 10:
                print(f"Too few weeks ({len(weekly)})")
                failed.append(ticker)
                continue

            for col in ['Open', 'High', 'Low', 'Close']:
                key = f"{ticker}_{col.lower()}"
                data[key] = weekly[col]

            print(f"{len(weekly)} weeks")
            time.sleep(0.25)

        except Exception as e:
            print(f"Error")
            failed.append(ticker)

    if not data:
        raise ValueError("No ETF data downloaded!")

    df = pd.DataFrame(data)
    df = df.sort_index()
    df = df.ffill().bfill()

    print(f"\nSuccess: {len(tickers) - len(failed)}/{len(tickers)}")
    if failed:
        print(f"Failed: {', '.join(failed)}")

    return df

# === STEP 3: SAVE TO CSV ===
def save_data(df):
    df.to_csv(OUTPUT_CSV)
    size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
    print(f"\nSaved to: {OUTPUT_CSV}")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Weeks: {len(df)}")
    print(f"   First date: {df.index[0].strftime('%Y-%m-%d')}")
    print(f"   Last date:  {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"   Columns: {list(df.columns)[:8]}...")

# === MAIN ===
def main():
    print("="*70)
    print("SATID ETF WEEKLY OHLC DOWNLOADER")
    print("="*70)

    tickers = get_active_etfs()
    if not tickers:
        print("No active ETFs found!")
        return

    df = download_weekly_ohlc(tickers)
    save_data(df)

    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE!")
    print("Ready for Market Structure Analysis.")
    print("="*70)

if __name__ == "__main__":
    main()
