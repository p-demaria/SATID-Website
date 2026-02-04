"""
SATID FBIS OPTIMIZER - Constrained Breakout-Based Optimization
===============================================================
Generates: Support_Levels_Interactive.html
          SATID_Fbis_Optimized_Parameters.json

This script:
1. Loads latest weekly price data from CSV
2. DETECTS TREND CHANGES using downtrend line breakout method
3. RUNS CONSTRAINED OPTIMIZATION with asset-class specific ranges
4. Saves optimized parameters to JSON file
5. Generates interactive HTML dashboard

Key Features:
- Automatic trend change detection (no arbitrary start dates)
- Asset-class constraints prevent extreme solutions
- Breach penalty = 3.0 (balanced - accepts breaches as signals)
- Charts: Price (black) from Jan 2020, Fbis (red dotted) from Sep 2022

Use this script when: You want to RE-OPTIMIZE support levels (monthly/quarterly)

Author: SATID Risk Management System
Date: December 2025
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from scipy import stats
import os

# ================================
# CONFIGURATION
# ================================
CSV_FILE = "SATID_portfolio_etf_data_weekly_ohlc.csv"
PARAMS_FILE = "SATID_Fbis_Optimized_Parameters.json"
OUTPUT_HTML = "Support_Levels_Interactive.html"

# Scoring parameters
SUPPORT_TEST_REWARD = 1.0
BREACH_PENALTY = 3.0  # Balanced penalty - accepts breaches as signals
TOUCH_TOLERANCE_PCT = 2.5

# ================================
# ASSET CLASS DEFINITIONS
# ================================
ASSET_CLASSES = {
    # Large Cap Equity
    'SPY': 'large_cap', 'VGK': 'large_cap', 'EWG': 'large_cap',
    'EWQ': 'large_cap', 'EWI': 'large_cap', 'EWJ': 'large_cap',
    
    # Growth/Tech
    'QQQ': 'growth_tech', 'XLK': 'growth_tech', 'XLY': 'growth_tech',
    
    # Bonds - High Yield
    'HYS': 'bond_hy', 'EMB': 'bond_hy', 'CEMB': 'bond_hy',
    
    # Bonds - Investment Grade
    'BIL': 'bond_ig', 'IGSB': 'bond_ig', 'IGIB': 'bond_ig', 'LQD': 'bond_ig',
    
    # Sector ETFs
    'XLV': 'sector', 'XLI': 'sector', 'XLC': 'sector', 'SMH': 'sector',
    'HEAL': 'sector', 'PPA': 'sector', 'PAVE': 'sector',
    
    # Emerging Markets
    'EWZ': 'emerging', 'INDA': 'emerging', 'MCHI': 'emerging',
    
    # Thematic/Alternative
    'ARKF': 'thematic', 'AIQ': 'thematic', 'EBIZ': 'thematic',
    'BKCH': 'thematic', 'QTUM': 'thematic', 'ARKX': 'thematic',
    'ESPO': 'thematic', 'GLD': 'thematic', 'FTLS': 'thematic',
    'QAI': 'thematic', 'WTMF': 'thematic',
}

# Asset-class constrained ranges (TIGHT - best results)
CONSTRAINTS = {
    'large_cap': {
        'ema_range': range(18, 25, 2),
        'shift_range': np.arange(-0.06, -0.015, 0.005),
    },
    'growth_tech': {
        'ema_range': range(18, 25, 2),
        'shift_range': np.arange(-0.07, -0.015, 0.005),
    },
    'bond_hy': {
        'ema_range': range(16, 21, 2),
        'shift_range': np.arange(-0.03, 0.005, 0.005),
    },
    'bond_ig': {
        'ema_range': range(16, 21, 2),
        'shift_range': np.arange(-0.02, 0.005, 0.005),
    },
    'sector': {
        'ema_range': range(18, 27, 2),
        'shift_range': np.arange(-0.08, -0.015, 0.005),
    },
    'emerging': {
        'ema_range': range(18, 25, 2),
        'shift_range': np.arange(-0.10, -0.025, 0.005),
    },
    'thematic': {
        'ema_range': range(20, 29, 2),
        'shift_range': np.arange(-0.12, -0.025, 0.005),
    },
}


# ================================
# TREND DETECTION FUNCTIONS
# ================================
def find_swing_highs(high_series, window=4):
    """Find swing highs (local maxima)"""
    swing_highs = []
    for i in range(window, len(high_series) - window):
        local_window = high_series.iloc[i-window:i+window+1]
        if high_series.iloc[i] == local_window.max():
            swing_highs.append({'date': high_series.index[i], 'price': high_series.iloc[i]})
    return swing_highs


def find_swing_lows(low_series, window=4):
    """Find swing lows (local minima)"""
    swing_lows = []
    for i in range(window, len(low_series) - window):
        local_window = low_series.iloc[i-window:i+window+1]
        if low_series.iloc[i] == local_window.min():
            swing_lows.append({'date': low_series.index[i], 'price': low_series.iloc[i]})
    return swing_lows


def identify_lower_highs(swing_highs, min_highs=2):
    """Identify sequence of lower highs (downtrend)"""
    if len(swing_highs) < min_highs:
        return []
    
    sequences = []
    for start_idx in range(len(swing_highs) - 1):
        sequence = [swing_highs[start_idx]]
        for j in range(start_idx + 1, len(swing_highs)):
            if swing_highs[j]['price'] < sequence[-1]['price']:
                sequence.append(swing_highs[j])
            else:
                break
        if len(sequence) >= min_highs:
            sequences.append(sequence)
    
    return max(sequences, key=len) if sequences else []


def create_downtrend_line(lower_highs):
    """Create linear resistance line connecting lower highs"""
    if len(lower_highs) < 2:
        return None
    
    first_date = lower_highs[0]['date']
    dates_numeric = [(h['date'] - first_date).days for h in lower_highs]
    prices = [h['price'] for h in lower_highs]
    
    slope, intercept, r_value, _, _ = stats.linregress(dates_numeric, prices)
    
    def resistance_at_date(date):
        return slope * (date - first_date).days + intercept
    
    return {'function': resistance_at_date, 'r_squared': r_value ** 2, 'first_date': first_date}


def detect_breakout(close_series, downtrend_line, start_after_date):
    """Detect when price breaks above downtrend line"""
    if downtrend_line is None:
        return None
    
    resistance_func = downtrend_line['function']
    check_data = close_series[close_series.index > start_after_date]
    
    for date in check_data.index:
        if check_data.loc[date] > resistance_func(date):
            return {'date': date, 'price': check_data.loc[date]}
    return None


def confirm_higher_low(low_series, breakout_info, pre_breakout_low, weeks_to_wait=12):
    """Confirm breakout with higher low"""
    if breakout_info is None:
        return None
    
    breakout_date = breakout_info['date']
    confirmation_window = low_series[
        (low_series.index > breakout_date) & 
        (low_series.index <= breakout_date + pd.DateOffset(weeks=weeks_to_wait))
    ]
    
    if len(confirmation_window) == 0:
        return None
    
    pullback_low_price = confirmation_window.min()
    if pullback_low_price > pre_breakout_low['price']:
        return {'date': confirmation_window.idxmin(), 'confirmed': True}
    return None


def detect_trend_change(close_series, high_series, low_series):
    """
    Detect trend change using downtrend line breakout method
    Returns: (trend_start_date, detection_info)
    """
    swing_highs = find_swing_highs(high_series, window=4)
    if len(swing_highs) < 2:
        return close_series.idxmin(), {}
    
    lower_highs = identify_lower_highs(swing_highs, min_highs=2)
    if len(lower_highs) < 2:
        return close_series.idxmin(), {}
    
    downtrend_line = create_downtrend_line(lower_highs)
    if downtrend_line is None:
        return close_series.idxmin(), {}
    
    breakout = detect_breakout(close_series, downtrend_line, lower_highs[-1]['date'])
    if breakout is None:
        return close_series.idxmin(), {}
    
    swing_lows = find_swing_lows(low_series, window=4)
    pre_breakout_lows = [l for l in swing_lows if l['date'] < breakout['date']]
    
    if not pre_breakout_lows:
        return breakout['date'], {'breakout': breakout}
    
    confirmation = confirm_higher_low(low_series, breakout, pre_breakout_lows[-1])
    
    if confirmation and confirmation['confirmed']:
        return confirmation['date'], {'breakout': breakout, 'confirmation': confirmation}
    return breakout['date'], {'breakout': breakout}


# ================================
# OPTIMIZATION CLASS
# ================================
class ConstrainedFbisOptimizer:
    """Optimize Fbis support level with constrained search"""
    
    def __init__(self, ticker, close_series, high_series, low_series):
        self.ticker = ticker
        self.close = close_series
        self.high = high_series
        self.low = low_series
        
        # Get asset class and constraints
        self.asset_class = ASSET_CLASSES.get(ticker, 'large_cap')
        self.constraints = CONSTRAINTS.get(self.asset_class, CONSTRAINTS['large_cap'])
        
        # Detect trend change
        self.trend_start, self.detection_info = detect_trend_change(
            close_series, high_series, low_series)
    
    def _calculate_ema(self, period):
        """Calculate EMA for given period"""
        return self.close.ewm(span=period, adjust=False).mean()
    
    def optimize(self):
        """
        Find optimal EMA period and vertical shift using constrained search
        
        Returns:
            dict with keys: period, shift, tests, breaches, score, trend_start
        """
        # Filter data for optimization period (from trend start)
        opt_mask = self.close.index >= self.trend_start
        opt_close = self.close[opt_mask]
        opt_low = self.low[opt_mask]
        
        if len(opt_close) < 10:
            return {
                'period': 20, 'shift': -0.05, 'tests': 0, 'breaches': 0, 
                'score': 0, 'trend_start': self.trend_start
            }
        
        best = None
        best_score = -999999
        
        # Grid search over CONSTRAINED parameter space
        for period in self.constraints['ema_range']:
            ema_full = self._calculate_ema(period)
            ema = ema_full[opt_mask]
            
            for shift in self.constraints['shift_range']:
                fbis_line = ema * (1 + shift)
                
                support_tests = 0
                breaches = 0
                
                # Evaluate each week
                for i in range(len(opt_close)):
                    fbis_level = fbis_line.iloc[i]
                    low_price = opt_low.iloc[i]
                    close_price = opt_close.iloc[i]
                    
                    distance_pct = ((low_price - fbis_level) / fbis_level) * 100
                    
                    # Support test: low touches within tolerance AND close holds above
                    if -TOUCH_TOLERANCE_PCT <= distance_pct <= TOUCH_TOLERANCE_PCT:
                        if close_price >= fbis_level:
                            support_tests += 1
                    # Breach: close finishes below Fbis
                    elif close_price < fbis_level:
                        breaches += 1
                
                # Calculate score
                score = (support_tests * SUPPORT_TEST_REWARD) - (breaches * BREACH_PENALTY)
                
                # Track best parameters
                if score > best_score:
                    best_score = score
                    best = {
                        'period': period,
                        'shift': shift,
                        'tests': support_tests,
                        'breaches': breaches,
                        'score': score,
                        'trend_start': self.trend_start,
                        'asset_class': self.asset_class
                    }
        
        return best or {
            'period': 20, 'shift': -0.05, 'tests': 0, 'breaches': 0, 
            'score': 0, 'trend_start': self.trend_start
        }


# ================================
# DATA LOADING
# ================================
def load_etf_prices(csv_file):
    """Load weekly OHLC price data for all ETFs"""
    print(f"📊 Loading price data from {csv_file}...")
    df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    
    # Ensure index is DatetimeIndex and remove timezone
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, utc=True)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    
    # Extract unique tickers
    tickers = [col.replace('_close', '') for col in df.columns if col.endswith('_close')]
    print(f"  ✓ Loaded {len(tickers)} ETFs")
    print(f"  ✓ Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"  ✓ Total weeks: {len(df)}")
    
    return df, tickers


# ================================
# OPTIMIZATION RUNNER
# ================================
def optimize_all_etfs(df, tickers):
    """Run constrained optimization for all ETFs"""
    print(f"\n🔍 Running CONSTRAINED BREAKOUT optimization for {len(tickers)} ETFs...")
    print(f"   Method: Automatic trend detection + asset-class constraints")
    print(f"   Breach penalty: {BREACH_PENALTY} (accepts breaches as signals)\n")
    
    params = {}
    
    for idx, ticker in enumerate(tickers, 1):
        print(f"[{idx}/{len(tickers)}] {ticker}")
        
        close_col = f"{ticker}_close"
        high_col = f"{ticker}_high"
        low_col = f"{ticker}_low"
        
        if close_col not in df.columns or high_col not in df.columns or low_col not in df.columns:
            print(f"  ⚠ Warning: Missing data columns")
            params[ticker] = {'period': 20, 'shift': -0.05}
            continue
        
        close_series = df[close_col].dropna()
        high_series = df[high_col].dropna()
        low_series = df[low_col].dropna()
        
        if len(close_series) < 52:
            print(f"  ⚠ Warning: Less than 1 year of data")
            params[ticker] = {'period': 20, 'shift': -0.05}
            continue
        
        # Run constrained optimization
        optimizer = ConstrainedFbisOptimizer(ticker, close_series, high_series, low_series)
        result = optimizer.optimize()
        
        # Print results
        asset_class = result.get('asset_class', 'unknown')
        trend_start = result['trend_start'].strftime('%Y-%m-%d')
        print(f"  Class: {asset_class} | Trend from: {trend_start}")
        print(f"  EMA({result['period']}) shift={result['shift']:.3f} | Tests={result['tests']} Breaches={result['breaches']} Score={result['score']:.1f}")
        
        params[ticker] = {
            'period': result['period'],
            'shift': result['shift']
        }
    
    print(f"\n  ✓ Optimization complete for {len(params)} ETFs")
    return params


# ================================
# CHART DATA GENERATION
# ================================
def generate_chart_data_js(df, tickers, params):
    """Generate JavaScript with all chart data"""
    
    print(f"\n📈 Generating chart data for {len(tickers)} ETFs...")
    
    js_code = "// Chart data for all ETFs\n"
    js_code += "const chartData = {};\n"
    js_code += "const optimizedParams = {};\n\n"
    
    for ticker in tickers:
        close_col = f"{ticker}_close"
        if close_col not in df.columns:
            continue
        
        prices = df[close_col].dropna()
        dates = [d.strftime('%Y-%m-%d') for d in prices.index]
        close_values = prices.tolist()
        
        period = params.get(ticker, {}).get('period', 20)
        shift = params.get(ticker, {}).get('shift', -0.05)
        
        js_code += f"chartData['{ticker}'] = {{\n"
        js_code += f"    dates: {json.dumps(dates)},\n"
        js_code += f"    close: {json.dumps(close_values)}\n"
        js_code += f"}};\n\n"
        
        js_code += f"optimizedParams['{ticker}'] = {{\n"
        js_code += f"    period: {period},\n"
        js_code += f"    shift: {shift}\n"
        js_code += f"}};\n\n"
    
    print(f"  ✓ Generated chart data")
    return js_code


def generate_chart_html(ticker, params):
    """Generate HTML for a single chart with controls"""
    
    period = params.get(ticker, {}).get('period', 20)
    shift = params.get(ticker, {}).get('shift', -0.05)
    shift_pct = shift * 100
    
    html = f"""
    <!-- {ticker} Chart -->
    <div class="chart-section">
        <h2>{ticker}</h2>
        
        <div class="controls">
            <div class="control-group">
                <label for="{ticker}_period">EMA Period: <span id="{ticker}_period_value">{period}</span></label>
                <input type="range" id="{ticker}_period" min="8" max="50" value="{period}" step="1">
            </div>
            
            <div class="control-group">
                <label for="{ticker}_shift">Vertical Shift: <span id="{ticker}_shift_value">{shift_pct:.1f}%</span></label>
                <input type="range" id="{ticker}_shift" min="-20" max="5" value="{shift_pct:.1f}" step="0.1">
            </div>
        </div>
        
        <div id="{ticker}_chart" class="chart-display"></div>
    </div>
    
    <script>
    (function() {{
        const ticker = '{ticker}';
        const chartDiv = document.getElementById(ticker + '_chart');
        const periodSlider = document.getElementById(ticker + '_period');
        const shiftSlider = document.getElementById(ticker + '_shift');
        const periodValue = document.getElementById(ticker + '_period_value');
        const shiftValue = document.getElementById(ticker + '_shift_value');
        
        // Store current values globally for saving
        window['current_period_' + ticker] = {period};
        window['current_shift_' + ticker] = {shift};
        
        function updateChart() {{
            const period = parseInt(periodSlider.value);
            const shift = parseFloat(shiftSlider.value) / 100;
            
            periodValue.textContent = period;
            shiftValue.textContent = (shift * 100).toFixed(1) + '%';
            
            window['current_period_' + ticker] = period;
            window['current_shift_' + ticker] = shift;
            
            const dates = chartData[ticker].dates;
            const close = chartData[ticker].close;
            const ema = calculateEMA(close, period);
            const fbis = ema.map(e => e * (1 + shift));
            
            // Filter data for chart display (from January 2020)
            const chartStartIdx = dates.findIndex(d => d >= '2020-01-01');
            const displayDates = dates.slice(chartStartIdx);
            const displayClose = close.slice(chartStartIdx);
            
            // Filter Fbis line (from September 2022)
            const fbisStartIdx = dates.findIndex(d => d >= '2022-09-01');
            const fbisDates = dates.slice(fbisStartIdx);
            const displayFbis = fbis.slice(fbisStartIdx);
            
            const traces = [
                {{
                    x: displayDates,
                    y: displayClose,
                    name: 'Price',
                    type: 'scatter',
                    line: {{ color: 'black', width: 2.5 }}
                }},
                {{
                    x: fbisDates,
                    y: displayFbis,
                    name: `Fbis (EMA${{period}} ${{(shift*100).toFixed(1)}}%)`,
                    type: 'scatter',
                    line: {{ color: 'red', width: 2, dash: 'dot' }}
                }}
            ];
            
            const layout = {{
                title: `${{ticker}} - Adjustable Support (EMA${{period}} @ ${{(shift*100).toFixed(1)}}%)`,
                xaxis: {{ title: 'Date', type: 'date' }},
                yaxis: {{ title: 'Price ($)' }},
                hovermode: 'x unified',
                showlegend: true,
                legend: {{ x: 0, y: 1 }},
                height: 480,
                margin: {{ l: 60, r: 30, t: 40, b: 40 }}
            }};
            
            Plotly.newPlot(chartDiv, traces, layout, {{responsive: true}});
        }}
        
        periodSlider.addEventListener('input', updateChart);
        shiftSlider.addEventListener('input', updateChart);
        
        updateChart();
    }})();
    </script>
