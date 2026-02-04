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
                        <span>Return 10 Yr</span>
                        <strong class="positive">{stats['annualized_return']*100:.2f}%</strong>
                    </div>
                    <div class="stat-row-allocation">
                        <span>Standard Deviation 10Yr</span>
                        <strong>{stats['volatility']*100:.2f}%</strong>
                    </div>
                </div>
                
                <div class="value-box">
                    <div class="value-row">
                        <span>Initial Value</span>
                        <span>$ {stats['initial_value']:.1f}</span>
                    </div>
                    <div class="value-row">
                        <span><strong>Final Value</strong></span>
                        <span><strong>$ {stats['final_value']:.1f}</strong></span>
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
    
    # Map portfolio names to their keys in the JSON
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
    <title>Model Portfolio Allocations</title>
    <style>
        /* ============================================
           SATID Website - COMPLETE MASTER STYLESHEET
           Embedded version for Model Portfolios
           ============================================ */
        
        /* 1. BASE STYLES & RESET */
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
            min-height: 100vh;
            padding: 20px;
        }}
        
        /* 2. MAIN CONTAINER */
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}
        
        /* 3. HEADER */
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d6cb9 100%);
            color: white;
            padding: 40px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1" fill="rgba(255,255,255,0.03)"/></svg>') repeat;
            opacity: 0.5;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
            position: relative;
            z-index: 1;
        }}
        
        .header p {{
            font-size: 1.2rem;
            font-weight: 300;
            letter-spacing: 0.5px;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }}
        
        /* 4. CONTENT AREA */
        .content {{
            padding: 50px 40px;
            background: #f8f9fa;
        }}
        
        /* 5. PORTFOLIO GRID */
        .portfolio-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 25px;
            margin: 30px 0;
        }}
        
        /* 6. PORTFOLIO CARDS */
        .portfolio-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: 1px solid #e2e8f0;
        }}
        
        .portfolio-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }}
        
        .portfolio-header {{
            padding: 18px 15px;
            color: white;
            font-size: 15px;
            font-weight: 600;
            text-align: center;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            letter-spacing: 0.3px;
        }}
        
        .portfolio-body {{
            padding: 20px;
            background: white;
        }}
        
        /* 7. ASSET CLASS HEADERS */
        .asset-class-header {{
            display: flex;
            justify-content: space-between;
            padding: 10px 12px;
            margin-top: 12px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.3px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* 8. ALLOCATION ITEMS */
        .allocation-item {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 8px;
            padding: 8px 12px;
            border-bottom: 1px solid #e9ecef;
            font-size: 12px;
            align-items: center;
            color: #4a5568;
            transition: background 0.2s ease;
        }}
        
        .allocation-item:hover {{
            background: #f8f9fa;
        }}
        
        .allocation-item span:nth-child(2) {{
            text-align: center;
            font-weight: 500;
        }}
        
        .allocation-item span:nth-child(3) {{
            text-align: right;
            font-weight: 600;
            color: #2a5298;
        }}
        
        /* 9. ALLOCATION TOTAL */
        .allocation-total {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 8px;
            padding: 12px;
            margin-top: 12px;
            border-top: 2px solid #1e3c72;
            font-size: 13px;
            font-weight: 700;
            background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
            border-radius: 6px;
            color: #1e3c72;
        }}
        
        .allocation-total span:nth-child(3) {{
            text-align: right;
        }}
        
        /* 10. STAT BOXES */
        .stat-box-allocation {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 18px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-row-allocation {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .value-box {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .value-row {{
            display: flex;
            justify-content: space-between;
            margin: 7px 0;
            font-size: 13px;
            font-weight: 500;
        }}
        
        .positive {{
            color: #90EE90;
            font-weight: 600;
        }}
        
        /* 11. FOOTER */
        footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 35px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1" fill="rgba(255,255,255,0.03)"/></svg>') repeat;
            opacity: 0.5;
        }}
        
        footer p {{
            margin: 5px 0;
            font-weight: 400;
            letter-spacing: 0.3px;
            position: relative;
            z-index: 1;
        }}
        
        footer p strong {{
            font-weight: 600;
            font-size: 1.1rem;
        }}
        
        /* 12. RESPONSIVE DESIGN */
        @media (max-width: 1400px) {{
            .portfolio-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
            
            .content {{
                padding: 40px 30px;
            }}
        }}
        
        @media (max-width: 900px) {{
            .portfolio-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .header p {{
                font-size: 1rem;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
        }}
        
        @media (max-width: 600px) {{
            .portfolio-grid {{
                grid-template-columns: 1fr;
            }}
            
            body {{
                padding: 10px;
            }}
            
            .container {{
                border-radius: 12px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .content {{
                padding: 25px 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Model Portfolio Allocations</h1>
            <p>Detailed Asset Allocation Breakdown</p>
        </div>
        
        <div class="content">
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
        
        <footer>
            <p><strong>Model Portfolio Allocations</strong></p>
            <p>Comprehensive breakdown of all portfolio holdings</p>
        </footer>
    </div>
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
