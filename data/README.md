# Data

US macroeconomic series from [FRED](https://fred.stlouisfed.org) (Federal Reserve Bank of St. Louis), downloaded 16 October 2026. Values are as published by FRED on that date, unadjusted by this project.

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
