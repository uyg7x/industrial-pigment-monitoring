from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.services.chart_service import make_line


def chart_panel(parent, df, x, y, title):
    frame = ttk.Frame(parent, style='Card.TFrame', padding=10)
    fig = make_line(df, x, y, title)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    return frame
