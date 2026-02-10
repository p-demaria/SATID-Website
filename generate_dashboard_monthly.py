#!/usr/bin/env python3
"""
Dashboard Generator - Monthly Data Version
Generates an interactive HTML dashboard from portfolio_results_monthly.json
"""

import json
import math
from datetime import datetime

def create_pie_svg(allocations):
    """Create SVG pie chart from allocations"""
    colors = {
        'Cash': '#9fc5e8',
        'Fixed Income': '#6fa8dc',
        'Equity': '#e06666',
        'Alternatives': '#f6b26b'
    }
    
    # Calculate category totals
    categories = {'Cash': 0, 'Fixed Income': 0, 'Equity': 0, 'Alternatives': 0}
    
    etf_categories = {
        'BIL': 'Cash',
        'SHY': 'Fixed Income', 'IGSB': 'Fixed Income', 'IGIB': 'Fixed Income',
        'LQD': 'Fixed Income', 'SHYG': 'Fixed Income', 'HYG': 'Fixed Income',
        'EMB': 'Fixed Income', 'CEMB': 'Fixed Income',
        'SPY': 'Equity', 'QQQ': 'Equity', 'IJK': 'Equity', 'IWM': 'Equity',
        'VGK': 'Equity', 'EWU': 'Equity', 'EWJ': 'Equity', 'EEM': 'Equity',
        'AAXJ': 'Equity', 'MCHI': 'Equity', 'INDA': 'Equity',
        'GLD': 'Alternatives', 'FTLS': 'Alternatives', 'QAI': 'Alternatives', 'WTMF': 'Alternatives'
    }
    
    for ticker, weight in allocations.items():
        if ticker in etf_categories:
            categories[etf_categories[ticker]] += weight
    
    # Create SVG paths
    svg_parts = []
    start_angle = -90  # Start at top
    cx, cy = 100, 100
    outer_r = 80
    inner_r = 45
    
    for category, percentage in categories.items():
        if percentage > 0:
            angle = percentage * 360
            end_angle = start_angle + angle
            
            # Convert to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            # Calculate outer arc points
            x1_outer = cx + outer_r * math.cos(start_rad)
            y1_outer = cy + outer_r * math.sin(start_rad)
            x2_outer = cx + outer_r * math.cos(end_rad)
            y2_outer = cy + outer_r * math.sin(end_rad)
            
            # Calculate inner arc points
            x1_inner = cx + inner_r * math.cos(end_rad)
            y1_inner = cy + inner_r * math.sin(end_rad)
            x2_inner = cx + inner_r * math.cos(start_rad)
            y2_inner = cy + inner_r * math.sin(start_rad)
            
            # Large arc flag
            large_arc = 1 if angle > 180 else 0
            
            # Create path
            path = f'M {x1_outer:.2f},{y1_outer:.2f} '
            path += f'A {outer_r},{outer_r} 0 {large_arc},1 {x2_outer:.2f},{y2_outer:.2f} '
            path += f'L {x1_inner:.2f},{y1_inner:.2f} '
            path += f'A {inner_r},{inner_r} 0 {large_arc},0 {x2_inner:.2f},{y2_inner:.2f} '
            path += 'Z'
            
            svg_parts.append(f'<path d="{path}" fill="{colors[category]}" stroke="white" stroke-width="2"/>')
            
            start_angle = end_angle
    
    svg = f'<svg viewBox="0 0 200 200" style="width: 100%; max-width: 180px; height: auto; margin: 0 auto; display: block;">{"".join(svg_parts)}</svg>'
    return svg

def format_recovery_time(months):
    """Format recovery time in months"""
    if months is None:
        return "Not recovered"
    return f"{months} months"

