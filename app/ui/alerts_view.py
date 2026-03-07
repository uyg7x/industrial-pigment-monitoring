from tkinter import ttk
from app.ui.common import section
from app.services.analytics_service import alerts, recommendations


def build(parent, process_df, inventory_df, delivery_df):
    frame = section(parent, 'Alerts and Recommendations', 'Actionable notifications for operators and managers')
    ttk.Label(frame, text='Alerts', style='Card.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor='w')
    for item in alerts(process_df, inventory_df, delivery_df):
        ttk.Label(frame, text='• ' + item, style='Card.TLabel', wraplength=950).pack(anchor='w', pady=2)
    ttk.Label(frame, text='Recommendations', style='Card.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(14, 4))
    for item in recommendations(process_df):
        ttk.Label(frame, text='• ' + item, style='Card.TLabel', wraplength=950).pack(anchor='w', pady=2)
    frame.pack(fill='x', padx=10, pady=10)
