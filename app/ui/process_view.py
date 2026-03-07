from tkinter import ttk
from app.ui.common import section
from app.ui.cards import metric_grid
from app.ui.table_view import data_table
from app.ui.charts_view import chart_panel
from app.services.analytics_service import summary


def build(parent, process_df):
    stats = section(parent, 'Process Overview', 'Core process KPIs and recent production records')
    metric_grid(stats, summary(process_df))
    stats.pack(fill='x', padx=10, pady=10)

    charts = ttk.Frame(parent)
    charts.pack(fill='x', padx=10)
    chart_panel(charts, process_df, 'Batch', 'COD', 'COD Trend').pack(side='left', fill='both', expand=True, padx=5)
    chart_panel(charts, process_df, 'Batch', 'BOD', 'BOD Trend').pack(side='left', fill='both', expand=True, padx=5)

    table_sec = section(parent, 'Recent Batch Data')
    data_table(table_sec, process_df).pack(fill='both', expand=True)
    table_sec.pack(fill='both', expand=True, padx=10, pady=10)
