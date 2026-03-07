import tkinter as tk
from tkinter import ttk
from app.utils import theme


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        bar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.body = ttk.Frame(canvas)
        self.body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.body, anchor='nw')
        canvas.configure(yscrollcommand=bar.set)
        canvas.pack(side='left', fill='both', expand=True)
        bar.pack(side='right', fill='y')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(1, width=e.width))
        self._bind_wheel(canvas)

    def _bind_wheel(self, canvas):
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-e.delta / 120), 'units'))
