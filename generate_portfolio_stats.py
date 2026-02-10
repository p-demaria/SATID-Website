"""
Portfolio Statistics Generator
Generates comprehensive portfolio statistics and interactive HTML dashboard
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from scipy import stats

def load_data():
    """Load ETF prices and portfolio allocations"""
    print("Loading data...")
    
    # Load prices
    prices = pd.read_csv('etf_prices.csv', index_col=0)
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
        'ytd': annualized_return(portfolio_returns[portfolio_returns.index.year == portfolio_returns.index[-1].year], 
                                len(portfolio_returns[portfolio_returns.index.year == portfolio_returns.index[-1].year])),
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
    
    # Maximum 1-year return and date
    rolling_1y = portfolio_returns.rolling(12).apply(lambda x: (1 + x).prod() - 1, raw=False)
    max_1y = rolling_1y.max()
    max_1y_date = rolling_1y.idxmax()
    
    stats_dict['max_1y_return'] = {
        'value': max_1y,
        'date': max_1y_date.strftime('%B %Y') if pd.notna(max_1y_date) else 'N/A'
    }
    
    # Sharpe ratio (assuming 2% risk-free rate)
    risk_free = 0.02
    excess_returns = portfolio_returns.mean() * 12 - risk_free
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
    <title>Portfolio Statistics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .tabs {
            display: flex;
            background: white;
            padding: 0 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            overflow-x: auto;
        }
        
        .tab {
            padding: 15px 25px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            white-space: nowrap;
            font-weight: 500;
        }
        
        .tab:hover {
            background: #f8f9fa;
        }
        
        .tab.active {
            border-bottom-color: #2a5298;
            color: #2a5298;
        }
        
        .content {
            display: none;
            padding: 30px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .content.active {
            display: block;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 450px 1fr;
            gap: 30px;
        }
        
        .left-panel, .right-panel {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .stat-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
        }
        
        .stat-table th {
            background: #1e3c72;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .stat-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .stat-table tr:hover {
            background: #f8f9fa;
        }
        
        .metric-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }
        
        .metric-row:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #495057;
        }
        
        .metric-value {
            font-weight: 600;
            color: #2a5298;
        }
        
        .positive {
            color: #28a745;
        }
        
        .negative {
            color: #dc3545;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #1e3c72;
            margin: 25px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        
        @media (max-width: 1200px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Portfolio Statistics Dashboard</h1>
        <p>Comprehensive Performance Analysis</p>
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
                            <th>Volatility</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>YTD</td>
                            <td class="{'positive' if returns['ytd'] > 0 else 'negative'}">{returns['ytd']*100:.1f}%</td>
                            <td>{stats['volatility']*100:.1f}%</td>
                        </tr>
                        <tr>
                            <td>1 Year</td>
                            <td class="{'positive' if returns['1y'] > 0 else 'negative'}">{returns['1y']*100:.1f}%</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>3 Year</td>
                            <td class="{'positive' if returns['3y'] > 0 else 'negative'}">{returns['3y']*100:.1f}%</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>5 Year</td>
                            <td class="{'positive' if returns['5y'] > 0 else 'negative'}">{returns['5y']*100:.1f}%</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>7 Year</td>
                            <td class="{'positive' if returns['7y'] > 0 else 'negative'}">{returns['7y']*100:.1f}%</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>10 Year</td>
                            <td class="{'positive' if returns['10y'] > 0 else 'negative'}">{returns['10y']*100:.1f}%</td>
                            <td></td>
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
                        <span class="metric-label">Max 1 Yr Return</span>
                        <span class="metric-value positive">{stats['max_1y_return']['value']*100:.0f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Return Date</span>
                        <span class="metric-value">{stats['max_1y_return']['date']}</span>
                    </div>
                </div>
                
                <div class="section-title">Risk Metrics</div>
                <div class="metric-box">
                    <div class="metric-row">
                        <span class="metric-label">Sharpe Ratio</span>
                        <span class="metric-value">{stats['sharpe_ratio']:.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Sortino Ratio</span>
                        <span class="metric-value">{stats['sortino_ratio']:.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">VaR (95%)</span>
                        <span class="metric-value negative">{stats['var_95']*100:.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Positive Months</span>
                        <span class="metric-value positive">{stats['positive_months_pct']*100:.1f}%</span>
                    </div>
                </div>
                
                <div class="section-title">Asset Class Correlations</div>
                <table class="stat-table">
                    <thead>
                        <tr>
                            <th></th>
"""
        
        # Add correlation matrix header
        corr_classes = list(correlations.keys())
        for class_name in corr_classes:
            html += f"                            <th>{class_name}</th>\n"
        
        html += """                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add correlation matrix rows
        for i_row, class1 in enumerate(corr_classes):
            html += f"                        <tr>\n                            <td><strong>{class1}</strong></td>\n"
            for j_col, class2 in enumerate(corr_classes):
                corr_value = correlations[class1][class2]
                if i_row == j_col:
                    html += "                            <td><strong>1.00</strong></td>\n"
                elif i_row > j_col:
                    html += f"                            <td>{corr_value:.2f}</td>\n"
                else:
                    html += "                            <td></td>\n"
            html += "                        </tr>\n"
        
        html += """                    </tbody>
                </table>
            </div>
            
            <div class="right-panel">
                <div class="section-title">Asset Allocation</div>
                <div class="chart-container">
                    <canvas id="pieChart""" + str(i) + """"></canvas>
                </div>
                
                <div class="section-title">10-Year Portfolio Growth (Base 100)</div>
                <div class="chart-container" style="height: 400px;">
                    <canvas id="navChart""" + str(i) + """"></canvas>
                </div>
                
                <div class="metric-box">
                    <div class="metric-row">
                        <span class="metric-label">Initial Value</span>
                        <span class="metric-value">$100.00</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Final Value</span>
                        <span class="metric-value positive">${stats['final_value']:.2f}</span>
                    </div>
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
        
        Object.keys(portfolioData).forEach((portName, index) => {
            const data = portfolioData[portName];
            const allocations = data.allocations;
            const assetClasses = data.asset_classes;
            const classAllocations = {};
            
            Object.keys(allocations).forEach(ticker => {
                const assetClass = assetClasses[ticker] || 'Other';
                classAllocations[assetClass] = (classAllocations[assetClass] || 0) + allocations[ticker];
            });
            
            const pieCtx = document.getElementById('pieChart' + index).getContext('2d');
            new Chart(pieCtx, {
                type: 'pie',
                data: {
                    labels: Object.keys(classAllocations).map((key) => {
                        const pct = (classAllocations[key] * 100).toFixed(1);
                        return key + ' (' + pct + '%)';
                    }),
                    datasets: [{
                        data: Object.values(classAllocations).map(v => v * 100),
                        backgroundColor: ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5', '#70AD47']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label;
                                }
                            }
                        }
                    }
                }
            });
            
            const navData = data.statistics.nav;
            const dates = data.dates;
            const assetClassNavs = data.asset_class_navs;
            const portfolioFinalValue = navData[navData.length - 1];
            
            const datasets = [{
                label: 'Portfolio ($' + portfolioFinalValue.toFixed(2) + ')',
                data: navData,
                borderColor: '#2a5298',
                backgroundColor: 'transparent',
                borderWidth: 2.5,
                tension: 0.1
            }];
            
            const colors = ['#90EE90', '#87CEEB', '#FF6B6B', '#FFD700'];
            let colorIndex = 0;
            Object.keys(assetClassNavs).forEach(className => {
                const finalValue = assetClassNavs[className][assetClassNavs[className].length - 1];
                datasets.push({
                    label: className + ' ($' + finalValue.toFixed(2) + ')',
                    data: assetClassNavs[className],
                    borderColor: colors[colorIndex % colors.length],
                    backgroundColor: 'transparent',
                    borderWidth: 1.5,
                    tension: 0.1
                });
                colorIndex++;
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
                        legend: { position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                                }
                            }
                        }
                    },
                    scales: {
                        x: { display: true, ticks: { maxTicksLimit: 12 } },
                        y: { display: true, title: { display: true, text: 'Value ($)' } }
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
    print("PORTFOLIO STATISTICS GENERATOR")
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
                'max_1y_return': port_data['statistics']['max_1y_return'],
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
    
    with open('portfolio_calculations.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("\nGenerating HTML dashboard...")
    html = generate_html(json_results)
    
    with open('portfolio_statistics.html', 'w') as f:
        f.write(html)
    
    print("\n" + "=" * 60)
    print("✓ Portfolio statistics generated successfully!")
    print("✓ Calculations saved to: portfolio_calculations.json")
    print("✓ Dashboard saved to: portfolio_statistics.html")
    print("\nOpen 'portfolio_statistics.html' in your browser to view the dashboard.")
    print("=" * 60)

if __name__ == "__main__":
    main()