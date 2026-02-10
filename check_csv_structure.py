"""
DIAGNOSTIC: Check CSV structure and HEAL price timeline
"""
import pandas as pd

CSV_FILE = 'SATID_portfolio_etf_data_weekly_ohlc.csv'

print("="*80)
print("CSV STRUCTURE ANALYSIS")
print("="*80)

# Read the raw CSV to check structure
print("\n[1] RAW CSV INSPECTION (first 10 lines):")
with open(CSV_FILE, 'r') as f:
    for i, line in enumerate(f):
        if i < 10:
            print(f"  Line {i}: {line.strip()[:100]}")  # First 100 chars
        else:
            break

# Load and analyze
print("\n[2] LOADED DATAFRAME:")
df = pd.read_csv(CSV_FILE)
print(f"  Shape: {df.shape} (rows × columns)")
print(f"  Columns: {df.columns.tolist()[:10]}")  # First 10 columns

# Check date column
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    print(f"\n[3] DATE ANALYSIS:")
    print(f"  First date: {df['date'].min()}")
    print(f"  Last date: {df['date'].max()}")
    print(f"  Total dates: {len(df)}")
    
    # Check for gaps/frequency
    df_sorted = df.sort_values('date')
    date_diffs = df_sorted['date'].diff()
    print(f"\n  Date frequency analysis:")
    print(f"    Min gap: {date_diffs.min()}")
    print(f"    Max gap: {date_diffs.max()}")
    print(f"    Most common gap: {date_diffs.mode()[0] if len(date_diffs.mode()) > 0 else 'N/A'}")
    
    # Show last 10 dates
    print(f"\n  Last 10 dates in CSV:")
    for idx, row in df_sorted.tail(10).iterrows():
        heal_price = row.get('HEAL_close', 'N/A')
        print(f"    {row['date'].date()}: HEAL = ${heal_price:.2f}" if isinstance(heal_price, (int, float)) else f"    {row['date'].date()}: HEAL = {heal_price}")

# Check if HEAL_close exists
if 'HEAL_close' in df.columns:
    print(f"\n[4] HEAL PRICE DATA:")
    heal_data = df[['date', 'HEAL_close']].dropna()
    print(f"  Non-null HEAL prices: {len(heal_data)}")
    print(f"  Last 10 HEAL entries:")
    for idx, row in heal_data.tail(10).iterrows():
        print(f"    {row['date']}: ${row['HEAL_close']:.2f}")
    
    # Check for 26.56
    price_26_56 = heal_data[heal_data['HEAL_close'].between(26.55, 26.57)]
    if len(price_26_56) > 0:
        print(f"\n  ⚠ Found $26.56 HEAL price at:")
        for idx, row in price_26_56.iterrows():
            print(f"    {row['date']}")
    else:
        print(f"\n  No $26.56 price found in HEAL data")
    
    # Check for 28.28
    price_28_28 = heal_data[heal_data['HEAL_close'].between(28.27, 28.29)]
    if len(price_28_28) > 0:
        print(f"\n  ✓ Found $28.28 HEAL price at:")
        for idx, row in price_28_28.iterrows():
            print(f"    {row['date']}")
    else:
        print(f"\n  No $28.28 price found in HEAL data")

print("\n" + "="*80)
