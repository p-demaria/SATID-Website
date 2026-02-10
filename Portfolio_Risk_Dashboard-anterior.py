"""
PORTFOLIO RISK DASHBOARD - CORRECTED VERSION
=============================================
Generates: Portfolio_Risk_Dashboard.html

EXACT MATCH to original Tab 1:
- BLACK portfolio line (not blue)
- RED dotted Fbis line  
- "Risk-off Level" section with NAV values
- SATID scores display
- Portfolio Risk Exposure table

NOTE: All core calculations imported from SATID_core_calculations.py
      This ensures 100% consistency with SATID_Risk_Score.py
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Import all core SATID calculation functions from shared module
from SATID_core_calculations import (
    get_active_etfs_with_allocations,
    calculate_ema,
    calculate_portfolio_series,
    calculate_correlation_matrix,
    calculate_individual_volatilities,
    calculate_portfolio_volatility,
    calculate_risk_statistics,
    calculate_etf_volatility,
    calculate_satid_score_linear,
    analyze_etf_risk,
    calculate_portfolio_satid_scores,
    get_risk_level_class,
    load_portfolio_allocations,
    calculate_portfolio_risk
)

# File paths
PORTFOLIO_FILE = 'Model_Portfolio.xlsx'
OHLC_FILE = 'SATID_portfolio_etf_data_weekly_ohlc.csv'
FBIS_PARAMS_FILE = 'SATID_Fbis_Optimized_Parameters.json'
OUTPUT_HTML = 'Portfolio_Risk_Dashboard.html'
PORTFOLIO_VALUE = 10_000_000

RISK_THRESHOLDS = {
    'Cash': {'warning': -2.0, 'danger': -3.0},
    'Fixed Income': {'warning': -2.0, 'danger': -3.0},
    'Core Equity': {'warning': -3.5, 'danger': -5.0},
    'Sector & Thematic': {'warning': -3.5, 'danger': -5.0},
    'Secular Growth': {'warning': -3.5, 'danger': -5.0},
    'Alternative Investments': {'warning': -3.5, 'danger': -5.0}
}

COLORS = {'blue': '#34495e', 'orange': '#f39c12', 'red': '#e74c3c'}


# All core calculation functions imported from SATID_core_calculations.py
# This ensures 100% consistency with SATID_Risk_Score.py

def format_risk_exposure_table(risk_data, asset_class_summary, category_weights):
    html = """
    <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-family: Arial, sans-serif;">
        <thead>
            <tr style="background-color: #2c3e50; color: white;">
                <th style="padding: 12px; text-align: left; border: 1px solid #34495e;">Asset Class / Ticker</th>
                <th style="padding: 12px; text-align: center; border: 1px solid #34495e;">Allocation</th>
                <th style="padding: 12px; text-align: center; border: 1px solid #34495e;">% to Support</th>
                <th style="padding: 12px; text-align: right; border: 1px solid #34495e;">$ at Risk (if Support Breached)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    sorted_data = sorted(risk_data, key=lambda x: (x['Asset Class'], x['Ticker']))
    
    current_class = None
    for item in sorted_data:
        if item['Asset Class'] != current_class:
            current_class = item['Asset Class']
            summary = asset_class_summary.get(current_class, {})
            
            html += f"""
            <tr style="background-color: #ecf0f1; font-weight: bold;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;">{current_class}</td>
                <td style="padding: 10px; text-align: center; border: 1px solid #bdc3c7;">{summary.get('weight', 0):.1f}%</td>
                <td style="padding: 10px; text-align: center; border: 1px solid #bdc3c7;">{summary.get('avg_dist', 0):.2f}%</td>
                <td style="padding: 10px; text-align: right; border: 1px solid #bdc3c7;">${summary.get('usd_at_risk', 0):,.0f}</td>
            </tr>
            """
        
        pct_color = '#27ae60' if item['% to Support'] > 0 else '#e74c3c'
        
        html += f"""
        <tr style="background-color: white;">
            <td style="padding: 8px 8px 8px 30px; border: 1px solid #ecf0f1;">{item['Ticker']}</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ecf0f1;">{item['Allocation (%)']:.1f}%</td>
            <td style="padding: 8px; text-align: center; border: 1px solid #ecf0f1; color: {pct_color}; font-weight: bold;">
                {item['% to Support']:.2f}%
            </td>
            <td style="padding: 8px; text-align: right; border: 1px solid #ecf0f1;">${item['USD at Risk']:,.0f}</td>
        </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    return html

def generate_dashboard_html(dates, portfolio_values, portfolio_fbis, statistics,
                           current_value, fbis_value, distance_pct,
                           risk_data, asset_class_summary, category_weights,
                           portfolio_score_1week, portfolio_score_1month,
                           output_file):
    
    chart_dates = [str(d)[:10] for d in dates]
    chart_values = portfolio_values.tolist()
    fbis_dates = [str(d)[:10] for d in dates]
    fbis_values = portfolio_fbis.tolist()
    
    current_nav = current_value * PORTFOLIO_VALUE
    fbis_nav = fbis_value * PORTFOLIO_VALUE
    usd_distance = current_nav - fbis_nav
    
    stats_1w = statistics['1_week']
    stats_1m = statistics['1_month']
    stats_3m = statistics['3_months']
    
    portfolio_risk_exposure_html = format_risk_exposure_table(
        risk_data, asset_class_summary, category_weights
    )
    
    def get_risk_color_and_label(score):
        """Get risk level colors matching SATID methodology"""
        if score >= 90:
            return '#c0392b', "CRITICAL"  # Dark red
        elif score >= 75:
            return '#e74c3c', "HIGH"  # Red
        elif score >= 50:
            return '#f39c12', "MODERATE"  # Orange
        elif score >= 25:
            return '#27ae60', "LOW"  # Green
        else:
            return '#16a085', "MINIMAL"  # Teal
    
    bg_color_1w, risk_label_1w = get_risk_color_and_label(portfolio_score_1week)
    bg_color_1m, risk_label_1m = get_risk_color_and_label(portfolio_score_1month)
    
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
        /* ============================================
           SATID Website - COMPLETE MASTER STYLESHEET
           Merged from index-enhanced-8-3-2.html + styles.css
           This is the DEFINITIVE version with ALL styling
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
            max-width: 850px;
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

        .content-section h3 {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #1e3c72;
            margin-top: 35px;
            margin-bottom: 18px;
            position: relative;
            padding-bottom: 10px;
            letter-spacing: -0.3px;
        }}

        .content-section h3::after {{
            content: '';
            position: absolute;
            left: 0;
            bottom: 0;
            width: 50px;
            height: 3px;
            background: linear-gradient(90deg, #2a5298, #3d6cb9);
            border-radius: 2px;
        }}

        .content-section h3 a {{
            color: #1e3c72;
            text-decoration: underline;
            text-decoration-color: #1e3c72;
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
            transition: color 0.3s ease;
        }}

        .content-section h3 a:hover {{
            color: #2a5298;
            text-decoration-color: #2a5298;
        }}

        .content-section p {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: #4a5568;
            margin-bottom: 20px;
            font-weight: 400;
        }}

        /* ============================================
           6. CHART CONTAINERS
           ============================================ */

        .chart-container {{
            margin: 50px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }}

        #aok-chart,
        #chart-container {{
            width: 100%;
            min-height: 500px;
        }}

        /* ============================================
           7. KEY POINTS / HIGHLIGHT BOXES
           ============================================ */

        .key-point {{
            background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
            border-left: 4px solid #2a5298;
            padding: 30px 35px;
            margin: 30px 0;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
            transition: all 0.3s ease;
        }}

        .key-point:hover {{
            transform: translateX(5px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
        }}

        .key-point-large {{
            padding: 35px 40px;
            font-size: 1.05rem;
        }}

        .highlight-box {{
            background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
            border-left: 4px solid #2a5298;
            padding: 30px 35px;
            margin: 30px 0;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }}

        .highlight-box p {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: #4a5568;
        }}

        /* ============================================
           8. COMPARISON TABLES
           ============================================ */

        .comparison-table-wrapper {{
            margin-top: 60px;
            overflow: hidden;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}

        .comparison-table thead tr {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        }}

        .comparison-table th {{
            padding: 25px 20px;
            color: white;
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
            letter-spacing: 0.5px;
        }}

        .comparison-table th:first-child {{
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .comparison-table tbody tr {{
            transition: all 0.3s ease;
        }}

        .comparison-table tbody tr:nth-child(odd) {{
            background-color: #f7f9fc;
        }}

        .comparison-table tbody tr:nth-child(even) {{
            background-color: #ffffff;
        }}

        .comparison-table tbody tr:hover {{
            background-color: #e8f0fe;
            transform: scale(1.01);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .comparison-table td {{
            padding: 20px 25px;
            text-align: center;
            font-size: 1.05rem;
            color: #4a5568;
            line-height: 1.6;
        }}

        .comparison-table td:first-child {{
            border-right: 1px solid #e2e8f0;
        }}

        .comparison-table td u {{
            color: #2a5298;
            font-weight: 600;
            text-decoration: none;
            border-bottom: 2px solid #2a5298;
        }}

        /* ============================================
           9. FOOTER
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
           10. RESPONSIVE DESIGN
           ============================================ */

        @media (max-width: 1400px) {{
            .content-page {{
                padding: 50px 30px 60px 30px !important;
            }}
        }}

        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            .hero h2 {{
                font-size: 22px;
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
            
            .comparison-table th,
            .comparison-table td {{
                padding: 15px;
                font-size: 0.95rem;
            }}
            
            .nav-menu {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .dropdown-content {{
                position: static;
                box-shadow: none;
                background-color: #2c3e50;
            }}
            
            .dropdown:hover .dropdown-content {{
                display: none;
            }}
            
            .dropdown.active .dropdown-content {{
                display: block;
            }}
        }}

        /* ============================================
           11. UTILITY CLASSES
           ============================================ */

        .text-center {{
            text-align: center;
        }}

        .text-justify {{
            text-align: justify;
        }}

        .mb-20 {{
            margin-bottom: 20px;
        }}

        .mb-30 {{
            margin-bottom: 30px;
        }}

        .mb-40 {{
            margin-bottom: 40px;
        }}

        .mt-20 {{
            margin-top: 20px;
        }}

        .mt-30 {{
            margin-top: 30px;
        }}

        .mt-40 {{
            margin-top: 40px;
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
            <p class="hero-subtitle">Real-time Portfolio Risk Monitoring & Analysis</p>
        </div>
    </section>

    <!-- Main Content Container -->
    <div class="container">
        <div class="content-page">
            
            <!-- Portfolio Chart -->
            <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <div id="portfolio-chart"></div>
            </div>
            
            <!-- Risk-off Level Statistics -->
            <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <h2 style="color: #2c3e50; margin-bottom: 20px; font-size: 22px; text-align: center;">Risk-off Level</h2>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 25px;">
                    <div style="background: #ecf0f1; padding: 20px; border-radius: 8px;">
                        <div style="font-size: 14px; color: #7f8c8d; margin-bottom: 8px;">Current Portfolio NAV</div>
                        <div style="font-size: 28px; font-weight: bold; color: #2c3e50;">${current_nav:,.0f}</div>
                    </div>
                    <div style="background: #ecf0f1; padding: 20px; border-radius: 8px;">
                        <div style="font-size: 14px; color: #7f8c8d; margin-bottom: 8px;">Aggregate Fbis Support NAV</div>
                        <div style="font-size: 28px; font-weight: bold; color: #e74c3c;">${fbis_nav:,.0f}</div>
                    </div>
                </div>
                
                <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db;">
                    <div style="font-size: 14px; color: #2c3e50; margin-bottom: 8px;">USD Distance to Support</div>
                    <div style="font-size: 32px; font-weight: bold; color: #27ae60;">${usd_distance:,.0f}</div>
                    <div style="font-size: 16px; color: #7f8c8d; margin-top: 5px;">({distance_pct:.2%} above support)</div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px; font-size: 18px;">Probability of Reaching Risk-off Level</h3>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                        <div style="background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center;">
                            <div style="font-size: 13px; color: #7f8c8d; margin-bottom: 5px;">1 Week</div>
                            <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">{stats_1w['probability']:.1%}</div>
                        </div>
                        <div style="background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center;">
                            <div style="font-size: 13px; color: #7f8c8d; margin-bottom: 5px;">1 Month</div>
                            <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">{stats_1m['probability']:.1%}</div>
                        </div>
                        <div style="background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center;">
                            <div style="font-size: 13px; color: #7f8c8d; margin-bottom: 5px;">3 Months</div>
                            <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">{stats_3m['probability']:.1%}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 40px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 30px;">
                    <div>
                        <div style="text-align: center;">
                            <div style="background-color: {bg_color_1w}; color: white; font-size: 48px; font-weight: bold; padding: 20px; border-radius: 10px; margin-bottom: 10px;">
                                {portfolio_score_1week:.1f}
                            </div>
                            <div style="background-color: {bg_color_1w}; color: white; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 16px;">
                                {risk_label_1w} RISK
                            </div>
                            <div style="margin-top: 10px; font-size: 14px; color: #34495e;">
                                Portfolio SATID Score - 1 Week Horizon
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <div style="text-align: center;">
                            <div style="background-color: {bg_color_1m}; color: white; font-size: 48px; font-weight: bold; padding: 20px; border-radius: 10px; margin-bottom: 10px;">
                                {portfolio_score_1month:.1f}
                            </div>
                            <div style="background-color: {bg_color_1m}; color: white; font-weight: bold; padding: 12px; border-radius: 8px; font-size: 16px;">
                                {risk_label_1m} RISK
                            </div>
                            <div style="margin-top: 10px; font-size: 14px; color: #34495e;">
                                Portfolio SATID Score - 1 Month Horizon
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h2 style="color: #2c3e50; margin-bottom: 20px; font-size: 22px; text-align: center;">Portfolio Risk Exposure</h2>
                    {portfolio_risk_exposure_html}
                </div>
            </div>
        </div>
    </div>
    
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
                font: {{ size: 18 }}
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
            font: {{ family: 'Arial, sans-serif', size: 12 }},
            showlegend: true,
            legend: {{ x: 0.01, y: 0.99 }}
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
    print("PORTFOLIO RISK DASHBOARD - CORRECTED VERSION")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load data
        print("[1/7] Loading portfolio allocations...")
        allocations = get_active_etfs_with_allocations(PORTFOLIO_FILE)
        print(f"   ✓ Found {len(allocations)} ETFs")
        
        print("[2/7] Loading FBIS parameters...")
        with open(FBIS_PARAMS_FILE, 'r') as f:
            fbis_params = json.load(f)
        print(f"   ✓ Loaded parameters for {len(fbis_params)} ETFs")
        
        # Calculate portfolio series
        print("[3/7] Calculating portfolio value and Fbis...")
        dates, portfolio_values, portfolio_fbis = calculate_portfolio_series(
            OHLC_FILE, allocations, fbis_params
        )
        current_value = portfolio_values[-1]
        fbis_value = portfolio_fbis[-1]
        print(f"   ✓ Current Value: {current_value:.4f}")
        print(f"   ✓ Fbis Level: {fbis_value:.4f}")
        
        # Calculate volatility and correlations
        print("[4/7] Calculating correlations and volatility...")
        tickers = list(allocations.keys())
        corr_matrix = calculate_correlation_matrix(OHLC_FILE, tickers, weeks=13)
        individual_vols = calculate_individual_volatilities(OHLC_FILE, tickers, weeks=13)
        portfolio_vol = calculate_portfolio_volatility(allocations, corr_matrix, individual_vols)
        
        # Calculate statistics
        print("[5/7] Calculating risk statistics...")
        statistics, distance_pct = calculate_risk_statistics(
            current_value, fbis_value, portfolio_vol
        )
        
        # Load portfolio for exposure table
        print("[6/7] Calculating portfolio risk exposure...")
        allocations_exp, asset_classes, category_weights = load_portfolio_allocations(PORTFOLIO_FILE)
        df = pd.read_csv(OHLC_FILE, index_col=0, parse_dates=True)
        risk_data, asset_class_summary = calculate_portfolio_risk(
            df, allocations_exp, asset_classes, fbis_params, PORTFOLIO_VALUE
        )
        
        # Calculate SATID scores for display
        df_scoring = pd.read_csv(OHLC_FILE)
        df_scoring['Date'] = pd.to_datetime(df_scoring['Date'])
        df_scoring = df_scoring.sort_values('Date').reset_index(drop=True)
        
        etf_results = []
        for ticker in allocations.keys():
            close_col = f"{ticker}_close"
            if close_col not in df_scoring.columns:
                continue
            prices = df_scoring[close_col].values
            result = analyze_etf_risk(ticker, prices, fbis_params)
            etf_results.append(result)
        
        portfolio_score_1week, portfolio_score_1month = calculate_portfolio_satid_scores(
            etf_results, allocations
        )
        
        # Generate HTML
        print("[7/7] Generating HTML dashboard...")
        generate_dashboard_html(
            dates, portfolio_values, portfolio_fbis, statistics,
            current_value, fbis_value, distance_pct,
            risk_data, asset_class_summary, category_weights,
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
