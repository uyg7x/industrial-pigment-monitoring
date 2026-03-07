from tkinter import ttk


def metric_grid(parent, metrics: dict):
    wrap = ttk.Frame(parent, style='Card.TFrame')
    wrap.pack(fill='x')
    for i, (label, value) in enumerate(metrics.items()):
        card = ttk.Frame(wrap, style='Card.TFrame', padding=14)
        r, c = divmod(i, 3)
        card.grid(row=r, column=c, sticky='nsew', padx=6, pady=6)
        wrap.columnconfigure(c, weight=1)
        ttk.Label(card, text=label, style='Card.TLabel', font=('Segoe UI', 9)).pack(anchor='w')
        ttk.Label(card, text=str(value), style='Card.TLabel', font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(6, 0))
    return wrap
