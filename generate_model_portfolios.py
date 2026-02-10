"""
Model Portfolio Allocations Generator
Creates a detailed view of all portfolio allocations with statistics
"""

import json
from datetime import datetime

# Model Portfolios Definition with detailed allocations
MODEL_PORTFOLIOS = {
    "Conservative Income": {
        "color": "#6b8fc7",
        "allocations": {
            "Cash": [
                ("BIL", "1 to 3 month", 0.20)
            ],
            "Fixed Income": [
                ("SHY", "UST 1 to 3 Years", 0.04),
                ("IGSB", "Investment Grade 1 to 5 Years", 0.0533),
                ("IGIB", "Investment Grade 5 to 10 Years", 0.0933),
                ("LQD", "Investment Grade Bonds", 0.2667),
                ("SHYG", "High Yield 0 to 5 Years", 0.08),
                ("HYG", "High Yield Bonds", 0.1067),
                ("EMB", "Emerging Market Bonds", 0.08),
                ("CEMB", "Corporate Emerging Markets", 0.08)
            ],
            "Equity": [
                ("SPY", "US Equity Core", 0.00),
                ("QQQ", "Nasdaq", 0.00),
                ("IJK", "US MidCap Growth", 0.00),
                ("IWM", "US SmallCap", 0.00),
                ("VGK", "European Equity", 0.00),
                ("EWU", "UK Equity", 0.00),
                ("EWJ", "Japanese Equity", 0.00),
                ("EEM", "Emerging Market Equity", 0.00),
                ("AAXJ", "Asia ex Japan Equity", 0.00),
                ("MCHI", "China", 0.00),
                ("INDA", "India", 0.00)
            ],
            "Alternative Investments": [
                ("GLD", "Gold", 0.00),
                ("FTLS", "Equity Long/Short", 0.00),
                ("QAI", "Multi-Strategy", 0.00),
                ("WTMF", "CTA", 0.00)
            ]
        }
    },
    "Conservative Balanced": {
        "color": "#f4c430",
        "allocations": {
            "Cash": [
                ("BIL", "1 to 3 month", 0.05)
            ],
            "Fixed Income": [
                ("SHY", "UST 1 to 3 Years", 0.03125),
                ("IGSB", "Investment Grade 1 to 5 Years", 0.04167),
                ("IGIB", "Investment Grade 5 to 10 Years", 0.07292),
                ("LQD", "Investment Grade Bonds", 0.20833),
                ("SHYG", "High Yield 0 to 5 Years", 0.0625),
                ("HYG", "High Yield Bonds", 0.08333),
                ("EMB", "Emerging Market Bonds", 0.0625),
                ("CEMB", "Corporate Emerging Markets", 0.0625)
            ],
            "Equity": [
                ("SPY", "US Equity Core", 0.072),
                ("QQQ", "Nasdaq", 0.036),
                ("IJK", "US MidCap Growth", 0.027),
                ("IWM", "US SmallCap", 0.00),
                ("VGK", "European Equity", 0.027),
                ("EWU", "UK Equity", 0.009),
                ("EWJ", "Japanese Equity", 0.018),
                ("EEM", "Emerging Market Equity", 0.018),
                ("AAXJ", "Asia ex Japan Equity", 0.00),
                ("MCHI", "China", 0.00),
                ("INDA", "India", 0.00)
            ],
            "Alternative Investments": [
                ("GLD", "Gold", 0.025),
                ("FTLS", "Equity Long/Short", 0.025),
                ("QAI", "Multi-Strategy", 0.025),
                ("WTMF", "CTA", 0.025)
            ]
        }
    },
    "Balanced Portfolio": {
        "color": "#5a8f5a",
        "allocations": {
            "Cash": [
                ("BIL", "1 to 3 month", 0.05)
            ],
            "Fixed Income": [
                ("SHY", "UST 1 to 3 Years", 0.02),
                ("IGSB", "Investment Grade 1 to 5 Years", 0.02667),
                ("IGIB", "Investment Grade 5 to 10 Years", 0.04667),
                ("LQD", "Investment Grade Bonds", 0.13333),
                ("SHYG", "High Yield 0 to 5 Years", 0.04),
                ("HYG", "High Yield Bonds", 0.05333),
                ("EMB", "Emerging Market Bonds", 0.04),
                ("CEMB", "Corporate Emerging Markets", 0.04)
            ],
            "Equity": [
                ("SPY", "US Equity Core", 0.128),
                ("QQQ", "Nasdaq", 0.064),
                ("IJK", "US MidCap Growth", 0.048),
                ("IWM", "US SmallCap", 0.00),
                ("VGK", "European Equity", 0.048),
                ("EWU", "UK Equity", 0.016),
                ("EWJ", "Japanese Equity", 0.032),
                ("EEM", "Emerging Market Equity", 0.032),
                ("AAXJ", "Asia ex Japan Equity", 0.00),
                ("MCHI", "China", 0.00),
                ("INDA", "India", 0.00)
            ],
            "Alternative Investments": [
                ("GLD", "Gold", 0.0375),
                ("FTLS", "Equity Long/Short", 0.0375),
                ("QAI", "Multi-Strategy", 0.0375),
                ("WTMF", "CTA", 0.0375)
            ]
        }
    },
    "Growth Portfolio": {
        "color": "#e74c3c",
        "allocations": {
            "Cash": [
                ("BIL", "1 to 3 month", 0.00)
            ],
            "Fixed Income": [
                ("SHY", "UST 1 to 3 Years", 0.01),
                ("IGSB", "Investment Grade 1 to 5 Years", 0.01333),
                ("IGIB", "Investment Grade 5 to 10 Years", 0.02333),
                ("LQD", "Investment Grade Bonds", 0.06667),
                ("SHYG", "High Yield 0 to 5 Years", 0.02),
                ("HYG", "High Yield Bonds", 0.02667),
                ("EMB", "Emerging Market Bonds", 0.02),
                ("CEMB", "Corporate Emerging Markets", 0.02)
            ],
            "Equity": [
                ("SPY", "US Equity Core", 0.208),
                ("QQQ", "Nasdaq", 0.104),
                ("IJK", "US MidCap Growth", 0.078),
                ("IWM", "US SmallCap", 0.00),
                ("VGK", "European Equity", 0.078),
                ("EWU", "UK Equity", 0.026),
                ("EWJ", "Japanese Equity", 0.052),
                ("EEM", "Emerging Market Equity", 0.052),
                ("AAXJ", "Asia ex Japan Equity", 0.00),
                ("MCHI", "China", 0.00),
                ("INDA", "India", 0.00)
            ],
            "Alternative Investments": [
                ("GLD", "Gold", 0.0375),
                ("FTLS", "Equity Long/Short", 0.0375),
                ("QAI", "Multi-Strategy", 0.0375),
                ("WTMF", "CTA", 0.0375)
            ]
        }
    },
    "Aggressive Growth Portfolio": {
        "color": "#8b0000",
        "allocations": {
            "Cash": [
                ("BIL", "1 to 3 month", 0.00)
            ],
            "Fixed Income": [
                ("SHY", "UST 1 to 3 Years", 0.005),
                ("IGSB", "Investment Grade 1 to 5 Years", 0.00667),
                ("IGIB", "Investment Grade 5 to 10 Years", 0.01167),
                ("LQD", "Investment Grade Bonds", 0.03333),
                ("SHYG", "High Yield 0 to 5 Years", 0.01),
                ("HYG", "High Yield Bonds", 0.01333),
                ("EMB", "Emerging Market Bonds", 0.01),
                ("CEMB", "Corporate Emerging Markets", 0.01)
            ],
            "Equity": [
                ("SPY", "US Equity Core", 0.272),
                ("QQQ", "Nasdaq", 0.136),
                ("IJK", "US MidCap Growth", 0.102),
                ("IWM", "US SmallCap", 0.00),
                ("VGK", "European Equity", 0.102),
                ("EWU", "UK Equity", 0.034),
                ("EWJ", "Japanese Equity", 0.068),
                ("EEM", "Emerging Market Equity", 0.068),
                ("AAXJ", "Asia ex Japan Equity", 0.00),
                ("MCHI", "China", 0.00),
                ("INDA", "India", 0.00)
            ],
            "Alternative Investments": [
                ("GLD", "Gold", 0.0125),
                ("FTLS", "Equity Long/Short", 0.0125),
                ("QAI", "Multi-Strategy", 0.0125),
                ("WTMF", "CTA", 0.0125)
            ]
        }
    }
}

