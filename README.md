# Do Higher Interest Rates Lower Inflation?

Testing a core claim of monetary economics with US and UK data, and showing how confounding and reverse causality can make the raw data say the opposite of the truth.

## The problem

Economic theory says raising interest rates cools demand and brings inflation down. But in the raw data, interest rates and inflation move **together**:

| Correlation of policy rate with inflation | US 1965–2007 | UK 1975–2007 |
|---|---|---|
| Same month | +0.72 | +0.64 |
| Inflation 12 months later | +0.51 | +0.63 |

The reason is **reverse causality**: central banks raise rates *because* inflation is high. On top of that, **confounders** like oil and commodity shocks push inflation up and prompt rate rises at the same time. This project tests how much of the positive link disappears once those are accounted for.

## Method

1. **Forecast regressions.** Inflation 12 and 24 months ahead on today's policy rate, first alone, then controlling for current and lagged inflation, unemployment, output growth and commodity price growth (Newey-West standard errors).
2. **Recursive VARs.** Following Christiano, Eichenbaum and Evans (1999), a 12-lag monthly VAR with the policy rate ordered last, so the central bank can respond to the economy within the month but its rate surprise only affects the economy from the following month. Confounders are added one at a time:
   - **A:** prices + rate
   - **B:** + output (industrial production)
   - **C:** + commodity prices

   Responses are scaled to a +1 percentage point rate shock, with 90% residual-bootstrap bands (500 draws).

Main samples end in 2007, before rates hit zero and QE replaced rate changes as the main policy tool.

## Findings

![Price level response](results/price_response.png)

**1. Controls flip the sign in the US.** A +1pp higher Fed funds rate predicts inflation 0.15pp *higher* two years later with no controls, but **0.43pp lower** (s.e. 0.13) once the state of the economy is held fixed.

**2. Each confounder shrinks the "price puzzle".** In the US VAR, the price level's rise after a rate hike falls from +0.66% (A) to +0.34% (B) to +0.17% (C) at 24 months. With commodity prices included, prices are **0.43% lower after four years**, though the 90% band still just includes zero.

**3. Output responds as theory predicts in both countries.** A +1pp shock lowers industrial production by about **1.3% (US) and 1.5% (UK)** after 2–3 years, with bands clearly below zero. Rate rises do slow the economy.

![Output response](results/output_response.png)

**4. The UK price puzzle survives in 1975–2007, but disappears under inflation targeting.** Over the full sample, UK prices rise after a rate shock in every specification. Restricting to the inflation-targeting era (Oct 1992 onwards), prices fall by about **1.1% after four years** (spec C, band just touching zero with only 15 years of data), and the regression with controls gives **−0.30pp** inflation at 24 months (s.e. 0.06).

**5. The US post-1984 sample still shows the puzzle.** This is a known weakness of recursive VARs (Ramey, 2016): when the Fed acts systematically and predictably, few rate moves are true "surprises", so the method struggles to isolate them.

### What this means

The raw positive correlation is misleading. Controlling for confounders moves the estimates towards the textbook answer, and the output effect is robust. But the price effect is weaker and less certain than often claimed, and depends on the monetary regime. The UK result suggests the pre-1992 period, with shifting regimes (monetary targets, the ERM) and an omitted exchange rate, is hard to model with one stable VAR.

### Limitations

- Recursive identification assumes no within-month effect of rates on prices and output.
- The commodity price control is US PPI (all commodities), used for both countries.
- The UK model omits the exchange rate, which matters a lot for a small open economy.
- UK CPI before 1988 is spliced from OECD data, and is seasonally adjusted here with fixed monthly factors.

## Next steps

- [ ] Add the sterling exchange rate to the UK model
- [ ] Local projections (Jordà, 2005) as a robustness check
- [ ] High-frequency monetary policy shocks (market reaction on policy announcement days) to replace the recursive assumption
- [ ] Extend past 2007 using shadow rates or 2-year yields as the policy measure
- [ ] Other claims: money supply and inflation, the Phillips curve

## Data

US: FRED. UK: ONS (CPI, unemployment, industrial production), Bank of England (Bank Rate), OECD via FRED (CPI before 1988). Full details in [`data/README.md`](data/README.md).

## Run it

```bash
pip install -r requirements.txt
python run_analysis.py      # writes results/ (about 1 minute)
pytest                      # tests, incl. a check against statsmodels' VAR
```

## Structure

```
run_analysis.py      regressions, VARs, charts
src/load_data.py     builds the US and UK monthly panels
src/var.py           recursive VAR, impulse responses, bootstrap
tests/               unit tests
data/raw/            source data as downloaded
results/             summary tables and charts
```
