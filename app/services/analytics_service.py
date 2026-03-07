import pandas as pd
from app.services.model_service import batch_pass_prediction


def summary(df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]
    return {
        'Batches': int(len(df)),
        'Avg COD': round(df['COD'].mean(), 2),
        'Avg BOD': round(df['BOD'].mean(), 2),
        'Failure Risk %': round(df['FailLabel'].mean() * 100, 1),
        'Avg Output': round(df['Output'].mean(), 2),
        'Latest Batch': latest['Batch'],
    }


def alerts(df, inventory, deliveries):
    items = []
    latest = df.iloc[-1]
    if latest['COD'] > 220:
        items.append(f"High COD alert in {latest['Batch']}: {latest['COD']}")
    if latest['BOD'] > 120:
        items.append(f"High BOD alert in {latest['Batch']}: {latest['BOD']}")
    if latest['Vibration'] > 4.5 or latest['MotorCurrent'] > 18:
        items.append('Equipment warning: inspect mixer motor and vibration line.')
    low_stock = inventory[inventory['StockKg'] <= inventory['ReorderLevelKg']]
    items += [f"Low stock: {r.Material} ({r.StockKg} kg)" for _, r in low_stock.iterrows()]
    delayed = deliveries[deliveries['Status'] == 'Delayed']
    items += [f"Delayed delivery: {r.OrderID} to {r.Destination}" for _, r in delayed.iterrows()]
    return items or ['All monitored values are within normal operating range.']


def recommendations(df):
    last = df.iloc[-1]
    recs = []
    if last['pH'] < 6.7:
        recs.append('Increase pH slightly to reduce COD/BOD stress.')
    if last['DryerTemp'] > 126:
        recs.append('Reduce dryer temperature to improve pigment color stability.')
    if last['Vibration'] > 4.5:
        recs.append('Schedule predictive maintenance for the main mixer.')
    recs.append(f"Batch quality status: {batch_pass_prediction(last)}")
    return recs
