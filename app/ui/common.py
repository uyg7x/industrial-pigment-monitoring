import tkinter as tk
from tkinter import ttk
from app.utils import theme


def apply_style(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use('clam')
    root.configure(bg=theme.BG)
    style.configure('TFrame', background=theme.BG)
    style.configure('Card.TFrame', background=theme.CARD)
    style.configure('TLabel', background=theme.BG, foreground=theme.TEXT)
    style.configure('Sub.TLabel', background=theme.BG, foreground=theme.SUB)
    style.configure('Card.TLabel', background=theme.CARD, foreground=theme.TEXT)
    style.configure('TNotebook', background=theme.BG, borderwidth=0)
    style.configure('TNotebook.Tab', padding=(14, 8), background=theme.CARD, foreground=theme.TEXT)
    style.map('TNotebook.Tab', background=[('selected', theme.ACCENT)], foreground=[('selected', '#00111f')])
    return style


def section(parent, title, subtitle=''):
    frame = ttk.Frame(parent, style='Card.TFrame', padding=16)
    ttk.Label(frame, text=title, style='Card.TLabel', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
    if subtitle:
        ttk.Label(frame, text=subtitle, style='Card.TLabel', font=('Segoe UI', 9)).pack(anchor='w', pady=(2, 12))
    return frame
