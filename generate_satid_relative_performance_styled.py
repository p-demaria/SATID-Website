#!/usr/bin/env python3
"""
Generate SATID Relative Performance Dashboard
Compares ETF performance with rebased relative returns
Now with SATID Master Styles embedded
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

# Generate HTML with embedded SATID styles
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATID - Cross Asset Validations</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    
    <style>
/* ============================================
   SATID Website - COMPLETE MASTER STYLESHEET
   ============================================ */

/* ============================================
   1. BASE STYLES & RESET
   ============================================ */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}}

/* ============================================
   2. NAVIGATION STYLES - COMPLETE
   ============================================ */

.navbar {{
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}}

.nav-container {{
    max-width: 100% !important;
    padding: 0 40px !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.nav-logo {{
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 15px 0;
}}

.nav-menu {{
    display: flex;
    list-style: none;
    gap: 30px;
    justify-content: space-between !important;
    width: 100% !important;
}}

.nav-menu li {{
    list-style: none;
}}

.nav-menu a {{
    color: #ecf0f1;
    text-decoration: none;
    padding: 20px 0;
    display: block;
    transition: color 0.3s;
    font-size: 17px;
    font-weight: 400;
}}

.nav-menu a:hover,
.nav-menu a.active {{
    color: #3498db;
}}

/* Dropdown Menu */
.dropdown {{
    position: relative;
}}

.dropbtn {{
    cursor: pointer;
    color: #ecf0f1;
    text-decoration: none;
    padding: 20px 0;
    display: block;
    transition: color 0.3s;
    font-size: 17px;
    font-weight: 400;
}}

.dropdown-content {{
    display: none;
    position: absolute;
    background-color: #34495e;
    min-width: 250px;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.3);
    z-index: 1000;
    top: 100%;
    left: 0;
}}

.dropdown-content a {{
    color: #ecf0f1;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
    border-bottom: 1px solid #2c3e50;
}}

.dropdown-content a:hover {{
    background-color: #2c3e50;
    color: #3498db;
}}

.dropdown:hover .dropdown-content {{
    display: block;
}}

.dropdown:hover .dropbtn {{
    color: #3498db;
}}

/* ============================================
   3. HERO SECTION
   ============================================ */

.hero {{
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d6cb9 100%);
    padding: 40px 20px 80px;
    position: relative;
    overflow: hidden;
    color: white;
    text-align: center;
}}

.hero::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1" fill="rgba(255,255,255,0.03)"/></svg>') repeat;
    opacity: 0.5;
}}

.hero-content {{
    max-width: 1000px;
    margin: 0 auto;
    text-align: center;
    position: relative;
    z-index: 1;
}}

.hero h1 {{
    font-size: 3.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 20px;
    letter-spacing: -0.5px;
    animation: fadeInUp 0.8s ease-out;
}}

.hero h2 {{
    font-size: 28px;
    margin-bottom: 15px;
    font-weight: 400;
    color: #ecf0f1;
}}

.hero-subtitle {{
    font-size: 1.6rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 300;
    letter-spacing: 0.5px;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* ============================================
   4. CONTAINER & CONTENT PAGE
   ============================================ */

.container {{
    max-width: 100% !important;
    margin: -60px auto 60px;
    padding: 0 10px !important;
    position: relative;
    z-index: 2;
}}

.content-page {{
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    padding: 50px 30px 70px 30px !important;
    animation: fadeIn 1s ease-out;
    max-width: 1400px;
    margin-left: auto;
    margin-right: auto;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}

/* ============================================
   5. CONTENT SECTIONS
   ============================================ */

.content-section {{
    margin-bottom: 50px;
}}

.content-section h2 {{
    font-size: 2rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 30px;
    position: relative;
    color: #1e3c72;
    letter-spacing: -0.5px;
}}

.content-section h2::after {{
    content: '';
    display: block;
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #2a5298, #3d6cb9);
    margin: 15px auto 0;
    border-radius: 2px;
}}

.content-section p {{
    font-size: 1.1rem;
    line-height: 1.8;
    color: #4a5568;
    margin-bottom: 20px;
    font-weight: 400;
    text-align: center;
}}

/* ============================================
   6. GLOBAL CONTROLS
   ============================================ */

.global-controls {{
    background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
    padding: 20px 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    margin-bottom: 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    border-left: 4px solid #2a5298;
}}

.global-controls label {{
    font-weight: 600;
    color: #1e3c72;
    font-size: 1.1rem;
}}

.global-controls select {{
    padding: 10px 20px;
    border: 2px solid #2a5298;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
    background: white;
    color: #1e3c72;
}}

.global-controls select:hover {{
    border-color: #1e3c72;
    box-shadow: 0 2px 8px rgba(42, 82, 152, 0.2);
}}

.global-controls select:focus {{
    outline: none;
    border-color: #1e3c72;
    box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
}}

/* ============================================
   7. CHARTS GRID
   ============================================ */

.charts-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
    margin-bottom: 30px;
}}

.chart-card {{
    background: #f8f9fa;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
    border-left: 4px solid #2a5298;
}}

.chart-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}}

.chart-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #e2e8f0;
}}

.chart-header select {{
    padding: 8px 15px;
    border: 2px solid #2a5298;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    background: white;
    color: #1e3c72;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    padding-right: 35px;
}}

.chart-header select:hover {{
    border-color: #1e3c72;
    box-shadow: 0 2px 8px rgba(42, 82, 152, 0.2);
}}

.chart-header select:focus {{
    outline: none;
    border-color: #1e3c72;
    box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
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
    content: 'â–¼';
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: #2a5298;
    font-size: 10px;
}}

.chart-header .over-label {{
    font-size: 12px;
    color: #4a5568;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 0 4px;
}}

.chart-container {{
    height: 400px;
    background: white;
    border-radius: 8px;
    padding: 10px;
}}

/* ============================================
   8. FOOTER
   ============================================ */

footer {{
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: rgba(255, 255, 255, 0.9);
    text-align: center;
    padding: 30px 20px;
    margin-top: 80px;
    font-size: 0.95rem;
    letter-spacing: 0.5px;
}}

footer p {{
    margin: 0;
}}

/* ============================================
   9. RESPONSIVE DESIGN
   ============================================ */

@media (max-width: 1400px) {{
    .content-page {{
        padding: 50px 30px 60px 30px !important;
    }}
}}

@media (max-width: 1200px) {{
    .charts-grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 768px) {{
    .hero h1 {{
        font-size: 2.5rem;
    }}
    
    .hero-subtitle {{
        font-size: 1.1rem;
    }}
    
    .content-page {{
        padding: 40px 25px !important;
    }}
    
    .content-section h2 {{
        font-size: 1.6rem;
    }}
    
    .nav-menu {{
        flex-direction: column;
        gap: 10px;
    }}
    
    .global-controls {{
        flex-direction: column;
    }}
}}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <ul class="nav-menu">
                <li><a href="index.html">Index</a></li>
                <li><a href="Philosophy.html">Philosophy</a></li>
                <li><a href="Methodology.html">Methodology</a></li>
                <li><a href="Support_Levels_Interactive.html">Risk Level Setting</a></li>
                <li><a href="Portfolio_Risk_Exposure.html">Risk Exposure</a></li>
                <li><a href="SATID_Risk_Score.html">Risk Score</a></li>
                <li><a href="Portfolio_Risk_Dashboard.html">Risk Dashboard</a></li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Market Views</a>
                    <div class="dropdown-content">
                        <a href="Market_Views.html">About Market Views</a>
                        <a href="SATID_Relative_Performance.html" class="active">Cross Asset Validations</a>
                    </div>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Appendix</a>
                    <div class="dropdown-content">
                        <a href="Portfolios_Performance.html">Portfolio Performance Analysis</a>
                        <a href="Conventional_Portfolio_Profiles.html">Conventional Portfolio Profiles</a>
                        <a href="model_portfolios.html">Model Portfolios</a>
                        <a href="Portfolio_Statistics.html">Portfolio Statistics</a>
                    </div>
                </li>
            </ul>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Cross Asset Validations</h1>
            <p class="hero-subtitle">Compare ETF performance with rebased relative returns to validate market views</p>
        </div>
    </section>

    <!-- Main Content Container -->
    <div class="container">
        <div class="content-page">
            
            <section class="content-section">
                <h2>Relative Performance Analysis</h2>
                <p>Select any two ETFs to compare their relative performance over various time periods. Charts are rebased to 100 at the start of each period.</p>
            </section>
            
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

        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>&copy; 2024 SATID Investment Management. All rights reserved.</p>
    </footer>

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
                line: { color: '#1e3c72', width: 2.5 },
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
print(f"✓ SATID master styles embedded")
print(f"✓ Professional navigation with dropdown menus")
print(f"✓ Hero section with gradient background")
print(f"✓ 10 charts showing relative performance")
print(f"✓ Data source: {CSV_PATH}")
print(f"✓ {len(tickers)} ETFs available in dropdowns")
print(f"✓ Default lookback: 3 years (156 weeks)")
print(f"✓ Relative performance line: SATID blue (#1e3c72), 2.5px width")
print(f"✓ Zero reference line: Gray dashed")
print(f"✓ Ready for GitHub deployment")
print("="*70)
