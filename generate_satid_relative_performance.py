#!/usr/bin/env python3
"""
Generate SATID Relative Performance Dashboard
Compares ETF performance with rebased relative returns (clean version - no Fbis lines)
"""

import pandas as pd
from pathlib import Path
import json

# Configuration
CSV_PATH = Path("SATID_portfolio_etf_data_weekly_ohlc.csv")
OUTPUT_PATH = Path("SATID_Relative_Performance.html")

# Read the CSV
print(f"Reading data from {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)

# Extract all ticker symbols from columns
close_cols = [col for col in df.columns if col.endswith('_close')]
tickers = sorted([col.replace('_close', '') for col in close_cols])
print(f"Found {len(tickers)} ETFs: {', '.join(tickers)}")

# Prepare data for JavaScript
data_dict = {}
data_dict['dates'] = df['Date'].tolist()

for ticker in tickers:
    close_col = f'{ticker}_close'
    if close_col in df.columns:
        data_dict[ticker] = df[close_col].tolist()

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATID Relative Performance Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .global-controls {{
            background: white;
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
        }}
        
        .global-controls label {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .global-controls select {{
            padding: 8px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: border-color 0.2s;
        }}
        
        .global-controls select:hover {{
            border-color: #667eea;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .chart-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 48px rgba(0,0,0,0.15);
        }}
        
        .chart-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .chart-header select {{
            padding: 6px 10px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: border-color 0.2s;
        }}
        
        .chart-header select:hover {{
            border-color: #667eea;
        }}
        
        .chart-header select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .chart-header .select-container {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .chart-header .select-wrapper {{
            position: relative;
        }}
        
        .chart-header .select-wrapper::after {{
            content: '▼';
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: #667eea;
            font-size: 10px;
        }}
        
        .chart-header select {{
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            padding-right: 30px;
            background: white;
        }}
        
        .chart-header .over-label {{
            font-size: 11px;
            color: #a0aec0;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 0 4px;
        }}
        
        .chart-container {{
            height: 400px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SATID Relative Performance</h1>
        <p>Compare ETF pairs with rebased relative returns</p>
    </div>
    
    <div class="global-controls">
        <label>Lookback Period:</label>
        <select id="global-period" onchange="updateAllCharts()">
            <option value="52">1 Year (52 weeks)</option>
            <option value="104">2 Years (104 weeks)</option>
            <option value="156" selected>3 Years (156 weeks)</option>
            <option value="260">5 Years (260 weeks)</option>
            <option value="520">10 Years (520 weeks)</option>
        </select>
    </div>
    
    <div class="charts-grid">
'''

# Default ETF pairs
default_pairs = [
    ('ARKF', 'SPY'),
    ('QQQ', 'SPY'),
    ('SMH', 'QQQ'),
    ('MCHI', 'SPY'),
    ('EWZ', 'SPY'),
    ('GLD', 'SPY'),
    ('XLK', 'SPY'),
    ('VGK', 'SPY'),
    ('INDA', 'SPY'),
    ('EMB', 'SPY')
]

# Generate 10 chart cards
for i in range(10):
    etf1, etf2 = default_pairs[i]
    
    # Generate options for dropdowns
    options1 = ''.join([f'<option value="{t}" {"selected" if t == etf1 else ""}>{t}</option>' for t in tickers])
    options2 = ''.join([f'<option value="{t}" {"selected" if t == etf2 else ""}>{t}</option>' for t in tickers])
    
    html += f'''
        <!-- Chart {i+1} -->
        <div class="chart-card">
            <div class="chart-header">
                <div class="select-container">
                    <div class="select-wrapper">
                        <select id="etf1-{i}" onchange="updateChart({i})">
                            {options1}
                        </select>
                    </div>
                    <span class="over-label">over</span>
                    <div class="select-wrapper">
                        <select id="etf2-{i}" onchange="updateChart({i})">
                            {options2}
                        </select>
                    </div>
                </div>
            </div>
            
            <div id="chart-{i}" class="chart-container"></div>
        </div>
'''

html += '''
    </div>

    <script>
        // Data from CSV
        const rawData = ''' + json.dumps(data_dict) + ''';
        
        // Parse dates
        const dates = rawData.dates.map(d => new Date(d));
        
        // Calculate relative performance (rebased to 100)
        function calculateRelativePerformance(etf1Data, etf2Data, lookbackWeeks) {
            const startIdx = Math.max(0, etf1Data.length - lookbackWeeks);
            
            // Slice data
            const etf1Slice = etf1Data.slice(startIdx);
            const etf2Slice = etf2Data.slice(startIdx);
            const datesSlice = dates.slice(startIdx);
            
            // Rebase to 100
            const etf1Base = etf1Slice[0];
            const etf2Base = etf2Slice[0];
            
            const etf1Rebased = etf1Slice.map(v => (v / etf1Base) * 100);
            const etf2Rebased = etf2Slice.map(v => (v / etf2Base) * 100);
            
            // Calculate difference
            const relPerf = etf1Rebased.map((v, i) => v - etf2Rebased[i]);
            
            return { relPerf, dates: datesSlice };
        }
        
        // Update individual chart
        function updateChart(chartIdx) {
            const etf1 = document.getElementById(`etf1-${chartIdx}`).value;
            const etf2 = document.getElementById(`etf2-${chartIdx}`).value;
            const lookbackWeeks = parseInt(document.getElementById('global-period').value);
            
            const etf1Data = rawData[etf1];
            const etf2Data = rawData[etf2];
            
            const { relPerf, dates: chartDates } = calculateRelativePerformance(etf1Data, etf2Data, lookbackWeeks);
            
            // Create traces
            const trace1 = {
                x: chartDates,
                y: relPerf,
                type: 'scatter',
                mode: 'lines',
                name: `${etf1} over ${etf2}`,
                line: { color: 'black', width: 2.5 },
                hovertemplate: '<b>%{x|%Y-%m-%d}</b><br>Relative: %{y:.2f}%<extra></extra>'
            };
            
            const trace2 = {
                x: chartDates,
                y: new Array(chartDates.length).fill(0),
                type: 'scatter',
                mode: 'lines',
                name: 'Zero Line',
                line: { color: 'rgba(100, 100, 100, 0.3)', width: 1, dash: 'dash' },
                showlegend: false,
                hoverinfo: 'skip'
            };
            
            const layout = {
                margin: { l: 50, r: 30, t: 10, b: 40 },
                xaxis: { 
                    showgrid: true,
                    gridcolor: 'rgba(0,0,0,0.05)',
                    zeroline: false
                },
                yaxis: { 
                    title: 'Relative Performance (%)',
                    showgrid: true,
                    gridcolor: 'rgba(0,0,0,0.05)',
                    zeroline: false
                },
                hovermode: 'x unified',
                showlegend: true,
                legend: {
                    x: 0.02,
                    y: 0.98,
                    bgcolor: 'rgba(255,255,255,0.9)',
                    bordercolor: 'rgba(0,0,0,0.1)',
                    borderwidth: 1
                },
                plot_bgcolor: 'white',
                paper_bgcolor: 'white'
            };
            
            Plotly.newPlot(`chart-${chartIdx}`, [trace2, trace1], layout, {
                responsive: true,
                displayModeBar: false
            });
        }
        
        // Update all charts
        function updateAllCharts() {
            for (let i = 0; i < 10; i++) {
                updateChart(i);
            }
        }
        
        // Initialize all charts on load
        window.addEventListener('load', () => {
            updateAllCharts();
        });
    </script>
</body>
</html>'''

# Write HTML file
print(f"\nWriting HTML to {OUTPUT_PATH}...")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("\n" + "="*70)
print("GENERATION COMPLETE")
print("="*70)
print(f"✓ HTML dashboard: {OUTPUT_PATH}")
print(f"✓ 10 charts showing relative performance")
print(f"✓ Data source: {CSV_PATH}")
print(f"✓ {len(tickers)} ETFs available in dropdowns")
print(f"✓ Default lookback: 3 years (156 weeks)")
print(f"✓ Relative performance line: Black, 2.5px width")
print(f"✓ Zero reference line: Gray dashed")
print("="*70)
