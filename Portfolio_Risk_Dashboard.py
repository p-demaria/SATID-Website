"""
PORTFOLIO RISK DASHBOARD - SIMPLIFIED VERSION
==============================================
Generates: Portfolio_Risk_Dashboard.html

Simplified layout showing:
1. Portfolio Value & FBIS chart
2. Distance to FBIS (% and USD)
3. SATID scores (1-week and 1-month)

NOTE: All core calculations imported from SATID_core_calculations.py
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

# Import all core SATID calculation functions from shared module
from SATID_core_calculations import (
    get_active_etfs_with_allocations,
    calculate_portfolio_series,
    calculate_correlation_matrix,
    calculate_individual_volatilities,
    calculate_portfolio_volatility,
    calculate_risk_statistics,
    analyze_etf_risk,
    calculate_portfolio_satid_scores
)

# File paths
PORTFOLIO_FILE = 'Model_Portfolio.xlsx'
OHLC_FILE = 'SATID_portfolio_etf_data_weekly_ohlc.csv'
FBIS_PARAMS_FILE = 'SATID_Fbis_Optimized_Parameters.json'
OUTPUT_HTML = 'Portfolio_Risk_Dashboard.html'
PORTFOLIO_VALUE = 10_000_000


def get_risk_color_and_label(score):
    """Get risk level colors matching SATID methodology"""
    if score >= 90:
        return '#c0392b', "CRITICAL"
    elif score >= 75:
        return '#e74c3c', "HIGH"
    elif score >= 50:
        return '#f39c12', "MODERATE"
    elif score >= 25:
        return '#27ae60', "LOW"
    else:
        return '#16a085', "MINIMAL"


def generate_dashboard_html(dates, portfolio_values, portfolio_fbis,
                           current_value, fbis_value, distance_pct,
                           portfolio_score_1week, portfolio_score_1month,
                           output_file):
    
    chart_dates = [str(d)[:10] for d in dates]
    chart_values = portfolio_values.tolist()
    fbis_dates = [str(d)[:10] for d in dates]
    fbis_values = portfolio_fbis.tolist()
    
    current_nav = current_value * PORTFOLIO_VALUE
    fbis_nav = fbis_value * PORTFOLIO_VALUE
    usd_distance = current_nav - fbis_nav
    distance_pct_display = distance_pct * 100
    
    bg_color_1w, risk_label_1w = get_risk_color_and_label(portfolio_score_1week)
    bg_color_1m, risk_label_1m = get_risk_color_and_label(portfolio_score_1month)
    
    analysis_date = datetime.now().strftime("%B %d, %Y at %H:%M")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATID - Portfolio Risk Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
    <style>
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

        .nav-menu {{
            display: flex;
            list-style: none;
            gap: 30px;
            justify-content: space-between !important;
            width: 100% !important;
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

        .hero {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d6cb9 100%);
            padding: 40px 20px 80px;
            position: relative;
            overflow: hidden;
            color: white;
            text-align: center;
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
        }}

        .hero-subtitle {{
            font-size: 1.6rem;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 300;
            letter-spacing: 0.5px;
        }}

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
            max-width: 850px;
            margin-left: auto;
            margin-right: auto;
        }}

        .chart-section {{
            margin-bottom: 20px;
        }}

        #portfolio-chart {{
            width: 100%;
            height: 480px;
            margin-bottom: 8px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 20px 0 25px 0;
            max-width: 640px;
            margin-left: auto;
            margin-right: auto;
        }}

        .metric-card {{
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
        }}

        .metric-header {{
            padding: 12px;
            text-align: center;
            color: white;
            font-size: 0.88rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: #34495e;
        }}

        .metric-body {{
            padding: 17.5px 12.6px;
            text-align: center;
            background: white;
        }}

        .metric-value {{
            font-size: 1.715rem;
            font-weight: 700;
            margin-bottom: 7px;
        }}

        .scores-section {{
            margin-top: 35px;
        }}

        .section-title {{
            font-size: 1.8rem;
            font-weight: 600;
            color: #1e3c72;
            text-align: center;
            margin-bottom: 18px;
            position: relative;
        }}

        .section-title::after {{
            content: '';
            display: block;
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #2a5298, #3d6cb9);
            margin: 12px auto 0;
            border-radius: 2px;
        }}

        .scores-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 40px;
        }}

        .score-box {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .score-value {{
            font-size: 1.715rem;
            font-weight: bold;
            color: white;
            margin: 15px 0 11.25px 0;
            padding: 15px;
            border-radius: 10px;
        }}

        .score-label {{
            font-size: 0.88rem;
            font-weight: bold;
            color: white;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .score-description {{
            color: #7f8c8d;
            font-size: 13px;
            margin-top: 10px;
        }}

        .interpretation-section {{
            margin-top: 35px;
            padding: 25px 20px;
            background: #f8f9fa;
            border-radius: 12px;
        }}

        .interpretation-section h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #1e3c72;
            text-align: center;
            margin-bottom: 18px;
        }}

        .interpretation-grid {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .interpretation-box {{
            padding: 14px;
            border-radius: 8px;
            border-left: 5px solid;
            transition: transform 0.3s ease;
        }}

        .interpretation-box:hover {{
            transform: translateX(5px);
        }}

        .interpretation-box strong {{
            font-size: 1.05rem;
        }}

        .interpretation-box p {{
            margin: 5px 0 0 0;
            font-size: 0.9rem;
            line-height: 1.5;
        }}

        .analysis-date {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 30px;
        }}

        footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            padding: 30px 20px;
            margin-top: 80px;
            font-size: 0.95rem;
            letter-spacing: 0.5px;
        }}

        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            .metrics-grid,
            .scores-container {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .score-value {{
                font-size: 24px;
            }}
            
            .score-label {{
                font-size: 16px;
            }}
            
            .metric-value {{
                font-size: 1.4rem;
            }}
            
            .interpretation-section {{
                padding: 25px 15px;
            }}
            
            .interpretation-box {{
                padding: 12px;
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
                <li><a href="Portfolio_Risk_Dashboard.html" class="active">Risk Dashboard</a></li>
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
            <h1>Portfolio Risk Dashboard</h1>
            <p class="hero-subtitle">Comprehensive Portfolio Risk Assessment</p>
        </div>
    </section>

    <!-- Main Content -->
    <div class="container">
        <div class="content-page">
            
            <div class="analysis-date">Analysis: {analysis_date}</div>
            
            <!-- Chart Section -->
            <div class="chart-section">
                <div id="portfolio-chart"></div>
            </div>
            
            <!-- Portfolio Risk Metrics Section -->
            <div style="margin-top: 20px;">
                <h2 class="section-title">Portfolio Risk Metrics</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-header">Distance to Risk-off</div>
                        <div class="metric-body">
                            <div class="metric-value" style="color: {'#27ae60' if distance_pct_display > 0 else '#e74c3c'};">
                                {-abs(distance_pct_display):.2f}%
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">USD at Risk (if FBIS Breached)</div>
                        <div class="metric-body">
                            <div class="metric-value" style="color: #1e3c72;">
                                ${usd_distance:,.0f}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- SATID Scores Section -->
            <div class="scores-section">
                <h2 class="section-title">SATID Risk Scores</h2>
                
                <div class="scores-container">
                    <div class="score-box">
                        <h3 style="color: #34495e; margin-bottom: 7.5px;">1 Week Horizon</h3>
                        <div class="score-value" style="background-color: {bg_color_1w};">
                            {portfolio_score_1week:.1f}
                        </div>
                        <div class="score-label" style="background-color: {bg_color_1w};">
                            {risk_label_1w} RISK
                        </div>
                        <div class="score-description">
                            Weighted average of individual ETF scores
                        </div>
                    </div>
                    
                    <div class="score-box">
                        <h3 style="color: #34495e; margin-bottom: 7.5px;">1 Month Horizon</h3>
                        <div class="score-value" style="background-color: {bg_color_1m};">
                            {portfolio_score_1month:.1f}
                        </div>
                        <div class="score-label" style="background-color: {bg_color_1m};">
                            {risk_label_1m} RISK
                        </div>
                        <div class="score-description">
                            Adjusted for 1-month volatility (√4.33 weeks)
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Risk Level Interpretation Section -->
            <div class="interpretation-section">
                <h2>Risk Level Interpretation & Action Guidelines</h2>
                <div class="interpretation-grid">
                    <div class="interpretation-box" style="border-left-color: #c0392b; background-color: #fce4e4;">
                        <strong style="color: #c0392b;">CRITICAL (90-100)</strong>
                        <p>0-0.4σ from support. At or touching support - regime change likely. Switch to full SATID mode - actively reduce/exit positions.</p>
                    </div>
                    <div class="interpretation-box" style="border-left-color: #e74c3c; background-color: #fadbd8;">
                        <strong style="color: #e74c3c;">HIGH (75-89)</strong>
                        <p>0.4-1.0σ from support. Within one standard deviation - one typical move breaches support. High alert - prepare action plan.</p>
                    </div>
                    <div class="interpretation-box" style="border-left-color: #f39c12; background-color: #fef5e7;">
                        <strong style="color: #f39c12;">MODERATE (50-74)</strong>
                        <p>1.0-2.0σ from support. Need 1-2 standard moves to breach. Monitor closely, consider hybrid MPT/SATID approach.</p>
                    </div>
                    <div class="interpretation-box" style="border-left-color: #27ae60; background-color: #eafaf1;">
                        <strong style="color: #27ae60;">LOW (25-49)</strong>
                        <p>2.0-3.0σ from support. Comfortable distance from support. Normal MPT management with enhanced monitoring.</p>
                    </div>
                    <div class="interpretation-box" style="border-left-color: #16a085; background-color: #e8f8f5;">
                        <strong style="color: #16a085;">MINIMAL (0-24)</strong>
                        <p>Beyond 3.0σ from support. Very far from support. Full MPT mode - manage according to benchmark and allocations.</p>
                    </div>
                </div>
            </div>
            
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>&copy; 2024 SATID Investment Management. All rights reserved.</p>
    </footer>
    
    <script>
        const portfolioDates = {json.dumps(chart_dates)};
        const portfolioValues = {json.dumps(chart_values)};
        const fbisDates = {json.dumps(fbis_dates)};
        const fbisValues = {json.dumps(fbis_values)};
        
        const trace1 = {{
            x: portfolioDates,
            y: portfolioValues,
            type: 'scatter',
            mode: 'lines',
            name: 'Portfolio Value',
            line: {{ color: 'black', width: 2.5 }}
        }};
        
        const trace2 = {{
            x: fbisDates,
            y: fbisValues,
            type: 'scatter',
            mode: 'lines',
            name: 'Aggregate Fbis Support',
            line: {{ color: 'red', width: 2, dash: 'dot' }}
        }};
        
        const layout = {{
            title: {{
                text: 'Portfolio Value & Risk-off Level',
                font: {{ size: 18, family: 'Inter, sans-serif' }}
            }},
            xaxis: {{
                title: 'Date',
                gridcolor: '#ecf0f1'
            }},
            yaxis: {{
                title: 'Normalized Value',
                gridcolor: '#ecf0f1'
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#ffffff',
            paper_bgcolor: '#ffffff',
            font: {{ family: 'Inter, sans-serif', size: 12 }},
            showlegend: true,
            legend: {{ x: 0.01, y: 0.99 }},
            margin: {{ t: 50, b: 50, l: 60, r: 30 }}
        }};
        
        const config = {{ responsive: true, displayModeBar: true }};
        
        Plotly.newPlot('portfolio-chart', [trace1, trace2], layout, config);
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_file}")


def main():
    print("="*80)
    print("PORTFOLIO RISK DASHBOARD - SIMPLIFIED VERSION")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load data
        print("[1/5] Loading portfolio allocations...")
        allocations = get_active_etfs_with_allocations(PORTFOLIO_FILE)
        print(f"   ✓ Found {len(allocations)} ETFs")
        
        print("[2/5] Loading FBIS parameters...")
        with open(FBIS_PARAMS_FILE, 'r') as f:
            fbis_params = json.load(f)
        print(f"   ✓ Loaded parameters for {len(fbis_params)} ETFs")
        
        # Calculate portfolio series
        print("[3/5] Calculating portfolio value and Fbis...")
        dates, portfolio_values, portfolio_fbis = calculate_portfolio_series(
            OHLC_FILE, allocations, fbis_params
        )
        current_value = portfolio_values[-1]
        fbis_value = portfolio_fbis[-1]
        distance_pct = (current_value - fbis_value) / current_value
        print(f"   ✓ Current Value: {current_value:.4f}")
        print(f"   ✓ Fbis Level: {fbis_value:.4f}")
        print(f"   ✓ Distance: {distance_pct:.2%}")
        
        # Calculate SATID scores
        print("[4/5] Calculating SATID scores...")
        df = pd.read_csv(OHLC_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        etf_results = []
        for ticker in allocations.keys():
            close_col = f"{ticker}_close"
            if close_col not in df.columns:
                continue
            prices = df[close_col].values
            result = analyze_etf_risk(ticker, prices, fbis_params)
            etf_results.append(result)
        
        portfolio_score_1week, portfolio_score_1month = calculate_portfolio_satid_scores(
            etf_results, allocations
        )
        print(f"   ✓ 1-Week Score: {portfolio_score_1week:.1f}")
        print(f"   ✓ 1-Month Score: {portfolio_score_1month:.1f}")
        
        # Generate HTML
        print("[5/5] Generating HTML dashboard...")
        generate_dashboard_html(
            dates, portfolio_values, portfolio_fbis,
            current_value, fbis_value, distance_pct,
            portfolio_score_1week, portfolio_score_1month,
            OUTPUT_HTML
        )
        
        print("\n" + "="*80)
        print("✓ COMPLETE!")
        print("="*80)
        print(f"\nOutput: {OUTPUT_HTML}")
        print(f"Portfolio Value: {current_value:.4f}")
        print(f"Fbis Support: {fbis_value:.4f}")
        print(f"Distance: {distance_pct:.2%}")
        print(f"SATID Scores: 1W={portfolio_score_1week:.1f}, 1M={portfolio_score_1month:.1f}")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
