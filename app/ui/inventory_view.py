from tkinter import ttk
from app.ui.common import section
from app.ui.table_view import data_table


def build(parent, inventory_df):
    head = section(parent, 'Inventory Management', 'Material stock, reorder points and usage visibility')
    data_table(head, inventory_df, height=8).pack(fill='both', expand=True)
    head.pack(fill='both', expand=True, padx=10, pady=10)
