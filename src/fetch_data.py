"""Download raw asset prices (Yahoo Finance) and macro series (FRED).

Usage:
    python -m src.fetch_data

Writes:
    data/raw/prices.csv   adjusted close prices for assets and market controls
    data/raw/fred.csv     daily FRED macro series
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

from src.config import ASSETS, FRED_CONTROLS, MARKET_CONTROLS, START_DATE

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"


def fetch_prices(tickers: list[str], start: str = START_DATE) -> pd.DataFrame:
    """Adjusted close prices, one column per ticker."""
    data = yf.download(tickers, start=start, auto_adjust=True, progress=False)
    prices = data["Close"]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(tickers[0])
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    prices.index.name = "date"
    return prices[tickers]


def fetch_fred(series_ids: list[str], start: str = START_DATE) -> pd.DataFrame:
    """Daily FRED series via the public CSV endpoint (no API key needed)."""
    frames = []
    for sid in series_ids:
        df = pd.read_csv(FRED_URL.format(series=sid), index_col=0, parse_dates=True)
        # FRED marks missing values with "." in older files
        df[sid] = pd.to_numeric(df.iloc[:, 0], errors="coerce")
        frames.append(df[[sid]])
    fred = pd.concat(frames, axis=1)
    fred.index.name = "date"
    return fred.loc[start:]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    tickers = list(ASSETS) + list(MARKET_CONTROLS)
    prices = fetch_prices(tickers)
    prices.to_csv(RAW_DIR / "prices.csv")
    print(f"prices: {prices.shape[0]} rows x {prices.shape[1]} cols "
          f"({prices.index.min().date()} to {prices.index.max().date()})")

    fred = fetch_fred(list(FRED_CONTROLS))
    fred.to_csv(RAW_DIR / "fred.csv")
    print(f"fred:   {fred.shape[0]} rows x {fred.shape[1]} cols "
          f"({fred.index.min().date()} to {fred.index.max().date()})")


if __name__ == "__main__":
    main()
