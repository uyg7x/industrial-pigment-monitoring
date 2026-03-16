"""Generate realistic sample CSV for testing the Pigment Process Monitor."""

import argparse
import numpy as np
import pandas as pd
from datetime import date, timedelta

RNG = np.random.default_rng(42)

DESTINATIONS = [
    "Hamburg", "Rotterdam", "Barcelona", "Istanbul",
    "Mumbai", "Singapore", "Shanghai", "New York",
]


def generate(n: int = 100) -> pd.DataFrame:
    temperature  = RNG.normal(75, 8, n).clip(50, 100)
    pressure     = (1.5 + (temperature - 75) * 0.05 + RNG.normal(0, 0.3, n)).clip(0.5, 5.0)
    ph           = RNG.normal(7.0, 0.6, n).clip(5.0, 9.5)
    flow         = RNG.normal(100, 15, n).clip(50, 160)
    viscosity    = (40 + (ph - 7) * 5 + RNG.normal(0, 8, n)).clip(10, 120)
    cod          = (50 + 0.8*temperature + 10*(ph-7) + 0.3*flow + RNG.normal(0,12,n)).clip(20,300)
    bod          = (0.35*cod + 10 + RNG.normal(0, 6, n)).clip(5, 120)
    pigment_r    = (180 + RNG.normal(0, 15, n)).clip(0, 255).astype(int)
    pigment_g    = (60  + RNG.normal(0, 12, n)).clip(0, 255).astype(int)
    pigment_b    = (90  + RNG.normal(0, 18, n)).clip(0, 255).astype(int)
    dryer_temp   = RNG.normal(140, 10, n).clip(100, 200)
    motor_current= RNG.normal(25, 5, n).clip(10, 60)
    vibration    = RNG.exponential(0.8, n).clip(0, 8)
    runtime_hours= RNG.uniform(0, 8760, n)
    risk_raw     = (
        (vibration/8)*0.45
        + ((motor_current-10)/50)*0.30
        + (runtime_hours/8760)*0.25
    )
    fail_label   = (risk_raw > RNG.uniform(0.55, 1.0, n)).astype(int)
    today        = date.today()
    due_dates    = [today + timedelta(days=int(d)) for d in RNG.integers(-5, 30, n)]
    destinations = RNG.choice(DESTINATIONS, n)
    quantities   = RNG.integers(200, 5000, n)

    return pd.DataFrame({
        "Batch":        [f"B{i+1:04d}" for i in range(n)],
        "Temperature":  np.round(temperature, 1),
        "Pressure":     np.round(pressure, 2),
        "pH":           np.round(ph, 2),
        "Flow":         np.round(flow, 1),
        "COD":          np.round(cod, 1),
        "BOD":          np.round(bod, 1),
        "Pigment_R":    pigment_r,
        "Pigment_G":    pigment_g,
        "Pigment_B":    pigment_b,
        "Viscosity":    np.round(viscosity, 1),
        "DryerTemp":    np.round(dryer_temp, 1),
        "MotorCurrent": np.round(motor_current, 2),
        "Vibration":    np.round(vibration, 4),
        "RuntimeHours": np.round(runtime_hours, 1),
        "FailLabel":    fail_label,
        "Destination":  destinations,
        "DueDate":      [d.isoformat() for d in due_dates],
        "Quantity":     quantities,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--out",  type=str, default="sample_data.csv")
    args = parser.parse_args()
    df = generate(args.rows)
    df.to_csv(args.out, index=False)
    print(f"Generated {args.rows} rows -> {args.out}")
    print(f"  Failure rate : {df['FailLabel'].mean():.1%}")
    print(f"  Destinations : {', '.join(sorted(df['Destination'].unique()))}")
