import tkinter as tk
from app.ui.dashboard import PigmentProcessMonitoringApp


def launch() -> None:
    root = tk.Tk()
    PigmentProcessMonitoringApp(root)
    root.mainloop()
