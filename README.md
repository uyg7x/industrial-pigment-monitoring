# Pigment Process Monitor — Python 3.10+

A modular desktop analytics app for pigment manufacturing, featuring:

- **COD / BOD prediction** — OLS linear model, single-batch and batch-level prediction vs actuals
- **Pigment colour prediction** — RGB deviation analysis with In-Spec / Marginal / Out-of-Spec classification
- **Equipment failure prediction** — Weighted risk scoring (Low / Medium / High / Critical)
- **Delivery tracking** — Due-date status per batch (On Track / Due Soon / Overdue)
- **Charts** — 5 interactive matplotlib views embedded in the UI
- **Excel export** — Colour-coded multi-sheet workbook via openpyxl

## Quick start

```bash
pip install -r requirements.txt
python generate_sample.py        # creates sample_data.csv (optional)
python run.py
```

Then press **Load CSV** and select your file (or `sample_data.csv`).

## CSV format

```
Batch,Temperature,Pressure,pH,Flow,COD,BOD,Pigment_R,Pigment_G,Pigment_B,
Viscosity,DryerTemp,MotorCurrent,Vibration,RuntimeHours,FailLabel,
Destination,DueDate,Quantity
```

`DueDate` must be ISO-8601 (`YYYY-MM-DD`).  
`FailLabel` is `0` (no failure) or `1` (failure).

## File layout

```
pigment_app/
├── run.py                  ← entry point
├── generate_sample.py      ← sample data generator
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py             ← MainApp window + launch()
    ├── tabs.py             ← Dashboard, COD/BOD, Colour, Equipment, Delivery tabs
    ├── charts.py           ← matplotlib charts (ChartsFrame)
    ├── data_loader.py      ← CSV loading & validation
    ├── predictor.py        ← OLS models + risk scoring
    └── exporter.py         ← Excel export (openpyxl)
```

## Requirements

- Python ≥ 3.10
- pandas ≥ 2.0
- matplotlib ≥ 3.7
- openpyxl ≥ 3.1
- tkinter (bundled with Python on Windows/macOS; `sudo apt install python3-tk` on Ubuntu)
