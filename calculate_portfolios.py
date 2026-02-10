#!/usr/bin/env python3
"""
Portfolio Calculator - Updated to read allocations from Excel
Calculates comprehensive statistics for all portfolios defined in portfolio_allocations.xlsx
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_portfolios_from_excel(excel_path='portfolio_allocations.xlsx'):
    """Load portfolio allocations from Excel file"""
    df = pd.read_excel(excel_path, header=None)
    
    portfolio_configs = [
        {'name': 'Conservative Income', 'ticker_col': 2, 'value_col': 3},
        {'name': 'Conservative Balanced', 'ticker_col': 6, 'value_col': 7},
        {'name': 'Balanced Portfolio', 'ticker_col': 10, 'value_col': 11},
        {'name': 'Growth Portfolio', 'ticker_col': 14, 'value_col': 15},
        {'name': 'Aggressive Growth Portfolio', 'ticker_col': 18, 'value_col': 19}
    ]
    
    portfolios = {}
    
    for config in portfolio_configs:
        port_name = config['name']
        ticker_col = config['ticker_col']
        value_col = config['value_col']
        
        allocations = {}
        
        for row_idx in range(3, 30):
            ticker = df.iloc[row_idx, ticker_col]
            value = df.iloc[row_idx, value_col]
            
            if pd.notna(ticker) and pd.notna(value):
                try:
                    val_float = float(value)
                    if val_float > 0:
                        allocations[str(ticker)] = val_float
                except (ValueError, TypeError):
                    continue
        
        portfolios[port_name] = {
            'name': port_name,
            'allocations': allocations
        }
    
    return portfolios


def calculate_portfolio_stats(prices_df, allocations, initial_value=100):
    """Calculate comprehensive portfolio statistics"""
    
    # Calculate daily returns for each asset
    returns = prices_df.pct_change().dropna()
    
    # Calculate portfolio returns
    portfolio_returns = pd.Series(0, index=returns.index)
    for ticker, weight in allocations.items():
        if ticker in returns.columns:
            portfolio_returns += returns[ticker] * weight
    
    # Calculate portfolio value over time
    portfolio_values = (1 + portfolio_returns).cumprod() * initial_value
    
    # Basic metrics
    total_return = (portfolio_values.iloc[-1] / initial_value) - 1
    years = len(portfolio_values) / 252
    annualized_return = (1 + total_return) ** (1 / years) - 1
    
    # Volatility (annualized)
    volatility = portfolio_returns.std() * np.sqrt(252)
    
    # Risk-free rate (approximate)
    risk_free_rate = 0.02
    
    # Sharpe Ratio
    sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    # Sortino Ratio
    downside_returns = portfolio_returns[portfolio_returns < 0]
    downside_deviation = downside_returns.std() * np.sqrt(252)
    sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
    
    # Maximum Drawdown
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    max_dd_idx = drawdown.idxmin()
    max_drawdown_date = max_dd_idx
    
    # Time to Recovery
    recovery_date = None
    time_to_recovery = None
    if max_dd_idx is not None:
        future_values = cumulative[max_dd_idx:]
        recovery_mask = future_values >= running_max[max_dd_idx]
        if recovery_mask.any():
            recovery_date = future_values[recovery_mask].index[0]
            time_to_recovery = (recovery_date - max_dd_idx).days
    
    # Calmar Ratio
    calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # Best and Worst Periods
    returns.index = pd.to_datetime(returns.index, utc=True).tz_localize(None)
    portfolio_returns.index = pd.to_datetime(portfolio_returns.index, utc=True).tz_localize(None)
    monthly_returns = portfolio_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    best_month = monthly_returns.max()
    best_month_date = monthly_returns.idxmax()
    worst_month = monthly_returns.min()
    worst_month_date = monthly_returns.idxmin()
    
    # Format dates
    best_month_str = best_month_date.strftime('%B %Y') if best_month_date else None
    worst_month_str = worst_month_date.strftime('%B %Y') if worst_month_date else None
    
    # Win Rate
    win_rate = (monthly_returns > 0).sum() / len(monthly_returns) if len(monthly_returns) > 0 else 0
    
    # VaR (95% confidence)
    var_95 = np.percentile(portfolio_returns, 5) * portfolio_values.iloc[-1]
    
    return {
        "total_return": float(total_return),
        "annualized_return": float(annualized_return),
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "calmar_ratio": float(calmar_ratio),
        "max_drawdown": float(max_drawdown),
        "max_drawdown_date": max_drawdown_date.strftime('%Y-%m-%d') if max_drawdown_date else None,
        "time_to_recovery": int(time_to_recovery) if time_to_recovery else None,
        "recovery_date": recovery_date.strftime('%Y-%m-%d') if recovery_date else None,
        "best_month": float(best_month),
        "best_month_date": best_month_str,
        "worst_month": float(worst_month),
        "worst_month_date": worst_month_str,
        "win_rate": float(win_rate),
        "var_95": float(var_95),
        "final_value": float(portfolio_values.iloc[-1]),
        "initial_value": float(portfolio_values.iloc[0]),
        "years": float(years),
        "downside_deviation": float(downside_deviation)
    }


def main():
    print("=" * 60)
    print("PORTFOLIO CALCULATOR")
    print("=" * 60)
    print()
    
    # Load portfolio allocations from Excel
    print("Loading portfolio allocations from Excel...")
    portfolios = load_portfolios_from_excel()
    print(f"✓ Loaded {len(portfolios)} portfolios")
    print()
    
    # Load price data
    print("Loading price data...")
    prices_df = pd.read_csv('etf_prices.csv', index_col=0, parse_dates=True)
    print(f"Loaded price data: {len(prices_df)} days")
    print()
    
    # Calculate statistics for each portfolio
    results = {}
    
    for port_name, port_data in portfolios.items():
        print(f"Processing {port_name}...")
        allocations = port_data['allocations']
        stats = calculate_portfolio_stats(prices_df, allocations)
        stats['allocations'] = allocations
        results[port_name] = stats
    
    # Save results
    with open('portfolio_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("Results saved to portfolio_results.json")
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    for port_name, stats in results.items():
        print(f"{port_name}:")
        print(f"  10Y Return: {stats['annualized_return']*100:.2f}%")
        print(f"  Volatility: {stats['volatility']*100:.2f}%")
        print(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {stats['max_drawdown']*100:.2f}%")
        print(f"  Final Value: ${stats['final_value']:.2f}")
        print()


if __name__ == '__main__':
    main()