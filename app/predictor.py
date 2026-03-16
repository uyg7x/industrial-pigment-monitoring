"""Prediction models — OLS regression, colour deviation, equipment risk scoring."""

import numpy as np
import pandas as pd

_COD_BOD_FEATURES = ["Temperature", "Pressure", "pH", "Flow", "Viscosity"]


def _ols(X, y):
    X_b = np.c_[np.ones(len(X)), X]
    coef, _, _, _ = np.linalg.lstsq(X_b, y, rcond=None)
    return coef


def _norm(s):
    lo, hi = s.min(), s.max()
    return pd.Series(0.5, index=s.index) if hi == lo else (s - lo) / (hi - lo)


# ── COD / BOD ─────────────────────────────────────────────────────────────────

def predict_cod_bod(df: pd.DataFrame) -> pd.DataFrame:
    result = df[["Batch"]].copy().reset_index(drop=True)
    for target in ("COD", "BOD"):
        cols  = _COD_BOD_FEATURES + [target]
        valid = df[cols].dropna()
        actual = df[target].reset_index(drop=True)
        result[f"{target}_Actual"] = actual
        if len(valid) < 4:
            result[f"{target}_Pred"]     = np.nan
            result[f"{target}_Residual"] = np.nan
            continue
        coef   = _ols(valid[_COD_BOD_FEATURES].values, valid[target].values)
        X_all  = df[_COD_BOD_FEATURES].fillna(df[_COD_BOD_FEATURES].median()).values
        pred   = np.round(np.c_[np.ones(len(X_all)), X_all] @ coef, 2)
        result[f"{target}_Pred"]     = pred
        result[f"{target}_Residual"] = np.round(actual - pred, 2)
    return result


def predict_single_cod_bod(df: pd.DataFrame, inputs: dict) -> dict:
    out = {}
    medians = df[_COD_BOD_FEATURES].median()
    for target in ("COD", "BOD"):
        valid = df[_COD_BOD_FEATURES + [target]].dropna()
        if len(valid) < 4:
            out[target] = None
            continue
        coef  = _ols(valid[_COD_BOD_FEATURES].values, valid[target].values)
        x_vec = np.array([inputs.get(f, medians[f]) for f in _COD_BOD_FEATURES])
        out[target] = round(float(np.r_[1.0, x_vec] @ coef), 2)
    return out


# ── Pigment colour ────────────────────────────────────────────────────────────

def predict_color(df: pd.DataFrame) -> pd.DataFrame:
    result = df[["Batch"]].copy().reset_index(drop=True)
    r = df["Pigment_R"].fillna(0).values.astype(float)
    g = df["Pigment_G"].fillna(0).values.astype(float)
    b = df["Pigment_B"].fillna(0).values.astype(float)
    # Auto-scale if 0-1 range
    if r.max() <= 1.0: r = r * 255
    if g.max() <= 1.0: g = g * 255
    if b.max() <= 1.0: b = b * 255
    result["R"] = np.clip(r, 0, 255).astype(int)
    result["G"] = np.clip(g, 0, 255).astype(int)
    result["B"] = np.clip(b, 0, 255).astype(int)
    result["Hex"] = result.apply(
        lambda row: "#{:02X}{:02X}{:02X}".format(row["R"], row["G"], row["B"]), axis=1)
    for ch in ("R", "G", "B"):
        mu  = result[ch].mean()
        sig = result[ch].std() or 1.0
        result[f"z_{ch}"] = (result[ch] - mu) / sig
    result["Deviation"] = np.round(
        np.sqrt(result["z_R"]**2 + result["z_G"]**2 + result["z_B"]**2), 3)
    result.drop(columns=["z_R","z_G","z_B"], inplace=True)
    result["Color_Status"] = result["Deviation"].apply(
        lambda d: "In-Spec" if d < 1.5 else ("Marginal" if d < 2.5 else "Out-of-Spec"))
    return result


# ── Equipment failure ─────────────────────────────────────────────────────────

def predict_equipment(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Batch","MotorCurrent","Vibration","RuntimeHours","DryerTemp","FailLabel"]
    result = df[cols].copy().reset_index(drop=True)
    risk = (
        0.35 * _norm(result["Vibration"].fillna(0))
      + 0.30 * _norm(result["MotorCurrent"].fillna(0))
      + 0.20 * _norm(result["RuntimeHours"].fillna(0))
      + 0.15 * _norm(result["DryerTemp"].fillna(0))
    )
    result["Risk_Score"] = (risk * 100).round(1)
    result["Risk_Level"] = result["Risk_Score"].apply(
        lambda s: "Low" if s < 30 else ("Medium" if s < 55 else ("High" if s < 75 else "Critical")))
    return result