def generate_dashboard(results_file='portfolio_results_monthly.json', output_file='portfolio_dashboard.html'):
    """Generate HTML dashboard from results"""
    
    # Load results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Portfolio configurations
    portfolio_order = [
        'Conservative Income',
        'Conservative Balanced',
        'Balanced Portfolio',
        'Growth Portfolio',
        'Aggressive Growth Portfolio'
    ]
    
    portfolio_colors = {
        'Conservative Income': '#6b8fc7',
        'Conservative Balanced': '#f4c430',
        'Balanced Portfolio': '#5a8f5a',
        'Growth Portfolio': '#e74c3c',
        'Aggressive Growth Portfolio': '#8b0000'
    }
    
    # Calculate category totals for each portfolio
    def get_category_totals(allocations):
        categories = {'Cash': 0, 'Fixed Income': 0, 'Equity': 0, 'Alternatives': 0}
        etf_categories = {
            'BIL': 'Cash',
            'SHY': 'Fixed Income', 'IGSB': 'Fixed Income', 'IGIB': 'Fixed Income',
            'LQD': 'Fixed Income', 'SHYG': 'Fixed Income', 'HYG': 'Fixed Income',
            'EMB': 'Fixed Income', 'CEMB': 'Fixed Income',
            'SPY': 'Equity', 'QQQ': 'Equity', 'IJK': 'Equity', 'IWM': 'Equity',
            'VGK': 'Equity', 'EWU': 'Equity', 'EWJ': 'Equity', 'EEM': 'Equity',
            'AAXJ': 'Equity', 'MCHI': 'Equity', 'INDA': 'Equity',
            'GLD': 'Alternatives', 'FTLS': 'Alternatives', 'QAI': 'Alternatives', 'WTMF': 'Alternatives'
        }
        for ticker, weight in allocations.items():
            if ticker in etf_categories:
                categories[etf_categories[ticker]] += weight
        return categories
    
    # Start building HTML with SATID Master CSS
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATID Portfolio Analysis Dashboard - Monthly Data</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
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
   2. NAVIGATION STYLES
   ============================================ */

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
    max-width: 1800px;
    margin-left: auto;
    margin-right: auto;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* ============================================
   5. DASHBOARD-SPECIFIC STYLES
   ============================================ */

.update-info {
    background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
    border-left: 4px solid #2a5298;
    padding: 25px 30px;
    margin: 30px 0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    font-size: 1rem;
    color: #4a5568;
    line-height: 1.8;
}

.update-info strong {
    color: #1e3c72;
    font-weight: 600;
}

.section-title {
    font-size: 2rem;
    font-weight: 600;
    text-align: center;
    margin: 50px 0 30px 0;
    position: relative;
    color: #1e3c72;
    letter-spacing: -0.5px;
}

.section-title::after {
    content: '';
    display: block;
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #2a5298, #3d6cb9);
    margin: 15px auto 0;
    border-radius: 2px;
}

.portfolio-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin: 30px 0;
}

.portfolio-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s;
}

.portfolio-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.portfolio-header {
    padding: 15px;
    color: white;
    font-size: 15px;
    font-weight: 600;
    text-align: center;
    min-height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.portfolio-body {
    padding: 20px 15px;
}

.pie-container {
    margin: 15px 0;
}

.allocation-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    font-size: 14px;
    color: #4a5568;
}

.stat-box {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    font-size: 13px;
    color: #4a5568;
}

.value-box {
    background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
}

.value-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 13px;
    color: #4a5568;
}

.comparison-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin: 30px 0;
}

.comparison-card {
    background: white;
    border-radius: 12px;
    padding: 25px 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s;
}

.comparison-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.comparison-card h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e3c72;
    margin-bottom: 20px;
    text-align: center;
    padding-bottom: 15px;
    border-bottom: 2px solid #e9ecef;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    font-size: 13px;
    border-bottom: 1px solid #f0f0f0;
}

.metric-row:last-child {
    border-bottom: none;
}

.metric-label {
    color: #4a5568;
    font-weight: 400;
}

.metric-value {
    font-weight: 600;
    color: #2c3e50;
}

.positive {
    color: #27ae60;
}

.negative {
    color: #e74c3c;
}

/* ============================================
   6. FOOTER
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
    margin: 8px 0;
}

footer code {
    background: rgba(255,255,255,0.15);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: 'Courier New', monospace;
}

/* ============================================
   7. RESPONSIVE DESIGN
   ============================================ */

@media (max-width: 1400px) {
    .portfolio-grid,
    .comparison-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 1024px) {
    .portfolio-grid,
    .comparison-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
    }
    
    .content-page {
        padding: 40px 25px !important;
    }
    
    .portfolio-grid,
    .comparison-grid {
        grid-template-columns: 1fr;
    }
}

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
    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Portfolio Analysis Dashboard</h1>
            <p class="hero-subtitle">Professional Portfolio Analytics & Performance Metrics</p>
        </div>
    </section>

    <!-- Main Content -->
    <div class="container">
        <div class="content-page">
            <button onclick="history.back()" class="return-button">← Back</button>
            <div class="update-info">
                <strong>Data Updated:</strong> """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """<br>
                <strong>Analysis Period:</strong> 10 Years (Monthly Data)<br>
                <strong>Data Source:</strong> Yahoo Finance - Monthly Adjusted Close Prices
            </div>
            
            <h2 class="section-title">Model Portfolio Profiles</h2>
            <div class="portfolio-grid">
