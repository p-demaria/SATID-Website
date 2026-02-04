"""
Portfolio Statistics Generator - MONTHLY VERSION
Generates comprehensive portfolio statistics and interactive HTML dashboard
Uses monthly data for cleaner, more stable analysis
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from scipy import stats

def load_data():
    """Load monthly ETF prices and portfolio allocations"""
    print("Loading data...")
    
    # Load monthly prices
    prices = pd.read_csv('etf_prices_monthly.csv', index_col=0)
    # Explicitly convert index to datetime and handle timezone
    prices.index = pd.to_datetime(prices.index, utc=True).tz_localize(None)
    prices.index.name = 'Date'
    
    # Load allocations
    allocations_df = pd.read_excel('portfolio_allocations.xlsx', header=None)
    
    return prices, allocations_df

def parse_portfolio_allocations(allocations_df):
    """Parse portfolio allocations from Excel"""
    portfolio_configs = [
        {'name': 'Conservative Income', 'desc_col': 1, 'ticker_col': 2, 'value_col': 3},
        {'name': 'Conservative Balanced', 'desc_col': 5, 'ticker_col': 6, 'value_col': 7},
        {'name': 'Balanced Portfolio', 'desc_col': 9, 'ticker_col': 10, 'value_col': 11},
        {'name': 'Growth Portfolio', 'desc_col': 13, 'ticker_col': 14, 'value_col': 15},
        {'name': 'Aggressive Growth Portfolio', 'desc_col': 17, 'ticker_col': 18, 'value_col': 19}
    ]
    
    portfolios = {}
    
    for config in portfolio_configs:
        port_name = config['name']
        ticker_col = config['ticker_col']
        value_col = config['value_col']
        desc_col = config['desc_col']
        
        allocations = {}
        asset_classes = {}
        current_class = None
        
        # Read rows 3-30
        for row_idx in range(3, 31):
            description = allocations_df.iloc[row_idx, desc_col]
            ticker = allocations_df.iloc[row_idx, ticker_col]
            value = allocations_df.iloc[row_idx, value_col]
            
            if pd.notna(description):
                # Check if this is a category header
                if pd.isna(ticker):
                    current_class = str(description)
                else:
                    # This is an actual holding
                    try:
                        weight = float(value) if pd.notna(value) else 0.0
                        if weight > 0:
                            ticker_str = str(ticker)
                            allocations[ticker_str] = weight
                            asset_classes[ticker_str] = current_class
                    except (ValueError, TypeError):
                        continue
        
        portfolios[port_name] = {
            'allocations': allocations,
            'asset_classes': asset_classes
        }
    
    return portfolios

def calculate_portfolio_returns(prices, allocations):
    """Calculate portfolio returns from individual ETF returns"""
    returns = prices.pct_change().dropna()
    
    # Calculate weighted portfolio returns
    portfolio_returns = pd.Series(0.0, index=returns.index)
    
    for ticker, weight in allocations.items():
        if ticker in returns.columns:
            portfolio_returns += returns[ticker] * weight
    
    return portfolio_returns

def calculate_asset_class_returns(prices, allocations, asset_classes):
    """Calculate returns for each asset class"""
    returns = prices.pct_change().dropna()
    
    # Group by asset class
    class_allocations = {}
    for ticker, weight in allocations.items():
        asset_class = asset_classes.get(ticker, 'Other')
        if asset_class not in class_allocations:
            class_allocations[asset_class] = []
        class_allocations[asset_class].append((ticker, weight))
    
    # Calculate weighted returns for each class
    class_returns = {}
    for asset_class, holdings in class_allocations.items():
        total_weight = sum(w for _, w in holdings)
        class_ret = pd.Series(0.0, index=returns.index)
        
        for ticker, weight in holdings:
            if ticker in returns.columns:
                class_ret += returns[ticker] * (weight / total_weight)
        
        class_returns[asset_class] = class_ret
    
    return pd.DataFrame(class_returns)

def calculate_statistics(portfolio_returns, prices, allocations):
    """Calculate comprehensive portfolio statistics"""
    
    # Annualized returns for different periods
    def annualized_return(returns, periods):
        if len(returns) < periods:
            return np.nan
        recent = returns.iloc[-periods:]
        total_return = (1 + recent).prod() - 1
        years = periods / 12
        return (1 + total_return) ** (1/years) - 1
    
    stats_dict = {}
    
    # Returns for different periods
    stats_dict['returns'] = {
        '1y': annualized_return(portfolio_returns, 12),
        '3y': annualized_return(portfolio_returns, 36),
        '5y': annualized_return(portfolio_returns, 60),
        '7y': annualized_return(portfolio_returns, 84),
        '10y': annualized_return(portfolio_returns, 120)
    }
    
    # Volatility (10-year annualized) - use last 120 months
    if len(portfolio_returns) >= 120:
        returns_10y = portfolio_returns.iloc[-120:]
        stats_dict['volatility'] = returns_10y.std() * np.sqrt(12)
    else:
        stats_dict['volatility'] = portfolio_returns.std() * np.sqrt(12)
    
    # Maximum drawdown with time to recovery
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()
    
    # Calculate time to recovery
    time_to_recovery = 'N/A'
    if pd.notna(max_dd_date):
        drawdown_value = running_max.loc[max_dd_date]
        future_values = cumulative[cumulative.index > max_dd_date]
        recovery_dates = future_values[future_values >= drawdown_value]
        
        if len(recovery_dates) > 0:
            recovery_date = recovery_dates.index[0]
            months_to_recovery = len(portfolio_returns[max_dd_date:recovery_date]) - 1
            time_to_recovery = f"{months_to_recovery} months"
    
    stats_dict['max_drawdown'] = {
        'value': max_dd,
        'date': max_dd_date.strftime('%B %Y'),
        'time_to_recovery': time_to_recovery
    }
    
    # Rolling 1-year returns
    rolling_1y = portfolio_returns.rolling(12).apply(lambda x: (1 + x).prod() - 1, raw=False)
    
    # Best and worst 1-year returns
    max_1y = rolling_1y.max()
    max_1y_date = rolling_1y.idxmax()
    min_1y = rolling_1y.min()
    min_1y_date = rolling_1y.idxmin()
    
    stats_dict['best_1y_return'] = {
        'value': max_1y,
        'date': max_1y_date.strftime('%B %Y') if pd.notna(max_1y_date) else 'N/A'
    }
    
    stats_dict['worst_1y_return'] = {
        'value': min_1y,
        'date': min_1y_date.strftime('%B %Y') if pd.notna(min_1y_date) else 'N/A'
    }
    
    # Rolling 3-year returns
    rolling_3y = portfolio_returns.rolling(36).apply(lambda x: (1 + x).prod() - 1, raw=False)
    
    # Best and worst 3-year returns
    max_3y = rolling_3y.max()
    max_3y_date = rolling_3y.idxmax()
    min_3y = rolling_3y.min()
    min_3y_date = rolling_3y.idxmin()
    
    stats_dict['best_3y_return'] = {
        'value': max_3y,
        'date': max_3y_date.strftime('%B %Y') if pd.notna(max_3y_date) else 'N/A'
    }
    
    stats_dict['worst_3y_return'] = {
        'value': min_3y,
        'date': min_3y_date.strftime('%B %Y') if pd.notna(min_3y_date) else 'N/A'
    }
    
    # Sharpe ratio using BIL total return as risk-free rate
    if 'BIL' in prices.columns and len(portfolio_returns) >= 120:
        bil_returns = prices['BIL'].pct_change().dropna().iloc[-120:]
        risk_free_rate = (1 + bil_returns).prod() - 1  # Total return over 10 years
        risk_free_annualized = (1 + risk_free_rate) ** (1/10) - 1
    else:
        risk_free_annualized = 0.02  # Fallback to 2% if BIL not available
    
    excess_returns = stats_dict['returns']['10y'] - risk_free_annualized
    stats_dict['sharpe_ratio'] = excess_returns / stats_dict['volatility']
    
    # Sortino ratio (downside deviation)
    downside_returns = portfolio_returns[portfolio_returns < 0]
    downside_std = downside_returns.std() * np.sqrt(12)
    stats_dict['sortino_ratio'] = excess_returns / downside_std if downside_std > 0 else np.nan
    
    # Value at Risk (95% confidence)
    stats_dict['var_95'] = np.percentile(portfolio_returns, 5)
    
    # Percentage of positive months
    stats_dict['positive_months_pct'] = (portfolio_returns > 0).sum() / len(portfolio_returns)
    
    # NAV calculation (starting at 100)
    stats_dict['nav'] = (1 + portfolio_returns).cumprod() * 100
    stats_dict['final_value'] = stats_dict['nav'].iloc[-1]
    
    return stats_dict

def calculate_correlations(asset_class_returns):
    """Calculate correlation matrix between asset classes"""
    return asset_class_returns.corr()

def calculate_all_portfolios(prices, portfolios):
    """Calculate statistics for all portfolios"""
    results = {}
    
    for port_name, port_data in portfolios.items():
        print(f"Calculating {port_name}...")
        
        allocations = port_data['allocations']
        asset_classes = port_data['asset_classes']
        
        # Calculate returns
        portfolio_returns = calculate_portfolio_returns(prices, allocations)
        asset_class_returns = calculate_asset_class_returns(prices, allocations, asset_classes)
        
        # Calculate statistics
        stats = calculate_statistics(portfolio_returns, prices, allocations)
        
        # Calculate correlations
        correlations = calculate_correlations(asset_class_returns)
        
        # Calculate asset class NAVs
        asset_class_navs = {}
        for col in asset_class_returns.columns:
            asset_class_navs[col] = ((1 + asset_class_returns[col]).cumprod() * 100).tolist()
        
        results[port_name] = {
            'statistics': stats,
            'correlations': correlations.to_dict(),
            'asset_class_navs': asset_class_navs,
            'dates': portfolio_returns.index.strftime('%Y-%m-%d').tolist(),
            'allocations': allocations,
            'asset_classes': asset_classes
        }
    
    return results

def generate_html(results):
    """Generate interactive HTML dashboard"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Statistics Dashboard - Monthly Data</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        /* ============================================
           SATID Website - COMPLETE MASTER STYLESHEET
           Embedded version for Portfolio Statistics
           ============================================ */
        
        /* 1. BASE STYLES & RESET */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* 2. HEADER */
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d6cb9 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1" fill="rgba(255,255,255,0.03)"/></svg>') repeat;
            opacity: 0.5;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
            position: relative;
            z-index: 1;
        }
        
        .header p {
            font-size: 1.2rem;
            font-weight: 300;
            margin-bottom: 5px;
            position: relative;
            z-index: 1;
        }
        
        .header .subtitle {
            font-size: 0.95rem;
            opacity: 0.9;
            margin-top: 10px;
            position: relative;
            z-index: 1;
        }
        
        /* 3. TABS */
        .tabs {
            display: flex;
            background: white;
            padding: 0 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            overflow-x: auto;
        }
        
        .tab {
            padding: 18px 30px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
            font-weight: 600;
            font-size: 15px;
            color: #4a5568;
        }
        
        .tab:hover {
            background: #f0f4f8;
            color: #2a5298;
        }
        
        .tab.active {
            border-bottom-color: #2a5298;
            color: #2a5298;
            background: #f8f9fa;
        }
        
        /* 4. CONTENT */
        .content {
            display: none;
            padding: 40px 30px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .content.active {
            display: block;
        }
        
        /* 5. DASHBOARD LAYOUT */
        .dashboard {
            display: grid;
            grid-template-columns: 450px 1fr;
            gap: 30px;
        }
        
        .left-panel, .right-panel {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
        }
        
        .right-panel {
            overflow-x: visible;
        }
        
        /* 6. SECTION TITLES */
        .section-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #1e3c72;
            margin: 30px 0 20px 0;
            padding-bottom: 12px;
            border-bottom: 3px solid #e9ecef;
            letter-spacing: -0.3px;
        }
        
        .section-title:first-child {
            margin-top: 0;
        }
        
        /* 7. TABLES */
        .stat-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        
        .stat-table th {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 1rem;
            letter-spacing: 0.3px;
        }
        
        .stat-table td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
            color: #4a5568;
            font-size: 0.95rem;
        }
        
        .stat-table td.center,
        .stat-table td.center-align {
            text-align: center;
        }
        
        .stat-table tr:nth-child(odd) {
            background-color: #f7f9fc;
        }
        
        .stat-table tr:nth-child(even) {
            background-color: #ffffff;
        }
        
        .stat-table tr:hover {
            background: #e8f0fe;
            transition: all 0.3s ease;
        }
        
        .correlation-table {
            font-size: 11px;
        }
        
        .correlation-table th,
        .correlation-table td {
            padding: 8px 6px;
        }
        
        /* 8. METRIC BOXES */
        .metric-box {
            background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #dee2e6;
        }
        
        .metric-row:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 600;
            color: #495057;
            font-size: 0.95rem;
        }
        
        .metric-value {
            font-weight: 500;
            color: #2a5298;
            font-size: 0.95rem;
        }
        
        .positive {
            color: #28a745;
        }
        
        .negative {
            color: #dc3545;
        }
        
        /* 9. CHARTS */
        .chart-container {
            position: relative;
            height: 300px;
            margin: 25px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        
        /* 10. RESPONSIVE DESIGN */
        @media (max-width: 1200px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .content {
                padding: 30px 20px;
            }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .header p {
                font-size: 1rem;
            }
            
            .tabs {
                padding: 0 15px;
            }
            
            .tab {
                padding: 15px 20px;
                font-size: 14px;
            }
            
            .content {
                padding: 20px 15px;
            }
            
            .left-panel, .right-panel {
                padding: 20px;
            }
            
            .section-title {
                font-size: 1.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Portfolio Statistics Dashboard</h1>
        <p>Comprehensive Performance Analysis</p>
        <div class="subtitle">📅 Based on Monthly Data | 10-Year Analysis</div>
    </div>
    
    <div class="tabs">
"""
    
    # Generate tabs
    portfolio_names = list(results.keys())
    for i, name in enumerate(portfolio_names):
        active = ' active' if i == 0 else ''
        html += f'        <div class="tab{active}" onclick="showTab({i})">{name}</div>\n'
    
    html += """    </div>
    
"""
    
    # Generate content for each portfolio
    for i, (port_name, port_data) in enumerate(results.items()):
        active = ' active' if i == 0 else ''
        stats = port_data['statistics']
        returns = stats['returns']
        correlations = port_data['correlations']
        allocations = port_data['allocations']
        asset_classes_dict = port_data['asset_classes']
        
        # Group allocations by asset class
        class_totals = {}
        for ticker, weight in allocations.items():
            asset_class = asset_classes_dict.get(ticker, 'Other')
            class_totals[asset_class] = class_totals.get(asset_class, 0) + weight
        
        html += f"""    <div class="content{active}" id="tab{i}">
        <div class="dashboard">
            <div class="left-panel">
                <div class="section-title">Portfolio Returns</div>
                <table class="stat-table">
                    <thead>
                        <tr>
                            <th>Period</th>
                            <th>Return</th>
                            <th style="text-align: center;">Volatility</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1 Year</td>
                            <td class="{'positive' if returns['1y'] > 0 else 'negative'}">{returns['1y']*100:.1f}%</td>
                            <td class="center"></td>
                        </tr>
                        <tr>
                            <td>3 Year</td>
                            <td class="{'positive' if returns['3y'] > 0 else 'negative'}">{returns['3y']*100:.1f}%</td>
                            <td class="center"></td>
                        </tr>
                        <tr>
                            <td>5 Year</td>
                            <td class="{'positive' if returns['5y'] > 0 else 'negative'}">{returns['5y']*100:.1f}%</td>
                            <td class="center"></td>
                        </tr>
                        <tr>
                            <td>7 Year</td>
                            <td class="{'positive' if returns['7y'] > 0 else 'negative'}">{returns['7y']*100:.1f}%</td>
                            <td class="center"></td>
                        </tr>
                        <tr>
                            <td>10 Year</td>
                            <td class="{'positive' if returns['10y'] > 0 else 'negative'}">{returns['10y']*100:.1f}%</td>
                            <td class="center">{stats['volatility']*100:.1f}%</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="metric-box">
                    <div class="metric-row">
                        <span class="metric-label">Max Drawdown</span>
                        <span class="metric-value negative">{stats['max_drawdown']['value']*100:.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Drawdown Date</span>
                        <span class="metric-value">{stats['max_drawdown']['date']}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Time to Recovery</span>
                        <span class="metric-value">{stats['max_drawdown']['time_to_recovery']}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Positive Months</span>
                        <span class="metric-value positive">{stats['positive_months_pct']*100:.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Sharpe Ratio</span>
                        <span class="metric-value">{stats['sharpe_ratio']:.2f}</span>
                    </div>
                </div>
                
                <div class="metric-box">
                    <div class="metric-row">
                        <span class="metric-label">Worst 1 Year Return</span>
                        <span class="metric-value negative">{stats['worst_1y_return']['value']*100:.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Best 1 Year Return</span>
                        <span class="metric-value positive">{stats['best_1y_return']['value']*100:.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Worst 3 Year Return</span>
                        <span class="metric-value negative">{stats['worst_3y_return']['value']*100:.1f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Best 3 Year Return</span>
                        <span class="metric-value positive">{stats['best_3y_return']['value']*100:.1f}%</span>
                    </div>
                </div>
                
                <div class="section-title">Asset Class Correlations</div>
                <table class="stat-table" style="font-size: 12px;">
                    <thead>
                        <tr>
                            <th style="font-size: 12px;"></th>
"""
        
        # Add correlation matrix header - proper ordering
        asset_class_order = ['Cash', 'Fixed Income', 'Equity', 'Alternative Investments']
        corr_classes = [ac for ac in asset_class_order if ac in correlations.keys()]
        
        for class_name in corr_classes:
            html += f"                            <th style='font-size: 12px; text-align: center;'>{class_name}</th>\n"
        
        html += """                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add correlation matrix rows - FULL MATRIX (mirrored) with proper ordering
        for class1 in corr_classes:
            html += f"                        <tr>\n                            <td style='font-size: 12px;'><strong>{class1}</strong></td>\n"
            for class2 in corr_classes:
                corr_value = correlations[class1][class2]
                if class1 == class2:
                    html += "                            <td style='font-size: 12px; text-align: center;'><strong>1.00</strong></td>\n"
                else:
                    html += f"                            <td style='font-size: 12px; text-align: center;'>{corr_value:.2f}</td>\n"
            html += "                        </tr>\n"
        
        html += """                    </tbody>
                </table>
            </div>
            
            <div class="right-panel">
                <div class="section-title">Asset Allocation</div>
                <div class="chart-container">
                    <canvas id="pieChart""" + str(i) + """"></canvas>
                </div>
                
                <div class="section-title">10-Year Asset Class Performance (Base $100)</div>
                <div class="chart-container" style="height: 400px;">
                    <canvas id="navChart""" + str(i) + """"></canvas>
                </div>
            </div>
        </div>
    </div>
    
"""
    
    html += """    <script>
        function showTab(index) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.content').forEach(content => content.classList.remove('active'));
            document.querySelectorAll('.tab')[index].classList.add('active');
            document.getElementById('tab' + index).classList.add('active');
        }
        
        const portfolioData = """ + json.dumps(results, indent=8, default=str) + """;
        
        // Define consistent colors for asset classes
        const assetClassColors = {
            'Cash': '#87CEEB',
            'Fixed Income': '#90EE90',
            'Equity': '#FF6B6B',
            'Alternative Investments': '#FFD700'
        };
        
        Object.keys(portfolioData).forEach((portName, index) => {
            const data = portfolioData[portName];
            const allocations = data.allocations;
            const assetClasses = data.asset_classes;
            const classAllocations = {};
            
            Object.keys(allocations).forEach(ticker => {
                const assetClass = assetClasses[ticker] || 'Other';
                classAllocations[assetClass] = (classAllocations[assetClass] || 0) + allocations[ticker];
            });
            
            // Sort asset classes in standard order
            const assetClassOrder = ['Cash', 'Fixed Income', 'Equity', 'Alternative Investments'];
            const sortedLabels = assetClassOrder.filter(ac => classAllocations[ac]);
            const sortedData = sortedLabels.map(ac => classAllocations[ac] * 100);
            const sortedColors = sortedLabels.map(ac => assetClassColors[ac] || '#999999');
            
            const pieCtx = document.getElementById('pieChart' + index).getContext('2d');
            new Chart(pieCtx, {
                type: 'pie',
                data: {
                    labels: sortedLabels,
                    datasets: [{
                        data: sortedData,
                        backgroundColor: sortedColors
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: 40
                    },
                    plugins: {
                        legend: { 
                            display: false 
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    return label + ': ' + value.toFixed(1) + '%';
                                }
                            }
                        },
                        datalabels: {
                            color: '#000',
                            font: {
                                weight: 'bold',
                                size: 12
                            },
                            anchor: 'end',
                            align: 'end',
                            offset: 15,
                            formatter: (value, ctx) => {
                                const label = ctx.chart.data.labels[ctx.dataIndex];
                                return label + '\\n' + value.toFixed(1) + '%';
                            }
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });
            
            const navData = data.statistics.nav;
            const dates = data.dates;
            const assetClassNavs = data.asset_class_navs;
            const portfolioFinalValue = navData[navData.length - 1];
            
            // Define standard asset class order
            const datasets = [];
            
            // Add asset class datasets first (in standard order)
            assetClassOrder.forEach(className => {
                if (assetClassNavs[className]) {
                    const finalValue = assetClassNavs[className][assetClassNavs[className].length - 1];
                    datasets.push({
                        label: className + ' ($' + finalValue.toFixed(0) + ')',
                        data: assetClassNavs[className],
                        borderColor: assetClassColors[className] || '#999999',
                        backgroundColor: 'transparent',
                        borderWidth: 2.5,
                        tension: 0.1,
                        pointRadius: 0
                    });
                }
            });
            
            // Add portfolio line last (so it's on top)
            datasets.push({
                label: 'Portfolio ($' + portfolioFinalValue.toFixed(0) + ')',
                data: navData,
                borderColor: '#2a5298',
                backgroundColor: 'transparent',
                borderWidth: 3,
                tension: 0.1,
                pointRadius: 0
            });
            
            const navCtx = document.getElementById('navChart' + index).getContext('2d');
            new Chart(navCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 15,
                                font: {
                                    size: 13
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label.split(' ($')[0] + ': $' + context.parsed.y.toFixed(2);
                                }
                            }
                        },
                        datalabels: {
                            display: false
                        }
                    },
                    scales: {
                        x: { 
                            display: true,
                            type: 'time',
                            time: {
                                unit: 'month',
                                displayFormats: {
                                    month: 'MMM yyyy'
                                }
                            },
                            ticks: { 
                                maxTicksLimit: 12,
                                autoSkip: true
                            },
                            grid: { display: false }
                        },
                        y: { 
                            display: true, 
                            title: { display: true, text: 'Value ($)' },
                            grid: { color: '#e9ecef' }
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>"""
    
    return html

def main():
    """Main execution function"""
    print("=" * 60)
    print("PORTFOLIO STATISTICS GENERATOR - MONTHLY DATA")
    print("=" * 60)
    
    prices, allocations_df = load_data()
    print("\nParsing portfolio allocations...")
    portfolios = parse_portfolio_allocations(allocations_df)
    print("\nCalculating portfolio statistics...")
    results = calculate_all_portfolios(prices, portfolios)
    print("\nSaving calculations...")
    
    json_results = {}
    for port_name, port_data in results.items():
        json_results[port_name] = {
            'statistics': {
                'returns': port_data['statistics']['returns'],
                'volatility': port_data['statistics']['volatility'],
                'max_drawdown': port_data['statistics']['max_drawdown'],
                'best_1y_return': port_data['statistics']['best_1y_return'],
                'worst_1y_return': port_data['statistics']['worst_1y_return'],
                'best_3y_return': port_data['statistics']['best_3y_return'],
                'worst_3y_return': port_data['statistics']['worst_3y_return'],
                'sharpe_ratio': port_data['statistics']['sharpe_ratio'],
                'sortino_ratio': port_data['statistics']['sortino_ratio'],
                'var_95': port_data['statistics']['var_95'],
                'positive_months_pct': port_data['statistics']['positive_months_pct'],
                'final_value': port_data['statistics']['final_value'],
                'nav': port_data['statistics']['nav'].tolist()
            },
            'correlations': port_data['correlations'],
            'asset_class_navs': port_data['asset_class_navs'],
            'dates': port_data['dates'],
            'allocations': port_data['allocations'],
            'asset_classes': port_data['asset_classes']
        }
    
    with open('portfolio_calculations_monthly.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("\nGenerating HTML dashboard...")
    html = generate_html(json_results)
    
    with open('portfolio_statistics_monthly.html', 'w') as f:
        f.write(html)
    
    print("\n" + "=" * 60)
    print("✓ Portfolio statistics generated successfully!")
    print("✓ Calculations saved to: portfolio_calculations_monthly.json")
    print("✓ Dashboard saved to: portfolio_statistics_monthly.html")
    print("\nOpen 'portfolio_statistics_monthly.html' in your browser to view the dashboard.")
    print("=" * 60)

if __name__ == "__main__":
    main()
