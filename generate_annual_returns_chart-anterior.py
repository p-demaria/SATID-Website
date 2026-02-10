"""
Annual Returns Chart Generator - WITH WORKING BAR CHART
Table View + Bar Chart View
"""

import pandas as pd
import json

def main():
    print("=" * 70)
    print("ANNUAL RETURNS CHART WITH TABS")
    print("=" * 70)
    
    # Load data
    print("\nLoading data...")
    prices = pd.read_csv('etf_prices_monthly.csv', index_col=0)
    prices.index = pd.to_datetime(prices.index, utc=True).tz_localize(None)
    
    with open('portfolio_calculations_monthly.json', 'r') as f:
        portfolios = json.load(f)
    
    print(f"✓ Data loaded successfully")
    
    # Asset classes
    asset_classes = {
        'Cash': ['BIL'],
        'Fixed Income': ['SHY', 'IGSB', 'IGIB', 'LQD', 'SHYG', 'HYG', 'EMB', 'CEMB'],
        'Equity': ['SPY', 'QQQ', 'IJK', 'IWM', 'VGK', 'EWU', 'EWJ', 'EEM', 'AAXJ', 'MCHI', 'INDA'],
        'Alternative Investments': ['GLD', 'FTLS', 'QAI', 'WTMF']
    }
    
    colors = {
        'Cash': '#90EE90',
        'Fixed Income': '#4169E1',
        'Equity': '#FF6B6B',
        'Alternative Investments': '#FFD700',
        'Conservative Income': '#505050',
        'Conservative Balanced': '#707070',
        'Balanced Portfolio': '#909090',
        'Growth Portfolio': '#A8A8A8',
        'Aggressive Growth Portfolio': '#C0C0C0'
    }
    
    # Calculate returns
    print("Calculating returns...")
    years = [y for y in sorted(prices.index.year.unique()) if y >= 2015]
    
    # Asset class returns
    ac_returns = {}
    for ac_name, etf_list in asset_classes.items():
        valid_etfs = [e for e in etf_list if e in prices.columns]
        if not valid_etfs:
            continue
        
        returns = []
        for year in years:
            year_data = prices[prices.index.year == year][valid_etfs]
            if len(year_data) >= 2:
                ret = ((year_data.iloc[-1] / year_data.iloc[0]) - 1).mean() * 100
                returns.append(round(ret, 2))
        
        # YTD
        latest_year = max(years)
        ytd_data = prices[prices.index.year == latest_year][valid_etfs]
        if len(ytd_data) >= 2:
            ytd_ret = ((ytd_data.iloc[-1] / ytd_data.iloc[0]) - 1).mean() * 100
            returns.append(round(ytd_ret, 2))
        
        ac_returns[ac_name] = returns
    
    # Portfolio returns  
    port_returns = {}
    for port_name, port_data in portfolios.items():
        allocations = port_data['allocations']
        returns = []
        
        for year in years:
            year_prices = prices[prices.index.year == year]
            if len(year_prices) >= 2:
                year_rets = year_prices.pct_change().dropna()
                port_ret = sum(year_rets[etf].sum() * weight 
                             for etf, weight in allocations.items() 
                             if etf in year_rets.columns)
                returns.append(round(port_ret * 100, 2))
        
        # YTD
        latest_year = max(years)
        ytd_prices = prices[prices.index.year == latest_year]
        if len(ytd_prices) >= 2:
            ytd_rets = ytd_prices.pct_change().dropna()
            port_ret = sum(ytd_rets[etf].sum() * weight 
                         for etf, weight in allocations.items() 
                         if etf in ytd_rets.columns)
            returns.append(round(port_ret * 100, 2))
        
        port_returns[port_name] = returns
    
    year_labels = [str(y) for y in years] + ['YTD']
    
    # Find min/max for chart scaling
    all_values = []
    for vals in ac_returns.values():
        all_values.extend(vals)
    for vals in port_returns.values():
        all_values.extend(vals)
    y_max = max(max(all_values), abs(min(all_values)))  # Make symmetric
    
    print("✓ Returns calculated")
    print("Generating HTML with tabs...")
    
    # Generate HTML
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Annual Returns</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 30px; text-align: center; border-radius: 12px; margin-bottom: 20px; }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .controls { background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; }
        .section { margin-bottom: 20px; }
        .section h3 { color: #2a5298; font-size: 16px; margin-bottom: 12px; }
        .buttons { display: flex; flex-wrap: wrap; gap: 10px; }
        button { padding: 10px 20px; border: 2px solid #ddd; background: white; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; }
        button:hover { border-color: #2a5298; }
        button.active { background: #2a5298; color: white; border-color: #2a5298; }
        
        .view-tabs { background: white; padding: 10px 25px; border-radius: 12px 12px 0 0; margin-bottom: -10px; display: flex; gap: 10px; }
        .tab-btn { padding: 12px 24px; border: none; background: transparent; border-radius: 8px 8px 0 0; cursor: pointer; font-size: 15px; font-weight: 600; color: #666; transition: all 0.2s; }
        .tab-btn:hover { background: #f0f0f0; }
        .tab-btn.active { background: white; color: #2a5298; border: 2px solid #e0e0e0; border-bottom: 2px solid white; margin-bottom: -2px; }
        
        .view-content { background: white; padding: 30px; border-radius: 0 0 12px 12px; display: none; }
        .view-content.active { display: block; }
        
        /* Table styles */
        table { border-collapse: collapse; width: 100%; }
        th { background: #2a5298; color: white; padding: 12px; text-align: left; position: sticky; top: 0; }
        td { padding: 10px; border-bottom: 1px solid #eee; }
        .positive { color: #28a745; font-weight: bold; }
        .negative { color: #dc3545; font-weight: bold; }
        tr.hidden { display: none; }
        
        /* Bar chart styles */
        .chart-scroll { overflow-x: auto; padding: 20px 0; }
        .chart-grid { display: inline-flex; gap: 40px; min-width: 100%; padding: 20px; }
        .year-group { display: flex; flex-direction: column; align-items: center; }
        .chart-area { height: 400px; display: flex; align-items: center; position: relative; }
        .baseline { position: absolute; left: 0; right: 0; top: 50%; height: 2px; background: #000; z-index: 1; }
        .bars { display: flex; gap: 3px; position: relative; }
        .bar { width: 28px; height: 200px; display: flex; align-items: center; justify-content: center; position: relative; }
        .bar.hidden { display: none; }
        .bar-rect { width: 100%; position: absolute; display: flex; align-items: flex-end; justify-content: center; }
        .bar-rect.positive { bottom: 50%; background: var(--bar-color); }
        .bar-rect.negative { top: 50%; background: var(--bar-color); align-items: flex-start; }
        .bar-label { font-size: 10px; font-weight: bold; white-space: nowrap; color: #000; position: absolute; left: 50%; transform: translateX(-50%); }
        .bar-label.positive { bottom: 100%; margin-bottom: 4px; }
        .bar-label.negative { top: 100%; margin-top: 4px; }
        .year-label { margin-top: 10px; font-weight: bold; font-size: 13px; }
        
        /* Legend styles */
        .legend { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .legend-title { font-weight: bold; font-size: 16px; margin-bottom: 15px; color: #2a5298; }
        .legend-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
        .legend-item { display: flex; align-items: center; gap: 10px; }
        .legend-color { width: 30px; height: 20px; border-radius: 4px; border: 1px solid #ddd; }
        .legend-label { font-size: 14px; }
        
        /* Return to Previous Page Button */
        .return-button {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #2c5f2d 0%, #4a7c59 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(44, 95, 45, 0.3);
            margin-bottom: 20px;
            cursor: pointer;
            border: none;
        }
        
        .return-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(44, 95, 45, 0.4);
            background: linear-gradient(135deg, #4a7c59 0%, #5d9973 100%);
        }
    </style>
</head>
<body>
    <div class="container">
        <button onclick="history.back()" class="return-button">← Back</button>
        <div class="header">
            <h1>Annual Returns Analysis</h1>
            <div>Portfolio Performance by Year</div>
        </div>
        
        <div class="controls">
            <div class="section">
                <h3>Asset Classes</h3>
                <div class="buttons">
                    <button id="toggleAC" class="active">Show/Hide All Asset Classes</button>
                </div>
            </div>
            
            <div class="section">
                <h3>Portfolio Profiles</h3>
                <div class="buttons">
"""
    
    port_names = list(port_returns.keys())
    for i, name in enumerate(port_names):
        html += f'                    <button onclick="togglePort({i})">{name}</button>\n'
    
    html += """                </div>
            </div>
        </div>
        
        <div class="view-tabs">
            <button class="tab-btn active" onclick="switchView('table')">Table View</button>
            <button class="tab-btn" onclick="switchView('chart')">Bar Chart View</button>
        </div>
        
        <!-- TABLE VIEW -->
        <div id="tableView" class="view-content active">
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
"""
    
    for year in year_labels:
        html += f'                        <th>{year}</th>\n'
    
    html += """                    </tr>
                </thead>
                <tbody>
"""
    
    # Asset class rows
    for ac_name, vals in ac_returns.items():
        html += f'                    <tr class="ac-row">\n                        <td><strong>{ac_name}</strong></td>\n'
        for val in vals:
            css_class = 'positive' if val >= 0 else 'negative'
            html += f'                        <td class="{css_class}">{val:+.2f}%</td>\n'
        html += '                    </tr>\n'
    
    # Portfolio rows
    for i, (port_name, vals) in enumerate(port_returns.items()):
        html += f'                    <tr class="port-row hidden" data-port="{i}">\n                        <td><strong>{port_name}</strong></td>\n'
        for val in vals:
            css_class = 'positive' if val >= 0 else 'negative'
            html += f'                        <td class="{css_class}">{val:+.2f}%</td>\n'
        html += '                    </tr>\n'
    
    html += """                </tbody>
            </table>
        </div>
        
        <!-- BAR CHART VIEW -->
        <div id="chartView" class="view-content">
            <div class="chart-scroll">
                <div class="chart-grid">
"""
    
    # Generate bar chart - simpler approach
    for year_idx, year in enumerate(year_labels):
        html += '                    <div class="year-group">\n'
        html += '                        <div class="chart-area">\n'
        html += '                            <div class="baseline"></div>\n'
        html += '                            <div class="bars">\n'
        
        # Asset class bars
        for ac_name, vals in ac_returns.items():
            val = vals[year_idx]
            height_pct = (abs(val) / y_max) * 100
            color = colors[ac_name]
            bar_class = 'positive' if val >= 0 else 'negative'
            
            html += f'                                <div class="bar ac-bar" data-group="{ac_name}">\n'
            html += f'                                    <div class="bar-rect {bar_class}" style="--bar-color: {color}; height: {height_pct}%;">\n'
            html += f'                                        <div class="bar-label {bar_class}">{val:.1f}%</div>\n'
            html += '                                    </div>\n'
            html += '                                </div>\n'
        
        # Portfolio bars
        for port_idx, (port_name, vals) in enumerate(port_returns.items()):
            val = vals[year_idx]
            height_pct = (abs(val) / y_max) * 100
            color = colors[port_name]
            bar_class = 'positive' if val >= 0 else 'negative'
            
            html += f'                                <div class="bar port-bar hidden" data-port="{port_idx}" data-group="{port_name}">\n'
            html += f'                                    <div class="bar-rect {bar_class}" style="--bar-color: {color}; height: {height_pct}%;">\n'
            html += f'                                        <div class="bar-label {bar_class}">{val:.1f}%</div>\n'
            html += '                                    </div>\n'
            html += '                                </div>\n'
        
        html += '                            </div>\n'
        html += '                        </div>\n'
        html += f'                        <div class="year-label">{year}</div>\n'
        html += '                    </div>\n'
    
    html += """                </div>
            </div>
            
            <div class="legend">
                <div class="legend-title">Color Legend</div>
                <div class="legend-grid">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #90EE90;"></div>
                        <div class="legend-label">Cash</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #4169E1;"></div>
                        <div class="legend-label">Fixed Income</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #FF6B6B;"></div>
                        <div class="legend-label">Equity</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #FFD700;"></div>
                        <div class="legend-label">Alternative Investments</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: linear-gradient(to right, #505050, #C0C0C0);"></div>
                        <div class="legend-label">Portfolios (Gray Shades)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let showAC = true;
        let activePorts = new Set();
        
        // Toggle asset classes
        document.getElementById('toggleAC').onclick = function() {
            showAC = !showAC;
            this.classList.toggle('active');
            document.querySelectorAll('.ac-row, .ac-bar').forEach(el => {
                el.classList.toggle('hidden', !showAC);
            });
        };
        
        // Toggle portfolios
        function togglePort(idx) {
            event.target.classList.toggle('active');
            document.querySelectorAll(`[data-port="${idx}"]`).forEach(el => {
                el.classList.toggle('hidden');
            });
        }
        
        // Switch between views
        function switchView(view) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('.view-content').forEach(content => {
                content.classList.remove('active');
            });
            
            if (view === 'table') {
                document.getElementById('tableView').classList.add('active');
            } else {
                document.getElementById('chartView').classList.add('active');
            }
        }
    </script>
</body>
</html>"""
    
    with open('annual_returns_chart.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n" + "=" * 70)
    print("✓ SUCCESS! File: annual_returns_chart.html")
    print("✓ Two views: Table and Bar Chart")
    print("=" * 70)

if __name__ == "__main__":
    main()
