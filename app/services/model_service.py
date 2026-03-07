import pandas as pd


def predict_cod(temp, pressure, ph, flow, viscosity):
    return round(88 + temp * 0.72 + pressure * 10 - ph * 4.8 + flow * 0.35 + viscosity * 0.09, 2)


def predict_bod(temp, pressure, ph, flow, viscosity):
    return round(42 + temp * 0.36 + pressure * 4.4 - ph * 2.2 + flow * 0.15 + viscosity * 0.05, 2)


def predict_color(temp, ph, rpm, dryer):
    r = max(0, min(255, int(140 + temp * 0.6 - ph * 3 + rpm * 0.02)))
    g = max(0, min(255, int(110 + dryer * 0.4 + ph * 6 - rpm * 0.01)))
    b = max(0, min(255, int(90 + ph * 8 + temp * 0.2 - dryer * 0.25)))
    return r, g, b


def failure_risk(vibration, motor_current, runtime_hours, dryer_temp):
    score = vibration * 12 + motor_current * 5 + runtime_hours * 0.08 + max(0, dryer_temp - 120) * 0.6
    level = 'Normal' if score < 70 else 'Warning' if score < 110 else 'High Risk'
    return round(min(score, 100), 2), level


def batch_pass_prediction(row: pd.Series):
    cod_ok = row['COD'] < 220
    bod_ok = row['BOD'] < 120
    fail_ok = row['FailLabel'] == 0
    return 'Pass' if cod_ok and bod_ok and fail_ok else 'Review'
