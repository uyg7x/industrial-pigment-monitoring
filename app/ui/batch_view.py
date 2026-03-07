from tkinter import ttk
from app.ui.common import section
from app.ui.table_view import data_table


def build(parent, process_df):
    frame = section(parent, 'Batch Management', 'Batch-wise traceability, quality outcome and operator review')
    view = process_df[['Batch', 'Operator', 'Stage', 'Output', 'COD', 'BOD', 'ColorScore', 'FailLabel']].copy()
    data_table(frame, view, height=9).pack(fill='both', expand=True)
    frame.pack(fill='both', expand=True, padx=10, pady=10)
