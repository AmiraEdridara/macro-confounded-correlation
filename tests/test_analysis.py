import numpy as np
import pandas as pd
import pytest
from statsmodels.tsa.api import VAR

from src.load_data import load, seasonally_adjust_log, uk_cpi
from src.var import fit_var, impulse_response


@pytest.fixture(scope="module")
def us():
    return load("US")


@pytest.fixture(scope="module")
def uk():
    return load("UK")


def test_irf_matches_statsmodels(us):
    d = us[["output", "prices", "commod", "rate"]].loc["1965":"2007"]
    mine = impulse_response(fit_var(d, 12), 48, "rate")
    ref = VAR(d.reset_index(drop=True)).fit(12).irf(48).orth_irfs[:, :, 3]
    np.testing.assert_allclose(mine, ref / ref[0, 3], atol=1e-10)


def test_shock_is_one_percentage_point(us):
    d = us[["prices", "rate"]].loc["1965":"2007"]
    irf = impulse_response(fit_var(d, 12), 12, "rate")
    assert irf[0, 1] == pytest.approx(1.0)
    assert irf[0, 0] == pytest.approx(0.0)  # prices ordered first: no impact effect


def test_uk_cpi_splice_is_continuous():
    cpi = uk_cpi()
    monthly_change = 100 * np.log(cpi).diff()
    # Splice month should look like a normal month, not a jump
    assert abs(monthly_change.loc["1988-01-01"]) < 1.5
    assert cpi.index.min() == pd.Timestamp("1970-01-01")


def test_seasonal_adjustment_removes_month_pattern():
    idx = pd.date_range("2000-01-01", periods=120, freq="MS")
    seasonal = np.tile([0.5, -0.2, 0.1, 0, 0, 0, -0.6, 0.2, 0, 0, 0, 0], 10)
    x = pd.Series(np.cumsum(0.2 + seasonal), index=idx)
    adj = seasonally_adjust_log(x).diff().dropna()
    assert adj.std() < 1e-10


CORE = ["output", "prices", "commod", "rate", "infl", "unemp"]


def test_panels_have_expected_coverage(us, uk):
    assert us.loc["1965":"2007", CORE].isna().sum().sum() == 0
    assert uk.loc["1975":"2007", CORE].isna().sum().sum() == 0
    assert uk["rate"].loc["2009-04-01"] == 0.5


def test_yields_cover_extended_samples(us, uk):
    assert us.loc["1965":"2026-08", "y5"].isna().sum() == 0
    assert us.loc["1976-06":"2026-08", "y2"].isna().sum() == 0
    assert uk.loc["1982":"2026-08", "y5"].isna().sum() == 0
