"""Universe of assets and macro control variables used in the project."""

START_DATE = "2010-01-01"

# Assets whose pairwise relationships we want to study (Yahoo Finance tickers)
ASSETS = {
    "SPY": "US large-cap equities",
    "QQQ": "US tech equities",
    "IWM": "US small-cap equities",
    "EEM": "Emerging-market equities",
    "TLT": "Long-dated US Treasuries",
    "HYG": "US high-yield credit",
    "GLD": "Gold",
    "XLE": "US energy equities",
}

# Market-based macro controls (Yahoo Finance tickers)
MARKET_CONTROLS = {
    "^VIX": "VIX implied volatility",
    "UUP": "US dollar index (ETF proxy)",
}

# Macro controls from FRED (series id -> description), all daily
FRED_CONTROLS = {
    "DGS2": "2-year Treasury yield (%)",
    "DGS10": "10-year Treasury yield (%)",
    "T10YIE": "10-year breakeven inflation (%)",
    "DCOILWTICO": "WTI crude oil price ($/bbl)",
}

# How each control is transformed into a daily change
#   "log_return": log(P_t / P_{t-1})
#   "diff":       X_t - X_{t-1}  (used for rates and spreads, in percentage points)
CONTROL_TRANSFORMS = {
    "^VIX": "log_return",
    "UUP": "log_return",
    "DGS2": "diff",
    "DGS10": "diff",
    "T10YIE": "diff",
    "DCOILWTICO": "log_return",
}
