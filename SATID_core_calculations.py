"""
SATID CORE CALCULATIONS MODULE
==============================
Shared calculation functions used by all SATID scripts.
This ensures 100% consistency across all dashboards.

Author: Patricio
Last Updated: 2025
"""

import pandas as pd
import numpy as np
from scipy import stats


# ==============================================================================
# CORE DATA FUNCTIONS
# ==============================================================================

def get_active_etfs_with_allocations(portfolio_file):
    """Load active ETFs with their allocations from portfolio Excel file."""
    df = pd.read_excel(portfolio_file)
    etfs = df[['Unnamed: 2', 'ALLOCATIONS']].copy()
    etfs.columns = ['Ticker', 'Allocation']
    etfs = etfs[etfs['Ticker'].notna()]
    etfs = etfs[etfs['Ticker'] != 'ETF']
    etfs['Allocation'] = pd.to_numeric(etfs['Allocation'], errors='coerce')
    etfs = etfs[etfs['Allocation'] > 0]
    return dict(zip(etfs['Ticker'], etfs['Allocation']))


# ==============================================================================
# EMA AND FBIS CALCULATIONS
# ==============================================================================

def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average.
    
    Formula: EMA[i] = Price[i] × k + EMA[i-1] × (1 - k)
    where k = 2 / (period + 1)
    
    Parameters:
    -----------
    prices : array-like
        Price series
    period : int
        EMA period
        
    Returns:
    --------
    numpy.ndarray
        EMA values
    """
    ema = np.zeros(len(prices))
    ema[0] = prices[0]
    k = 2 / (period + 1)
    for i in range(1, len(prices)):
        ema[i] = prices[i] * k + ema[i-1] * (1 - k)
    return ema


# ==============================================================================
# PORTFOLIO TIME SERIES CALCULATIONS
# ==============================================================================

def calculate_portfolio_series(ohlc_file, allocations, fbis_params):
    """
    Calculate normalized portfolio value and FBIS support series.
    
    Parameters:
    -----------
    ohlc_file : str
        Path to OHLC CSV file
    allocations : dict
        {ticker: weight} dictionary
    fbis_params : dict
        {ticker: {'period': int, 'shift': float}} dictionary
        
    Returns:
    --------
    tuple
        (dates, portfolio_values, portfolio_fbis)
    """
    df = pd.read_csv(ohlc_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    dates, n_periods = df['Date'].values, len(df)
    portfolio_values = np.zeros(n_periods)
    portfolio_fbis = np.zeros(n_periods)
    
    for ticker, weight in allocations.items():
        close_col = f"{ticker}_close"
        if close_col not in df.columns:
            continue
        prices = df[close_col].values
        period = fbis_params.get(ticker, {}).get('period', 8)
        shift = fbis_params.get(ticker, {}).get('shift', 0)
        ema = calculate_ema(prices, period)
        fbis = ema * (1 + shift)
        portfolio_values += prices / prices[0] * weight
        portfolio_fbis += fbis / prices[0] * weight
    
    return dates, portfolio_values, portfolio_fbis


# ==============================================================================
# VOLATILITY AND CORRELATION CALCULATIONS
# ==============================================================================

def calculate_correlation_matrix(ohlc_file, tickers, weeks=13):
    """
    Calculate correlation matrix using Pearson correlation.
    
    Parameters:
    -----------
    ohlc_file : str
        Path to OHLC CSV file
    tickers : list
        List of ticker symbols
    weeks : int, default=13
        Number of weeks for lookback period
        
    Returns:
    --------
    pandas.DataFrame
        Correlation matrix
    """
    df = pd.read_csv(ohlc_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').tail(weeks + 1)
    returns_data = {}
    for ticker in tickers:
        close_col = f"{ticker}_close"
        if close_col in df.columns:
            prices = df[close_col].values
            returns = np.diff(prices) / prices[:-1]
            returns_data[ticker] = returns
    return pd.DataFrame(returns_data).corr()


def calculate_individual_volatilities(ohlc_file, tickers, weeks=13):
    """
    Calculate individual ETF volatilities (weekly standard deviation).
    
    Formula: σ = √[Σ(Return[i] - μ)² / (n - 1)]
    Uses Bessel's correction (ddof=1)
    
    Parameters:
    -----------
    ohlc_file : str
        Path to OHLC CSV file
    tickers : list
        List of ticker symbols
    weeks : int, default=13
        Number of weeks for lookback period
        
    Returns:
    --------
    dict
        {ticker: weekly_volatility}
    """
    df = pd.read_csv(ohlc_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').tail(weeks + 1)
    volatilities = {}
    for ticker in tickers:
        close_col = f"{ticker}_close"
        if close_col in df.columns:
            prices = df[close_col].values
            returns = np.diff(prices) / prices[:-1]
            volatilities[ticker] = np.std(returns, ddof=1)
    return volatilities


def calculate_etf_volatility(prices, weeks=13):
    """
    Calculate volatility for a single ETF from price series.
    
    Parameters:
    -----------
    prices : array-like
        Price series
    weeks : int, default=13
        Number of weeks for lookback period
        
    Returns:
    --------
    float
        Weekly volatility
    """
    if len(prices) < weeks + 1:
        weeks = len(prices) - 1
    recent_prices = prices[-(weeks + 1):]
    returns = np.diff(recent_prices) / recent_prices[:-1]
    return np.std(returns, ddof=1)


def calculate_portfolio_volatility(allocations, correlation_matrix, individual_vols):
    """
    Calculate portfolio volatility using Modern Portfolio Theory.
    
    Formula: σ_portfolio = √(w' × Σ × w)
    where Σ is the covariance matrix
    
    Parameters:
    -----------
    allocations : dict
        {ticker: weight} dictionary
    correlation_matrix : pandas.DataFrame
        Correlation matrix
    individual_vols : dict
        {ticker: volatility} dictionary
        
    Returns:
    --------
    float
        Portfolio weekly volatility
    """
    tickers = list(allocations.keys())
    weights = np.array([allocations[t] for t in tickers])
    n = len(tickers)
    cov_matrix = np.zeros((n, n))
    for i, ticker_i in enumerate(tickers):
        for j, ticker_j in enumerate(tickers):
            if ticker_i in correlation_matrix.columns and ticker_j in correlation_matrix.columns:
                corr = correlation_matrix.loc[ticker_i, ticker_j]
                vol_i = individual_vols.get(ticker_i, 0)
                vol_j = individual_vols.get(ticker_j, 0)
                cov_matrix[i, j] = corr * vol_i * vol_j
    portfolio_variance = weights @ cov_matrix @ weights
    return np.sqrt(portfolio_variance)


# ==============================================================================
# RISK STATISTICS CALCULATIONS
# ==============================================================================

def calculate_risk_statistics(current_value, fbis_value, portfolio_vol_weekly):
    """
    Calculate probability of reaching FBIS and VaR for multiple horizons.
    
    Parameters:
    -----------
    current_value : float
        Current portfolio value (normalized)
    fbis_value : float
        FBIS support level (normalized)
    portfolio_vol_weekly : float
        Weekly portfolio volatility
        
    Returns:
    --------
    tuple
        (statistics_dict, distance_pct)
        statistics_dict contains probability and VaR for each horizon
    """
    distance_to_fbis = (current_value - fbis_value) / current_value
    horizons = {'1_week': 1, '1_month': 4.33, '3_months': 13}
    statistics = {}
    for horizon_name, weeks in horizons.items():
        vol_horizon = portfolio_vol_weekly * np.sqrt(weeks)
        z_score = -distance_to_fbis / vol_horizon
        prob_reach_fbis = stats.norm.cdf(z_score)
        var_95 = 1.645 * vol_horizon
        statistics[horizon_name] = {'probability': prob_reach_fbis, 'var_95': var_95}
    return statistics, distance_to_fbis


# ==============================================================================
# SATID SCORE CALCULATIONS (VOLATILITY-ADJUSTED)
# ==============================================================================

def calculate_satid_score_linear(distance_pct, volatility_weekly, horizon_weeks=1):
    """
    Calculate SATID score using volatility-adjusted z-score method.
    
    Formula: 
        σ_horizon = σ_weekly × √(horizon_weeks)
        z_score = distance_pct / σ_horizon
        score = 100 - (z_score × 25)
    
    Score Interpretation:
        100 = At or below FBIS (0σ)
        75  = 1σ above FBIS (HIGH RISK)
        50  = 2σ above FBIS (MODERATE RISK)
        25  = 3σ above FBIS (LOW RISK)
        0   = 4σ+ above FBIS (MINIMAL RISK)
    
    Parameters:
    -----------
    distance_pct : float
        Distance from FBIS as percentage (e.g., 0.05 for 5%)
    volatility_weekly : float
        Weekly volatility
    horizon_weeks : float, default=1
        Time horizon in weeks (1 for 1-week, 4.33 for 1-month, etc.)
        
    Returns:
    --------
    float
        SATID score (0-100)
    """
    if distance_pct <= 0:
        return 100.0
    volatility_horizon = volatility_weekly * np.sqrt(horizon_weeks)
    z_score = distance_pct / volatility_horizon
    score = 100 - (z_score * 25)
    return max(0, min(100, score))


def analyze_etf_risk(ticker, prices, fbis_params, weeks_lookback=13):
    """
    Analyze individual ETF risk and calculate SATID scores.
    
    This is the DEFINITIVE calculation method used across all SATID scripts.
    
    Parameters:
    -----------
    ticker : str
        ETF ticker symbol
    prices : array-like
        Price series
    fbis_params : dict
        FBIS parameters for this ticker
    weeks_lookback : int, default=13
        Lookback period for volatility calculation
        
    Returns:
    --------
    dict
        Contains ticker, prices, FBIS, distance, volatility, and SATID scores
    """
    current_price = prices[-1]
    period = fbis_params.get(ticker, {}).get('period', 8)
    shift = fbis_params.get(ticker, {}).get('shift', 0)
    ema = calculate_ema(prices, period)
    fbis = ema[-1] * (1 + shift)
    distance_pct = (current_price - fbis) / current_price
    volatility = calculate_etf_volatility(prices, weeks_lookback)
    score_1week = calculate_satid_score_linear(distance_pct, volatility, horizon_weeks=1)
    score_1month = calculate_satid_score_linear(distance_pct, volatility, horizon_weeks=4.33)
    
    return {
        'ticker': ticker,
        'current_price': current_price,
        'fbis': fbis,
        'distance_pct': distance_pct,
        'volatility_weekly': volatility,
        'satid_score_1week': score_1week,
        'satid_score_1month': score_1month,
        'allocation': 0,  # Will be filled in later
        'contribution_1week': 0,
        'contribution_1month': 0
    }


def calculate_portfolio_satid_scores(etf_results, allocations):
    """
    Calculate portfolio-level SATID scores as weighted average of ETF scores.
    
    Parameters:
    -----------
    etf_results : list
        List of ETF risk analysis dictionaries from analyze_etf_risk()
    allocations : dict
        {ticker: weight} dictionary
        
    Returns:
    --------
    tuple
        (portfolio_score_1week, portfolio_score_1month)
    """
    portfolio_score_1week = 0
    portfolio_score_1month = 0
    for result in etf_results:
        ticker = result['ticker']
        weight = allocations.get(ticker, 0)
        portfolio_score_1week += result['satid_score_1week'] * weight
        portfolio_score_1month += result['satid_score_1month'] * weight
        result['allocation'] = weight
        result['contribution_1week'] = result['satid_score_1week'] * weight
        result['contribution_1month'] = result['satid_score_1month'] * weight
    return portfolio_score_1week, portfolio_score_1month


def get_risk_level_class(score):
    """
    Get risk level classification and label from SATID score.
    
    Parameters:
    -----------
    score : float
        SATID score (0-100)
        
    Returns:
    --------
    tuple
        (css_class, label)
    """
    if score >= 90:
        return 'risk-critical', 'CRITICAL'
    elif score >= 75:
        return 'risk-high', 'HIGH'
    elif score >= 50:
        return 'risk-moderate', 'MODERATE'
    elif score >= 25:
        return 'risk-low', 'LOW'
    else:
        return 'risk-minimal', 'MINIMAL'


# ==============================================================================
# PORTFOLIO EXPOSURE ANALYSIS FUNCTIONS
# ==============================================================================

def load_portfolio_allocations(excel_file):
    """
    Load detailed portfolio allocations including asset class categorization.
    
    Parameters:
    -----------
    excel_file : str
        Path to portfolio Excel file
        
    Returns:
    --------
    tuple
        (allocations, asset_classes, category_weights)
    """
    df = pd.read_excel(excel_file, sheet_name='Portfolio')
    allocations, asset_classes, category_weights = {}, {}, {}
    current_category = None
    
    for idx, row in df.iterrows():
        if idx < 10:
            if pd.notna(row.iloc[1]):
                category_name_raw = str(row.iloc[1]).strip()
                if 'Cash' in category_name_raw and idx == 1:
                    category_weights['Cash'] = float(row['ALLOCATIONS'])
                elif 'Fixed Income' in category_name_raw and idx == 2:
                    category_weights['Fixed Income'] = float(row['ALLOCATIONS'])
                elif 'Core Equity' in category_name_raw and idx == 3:
                    category_weights['Core Equity'] = float(row['ALLOCATIONS'])
                elif 'Sectoral' in category_name_raw and idx == 4:
                    category_weights['Sector & Thematic'] = float(row['ALLOCATIONS'])
                elif 'Secular' in category_name_raw and idx == 5:
                    category_weights['Secular Growth'] = float(row['ALLOCATIONS'])
                elif 'Alternative' in category_name_raw and idx == 6:
                    category_weights['Alternative Investments'] = float(row['ALLOCATIONS'])
            continue
        
        if pd.notna(row.iloc[1]):
            category_name = str(row.iloc[1]).strip()
            if category_name in ['Cash', 'Fixed Income', 'Core Equity', 'Sector & Thematic', 
                               'Secular Growth', 'Alternative Investments']:
                current_category = category_name
                continue
        
        if pd.notna(row.iloc[2]) and current_category:
            ticker = str(row.iloc[2]).strip()
            if ticker and ticker != 'ETF':
                allocation = float(row['ALLOCATIONS']) if pd.notna(row['ALLOCATIONS']) else 0
                if allocation > 0:
                    allocations[ticker] = allocation
                    asset_classes[ticker] = current_category
    
    return allocations, asset_classes, category_weights


def calculate_portfolio_risk(df, allocations, asset_classes, fbis_params, portfolio_value):
    """
    Calculate detailed portfolio risk exposure by asset class.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        OHLC data
    allocations : dict
        {ticker: allocation_pct}
    asset_classes : dict
        {ticker: asset_class}
    fbis_params : dict
        FBIS parameters
    portfolio_value : float
        Total portfolio value in USD
        
    Returns:
    --------
    tuple
        (risk_data, asset_class_summary)
    """
    risk_data = []
    asset_class_summary = {}
    
    for ticker, allocation_pct in allocations.items():
        close_col = f"{ticker}_close"
        if close_col not in df.columns:
            continue
        
        current_price = df[close_col].iloc[-1]
        period = fbis_params.get(ticker, {}).get('period', 8)
        shift = fbis_params.get(ticker, {}).get('shift', 0)
        
        prices = df[close_col].values
        ema = calculate_ema(prices, period)
        fbis_support = ema[-1] * (1 + shift)
        
        pct_to_support = ((current_price - fbis_support) / current_price) * 100
        position_value = portfolio_value * (allocation_pct / 100)
        usd_at_risk = position_value * (-pct_to_support / 100)
        asset_class = asset_classes.get(ticker, 'Unknown')
        
        risk_data.append({
            'Ticker': ticker,
            'Asset Class': asset_class,
            'Allocation (%)': allocation_pct,
            '% to Support': pct_to_support,
            'USD at Risk': usd_at_risk
        })
        
        if asset_class not in asset_class_summary:
            asset_class_summary[asset_class] = {'weight': 0, 'avg_dist': 0, 'usd_at_risk': 0, 'count': 0}
        
        asset_class_summary[asset_class]['weight'] += allocation_pct
        asset_class_summary[asset_class]['avg_dist'] += pct_to_support * allocation_pct
        asset_class_summary[asset_class]['usd_at_risk'] += usd_at_risk
        asset_class_summary[asset_class]['count'] += 1
    
    for ac in asset_class_summary:
        w = asset_class_summary[ac]['weight']
        asset_class_summary[ac]['avg_dist'] = asset_class_summary[ac]['avg_dist'] / w if w > 0 else 0
    
    return risk_data, asset_class_summary