"""
    
    # Generate portfolio cards
    for portfolio_name in portfolio_order:
        if portfolio_name not in results:
            continue
            
        stats = results[portfolio_name]
        allocations = stats['allocations']
        categories = get_category_totals(allocations)
        
        # Shorten portfolio name for display
        display_name = portfolio_name.replace(' Portfolio', '')
        
        html += f"""
                <div class="portfolio-card">
                    <div class="portfolio-header" style="background: {portfolio_colors[portfolio_name]};">
                        {display_name}
                    </div>
                    <div class="portfolio-body">
                        <div class="pie-container">
                            {create_pie_svg(allocations)}
                        </div>

                        <div class="allocation-item">
                            <span><strong>Cash</strong></span>
                            <span>{categories['Cash']*100:.1f}%</span>
                        </div>

                        <div class="allocation-item">
                            <span><strong>Fixed Income</strong></span>
                            <span>{categories['Fixed Income']*100:.1f}%</span>
                        </div>

                        <div class="allocation-item">
                            <span><strong>Equity</strong></span>
                            <span>{categories['Equity']*100:.1f}%</span>
                        </div>

                        <div class="allocation-item">
                            <span><strong>Alternatives</strong></span>
                            <span>{categories['Alternatives']*100:.1f}%</span>
                        </div>

                        <div class="allocation-item" style="margin-top: 10px; padding-top: 10px; border-top: 2px solid #e0e0e0;">
                            <span><strong>Total</strong></span>
                            <span><strong>100.0%</strong></span>
                        </div>
                        
                        <div class="stat-box">
                            <div class="stat-row">
                                <span>Return 10 Yr</span>
                                <strong class="positive">{stats['annualized_return']*100:.2f}%</strong>
                            </div>
                            <div class="stat-row">
                                <span>Volatility (Annual Std Dev)</span>
                                <strong>{stats['volatility']*100:.2f}%</strong>
                            </div>
                            <div class="stat-row">
                                <span>Max Drawdown</span>
                                <strong class="negative">{stats['max_drawdown']*100:.2f}%</strong>
                            </div>
                        </div>
                        
                        <div class="value-box">
                            <div class="value-row">
                                <span>Initial Value</span>
                                <span>${stats['initial_value']:.2f}</span>
                            </div>
                            <div class="value-row">
                                <span><strong>Final Value</strong></span>
                                <span><strong>${stats['final_value']:.2f}</strong></span>
                            </div>
                        </div>
                    </div>
                </div>
"""
    
    html += """
            </div>

            <h2 class="section-title">Portfolio Comparison</h2>
            <div class="comparison-grid">
"""
    
    # Generate comparison cards
    for portfolio_name in portfolio_order:
        if portfolio_name not in results:
            continue
            
        stats = results[portfolio_name]
        display_name = portfolio_name.replace(' Portfolio', '')
        
        html += f"""
                <div class="comparison-card">
                    <h3>{display_name}</h3>
                    <div class="metric-row">
                        <span class="metric-label">Annualized Return</span>
                        <span class="metric-value positive">{stats['annualized_return']*100:.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Volatility (Annual Std Dev)</span>
                        <span class="metric-value">{stats['volatility']*100:.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Max Drawdown</span>
                        <span class="metric-value negative">{stats['max_drawdown']*100:.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Recovery Time</span>
                        <span class="metric-value">{format_recovery_time(stats.get('time_to_recovery_months'))}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Best Month <span style="font-size: 11px; color: #999;">({stats.get('best_month_date', 'N/A')})</span></span>
                        <span class="metric-value positive">{stats['best_month']*100:.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Worst Month <span style="font-size: 11px; color: #999;">({stats.get('worst_month_date', 'N/A')})</span></span>
                        <span class="metric-value negative">{stats['worst_month']*100:.2f}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Positive Months</span>
                        <span class="metric-value">{stats['win_rate']*100:.1f}%</span>
                    </div>
                    <div class="metric-row" style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #1e3c72;">
                        <span class="metric-label"><strong>Final Value ($100)</strong></span>
                        <span class="metric-value positive"><strong>${stats['final_value']:.2f}</strong></span>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p><strong>SATID Portfolio Analysis Dashboard</strong></p>
        <p>Generated with monthly adjusted close data from Yahoo Finance</p>
        <p style="margin-top: 10px;">To update: <code>python3 run_analysis_monthly.py</code></p>
    </footer>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✓ Dashboard generated: {output_file}")
    print(f"  Open this file in your browser to view the results!")

def main():
    """Main function"""
    print("="*60)
    print("DASHBOARD GENERATOR - MONTHLY DATA")
    print("="*60)
    print()
    
    generate_dashboard()
    
    print()
    print("="*60)
    print("DASHBOARD GENERATION COMPLETE!")
    print("="*60)

if __name__ == '__main__':
    main()
