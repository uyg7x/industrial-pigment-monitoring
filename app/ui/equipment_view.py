from tkinter import ttk
from app.ui.common import section
from app.ui.charts_view import chart_panel


def build(parent, process_df):
    head = section(parent, 'Equipment Monitoring', 'Machine condition, runtime, vibration and current patterns')
    head.pack(fill='x', padx=10, pady=10)
    charts = ttk.Frame(parent)
    charts.pack(fill='x', padx=10)
    chart_panel(charts, process_df, 'Batch', 'Vibration', 'Vibration Trend').pack(side='left', fill='both', expand=True, padx=5)
    chart_panel(charts, process_df, 'Batch', 'MotorCurrent', 'Motor Current Trend').pack(side='left', fill='both', expand=True, padx=5)
