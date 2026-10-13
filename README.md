# Macroeconomic-Confounded Correlation

A quantitative framework for measuring how much of the relationship between two assets survives after controlling for shared macroeconomic drivers.

## Why

Raw correlations between assets can mislead. Interest rates, inflation expectations, USD strength, volatility and broad equity moves all hit many assets at once, so two ETFs can look tightly linked when they are mostly just exposed to the same factors.

This project separates the two:

```
SPY ↔ EEM
  raw correlation:          0.72
  conditional on macro:     0.31   ← the residual relationship
```

## Method (planned)

1. Compute daily log returns for assets and daily changes for macro controls
2. Regress each asset's returns on the controls and keep the residuals
3. Correlate the residuals (partial correlation), with confidence intervals
4. Repeat on rolling windows and across market regimes
5. Plot raw vs. conditional correlation over time

## Data

| Type | Series | Source | Transform |
|---|---|---|---|
| Assets | SPY, QQQ, IWM, EEM, TLT, HYG, GLD, XLE | Yahoo Finance | log return |
| Volatility | VIX | Yahoo Finance | log change |
| USD | UUP (dollar index ETF) | Yahoo Finance | log return |
| Rates | 2y and 10y Treasury yields | FRED (DGS2, DGS10) | daily difference |
| Inflation | 10y breakeven inflation | FRED (T10YIE) | daily difference |
| Commodities | WTI crude | FRED (DCOILWTICO) | log return |

Everything is aligned to the US equity trading calendar from 2010. FRED gaps from holiday mismatches are forward-filled for up to 3 days; any day still incomplete is dropped. The April 2020 negative oil print is excluded since log returns are undefined there.

The universe lives in [`src/config.py`](src/config.py), so adding an asset or control is a one-line change.

## Quick start

```bash
pip install -r requirements.txt
python -m src.fetch_data      # download raw data into data/raw/
python -m src.prepare_data    # build data/processed/returns.csv
pytest                        # run tests
```

## Project structure

```
src/
  config.py          asset universe and macro controls
  fetch_data.py      download prices (Yahoo) and macro series (FRED)
  prepare_data.py    align calendars, compute returns and changes
tests/
  test_prepare_data.py
data/
  raw/               downloaded data (git-ignored)
  processed/         model-ready panel (git-ignored)
```

## Roadmap

- [x] Data pipeline: download, align and transform assets and macro controls
- [ ] Rolling raw correlations
- [ ] Regression-based residualisation
- [ ] Rolling partial correlations with confidence intervals
- [ ] Raw vs. conditional correlation charts
- [ ] Regime-dependent correlations (e.g. high vs. low VIX)
- [ ] PCA / factor decomposition
- [ ] Shrinkage covariance and portfolio optimisation on conditional covariances
