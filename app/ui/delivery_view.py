from tkinter import ttk
from app.ui.common import section
from app.ui.table_view import data_table


def build(parent, delivery_df):
    head = section(parent, 'Delivery Monitoring', 'Orders, schedules, destinations and dispatch status')
    data_table(head, delivery_df, height=8).pack(fill='both', expand=True)
    head.pack(fill='both', expand=True, padx=10, pady=10)
