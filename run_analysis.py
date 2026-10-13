"""Does raising interest rates lower inflation? US and UK evidence.

Three steps, each adding a layer of control for confounding:

1. Naive correlation between the policy rate and inflation
2. Regressions of future inflation on today's rate, with and without controls
3. Recursive VARs, adding confounders one at a time, to trace the response
   of the price level to a +1 percentage point interest rate shock

Usage:
    python run_analysis.py            # full run, 500 bootstrap draws
    python run_analysis.py --quick    # 100 draws, for a fast check
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.load_data import load
from src.var import bootstrap_irf

OUT = Path(__file__).resolve().parent / "results"
LAGS = 12
HORIZON = 48
REPS = 100 if "--quick" in sys.argv else 500

SAMPLES = {
    # Main samples end in 2007, before rates hit zero and QE took over
    "US": [("1965-01", "2007-12", "main"), ("1984-01", "2007-12", "post-Volcker")],
    "UK": [("1975-01", "2007-12", "main"), ("1992-10", "2007-12", "inflation targeting")],
}

SPECS = {
    "A: prices + rate": ["prices", "rate"],
    "B: + output": ["output", "prices", "rate"],
    "C: + commodity prices": ["output", "prices", "commod", "rate"],
}
RATE_NAME = {"US": "Fed funds rate", "UK": "Bank Rate"}


def naive_correlations(df: pd.DataFrame) -> dict:
    d = df[["rate", "infl"]].dropna()
    return {
        "same month": d["rate"].corr(d["infl"]),
        "inflation 12m later": d["rate"].corr(d["infl"].shift(-12)),
        "inflation 24m later": d["rate"].corr(d["infl"].shift(-24)),
    }


def forecast_regression(df: pd.DataFrame, h: int, controls: bool):
    """Regress inflation h months ahead on today's rate (Newey-West errors)."""
    d = pd.DataFrame({"y": df["infl"].shift(-h), "rate": df["rate"]})
    if controls:
        d["infl"] = df["infl"]
        d["infl_l12"] = df["infl"].shift(12)
        d["unemp"] = df["unemp"]
        d["output_growth"] = df["output"].diff(12)
        d["commod_growth"] = df["commod"].diff(12)
    d = d.dropna()
    res = sm.OLS(d["y"], sm.add_constant(d.drop(columns="y"))).fit(
        cov_type="HAC", cov_kwds={"maxlags": h + 1})
    return res.params["rate"], res.bse["rate"], int(res.nobs)


def summarise(boot: dict, var: str, horizons=(12, 24, 36, 48)) -> dict:
    j = boot["names"].index(var)
    out = {}
    for h in horizons:
        draws = boot["draws"][:, h, j]
        lo, hi = np.percentile(draws, [5, 95])
        out[h] = (boot["point"][h, j], lo, hi)
    return out


def main() -> None:
    OUT.mkdir(exist_ok=True)
    lines, rows = [], []
    boots = {}

    for country, samples in SAMPLES.items():
        df_all = load(country)
        for start, end, label in samples:
            df = df_all.loc[start:end]
            lines.append(f"\n=== {country} {start} to {end} ({label}) ===")

            lines.append("Naive correlation of rate with inflation:")
            for k, v in naive_correlations(df).items():
                lines.append(f"  {k:22s} {v:+.2f}")

            lines.append("Effect of +1pp rate today on inflation h months ahead (pp):")
            for h in (12, 24):
                for ctrl in (False, True):
                    b, se, n = forecast_regression(df, h, ctrl)
                    tag = "with controls" if ctrl else "no controls  "
                    lines.append(f"  h={h:2d} {tag} {b:+.2f} (se {se:.2f}, n={n})")
                    rows.append(dict(country=country, sample=label, method=f"regression {tag.strip()}",
                                     horizon=h, estimate=b, lo=b - 1.645 * se, hi=b + 1.645 * se))

            lines.append("VAR: response of price level (%) to a +1pp rate shock [90% band]:")
            for spec, cols in SPECS.items():
                data = df[cols].dropna()
                boot = bootstrap_irf(data, LAGS, HORIZON, "rate", reps=REPS)
                boots[(country, label, spec)] = boot
                s = summarise(boot, "prices")
                txt = "  ".join(f"{h}m {v[0]:+.2f} [{v[1]:+.2f},{v[2]:+.2f}]" for h, v in s.items())
                lines.append(f"  {spec:24s} {txt}")
                for h, (pt, lo, hi) in s.items():
                    rows.append(dict(country=country, sample=label, method=f"VAR {spec}",
                                     horizon=h, estimate=pt, lo=lo, hi=hi))
                if "output" in cols:
                    so = summarise(boot, "output")
                    rows += [dict(country=country, sample=label, method=f"VAR {spec} (output)",
                                  horizon=h, estimate=v[0], lo=v[1], hi=v[2]) for h, v in so.items()]

    text = "\n".join(lines)
    print(text)
    (OUT / "summary.txt").write_text(text + "\n")
    pd.DataFrame(rows).round(3).to_csv(OUT / "summary.csv", index=False)
    plot_price_responses(boots)
    plot_output_responses(boots)


def _band(ax, boot, var, color, label):
    j = boot["names"].index(var)
    x = np.arange(boot["point"].shape[0])
    lo, hi = np.percentile(boot["draws"][:, :, j], [5, 95], axis=0)
    ax.fill_between(x, lo, hi, color=color, alpha=0.15, lw=0)
    ax.plot(x, boot["point"][:, j], color=color, lw=2, label=label)


def plot_price_responses(boots: dict) -> None:
    colors = ["#c0392b", "#e67e22", "#2471a3"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, country in zip(axes, ["US", "UK"]):
        for color, spec in zip(colors, SPECS):
            _band(ax, boots[(country, "main", spec)], "prices", color, spec)
        start, end, _ = SAMPLES[country][0]
        ax.axhline(0, color="black", lw=0.8)
        ax.set_title(f"{country}: price level after +1pp {RATE_NAME[country]} shock\n({start[:4]} to {end[:4]})")
        ax.set_xlabel("Months after shock")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("% change in price level")
    axes[0].legend(frameon=False, fontsize=9)
    fig.text(0.5, -0.02, "Shaded areas: 90% bootstrap bands. Rate ordered last in a recursive VAR with 12 lags.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout()
    fig.savefig(OUT / "price_response.png", dpi=150, bbox_inches="tight")


def plot_output_responses(boots: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    spec = "C: + commodity prices"
    for ax, country in zip(axes, ["US", "UK"]):
        _band(ax, boots[(country, "main", spec)], "output", "#2471a3", "Industrial production")
        ax.axhline(0, color="black", lw=0.8)
        ax.set_title(f"{country}: output after +1pp {RATE_NAME[country]} shock (spec C)")
        ax.set_xlabel("Months after shock")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("% change in industrial production")
    fig.tight_layout()
    fig.savefig(OUT / "output_response.png", dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    main()
