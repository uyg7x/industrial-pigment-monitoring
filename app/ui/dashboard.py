import tkinter as tk
from tkinter import ttk
from app.services.data_service import load_deliveries, load_inventory, load_process
from app.ui import alerts_view, batch_view, delivery_view, equipment_view, inventory_view, prediction_view, process_view, quality_view, reports_view
from app.ui.common import apply_style
from app.ui.scrollable import ScrollableFrame
from app.utils import theme


class PigmentProcessMonitoringApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(theme.TITLE)
        self.root.geometry(theme.WINDOW)
        apply_style(root)
        self.process_df = load_process()
        self.inventory_df = load_inventory()
        self.delivery_df = load_deliveries()
        self._build_layout()

    def _build_layout(self):
        header = ttk.Frame(self.root, padding=(18, 14), style='Card.TFrame')
        header.pack(fill='x', padx=10, pady=10)
        ttk.Label(header, text='Pigment Process Monitoring', style='Card.TLabel', font=('Segoe UI', 22, 'bold')).pack(anchor='w')
        ttk.Label(header, text='Operations dashboard for quality, equipment, stock, deliveries and predictive insights', style='Card.TLabel').pack(anchor='w')

        book = ttk.Notebook(self.root)
        book.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        tabs = [
            ('Dashboard', lambda p: process_view.build(p, self.process_df)),
            ('Quality', lambda p: quality_view.build(p, self.process_df)),
            ('Predictions', prediction_view.build),
            ('Equipment', lambda p: equipment_view.build(p, self.process_df)),
            ('Batches', lambda p: batch_view.build(p, self.process_df)),
            ('Inventory', lambda p: inventory_view.build(p, self.inventory_df)),
            ('Deliveries', lambda p: delivery_view.build(p, self.delivery_df)),
            ('Alerts', lambda p: alerts_view.build(p, self.process_df, self.inventory_df, self.delivery_df)),
            ('Reports', lambda p: reports_view.build(p, self.process_df, self.inventory_df, self.delivery_df)),
        ]
        for name, builder in tabs:
            pane = ScrollableFrame(book)
            book.add(pane, text=name)
            builder(pane.body)
