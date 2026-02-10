"""
SATID FBIS LEVELS - NO OPTIMIZATION VERSION
============================================
Generates: Support_Levels_Interactive.html

This script:
1. Loads latest weekly price data from CSV
2. READS existing optimized parameters from JSON (NO optimization)
3. Generates interactive HTML dashboard using those parameters

Key Features:
- Uses parameters from SATID_Fbis_Optimized_Parameters.json
- Updates charts with latest price data
- NO optimization - preserves manually adjusted or previously optimized levels
- Charts: Price (black) from Jan 2020, Fbis (red dotted) from Sep 2022

Use this script when: You want to UPDATE CHARTS with fresh prices 
                      WITHOUT re-optimizing support levels

Author: SATID Risk Management System
Date: February 2026
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

# ================================
# CONFIGURATION
# ================================
CSV_FILE = "SATID_portfolio_etf_data_weekly_ohlc.csv"
PARAMS_FILE = "SATID_Fbis_Optimized_Parameters.json"
OUTPUT_HTML = "Support_Levels_Interactive.html"

# Chart display settings
PRICE_START_DATE = "2020-01-01"
FBIS_START_DATE = "2022-09-01"


# ================================
# DATA LOADING
# ================================
def load_etf_prices(filename):
    """Load ETF data from CSV"""
    print("Loading ETF price data...")
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Price data file not found: {filename}")
    
    df = pd.read_csv(filename, parse_dates=['Date'])
    df = df.sort_values('Date')
    df.set_index('Date', inplace=True)
    
    tickers = [col.replace('_close', '') for col in df.columns if col.endswith('_close')]
    
    print(f"  ✓ Loaded {len(df)} weeks of data")
    print(f"  ✓ Date range: {df.index.min().date()} to {df.index.max().date()}")
    print(f"  ✓ Found {len(tickers)} ETFs")
    
    return df, tickers


def load_parameters(filename):
    """Load optimized parameters from JSON file"""
    print("\nLoading optimized parameters from JSON...")
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Parameters file not found: {filename}\n"
                              f"Please run generate_Fbis_Levels_Interactive.py first to create it.")
    
    with open(filename, 'r') as f:
        params = json.load(f)
    
    print(f"  ✓ Loaded parameters for {len(params)} ETFs")
    
    return params


# ================================
# HTML GENERATION
# ================================
def generate_chart_html(ticker, params):
    """Generate HTML for individual ticker chart"""
    
    period = params[ticker]['period']
    shift = params[ticker]['shift']
    
    html = f"""
    <!-- {ticker} Chart -->
    <div class="chart-container">
        <div class="chart-header">
            <h2>{ticker}</h2>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="period_{ticker}">EMA Period: <span id="period_value_{ticker}">{period}</span></label>
                <input type="range" id="period_{ticker}" min="12" max="36" value="{period}" 
                       oninput="document.getElementById('period_value_{ticker}').textContent = this.value; 
                                window['current_period_{ticker}'] = parseInt(this.value); 
                                updateChart_{ticker}()">
            </div>
            
            <div class="control-group">
                <label for="shift_{ticker}">Vertical Shift: <span id="shift_value_{ticker}">{shift:.3f}</span></label>
                <input type="range" id="shift_{ticker}" min="-0.15" max="0.05" step="0.005" value="{shift}"
                       oninput="document.getElementById('shift_value_{ticker}').textContent = parseFloat(this.value).toFixed(3);
                                window['current_shift_{ticker}'] = parseFloat(this.value);
                                updateChart_{ticker}()">
            </div>
        </div>
        
        <div id="chart_{ticker}"></div>
    </div>
    
    <script>
    // Initialize current values
    window['current_period_{ticker}'] = {period};
    window['current_shift_{ticker}'] = {shift};
    
    function updateChart_{ticker}() {{
        const data = chartData['{ticker}'];
        const period = window['current_period_{ticker}'];
        const shift = window['current_shift_{ticker}'];
        
        // Calculate EMA
        const ema = calculateEMA(data.close, period);
        
        // Apply vertical shift
        const fbis = ema.map(val => val * (1 + shift));
        
        // Filter data for display (price from 2020, Fbis from Sep 2022)
        const priceStartIdx = data.date.findIndex(d => d >= '2020-01-01');
        const fbisStartIdx = data.date.findIndex(d => d >= '2022-09-01');
        
        const traces = [
            {{
                x: data.date.slice(priceStartIdx),
                y: data.close.slice(priceStartIdx),
                type: 'scatter',
                mode: 'lines',
                name: '{ticker} Price',
                line: {{ color: 'black', width: 2 }},
                hovertemplate: '<b>{ticker}</b><br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
            }},
            {{
                x: data.date.slice(fbisStartIdx),
                y: fbis.slice(fbisStartIdx),
                type: 'scatter',
                mode: 'lines',
                name: 'Fbis Support',
                line: {{ color: 'red', width: 2, dash: 'dot' }},
                hovertemplate: '<b>Fbis Support</b><br>Date: %{{x}}<br>Level: $%{{y:.2f}}<extra></extra>'
            }}
        ];
        
        const layout = {{
            hovermode: 'x unified',
            showlegend: true,
            legend: {{
                x: 0.02,
                y: 0.98,
                xanchor: 'left',
                yanchor: 'top',
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                bordercolor: '#34495e',
                borderwidth: 1
            }},
            xaxis: {{
                title: '',
                gridcolor: '#ecf0f1',
                showgrid: true
            }},
            yaxis: {{
                title: 'Price ($)',
                gridcolor: '#ecf0f1',
                showgrid: true,
                tickformat: '$.2f'
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 20, b: 40, l: 60 }},
            height: 400
        }};
        
        const config = {{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d']
        }};
        
        Plotly.newPlot('chart_{ticker}', traces, layout, config);
    }}
    
    // Initial render
    updateChart_{ticker}();
    </script>
    """
    
    return html


def generate_chart_data_js(df, tickers):
    """Generate JavaScript object with chart data for all tickers"""
    
    js_data = "const chartData = {\n"
    
    for ticker in tickers:
        if f"{ticker}_close" in df.columns:
            dates = [d.strftime('%Y-%m-%d') for d in df.index]
            closes = df[f"{ticker}_close"].tolist()
            
            js_data += f"    '{ticker}': {{\n"
            js_data += f"        date: {json.dumps(dates)},\n"
            js_data += f"        close: {json.dumps(closes)}\n"
            js_data += f"    }},\n"
    
    js_data += "};\n"
    
    return js_data


def generate_html(df, tickers, params):
    """Generate complete HTML dashboard"""
    
    print("\nGenerating interactive HTML dashboard...")
    
    # Validate that all tickers have parameters
    missing_params = [t for t in tickers if t not in params]
    if missing_params:
        print(f"  ⚠ WARNING: Missing parameters for: {', '.join(missing_params)}")
        tickers = [t for t in tickers if t in params]
    
    # Generate JavaScript data
    chart_data_js = generate_chart_data_js(df, tickers)
    
    # SATID Master CSS
    satid_css = """/* ============================================
   SATID Website - COMPLETE MASTER STYLESHEET
   Merged from index-enhanced-8-3-2.html + styles.css
   This is the DEFINITIVE version with ALL styling
   ============================================ */

