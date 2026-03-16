"""CSV loading, validation, and summary statistics."""

import pandas as pd

REQUIRED_COLS = [
    "Batch", "Temperature", "Pressure", "pH", "Flow",
    "COD", "BOD", "Pigment_R", "Pigment_G", "Pigment_B",
    "Viscosity", "DryerTemp", "MotorCurrent", "Vibration",
    "RuntimeHours", "FailLabel", "Destination", "DueDate", "Quantity",
]

NUMERIC_COLS = [
    "Temperature", "Pressure", "pH", "Flow", "COD", "BOD",
    "Pigment_R", "Pigment_G", "Pigment_B", "Viscosity",
    "DryerTemp", "MotorCurrent", "Vibration", "RuntimeHours", "Quantity",
]


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(missing)}\n\n"
            "Expected: " + ", ".join(REQUIRED_COLS)
        )
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["FailLabel"] = pd.to_numeric(df["FailLabel"], errors="coerce").fillna(0).astype(int)
    df["DueDate"]   = pd.to_datetime(df["DueDate"], errors="coerce")
    df["Batch"]       = df["Batch"].astype(str)
    df["Destination"] = df["Destination"].astype(str)
    return df


def get_summary(df: pd.DataFrame) -> dict:
    return {
        "total_batches": len(df),
        "avg_cod":       round(float(df["COD"].mean()), 2),
        "avg_bod":       round(float(df["BOD"].mean()), 2),
        "fail_count":    int(df["FailLabel"].sum()),
        "fail_rate":     round(float(df["FailLabel"].mean()) * 100, 1),
        "destinations":  int(df["Destination"].nunique()),
        "total_quantity":int(df["Quantity"].sum()),
        "avg_vibration": round(float(df["Vibration"].mean()), 3),
        "avg_runtime":   round(float(df["RuntimeHours"].mean()), 1),
        "avg_temp":      round(float(df["Temperature"].mean()), 1),
        "avg_ph":        round(float(df["pH"].mean()), 2),
        "avg_motor":     round(float(df["MotorCurrent"].mean()), 2),
    }
