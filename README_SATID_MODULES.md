# SATID CALCULATION MODULES - DOCUMENTATION

## Overview

The SATID calculation functions have been refactored into a shared core module to ensure **100% consistency** across all dashboard scripts. This prevents calculation discrepancies and makes maintenance much easier.

## File Structure

```
SATID_core_calculations.py       ← CORE MODULE (import this)
├── All shared calculation functions
├── EMA, FBIS, volatility calculations
├── SATID scoring (volatility-adjusted)
├── Portfolio risk analysis
└── Statistical functions

SATID_Risk_Score.py              ← Individual ETF Risk Dashboard
├── Imports from SATID_core_calculations
├── Excel export function
├── HTML generation
└── Main execution

Portfolio_Risk_Dashboard.py      ← Portfolio Overview Dashboard
├── Imports from SATID_core_calculations
├── Risk exposure table formatting
├── HTML generation
└── Main execution
```

## Key Improvements

### 1. **Single Source of Truth**
All calculation logic lives in `SATID_core_calculations.py`. Any bug fixes or improvements only need to be made once.

### 2. **100% Consistent SATID Scores**
Both dashboards now use the **exact same** volatility-adjusted z-score methodology:

```python
σ_horizon = σ_weekly × √(horizon_weeks)
z_score = distance% / σ_horizon  
score = 100 - (z_score × 25)
```

**No more discrepancies!**

### 3. **Correct Risk Level Thresholds**
Both scripts now use the same 5-level risk classification:

| Score Range | Risk Level | Color |
|-------------|------------|-------|
| 90-100 | CRITICAL | Dark Red |
| 75-89 | HIGH | Red |
| 50-74 | MODERATE | Orange |
| 25-49 | LOW | Green |
| 0-24 | MINIMAL | Teal |

### 4. **Different Scores for Different Horizons**
The corrected calculation properly scales volatility:
- 1-week score uses σ_weekly × √1
- 1-month score uses σ_weekly × √4.33
- Same distance = different scores for different horizons ✓

## What Was Fixed

### Previous Issues in Portfolio_Risk_Dashboard.py:

**WRONG (Old Method):**
```python
def calculate_score(pct_dist):
    # No volatility consideration!
    return max(0, 100 * (1 - pct_dist / 20))

score_1week = calculate_score(pct_to_support)
score_1month = calculate_score(pct_to_support)  # Same as 1-week!
```

**CORRECT (New Method):**
```python
from SATID_core_calculations import (
    calculate_etf_volatility,
    calculate_satid_score_linear,
    analyze_etf_risk
)

# Now uses volatility-adjusted z-score
# 1-week and 1-month scores are properly different
```

## How to Use

### Running Individual Scripts

```bash
# Generate Risk Score Dashboard
python SATID_Risk_Score.py

# Generate Portfolio Dashboard  
python Portfolio_Risk_Dashboard.py
```

Both scripts will automatically import calculations from `SATID_core_calculations.py`.

### Adding New Dashboards

When creating new SATID analysis scripts:

```python
# Import the functions you need
from SATID_core_calculations import (
    get_active_etfs_with_allocations,
    analyze_etf_risk,
    calculate_portfolio_satid_scores,
    # ... any other functions
)

# Your unique dashboard code here
```

## Core Calculation Functions

### Data Loading
- `get_active_etfs_with_allocations()` - Load portfolio from Excel
- `load_portfolio_allocations()` - Load with asset class details

### EMA & FBIS
- `calculate_ema()` - Exponential Moving Average
- `calculate_portfolio_series()` - Portfolio value & FBIS time series

### Volatility & Correlation
- `calculate_etf_volatility()` - Individual ETF volatility (13 weeks)
- `calculate_individual_volatilities()` - Batch volatility calculation
- `calculate_correlation_matrix()` - Pearson correlation matrix
- `calculate_portfolio_volatility()` - Portfolio-level volatility using MPT

### Risk Statistics
- `calculate_risk_statistics()` - Probability of reaching FBIS, VaR
- `calculate_portfolio_risk()` - Asset class risk exposure

### SATID Scoring (★ CORE METHODOLOGY ★)
- `calculate_satid_score_linear()` - Volatility-adjusted score
- `analyze_etf_risk()` - Complete ETF analysis
- `calculate_portfolio_satid_scores()` - Portfolio weighted scores
- `get_risk_level_class()` - Risk level classification

## Mathematical Formulas

All formulas are documented in the core module with detailed docstrings:

- **EMA:** EMA[i] = Price[i] × k + EMA[i-1] × (1-k), where k = 2/(period+1)
- **FBIS:** EMA × (1 + vertical_shift)
- **Returns:** (Price[i] - Price[i-1]) / Price[i-1]
- **Volatility:** σ = √[Σ(r - μ)² / (n-1)] with Bessel's correction
- **Z-Score:** distance% / (σ_weekly × √weeks)
- **SATID Score:** 100 - (z_score × 25)

## Maintenance

### Modifying Calculations

**DO:**
- Make changes in `SATID_core_calculations.py`
- Update docstrings to reflect changes
- Test with both dashboard scripts

**DON'T:**
- Duplicate functions in individual scripts
- Create script-specific calculation variations
- Modify formulas without updating documentation

### Adding New Functions

1. Add function to `SATID_core_calculations.py`
2. Add comprehensive docstring with formula
3. Import in scripts that need it
4. Update this README

## Dependencies

```python
pandas >= 1.3.0
numpy >= 1.21.0
scipy >= 1.7.0
openpyxl >= 3.0.0
```

## Version History

**v2.0 - February 2025**
- Refactored to modular structure
- Fixed Portfolio_Risk_Dashboard scoring methodology
- Unified risk level thresholds
- Added comprehensive documentation

**v1.0 - Prior**
- Original monolithic scripts
- Inconsistent calculations between dashboards

---

## Questions?

If you need to understand any specific calculation, check the docstrings in `SATID_core_calculations.py` - they include full mathematical formulas and explanations.

For SATID methodology questions, refer to the main SATID documentation.

**Remember:** Always import from the core module. Never duplicate calculation logic!
