"""Recursive (Cholesky) VAR with bootstrapped impulse responses.

The identifying assumption is the ordering of the variables: the interest
rate is placed last, so a monetary policy shock can affect output and prices
only from the following month onwards, while the central bank can react to
everything ordered before it within the month. This is the standard approach
of Christiano, Eichenbaum and Evans (1999).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class VARFit:
    coefs: np.ndarray      # (k*p + 1, k) stacked [const, lag1, ..., lagp]
    resid: np.ndarray      # (T, k)
    sigma: np.ndarray      # (k, k) residual covariance
    p: int
    names: list
    data: np.ndarray       # (T + p, k) original data used


def _lag_matrix(y: np.ndarray, p: int) -> np.ndarray:
    T = y.shape[0]
    X = [np.ones((T - p, 1))]
    for lag in range(1, p + 1):
        X.append(y[p - lag: T - lag])
    return np.hstack(X)


def fit_var(df: pd.DataFrame, p: int = 12) -> VARFit:
    y = df.to_numpy(dtype=float)
    X = _lag_matrix(y, p)
    Y = y[p:]
    coefs, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ coefs
    dof = Y.shape[0] - X.shape[1]
    sigma = resid.T @ resid / dof
    return VARFit(coefs, resid, sigma, p, list(df.columns), y)


def impulse_response(fit: VARFit, horizon: int, shock: str, scale_to_impact: float = 1.0) -> np.ndarray:
    """Responses of all variables to an orthogonalised shock in `shock`.

    The shock is scaled so the shocked variable moves by `scale_to_impact`
    on impact (e.g. a 1 percentage point rise in the policy rate).
    Returns an array of shape (horizon + 1, k).
    """
    k, p = len(fit.names), fit.p
    A = [fit.coefs[1 + i * k: 1 + (i + 1) * k].T for i in range(p)]
    P = np.linalg.cholesky(fit.sigma)
    j = fit.names.index(shock)
    impact = P[:, j] * scale_to_impact / P[j, j]

    irf = np.zeros((horizon + 1, k))
    irf[0] = impact
    for h in range(1, horizon + 1):
        for i in range(min(h, p)):
            irf[h] += A[i] @ irf[h - 1 - i]
    return irf


def _simulate(fit: VARFit, resid: np.ndarray) -> np.ndarray:
    k, p = len(fit.names), fit.p
    T = resid.shape[0]
    y = np.zeros((T + p, k))
    y[:p] = fit.data[:p]
    c = fit.coefs[0]
    A = [fit.coefs[1 + i * k: 1 + (i + 1) * k].T for i in range(p)]
    for t in range(p, T + p):
        y[t] = c + resid[t - p] + sum(A[i] @ y[t - 1 - i] for i in range(p))
    return y


def bootstrap_irf(df: pd.DataFrame, p: int, horizon: int, shock: str,
                  reps: int = 500, seed: int = 0) -> dict:
    """Point estimate plus residual-bootstrap draws of the impulse responses."""
    rng = np.random.default_rng(seed)
    fit = fit_var(df, p)
    point = impulse_response(fit, horizon, shock)
    draws = np.empty((reps, horizon + 1, len(fit.names)))
    T = fit.resid.shape[0]
    for r in range(reps):
        sim = _simulate(fit, fit.resid[rng.integers(0, T, T)])
        draws[r] = impulse_response(fit_var(pd.DataFrame(sim, columns=fit.names), p), horizon, shock)
    return {"point": point, "draws": draws, "names": fit.names, "fit": fit}
