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
        /* ============================================
           SATID Website - COMPLETE MASTER STYLESHEET
           Embedded version for Annual Returns Chart
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
            padding: 20px;
        }
        
        /* 2. CONTAINER */
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        /* 3. HEADER */
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d6cb9 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            border-radius: 16px;
            margin-bottom: 20px;
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
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
            position: relative;
            z-index: 1;
        }
        
        .header div {
            font-size: 1.4rem;
            font-weight: 300;
            letter-spacing: 0.5px;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        /* 4. CONTROLS */
        .controls {
            background: white;
            padding: 30px 35px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
        }
        
        .section {
            margin-bottom: 25px;
        }
        
        .section:last-child {
            margin-bottom: 0;
        }
        
        .section h3 {
            color: #1e3c72;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 15px;
            letter-spacing: -0.3px;
        }
        
        .buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        button {
            padding: 12px 24px;
            border: 2px solid #e2e8f0;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            color: #4a5568;
        }
        
        button:hover {
            border-color: #2a5298;
            background: #f0f4f8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        button.active {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            border-color: #2a5298;
            box-shadow: 0 4px 12px rgba(42, 82, 152, 0.3);
        }
        
        /* 5. VIEW TABS */
        .view-tabs {
            background: white;
            padding: 10px 25px 0 25px;
            border-radius: 16px 16px 0 0;
            margin-bottom: 0;
            display: flex;
            gap: 10px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.02);
        }
        
        .tab-btn {
            padding: 15px 30px;
            border: none;
            background: transparent;
            border-radius: 12px 12px 0 0;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .tab-btn:hover {
            background: #f0f4f8;
            color: #2a5298;
        }
        
        .tab-btn.active {
            background: white;
            color: #2a5298;
            border: 2px solid #e9ecef;
            border-bottom: 2px solid white;
            margin-bottom: -2px;
        }
        
        /* 6. VIEW CONTENT */
        .view-content {
            background: white;
            padding: 35px;
            border-radius: 0 0 16px 16px;
            display: none;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
        }
        
        .view-content.active {
            display: block;
        }
        
        /* 7. TABLE STYLES */
        table {
            border-collapse: collapse;
            width: 100%;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        
        th {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 18px 20px;
            text-align: left;
            position: sticky;
            top: 0;
            font-size: 1.1rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        td {
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 1.05rem;
            color: #4a5568;
        }
        
        tr:nth-child(odd) {
            background-color: #f7f9fc;
        }
        
        tr:nth-child(even) {
            background-color: #ffffff;
        }
        
        tr:hover {
            background-color: #e8f0fe;
            transform: scale(1.01);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .positive {
            color: #28a745;
            font-weight: bold;
        }
        
        .negative {
            color: #dc3545;
            font-weight: bold;
        }
        
        tr.hidden {
            display: none;
        }
        
        /* 8. BAR CHART STYLES */
        .chart-scroll {
            overflow-x: auto;
            padding: 20px 0;
        }
        
        .chart-grid {
            display: inline-flex;
            gap: 40px;
            min-width: 100%;
            padding: 20px;
        }
        
        .year-group {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .chart-area {
            height: 400px;
            display: flex;
            align-items: center;
            position: relative;
        }
        
        .baseline {
            position: absolute;
            left: 0;
            right: 0;
            top: 50%;
            height: 2px;
            background: #2c3e50;
            z-index: 1;
        }
        
        .bars {
            display: flex;
            gap: 3px;
            position: relative;
        }
        
        .bar {
            width: 28px;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .bar.hidden {
            display: none;
        }
        
        .bar-rect {
            width: 100%;
            position: absolute;
            display: flex;
            align-items: flex-end;
            justify-content: center;
        }
        
        .bar-rect.positive {
            bottom: 50%;
            background: var(--bar-color);
        }
        
        .bar-rect.negative {
            top: 50%;
            background: var(--bar-color);
            align-items: flex-start;
        }
        
        .bar-label {
            font-size: 10px;
            font-weight: bold;
            white-space: nowrap;
            color: #2c3e50;
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
        }
        
        .bar-label.positive {
            bottom: 100%;
            margin-bottom: 4px;
        }
        
        .bar-label.negative {
            top: 100%;
            margin-top: 4px;
        }
        
        .year-label {
            margin-top: 10px;
            font-weight: bold;
            font-size: 13px;
            color: #1e3c72;
        }
        
        /* 9. LEGEND STYLES */
        .legend {
            margin-top: 40px;
            padding: 25px;
            background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        
        .legend-title {
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: #1e3c72;
            letter-spacing: -0.3px;
        }
        
        .legend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .legend-color {
            width: 35px;
            height: 25px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .legend-label {
            font-size: 14px;
            color: #4a5568;
            font-weight: 500;
        }
        
        /* 10. RESPONSIVE DESIGN */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .header div {
                font-size: 1.1rem;
            }
            
            .controls {
                padding: 20px;
            }
            
            .section h3 {
                font-size: 1.2rem;
            }
            
            .view-content {
                padding: 20px;
            }
            
            th, td {
                padding: 12px 15px;
                font-size: 0.95rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
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
