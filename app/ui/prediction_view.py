import tkinter as tk
from tkinter import ttk
from app.ui.common import section
from app.services.model_service import predict_cod, predict_bod, predict_color, failure_risk


def build(parent):
    frame = section(parent, 'Prediction Studio', 'Estimate quality and machine risk from process inputs')
    fields = ['Temperature', 'Pressure', 'pH', 'Flow', 'Viscosity', 'RPM', 'DryerTemp', 'MotorCurrent', 'Vibration', 'RuntimeHours']
    entries = {name: tk.StringVar(value='0') for name in fields}
    grid = ttk.Frame(frame, style='Card.TFrame'); grid.pack(fill='x')
    for i, name in enumerate(fields):
        ttk.Label(grid, text=name, style='Card.TLabel').grid(row=i//2, column=(i%2)*2, sticky='w', padx=6, pady=6)
        ttk.Entry(grid, textvariable=entries[name], width=16).grid(row=i//2, column=(i%2)*2+1, padx=6, pady=6)
    out = tk.StringVar(value='Enter values and click Predict')

    def run_prediction():
        vals = {k: float(v.get() or 0) for k, v in entries.items()}
        cod = predict_cod(vals['Temperature'], vals['Pressure'], vals['pH'], vals['Flow'], vals['Viscosity'])
        bod = predict_bod(vals['Temperature'], vals['Pressure'], vals['pH'], vals['Flow'], vals['Viscosity'])
        rgb = predict_color(vals['Temperature'], vals['pH'], vals['RPM'], vals['DryerTemp'])
        risk, level = failure_risk(vals['Vibration'], vals['MotorCurrent'], vals['RuntimeHours'], vals['DryerTemp'])
        out.set(f'Predicted COD: {cod} | Predicted BOD: {bod} | Color RGB: {rgb} | Failure Risk: {risk}% ({level})')

    ttk.Button(frame, text='Predict', command=run_prediction).pack(anchor='w', pady=10)
    ttk.Label(frame, textvariable=out, style='Card.TLabel', wraplength=980).pack(anchor='w')
    frame.pack(fill='x', padx=10, pady=10)