def load_portfolio_stats():
    """Load portfolio statistics from JSON"""
    with open('portfolio_results.json', 'r') as f:
        return json.load(f)

def generate_portfolio_card(portfolio_name, portfolio_info, stats):
    """Generate HTML for a single portfolio card"""
    color = portfolio_info["color"]
    allocations = portfolio_info["allocations"]
    
    html = f"""
        <div class="portfolio-card">
            <div class="portfolio-header" style="background: {color};">
                {portfolio_name}
            </div>
            <div class="portfolio-body">
"""
    
    # Generate allocation sections
    for asset_class, items in allocations.items():
        # Calculate total for asset class (including zeros)
        total_pct = sum(pct for _, _, pct in items) * 100
        
        html += f"""
                <div class="asset-class-header">
                    <strong>{asset_class}</strong>
                    <strong>{total_pct:.1f}%</strong>
                </div>
"""
        
        # Add individual items (including zeros)
        for ticker, description, pct in items:
            pct_display = f"{pct*100:.1f}%"
            html += f"""
                <div class="allocation-item">
                    <span>{description}</span>
                    <span>{ticker}</span>
                    <span>{pct_display}</span>
                </div>
"""
    
    # Add total
    html += f"""
                <div class="allocation-total">
                    <span><strong>Total</strong></span>
                    <span></span>
                    <span><strong>100.0%</strong></span>
                </div>
                
                <div class="stat-box-allocation">
                    <div class="stat-row-allocation">
                        <span>Annualized Return:</span>
                        <span class="positive">{stats['annualized_return']*100:.2f}%</span>
                    </div>
                    <div class="stat-row-allocation">
                        <span>Annual Volatility:</span>
                        <span>{stats['volatility']*100:.2f}%</span>
                    </div>
                    <div class="stat-row-allocation">
                        <span>Sharpe Ratio:</span>
                        <span class="positive">{stats['sharpe_ratio']:.2f}</span>
                    </div>
                    <div class="stat-row-allocation">
                        <span>Max Drawdown:</span>
                        <span>{stats['max_drawdown']*100:.2f}%</span>
                    </div>
                </div>
            </div>
        </div>
"""
    
    return html

