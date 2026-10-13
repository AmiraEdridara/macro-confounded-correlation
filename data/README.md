# Data

US macroeconomic series from [FRED](https://fred.stlouisfed.org) (Federal Reserve Bank of St. Louis), downloaded October 2026. Values are as published by FRED at the time, unadjusted by this project.

## `raw/fred_monthly.csv` (Jan 1959 to Sep 2026)

| Column | Series | Units | Role |
|---|---|---|---|
| FEDFUNDS | Effective federal funds rate | % | Policy interest rate (the "cause") |
| CPIAUCSL | CPI, all items | Index 1982-84=100, SA | Headline inflation (the "outcome") |
| CPILFESL | CPI excluding food and energy | Index 1982-84=100, SA | Core inflation |
| PCEPILFE | Core PCE price index | Index 2017=100, SA | The Fed's preferred inflation gauge |
| UNRATE | Unemployment rate | %, SA | Labour market slack |
| INDPRO | Industrial production | Index 2017=100, SA | Monthly activity proxy |
| M2SL | M2 money stock | $bn, SA | Money supply |
| MICH | Michigan 1-year inflation expectations | % | Expectations (from 1978) |
| GS10 | 10-year Treasury yield | % | Long-term rates |
| MCOILWTICO | WTI crude oil | $/barrel | Supply shocks (from 1986) |
| PPIACO | Producer price index, all commodities | Index 1982=100, NSA | Cost pressures |

Most recent months may be blank where FRED hasn't published yet. October 2025 is missing for CPI and unemployment because the BLS did not publish those during the US government shutdown.

## `raw/fred_quarterly.csv` (Q1 1959 to Q2 2026)

| Column | Series | Units |
|---|---|---|
| GDPC1 | Real GDP | Chained 2017 $bn, SAAR |
| GDPPOT | CBO real potential GDP | Chained 2017 $bn |

Output gap = `100 * (GDPC1 - GDPPOT) / GDPPOT`.

## UK files (downloaded October 2026)

| File | Columns | Source | Coverage |
|---|---|---|---|
| `raw/uk_bank_rate.csv` | BANK_RATE: monthly average of official Bank Rate, % | Bank of England database, series IUMABEDR | Jan 1975 to Sep 2026 |
| `raw/uk_ons_monthly.csv` | CPI: CPI index 2015=100, NSA (ONS D7BT) | ONS | Jan 1988 to Aug 2026 |
| | UNEMP: unemployment rate 16+, %, SA, rolling 3 months (ONS MGSX) | ONS | Feb 1971 to Jun 2026 |
| | IOP: index of production, CVM SA (ONS K222) | ONS | Jan 1970 to Aug 2026 |
| `raw/uk_oecd_cpi_1970_1988.csv` | CPI_OECD: UK CPI, 2015=100 (FRED GBRCPIALLMINMEI) | OECD via FRED | Jan 1970 to Dec 1988 |

## Bond yields (downloaded October 2026)

| File | Columns | Source | Coverage |
|---|---|---|---|
| `raw/fred_treasury_yields.csv` | GS2, GS5: 2-year and 5-year Treasury constant maturity yields, monthly average, % | FRED | GS5 from 1965, GS2 from Jun 1976, to Sep 2026 |
| `raw/uk_gilt_5y.csv` | GILT_5Y: 5-year nominal zero coupon gilt yield, monthly average, % | Bank of England database, series IUMASNZC | Jan 1982 to Sep 2026 |

The Bank of England database has monthly gilt yields at 5, 10 and 20 years only, so the 5-year is used for both countries.

## Notes

The ONS CPI starts in 1988, so `src/load_data.py` extends it back using the OECD series' growth rates, rescaled to match ONS in January 1988. The two indexes differ in level by about 3% because of vintage and rounding differences.