/* ============================================
   1. BASE STYLES & RESET
   ============================================ */

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

/* ============================================
   2. NAVIGATION STYLES - COMPLETE
   ============================================ */

.navbar {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-container {
    max-width: 100% !important;
    padding: 0 40px !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-logo {
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 15px 0;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 30px;
    justify-content: space-between !important;
    width: 100% !important;
}

.nav-menu li {
    list-style: none;
}

.nav-menu a {
    color: #ecf0f1;
    text-decoration: none;
    padding: 20px 0;
    display: block;
    transition: color 0.3s;
    font-size: 17px;
    font-weight: 400;
}

.nav-menu a:hover,
.nav-menu a.active {
    color: #3498db;
}

/* Dropdown Menu */
.dropdown {
    position: relative;
}

.dropbtn {
    cursor: pointer;
    color: #ecf0f1;
    text-decoration: none;
    padding: 20px 0;
    display: block;
    transition: color 0.3s;
    font-size: 17px;
    font-weight: 400;
}

.dropdown-content {
    display: none;
    position: absolute;
    background-color: #34495e;
    min-width: 250px;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.3);
    z-index: 1000;
    top: 100%;
    left: 0;
}

/* Right-align the last dropdown to prevent overflow */
.nav-menu li.dropdown:last-of-type .dropdown-content {
    left: auto;
    right: 0;
}

.dropdown-content a {
    color: #ecf0f1;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
    border-bottom: 1px solid #2c3e50;
}

.dropdown-content a:hover {
    background-color: #2c3e50;
    color: #3498db;
}

.dropdown:hover .dropdown-content {
    display: block;
}

.dropdown:hover .dropbtn {
    color: #3498db;
}

/* ============================================
   3. HERO SECTION
   ============================================ */

.hero {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d6cb9 100%);
    padding: 40px 20px 80px;
    position: relative;
    overflow: hidden;
    color: white;
    text-align: center;
}

.hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1" fill="rgba(255,255,255,0.03)"/></svg>') repeat;
    opacity: 0.5;
}

.hero-content {
    max-width: 1000px;
    margin: 0 auto;
    text-align: center;
    position: relative;
    z-index: 1;
}

.hero h1 {
    font-size: 3.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 20px;
    letter-spacing: -0.5px;
    animation: fadeInUp 0.8s ease-out;
}

.hero h2 {
    font-size: 28px;
    margin-bottom: 15px;
    font-weight: 400;
    color: #ecf0f1;
}

.hero-subtitle {
    font-size: 1.6rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 300;
    letter-spacing: 0.5px;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ============================================
   4. CONTAINER & CONTENT PAGE
   ============================================ */

.container {
    max-width: 100% !important;
    margin: -60px auto 60px;
    padding: 0 10px !important;
    position: relative;
    z-index: 2;
}

.content-page {
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    padding: 50px 30px 70px 30px !important;
    animation: fadeIn 1s ease-out;
    max-width: 850px;
    margin-left: auto;
    margin-right: auto;
}

.chart-page-container {
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    padding: 50px 30px 70px 30px !important;
    animation: fadeIn 1s ease-out;
    max-width: 1020px;
    margin-left: auto;
    margin-right: auto;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* ============================================
   5. CONTENT SECTIONS
   ============================================ */

.content-section {
    margin-bottom: 50px;
}

.content-section h2 {
    font-size: 2rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 30px;
    position: relative;
    color: #1e3c72;
    letter-spacing: -0.5px;
}

.content-section h2::after {
    content: '';
    display: block;
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #2a5298, #3d6cb9);
    margin: 15px auto 0;
    border-radius: 2px;
}

.content-section h3 {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1e3c72;
    margin-top: 35px;
    margin-bottom: 18px;
    position: relative;
    padding-bottom: 10px;
    letter-spacing: -0.3px;
}

.content-section h3::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 50px;
    height: 3px;
    background: linear-gradient(90deg, #2a5298, #3d6cb9);
    border-radius: 2px;
}

.content-section h3 a {
    color: #1e3c72;
    text-decoration: underline;
    text-decoration-color: #1e3c72;
    text-decoration-thickness: 2px;
    text-underline-offset: 4px;
    transition: color 0.3s ease;
}

.content-section h3 a:hover {
    color: #2a5298;
    text-decoration-color: #2a5298;
}

.content-section p {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #4a5568;
    margin-bottom: 20px;
    font-weight: 400;
}

/* ============================================
   6. CHART CONTAINERS
   ============================================ */

.chart-container {
    margin: 50px 0;
    padding: 30px;
    background: #f8f9fa;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.chart-section {
    background-color: #f8f9fa;
    padding: 30px;
    margin-bottom: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.chart-section h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #1e3c72;
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
}

#aok-chart,
#chart-container {
    width: 100%;
    min-height: 500px;
}

/* ============================================
   7. KEY POINTS / HIGHLIGHT BOXES
   ============================================ */

.key-point {
    background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
    border-left: 4px solid #2a5298;
    padding: 30px 35px;
    margin: 30px 0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
}

.key-point:hover {
    transform: translateX(5px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.key-point-large {
    padding: 35px 40px;
    font-size: 1.05rem;
}

.highlight-box {
    background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
    border-left: 4px solid #2a5298;
    padding: 30px 35px;
    margin: 30px 0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.highlight-box p {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #4a5568;
}

/* ============================================
   8. COMPARISON TABLES
   ============================================ */

.comparison-table-wrapper {
    margin-top: 60px;
    overflow: hidden;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

.comparison-table thead tr {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}

.comparison-table th {
    padding: 25px 20px;
    color: white;
    font-size: 1.2rem;
    font-weight: 600;
    text-align: center;
    letter-spacing: 0.5px;
}

.comparison-table th:first-child {
    border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.comparison-table tbody tr {
    transition: all 0.3s ease;
}

.comparison-table tbody tr:nth-child(odd) {
    background-color: #f7f9fc;
}

.comparison-table tbody tr:nth-child(even) {
    background-color: #ffffff;
}

.comparison-table tbody tr:hover {
    background-color: #e8f0fe;
    transform: scale(1.01);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.comparison-table td {
    padding: 20px 25px;
    text-align: center;
    font-size: 1.05rem;
    color: #4a5568;
    line-height: 1.6;
}

.comparison-table td:first-child {
    border-right: 1px solid #e2e8f0;
}

.comparison-table td u {
    color: #2a5298;
    font-weight: 600;
    text-decoration: none;
    border-bottom: 2px solid #2a5298;
}

/* ============================================
   9. CONTROLS
   ============================================ */

.controls {
    display: flex;
    gap: 30px;
    margin-bottom: 25px;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.control-group {
    flex: 1;
}

.control-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2a5298;
    font-size: 0.95rem;
}

.control-group input[type="range"] {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: #e9ecef;
    outline: none;
    -webkit-appearance: none;
}

.control-group input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #2a5298;
    cursor: pointer;
    transition: all 0.2s ease;
}

.control-group input[type="range"]::-webkit-slider-thumb:hover {
    background: #1e3c72;
    transform: scale(1.15);
}

.control-group input[type="range"]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #2a5298;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
}

.control-group input[type="range"]::-moz-range-thumb:hover {
    background: #1e3c72;
    transform: scale(1.15);
}

/* ============================================
   10. SAVE BUTTON
   ============================================ */

.save-section {
    position: fixed;
    bottom: 30px;
    right: 20px;
    z-index: 1000;
}

.save-btn {
    padding: 14px 28px;
    background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.05rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
}

.save-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
    background: linear-gradient(135deg, #229954 0%, #27ae60 100%);
}

/* ============================================
   11. FOOTER
   ============================================ */

footer {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: rgba(255, 255, 255, 0.9);
    text-align: center;
    padding: 30px 20px;
    margin-top: 80px;
    font-size: 0.95rem;
    letter-spacing: 0.5px;
}

footer p {
    margin: 0;
}

/* ============================================
   12. RESPONSIVE DESIGN
   ============================================ */

@media (max-width: 1400px) {
    .content-page {
        padding: 50px 30px 60px 30px !important;
    }
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2.5rem;
    }
    
    .hero h2 {
        font-size: 22px;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
    }
    
    .content-page {
        padding: 40px 25px !important;
    }
    
    .chart-page-container {
        padding: 30px 20px !important;
    }
    
    .content-section h2 {
        font-size: 1.6rem;
    }
    
    .comparison-table th,
    .comparison-table td {
        padding: 15px;
        font-size: 0.95rem;
    }
    
    .controls {
        flex-direction: column;
        gap: 20px;
    }
    
    .nav-menu {
        flex-direction: column;
        gap: 10px;
    }
    
    .dropdown-content {
        position: static;
        box-shadow: none;
        background-color: #2c3e50;
    }
    
    .dropdown:hover .dropdown-content {
        display: none;
    }
    
    .dropdown.active .dropdown-content {
        display: block;
    }
}

/* ============================================
   13. UTILITY CLASSES
   ============================================ */

.text-center {
    text-align: center;
}

.text-justify {
    text-align: justify;
}

.mb-20 {
    margin-bottom: 20px;
}

.mb-30 {
    margin-bottom: 30px;
}

.mb-40 {
    margin-bottom: 40px;
}

.mt-20 {
    margin-top: 20px;
}

.mt-30 {
    margin-top: 30px;
}

.mt-40 {
    margin-top: 40px;
}"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-75MKR2S7LT"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-75MKR2S7LT');
    </script>
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATID - Risk Level Setting</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
{satid_css}
    </style>
</head>
<body>
    <!-- Save Button -->
    <div class="save-section">
        <button class="save-btn" onclick="saveAllParameters()">💾 Save All Parameters</button>
    </div>

    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <ul class="nav-menu">
                <li><a href="index.html">Index</a></li>
                <li><a href="Philosophy.html">Philosophy</a></li>
                <li><a href="Methodology.html">Methodology</a></li>
                <li><a href="Support_Levels_Interactive.html" class="active">Risk Level Setting</a></li>
                <li><a href="Portfolio_Risk_Exposure.html">Risk Exposure</a></li>
                <li><a href="SATID_Risk_Score.html">Risk Score</a></li>
                <li><a href="Portfolio_Risk_Dashboard.html">Risk Dashboard</a></li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Market Views</a>
                    <div class="dropdown-content">
                        <a href="Market_Views.html">About Market Views</a>
                        <a href="SATID_Relative_Performance.html">Cross Asset Validations</a>
                    </div>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Appendix</a>
                    <div class="dropdown-content">
                        <a href="portfolio_dashboard.html">Portfolios Profile Snapshot</a>
                        <a href="model_portfolios.html">Model Portfolios</a>
                        <a href="portfolio_statistics_monthly.html">Portfolio Statistics</a>
                        <a href="generate_annual_returns_chart.html">Annual Returns</a>
                    </div>
                </li>
            </ul>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Risk Level Setting</h1>
            <p class="hero-subtitle">Interactive support levels with adjustable EMA parameters</p>
        </div>
    </section>

    <!-- Main Content Container -->
    <div class="container">
        <div class="chart-page-container">
    
    <script>
    {chart_data_js}
    
    // Calculate EMA
    function calculateEMA(data, period) {{
        const k = 2 / (period + 1);
        const ema = [data[0]];
        
        for (let i = 1; i < data.length; i++) {{
            ema.push(data[i] * k + ema[i - 1] * (1 - k));
        }}
        
        return ema;
    }}
    
    // Save all parameters to JSON
    function saveAllParameters() {{
        const params = {{}};
        const tickers = Object.keys(chartData);
        
        for (let ticker of tickers) {{
            const period = window['current_period_' + ticker];
            const shift = window['current_shift_' + ticker];
            
            params[ticker] = {{
                period: period,
                shift: parseFloat(shift.toFixed(4))
            }};
        }}
        
        const jsonStr = JSON.stringify(params, null, 2);
        const blob = new Blob([jsonStr], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'SATID_Fbis_Optimized_Parameters.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert('✅ Parameters saved!\\n\\nFile: SATID_Fbis_Optimized_Parameters.json\\n\\nPlace this file in your SATID folder.');
    }}
    </script>
"""
    
    # Generate chart HTML for each ticker
    for ticker in tickers:
        if f"{ticker}_close" in df.columns:
            html += generate_chart_html(ticker, params)
    
    html += """
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>&copy; 2024 SATID Investment Management. All rights reserved.</p>
    </footer>
</body>
</html>"""
    
    print(f"  ✓ Generated HTML with {len(tickers)} charts")
    
    return html


# ================================
# MAIN EXECUTION
# ================================
def main():
    print("=" * 80)
    print("SATID FBIS LEVELS - NO OPTIMIZATION VERSION")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("🔒 Using existing parameters from JSON file (NO optimization)")
    print("=" * 80)
    print()
    
    try:
        # Load data
        df, tickers = load_etf_prices(CSV_FILE)
        
        # Load existing parameters (NO OPTIMIZATION)
        params = load_parameters(PARAMS_FILE)
        
        # Generate HTML
        html = generate_html(df, tickers, params)
        
        # Save HTML
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("\n" + "=" * 80)
        print("✓ GENERATION COMPLETE!")
        print("=" * 80)
        print(f"  ✓ Output HTML: {OUTPUT_HTML}")
        print(f"  ✓ Used parameters from: {PARAMS_FILE}")
        print(f"  ✓ ETFs processed: {len([t for t in tickers if t in params])}")
        print("\n📋 What happened:")
        print("  • Loaded latest price data from CSV")
        print("  • Used existing optimized parameters from JSON")
        print("  • Generated interactive charts with current prices")
        print("  • NO optimization was performed")
        print("\n🎯 Charts display:")
        print("  • Price (black line) from January 2020")
        print("  • Fbis support (red dotted line) from September 2022")
        print("  • Interactive sliders to adjust parameters if needed")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}")
        print("\nRequired files:")
        print(f"  - {CSV_FILE} (price data)")
        print(f"  - {PARAMS_FILE} (optimized parameters)")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
