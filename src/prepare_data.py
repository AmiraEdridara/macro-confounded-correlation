"""Turn raw prices and macro levels into an aligned daily panel of returns/changes.

Usage:
    python -m src.prepare_data

Reads data/raw/prices.csv and data/raw/fred.csv, writes data/processed/returns.csv
with one row per trading day and one column per asset return or macro change.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import ASSETS, CONTROL_TRANSFORMS

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1))


def to_changes(levels: pd.DataFrame, transforms: dict[str, str]) -> pd.DataFrame:
    """Apply the configured transform to each control column."""
    out = {}
    for col in levels.columns:
        how = transforms.get(col, "log_return")
        if how == "diff":
            out[col] = levels[col].diff()
        elif how == "log_return":
            out[col] = np.log(levels[col] / levels[col].shift(1))
        else:
            raise ValueError(f"Unknown transform '{how}' for {col}")
    return pd.DataFrame(out, index=levels.index)


def build_panel(prices: pd.DataFrame, fred: pd.DataFrame,
                max_ffill_days: int = 3) -> pd.DataFrame:
    """Align on the equity trading calendar and compute returns/changes.

    FRED series follow a slightly different holiday calendar, so they are
    forward-filled for at most `max_ffill_days` before differencing. Days with
    any remaining gaps are dropped so every row is a complete observation.
    """
    calendar = prices["SPY"].dropna().index
    prices = prices.reindex(calendar)
    fred = fred.reindex(calendar).ffill(limit=max_ffill_days)

    # Oil went negative in April 2020, which breaks log returns
    if "DCOILWTICO" in fred:
        fred.loc[fred["DCOILWTICO"] <= 0, "DCOILWTICO"] = np.nan

    asset_cols = [c for c in prices.columns if c in ASSETS]
    control_price_cols = [c for c in prices.columns if c not in ASSETS]

    panel = pd.concat(
        [
            log_returns(prices[asset_cols]),
            to_changes(prices[control_price_cols], CONTROL_TRANSFORMS),
            to_changes(fred, CONTROL_TRANSFORMS),
        ],
        axis=1,
    )
    return panel.dropna()


def main() -> None:
    prices = pd.read_csv(RAW_DIR / "prices.csv", index_col="date", parse_dates=True)
    fred = pd.read_csv(RAW_DIR / "fred.csv", index_col="date", parse_dates=True)

    panel = build_panel(prices, fred)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    panel.to_csv(PROCESSED_DIR / "returns.csv")
    print(f"returns: {panel.shape[0]} days x {panel.shape[1]} series "
          f"({panel.index.min().date()} to {panel.index.max().date()})")
    print(panel.describe().T[["mean", "std", "min", "max"]].round(4))


if __name__ == "__main__":
    main()