"""
    
    return html


# ================================
# HTML GENERATION
# ================================
def generate_html(df, tickers, params):
    """Generate complete standalone HTML"""
    
    print(f"\n🔨 Generating HTML...")
    
    chart_data_js = generate_chart_data_js(df, tickers, params)
    
    # Read the SATID master CSS
    satid_css = """/* ============================================
   SATID Website - COMPLETE MASTER STYLESHEET
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

.container {
    max-width: 100% !important;
    margin: -60px auto 60px;
    padding: 0 10px !important;
    position: relative;
    z-index: 2;
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

/* Chart-specific styles */
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
    height: 8px;
    border-radius: 5px;
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
    box-shadow: 0 2px 4px rgba(42, 82, 152, 0.3);
}

.control-group input[type="range"]::-webkit-slider-thumb:hover {
    background: #1e3c72;
    transform: scale(1.1);
}

.control-group input[type="range"]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #2a5298;
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 4px rgba(42, 82, 152, 0.3);
}

.control-group input[type="range"]::-moz-range-thumb:hover {
    background: #1e3c72;
    transform: scale(1.1);
}

.chart-display {
    margin-top: 20px;
    background: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.save-section {
    position: fixed;
    top: 100px;
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

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
    }
    
    .chart-page-container {
        padding: 30px 20px !important;
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
}"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
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
    print("SATID FBIS OPTIMIZER - Constrained Breakout-Based Optimization")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load data
        df, tickers = load_etf_prices(CSV_FILE)
        
        # Run optimization
        params = optimize_all_etfs(df, tickers)
        
        # Save parameters to JSON
        with open(PARAMS_FILE, 'w') as f:
            json.dump(params, f, indent=2)
        print(f"\n💾 Saved optimized parameters to: {PARAMS_FILE}")
        
        # Generate HTML
        html = generate_html(df, tickers, params)
        
        # Save HTML
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("\n" + "=" * 80)
        print("✓ OPTIMIZATION COMPLETE!")
        print("=" * 80)
        print(f"  ✓ Output HTML: {OUTPUT_HTML}")
        print(f"  ✓ Parameters JSON: {PARAMS_FILE}")
        print(f"  ✓ ETFs optimized: {len(tickers)}")
        print("\n📋 Next steps:")
        print("  1. Open Support_Levels_Interactive.html in your browser")
        print("  2. Review constrained optimized Fbis support levels")
        print("  3. Adjust parameters if needed using sliders")
        print("  4. Click '💾 Save All Parameters' to export adjusted values")
        print("  5. Use the JSON file with other SATID scripts")
        print("\n🎯 Optimization method:")
        print("  • Automatic trend change detection (downtrend line breakout)")
        print("  • Asset-class specific parameter constraints")
        print(f"  • Breach penalty = {BREACH_PENALTY} (balanced - accepts breaches as signals)")
        print("  • Chart: Price (black) from Jan 2020, Fbis (red dotted) from Sep 2022")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: File not found - {e}")
        print("\nMake sure these files are in the same directory:")
        print(f"  - {CSV_FILE}")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
