"""Load raw US and UK data into clean monthly panels.

Each panel has the same columns so the same model can run on both countries:

    output   log industrial production x 100
    prices   log CPI x 100 (seasonally adjusted)
    commod   log commodity price index x 100 (US PPI, all commodities)
    rate     policy interest rate, % (Fed funds / Bank Rate)
    infl     12-month CPI inflation, %
    unemp    unemployment rate, %
    y5       5-year government bond yield, % (US Treasury / UK gilt)
    y2       2-year Treasury yield, % (US only)
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def _monthly_index(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index).to_period("M").to_timestamp()
    df.index.name = "date"
    return df


def seasonally_adjust_log(x: pd.Series) -> pd.Series:
    """Remove fixed monthly seasonal factors from a log series.

    Takes month-on-month log changes, subtracts each calendar month's mean
    change (keeping the overall mean), and cumulates back to a level.
    """
    d = x.diff()
    month = d.index.month
    seasonal = d.groupby(month).transform("mean") - d.mean()
    adjusted = (d - seasonal).cumsum() + x.iloc[0]
    adjusted.iloc[0] = x.iloc[0]
    return adjusted


def load_us() -> pd.DataFrame:
    m = _monthly_index(pd.read_csv(RAW / "fred_monthly.csv", index_col=0))
    out = pd.DataFrame(index=m.index)
    out["output"] = 100 * np.log(m["INDPRO"])
    out["prices"] = 100 * np.log(m["CPIAUCSL"])  # already seasonally adjusted
    out["commod"] = 100 * np.log(m["PPIACO"])
    out["rate"] = m["FEDFUNDS"]
    out["infl"] = 100 * (m["CPIAUCSL"] / m["CPIAUCSL"].shift(12) - 1)
    out["unemp"] = m["UNRATE"]
    ylds = _monthly_index(pd.read_csv(RAW / "fred_treasury_yields.csv", index_col=0))
    out["y5"] = ylds["GS5"].reindex(out.index)
    out["y2"] = ylds["GS2"].reindex(out.index)
    return out


def uk_cpi() -> pd.Series:
    """ONS CPI (2015=100) from 1988, extended back with OECD CPI growth rates."""
    ons = _monthly_index(pd.read_csv(RAW / "uk_ons_monthly.csv", index_col=0))["CPI"]
    oecd = _monthly_index(pd.read_csv(RAW / "uk_oecd_cpi_1970_1988.csv", index_col=0))["CPI_OECD"]
    splice = pd.Timestamp("1988-01-01")
    back = oecd.loc[:splice] * ons.loc[splice] / oecd.loc[splice]
    return pd.concat([back.loc[: splice - pd.offsets.MonthBegin()], ons.loc[splice:]]).dropna()


def load_uk() -> pd.DataFrame:
    ons = _monthly_index(pd.read_csv(RAW / "uk_ons_monthly.csv", index_col=0))
    rate = _monthly_index(pd.read_csv(RAW / "uk_bank_rate.csv", index_col=0))["BANK_RATE"]
    us = _monthly_index(pd.read_csv(RAW / "fred_monthly.csv", index_col=0))

    out = pd.DataFrame(index=ons.index)
    out["output"] = 100 * np.log(ons["IOP"])
    log_cpi = 100 * np.log(uk_cpi()).reindex(out.index)
    out["prices"] = seasonally_adjust_log(log_cpi.dropna()).reindex(out.index)
    out["commod"] = 100 * np.log(us["PPIACO"]).reindex(out.index)
    out["rate"] = rate.reindex(out.index)
    cpi = uk_cpi().reindex(out.index)
    out["infl"] = 100 * (cpi / cpi.shift(12) - 1)  # 12-month change needs no seasonal adjustment
    out["unemp"] = ons["UNEMP"]
    gilt = _monthly_index(pd.read_csv(RAW / "uk_gilt_5y.csv", index_col=0))["GILT_5Y"]
    out["y5"] = gilt.reindex(out.index)
    return out


def load(country: str) -> pd.DataFrame:
    return {"US": load_us, "UK": load_uk}[country]()
