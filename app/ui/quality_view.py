from tkinter import ttk
from app.ui.common import section
from app.ui.charts_view import chart_panel


def build(parent, process_df):
    top = section(parent, 'Quality Monitoring', 'COD, BOD, color and output analysis')
    msg = 'Track critical water-quality and product-quality indicators across batches.'
    ttk.Label(top, text=msg, style='Card.TLabel', wraplength=900).pack(anchor='w')
    top.pack(fill='x', padx=10, pady=10)

    charts = ttk.Frame(parent)
    charts.pack(fill='x', padx=10)
    chart_panel(charts, process_df, 'Batch', 'Output', 'Production Output').pack(side='left', fill='both', expand=True, padx=5)
    chart_panel(charts, process_df, 'Batch', 'ColorScore', 'Pigment Color Score').pack(side='left', fill='both', expand=True, padx=5)
