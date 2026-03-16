"""
Pigment Process Control System — Main Window v3.1
Industrial HMI design. Entry point: launch()
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from datetime import datetime

from app import theme as T
from app.data_loader import load_csv
from app.predictor import predict_cod_bod, predict_color, predict_equipment
from app.charts import ChartsFrame
from app.tabs import DashboardTab, CodBodTab, ColorTab, EquipmentTab, DeliveryTab
from app.widgets import LED


def _configure_styles():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TNotebook",
                    background=T.BG_DEEP, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=T.BG_RAISED, foreground=T.TEXT_SEC,
                    padding=[20, 9],
                    font=("Courier New", 9, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", T.BG_BASE)],
              foreground=[("selected", T.CYAN)])

    style.configure("HMI.TFrame", background=T.BG_BASE)
    style.configure("TFrame",     background=T.BG_BASE)
    style.configure("TLabel",
                    background=T.BG_BASE, foreground=T.TEXT_PRI,
                    font=("Courier New", 9))

    style.configure("Treeview",
                    background=T.BG_PANEL,
                    foreground=T.TEXT_PRI,
                    fieldbackground=T.BG_PANEL,
                    rowheight=24,
                    font=("Courier New", 9))
    style.configure("Treeview.Heading",
                    background=T.BG_RAISED,
                    foreground=T.CYAN,
                    font=("Courier New", 8, "bold"),
                    relief="flat")
    style.map("Treeview",
              background=[("selected", T.CYAN_DIM)],
              foreground=[("selected", "#FFFFFF")])

    style.configure("TScrollbar",
                    background=T.BG_RAISED,
                    troughcolor=T.BG_DEEP,
                    borderwidth=0,
                    arrowsize=10)


class MainApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PIGMENT PROCESS CONTROL SYSTEM  v3.1")
        self.root.geometry("1420x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg=T.BG_DEEP)

        self.df            = None
        self.cod_bod_preds = None
        self.color_preds   = None
        self.equip_preds   = None

        _configure_styles()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()
        self._tick_clock()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=T.BG_RAISED, height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Left accent bar
        tk.Frame(hdr, bg=T.CYAN, width=5).pack(side="left", fill="y")

        # Wordmark
        logo = tk.Frame(hdr, bg=T.BG_RAISED)
        logo.pack(side="left", padx=(14, 0), pady=8)
        tk.Label(logo,
                 text="⬡  PIGMENT PROCESS CONTROL SYSTEM",
                 bg=T.BG_RAISED, fg=T.CYAN,
                 font=("Courier New", 13, "bold")).pack(anchor="w")
        tk.Label(logo,
                 text="INDUSTRIAL ANALYTICS PLATFORM  |  REV 3.1  |  ALL MODULES ACTIVE",
                 bg=T.BG_RAISED, fg=T.TEXT_DIM,
                 font=("Courier New", 8)).pack(anchor="w")

        tk.Frame(hdr, bg=T.BORDER, width=1).pack(
            side="left", fill="y", padx=18, pady=12)

        # System status
        status_block = tk.Frame(hdr, bg=T.BG_RAISED)
        status_block.pack(side="left", pady=14)
        self._sys_led = LED(status_block, color=T.AMBER,
                            size=10, bg=T.BG_RAISED)
        self._sys_led.pack(side="left", padx=(0, 5))
        self._sys_label = tk.Label(status_block,
                                   text="NO DATA LOADED",
                                   bg=T.BG_RAISED, fg=T.AMBER,
                                   font=("Courier New", 9, "bold"))
        self._sys_label.pack(side="left")

        # Right: clock + buttons
        self._clock_var = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._clock_var,
                 bg=T.BG_RAISED, fg=T.TEXT_SEC,
                 font=("Courier New", 9)).pack(side="right", padx=14)
        tk.Frame(hdr, bg=T.BORDER, width=1).pack(
            side="right", fill="y", padx=0, pady=12)

        for text, cmd, fg, bg_col in [
            ("EXPORT XLSX", self._export_excel, T.TEXT_SEC, T.BG_PANEL),
            ("LOAD CSV",    self._load_file,    "#FFFFFF",  T.CYAN),
        ]:
            tk.Button(hdr, text=text, command=cmd,
                      bg=bg_col, fg=fg,
                      font=("Courier New", 9, "bold"),
                      relief="flat", padx=14, pady=7,
                      cursor="hand2",
                      activebackground=(T.CYAN_DIM if bg_col == T.CYAN
                                        else T.BG_RAISED),
                      activeforeground="#FFFFFF",
                      ).pack(side="right", padx=(0, 8), pady=12)

        tk.Frame(self.root, bg=T.CYAN,   height=2).pack(fill="x")
        tk.Frame(self.root, bg=T.BORDER, height=1).pack(fill="x")

    def _tick_clock(self):
        self._clock_var.set(
            datetime.now().strftime("SYS TIME  %Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    # ── Notebook ──────────────────────────────────────────────────────────────

    def _build_notebook(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)

        self.tab_dashboard = DashboardTab(self.nb, self)
        self.tab_cod_bod   = CodBodTab(self.nb, self)
        self.tab_color     = ColorTab(self.nb, self)
        self.tab_equipment = EquipmentTab(self.nb, self)
        self.tab_delivery  = DeliveryTab(self.nb, self)
        self.tab_charts    = ChartsFrame(self.nb, self)

        for tab, label in [
            (self.tab_dashboard,  "  DASHBOARD  "),
            (self.tab_cod_bod,    "  COD / BOD  "),
            (self.tab_color,      "  COLOUR  "),
            (self.tab_equipment,  "  EQUIPMENT  "),
            (self.tab_delivery,   "  DELIVERY  "),
            (self.tab_charts,     "  CHARTS  "),
        ]:
            self.nb.add(tab, text=label)

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_statusbar(self):
        self._status_var = tk.StringVar(
            value="SYSTEM READY — AWAITING DATA INPUT")
        bar = tk.Frame(self.root, bg=T.BG_DEEP, height=24,
                       highlightbackground=T.BORDER,
                       highlightthickness=1)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=T.BORDER, width=1).pack(side="left", fill="y")
        tk.Label(bar, text=" ◈ ",
                 bg=T.BG_DEEP, fg=T.CYAN_DIM,
                 font=("Courier New", 8)).pack(side="left")
        tk.Label(bar, textvariable=self._status_var,
                 bg=T.BG_DEEP, fg=T.TEXT_SEC,
                 font=("Courier New", 8), anchor="w").pack(side="left")

    def _set_status(self, msg: str):
        self._status_var.set(msg)
        self.root.update_idletasks()

    # ── File actions ──────────────────────────────────────────────────────────

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Open Process CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return
        self._set_status("LOADING DATA...")
        try:
            df = load_csv(path)
            self.df            = df
            self.cod_bod_preds = predict_cod_bod(df)
            self.color_preds   = predict_color(df)
            self.equip_preds   = predict_equipment(df)

            fname  = Path(path).name
            fail_n = int(df["FailLabel"].sum())
            fail_r = round(float(df["FailLabel"].mean()) * 100, 1)

            self._set_status(
                f"ACTIVE: {fname}  |  {len(df)} BATCHES  |  "
                f"{len(df.columns)} CHANNELS  |  "
                f"FAILURES: {fail_n} ({fail_r}%)  |  ALL MODELS COMPUTED"
            )
            self._sys_label.config(text="SYSTEM ONLINE", fg=T.GREEN_HMI)
            self._sys_led.set_color(T.GREEN_HMI, blink=False)

            for tab in (self.tab_dashboard, self.tab_cod_bod,
                        self.tab_color, self.tab_equipment,
                        self.tab_delivery, self.tab_charts):
                tab.refresh()

        except Exception as exc:
            import traceback
            detail = traceback.format_exc()
            self._set_status(f"LOAD FAILED: {exc}")
            self._sys_label.config(text="LOAD ERROR", fg=T.RED_HMI)
            self._sys_led.set_color(T.RED_HMI, blink=True)
            messagebox.showerror("Load Error", f"{exc}\n\n{detail}")

    def _export_excel(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load a CSV file first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Excel Report",
            initialdir="exports",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
        )
        if not path:
            return
        self._set_status("EXPORTING REPORT...")
        try:
            os.makedirs("exports", exist_ok=True)
            from app.exporter import export_to_excel
            export_to_excel(self.df, self.cod_bod_preds,
                            self.color_preds, self.equip_preds, path)
            self._set_status(f"EXPORT COMPLETE: {path}")
            messagebox.showinfo("Export Complete", f"Report saved:\n{path}")
        except Exception as exc:
            self._set_status(f"EXPORT FAILED: {exc}")
            messagebox.showerror("Export Error", str(exc))


def launch():
    root = tk.Tk()
    MainApp(root)
    root.mainloop()