def generate_html():
    """Generate complete HTML page"""
    # Load stats
    portfolio_results = load_portfolio_stats()
    
    # Map portfolio names to JSON keys
    name_map = {
        "Conservative Income": "Conservative Income",
        "Conservative Balanced": "Conservative Balanced",
        "Balanced Portfolio": "Balanced Portfolio",
        "Growth Portfolio": "Growth Portfolio",
        "Aggressive Growth Portfolio": "Aggressive Growth Portfolio"
    }
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Portfolio Allocations - SATID</title>
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>
    
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
           2. NAVIGATION STYLES
           ============================================ */

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
            max-width: 1600px;
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
           6. PORTFOLIO GRID & CARDS
           ============================================ */

        .portfolio-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 25px;
            margin: 40px 0;
        }}

        .portfolio-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .portfolio-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }}

        .portfolio-header {{
            padding: 20px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            min-height: 65px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .portfolio-body {{
            padding: 25px;
        }}

        .asset-class-header {{
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            margin-top: 15px;
            background: #1e3c72;
            color: white;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
        }}

        .allocation-item {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 10px;
            padding: 8px 15px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
            align-items: center;
        }}

        .allocation-item span:nth-child(2) {{
            text-align: center;
            font-weight: 500;
            color: #2c3e50;
        }}

        .allocation-item span:nth-child(3) {{
            text-align: right;
            font-weight: 600;
            color: #1e3c72;
        }}

        .allocation-total {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 10px;
            padding: 12px 15px;
            margin-top: 15px;
            border-top: 2px solid #2c3e50;
            font-size: 14px;
            font-weight: bold;
        }}

        .allocation-total span:nth-child(3) {{
            text-align: right;
        }}

        .stat-box-allocation {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}

        .stat-row-allocation {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 13px;
        }}

        .positive {{
            color: #90EE90;
            font-weight: 600;
        }}

        /* ============================================
           7. KEY POINTS & HIGHLIGHT BOXES
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
            margin: 8px 0;
        }}

        /* ============================================
           10. RESPONSIVE DESIGN
           ============================================ */

        @media (max-width: 1400px) {{
            .portfolio-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
            
            .content-page {{
                padding: 50px 30px 60px 30px !important;
            }}
        }}

        @media (max-width: 900px) {{
            .portfolio-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            .hero-subtitle {{
                font-size: 1.1rem;
            }}
        }}

        @media (max-width: 768px) {{
            .nav-menu {{
                flex-direction: column;
                gap: 0;
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
            
            .content-page {{
                padding: 40px 25px !important;
            }}
        }}

        @media (max-width: 600px) {{
            .portfolio-grid {{
                grid-template-columns: 1fr;
            }}
            
            .hero h1 {{
                font-size: 2rem;
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

        /* Return to Previous Page Button */
        .return-button {{
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
        }}

        .return-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(44, 95, 45, 0.4);
            background: linear-gradient(135deg, #4a7c59 0%, #5d9973 100%);
        }}
    </style>
</head>
<body>
    <!-- Main Container -->
    <div class="container">
        <div class="content-page">
            <button onclick="history.back()" class="return-button">← Back</button>
            <!-- Hero Section -->
            <div class="hero">
                <h1>📋 Model Portfolio Allocations</h1>
                <p class="hero-subtitle">Detailed Asset Allocation Breakdown Across Risk Profiles</p>
            </div>

            <!-- Portfolio Grid -->
            <div class="portfolio-grid">
"""
    
    # Generate cards for each portfolio
    for portfolio_name, portfolio_info in MODEL_PORTFOLIOS.items():
        data_key = name_map[portfolio_name]
        stats = portfolio_results[data_key]
        html += generate_portfolio_card(portfolio_name, portfolio_info, stats)
    
    html += """
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p><strong>SATID - Structured Approach To Investment Decisions</strong></p>
        <p>Professional Portfolio Risk Management Methodology</p>
        <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.8;">
            © 2024-2026 SATID Methodology. All rights reserved.
        </p>
    </footer>
</body>
</html>
"""
    
    return html

def main():
    """Main function"""
    print("=" * 60)
    print("MODEL PORTFOLIO ALLOCATIONS GENERATOR")
    print("=" * 60)
    
    print("\nGenerating HTML...")
    html = generate_html()
    
    print("Writing to file...")
    with open('model_portfolios.html', 'w') as f:
        f.write(html)
    
    print("\n✓ Model portfolios page generated successfully!")
    print("\nOpen 'model_portfolios.html' in your browser to view.")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
