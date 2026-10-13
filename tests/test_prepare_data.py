import numpy as np
import pandas as pd

from src.config import ASSETS, FRED_CONTROLS, MARKET_CONTROLS
from src.prepare_data import build_panel


def make_raw(n=50, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2024-01-01", periods=n)
    tickers = list(ASSETS) + list(MARKET_CONTROLS)
    prices = pd.DataFrame(
        100 * np.exp(rng.normal(0, 0.01, (n, len(tickers))).cumsum(axis=0)),
        index=dates, columns=tickers,
    )
    fred = pd.DataFrame(
        3 + rng.normal(0, 0.02, (n, len(FRED_CONTROLS))).cumsum(axis=0),
        index=dates, columns=list(FRED_CONTROLS),
    )
    fred["DCOILWTICO"] = 70 + fred["DCOILWTICO"]
    return prices, fred


def test_panel_shape_and_no_nans():
    prices, fred = make_raw()
    panel = build_panel(prices, fred)
    assert panel.shape[1] == len(ASSETS) + len(MARKET_CONTROLS) + len(FRED_CONTROLS)
    assert not panel.isna().any().any()
    assert len(panel) == len(prices) - 1  # first row lost to differencing


def test_rates_are_differenced_not_logged():
    prices, fred = make_raw()
    panel = build_panel(prices, fred)
    expected = fred["DGS10"].diff().iloc[1:]
    pd.testing.assert_series_equal(panel["DGS10"], expected, check_names=False)


def test_fred_holiday_gap_is_forward_filled():
    prices, fred = make_raw()
    fred = fred.drop(fred.index[10])  # FRED missing a day equities traded
    panel = build_panel(prices, fred)
    assert prices.index[10] in panel.index


def test_negative_oil_rows_dropped():
    prices, fred = make_raw()
    fred.iloc[20, fred.columns.get_loc("DCOILWTICO")] = -37.6
    panel = build_panel(prices, fred)
    assert prices.index[20] not in panel.index
