"""
Tab frame classes — Industrial HMI Pigment Process Control System.
All tabs extend ScrollableTab for proper vertical scrolling.
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd

from app import theme as T
from app.widgets import (ScrollableTab, LED, HMIPanel, KPICard, ArcGauge,
                         hmi_tree, populate_tree, section, SearchableTable)
from app.predictor import predict_single_cod_bod

_FEATS = ["Temperature", "Pressure", "pH", "Flow", "Viscosity"]
_FEAT_RANGES = {
    "Temperature": (40, 110),
    "Pressure":    (0.5, 6.0),
    "pH":          (4.0, 10.0),
    "Flow":        (30, 200),
    "Viscosity":   (5, 150),
}
_DEFAULTS = {
    "Temperature": 75, "Pressure": 2.5, "pH": 7.0,
    "Flow": 100, "Viscosity": 50,
}


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════════════════════════════════════════

class DashboardTab(ScrollableTab):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app     = app
        self._kpis   = {}
        self._gauges = {}
        self._build()

    def _build(self):
        p = self.inner   # all widgets go here

        section(p, "System KPIs")
        kpi_row = tk.Frame(p, bg=T.BG_BASE)
        kpi_row.pack(fill="x", padx=12, pady=(0, 6))

        kpi_defs = [
            ("Total Batches",  "total_batches",  T.CYAN,      ""),
            ("Avg COD",        "avg_cod",         T.CYAN,      "mg/L"),
            ("Avg BOD",        "avg_bod",         "#44AAFF",   "mg/L"),
            ("Failures",       "fail_count",      T.RED_HMI,   ""),
            ("Fail Rate",      "fail_rate_pct",   T.AMBER,     "%"),
            ("Destinations",   "destinations",    T.GREEN_HMI, ""),
            ("Total Qty",      "total_quantity",  T.MAGENTA,   "units"),
        ]
        for col, (label, key, color, unit) in enumerate(kpi_defs):
            card = KPICard(kpi_row, label=label, unit=unit, color=color)
            card.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")
            kpi_row.columnconfigure(col, weight=1)
            self._kpis[key] = card

        section(p, "Process Health Gauges")
        gauge_row = tk.Frame(p, bg=T.BG_BASE)
        gauge_row.pack(fill="x", padx=12, pady=(0, 6))

        gauge_defs = [
            ("Fail Rate",   "gauge_fail"),
            ("Vibration",   "gauge_vib"),
            ("Runtime",     "gauge_runtime"),
            ("Temperature", "gauge_temp"),
            ("COD Load",    "gauge_cod"),
        ]
        for col, (label, key) in enumerate(gauge_defs):
            gp = HMIPanel(gauge_row, title=label, title_color=T.CYAN_DIM)
            gp.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")
            gauge_row.columnconfigure(col, weight=1)
            g = ArcGauge(gp.get_body(), label=label, size=115)
            g.pack(pady=(4, 8))
            self._gauges[key] = g

        section(p, "Batch Data Feed")
        cols = ["Batch","Temp","pH","COD","BOD",
                "Pig_R","Pig_G","Pig_B","Vibration","Fail","Destination","DueDate"]
        self._table = SearchableTable(p, columns=cols, height=12)
        self._table.pack(fill="both", expand=True, padx=12)

        self._hint = tk.Frame(p, bg=T.BG_BASE)
        self._hint.pack(fill="x", padx=12, pady=20)
        tk.Label(self._hint,
                 text="[ AWAITING DATA FEED — LOAD CSV TO INITIALISE ]",
                 bg=T.BG_BASE, fg=T.TEXT_DIM,
                 font=("Courier New", 11, "bold")).pack()

    def refresh(self):
        df = self.app.df
        if df is None:
            return
        self._hint.pack_forget()

        from app.data_loader import get_summary
        s = get_summary(df)

        self._kpis["total_batches"].set(str(s["total_batches"]))
        self._kpis["avg_cod"].set(str(s["avg_cod"]))
        self._kpis["avg_bod"].set(str(s["avg_bod"]))
        self._kpis["fail_count"].set(str(s["fail_count"]))
        self._kpis["fail_rate_pct"].set(f"{s['fail_rate']}%")
        self._kpis["destinations"].set(str(s["destinations"]))
        self._kpis["total_quantity"].set(f"{s['total_quantity']:,}")

        max_cod = float(df["COD"].max()) or 1.0
        max_vib = float(df["Vibration"].max()) or 1.0
        max_rt  = float(df["RuntimeHours"].max()) or 1.0
        max_tmp = float(df["Temperature"].max()) or 1.0

        self._gauges["gauge_fail"].set_value(s["fail_rate"])
        self._gauges["gauge_vib"].set_value(
            min(100.0, s["avg_vibration"] / max_vib * 100))
        self._gauges["gauge_runtime"].set_value(
            min(100.0, s["avg_runtime"] / max_rt * 100))
        self._gauges["gauge_temp"].set_value(
            min(100.0, float(df["Temperature"].mean()) / max_tmp * 100))
        self._gauges["gauge_cod"].set_value(
            min(100.0, s["avg_cod"] / max_cod * 100))

        src = ["Batch","Temperature","pH","COD","BOD",
               "Pigment_R","Pigment_G","Pigment_B",
               "Vibration","FailLabel","Destination","DueDate"]
        rows = []
        for _, row in df[src].iterrows():
            rows.append([
                str(v.date()) if hasattr(v, "date")
                else (f"{v:.1f}" if isinstance(v, float) else str(v))
                for v in row
            ])

        # FIX: FailLabel is int (0 or 1), not string "1"
        def tag_fn(i, row):
            try:
                return "crit" if int(float(row[9])) == 1 else ("odd" if i % 2 else "even")
            except (ValueError, TypeError):
                return "odd" if i % 2 else "even"

        self._table.load(rows, tag_fn)


# ══════════════════════════════════════════════════════════════════════════════
# COD / BOD
# ══════════════════════════════════════════════════════════════════════════════

class CodBodTab(ScrollableTab):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app      = app
        self._inputs  = {}
        self._cod_var = tk.StringVar(value="---.--")
        self._bod_var = tk.StringVar(value="---.--")
        self._cod_st  = tk.StringVar(value="STANDBY")
        self._bod_st  = tk.StringVar(value="STANDBY")
        self._build()

    def _build(self):
        p = self.inner

        section(p, "Single-Batch Process Predictor")
        top = tk.Frame(p, bg=T.BG_BASE)
        top.pack(fill="x", padx=12, pady=(0, 8))
        top.columnconfigure(0, weight=2)
        top.columnconfigure(1, weight=1)

        # Input panel
        inp_panel = HMIPanel(top, title="Process Parameter Inputs",
                             led_color=T.GREEN_HMI)
        inp_panel.grid(row=0, column=0, padx=(0, 6), pady=2, sticky="nsew")
        body = inp_panel.get_body()
        body.configure(padx=14, pady=10)

        for i, feat in enumerate(_FEATS):
            lo, hi = _FEAT_RANGES[feat]
            rf = tk.Frame(body, bg=T.BG_PANEL)
            rf.grid(row=i, column=0, sticky="ew", pady=3)
            body.columnconfigure(0, weight=1)
            tk.Label(rf, text=f"{feat.upper():<14}",
                     bg=T.BG_PANEL, fg=T.TEXT_SEC,
                     font=T.FONT_HMI_SM).pack(side="left")
            var = tk.StringVar(value=str(_DEFAULTS[feat]))
            self._inputs[feat] = var
            tk.Entry(rf, textvariable=var,
                     bg=T.BG_FIELD, fg=T.CYAN,
                     font=("Courier New", 11, "bold"),
                     width=9, relief="flat",
                     insertbackground=T.CYAN,
                     highlightbackground=T.BORDER,
                     highlightthickness=1).pack(side="left", padx=8)
            tk.Label(rf, text=f"[{lo} - {hi}]",
                     bg=T.BG_PANEL, fg=T.TEXT_DIM,
                     font=T.FONT_SMALL).pack(side="left")

        tk.Button(body, text="EXECUTE PREDICTION",
                  bg=T.CYAN, fg="#FFFFFF",
                  font=("Courier New", 11, "bold"),
                  relief="flat", padx=18, pady=7,
                  cursor="hand2",
                  activebackground=T.CYAN_DIM,
                  activeforeground="#FFFFFF",
                  command=self._predict_single,
                  ).grid(row=len(_FEATS) + 1, column=0,
                         sticky="ew", pady=(14, 2))

        # Result panels
        res_col = tk.Frame(top, bg=T.BG_BASE)
        res_col.grid(row=0, column=1, padx=(6, 0), pady=2, sticky="nsew")

        for label, var, svar, color in [
            ("COD OUTPUT", self._cod_var, self._cod_st, T.CYAN),
            ("BOD OUTPUT", self._bod_var, self._bod_st, "#44AAFF"),
        ]:
            rp = HMIPanel(res_col, title=label, title_color=color)
            rp.pack(fill="both", expand=True, pady=(0, 6))
            b = rp.get_body()
            b.configure(padx=16, pady=12)
            tk.Label(b, textvariable=var,
                     bg=T.BG_PANEL, fg=color,
                     font=("Courier New", 34, "bold")).pack()
            tk.Label(b, text="mg/L",
                     bg=T.BG_PANEL, fg=T.TEXT_DIM,
                     font=T.FONT_SMALL).pack()
            tk.Label(b, textvariable=svar,
                     bg=T.BG_PANEL, fg=T.TEXT_SEC,
                     font=T.FONT_LABEL).pack(pady=(4, 0))

        section(p, "Batch Prediction Log")
        cols = ["Batch","COD_Actual","COD_Pred","COD_Residual",
                "BOD_Actual","BOD_Pred","BOD_Residual"]
        self._table = SearchableTable(p, columns=cols, height=14)
        self._table.pack(fill="both", expand=True, padx=12)

    def _predict_single(self):
        df = self.app.df
        if df is None:
            return
        try:
            inputs = {f: float(self._inputs[f].get()) for f in _FEATS}
            r      = predict_single_cod_bod(df, inputs)
            cod    = r.get("COD")
            bod    = r.get("BOD")
            self._cod_var.set(f"{cod:.2f}" if cod is not None else "ERR")
            self._bod_var.set(f"{bod:.2f}" if bod is not None else "ERR")
            self._cod_st.set("PREDICTION COMPLETE")
            self._bod_st.set("PREDICTION COMPLETE")
        except (ValueError, TypeError):
            self._cod_var.set("ERR")
            self._bod_var.set("ERR")
            self._cod_st.set("INPUT ERROR — CHECK VALUES")
            self._bod_st.set("INPUT ERROR — CHECK VALUES")

    def refresh(self):
        preds = self.app.cod_bod_preds
        if preds is None:
            return
        cols = ["Batch","COD_Actual","COD_Pred","COD_Residual",
                "BOD_Actual","BOD_Pred","BOD_Residual"]
        rows = []
        for _, row in preds[cols].iterrows():
            rows.append([
                str(v) if not isinstance(v, float) else f"{v:.2f}"
                for v in row
            ])

        def tag_fn(i, row):
            try:
                res = abs(float(row[3]))
                if res > 30: return "crit"
                if res > 15: return "warn"
            except (ValueError, TypeError):
                pass
            return "odd" if i % 2 else "even"

        self._table.load(rows, tag_fn)


# ══════════════════════════════════════════════════════════════════════════════
# Colour
# ══════════════════════════════════════════════════════════════════════════════

class ColorTab(ScrollableTab):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._pill_vars = {
            "In-Spec":     tk.StringVar(value="--"),
            "Marginal":    tk.StringVar(value="--"),
            "Out-of-Spec": tk.StringVar(value="--"),
        }
        self._build()

    def _build(self):
        p = self.inner

        section(p, "Pigment Colour Swatch Array")
        swatch_panel = HMIPanel(
            p,
            title="Colour Output Array  |  Scroll horizontally to inspect all batches",
            title_color=T.MAGENTA,
            led_color=T.MAGENTA,
        )
        swatch_panel.pack(fill="x", padx=12, pady=(0, 6))
        body = swatch_panel.get_body()

        # Swatch canvas with horizontal scroll
        canvas_wrap = tk.Frame(body, bg=T.BG_PANEL, height=105)
        canvas_wrap.pack(fill="x", padx=6, pady=6)
        canvas_wrap.pack_propagate(False)
        self._swatch_canvas = tk.Canvas(canvas_wrap, bg=T.BG_PANEL,
                                        highlightthickness=0, height=90)
        hsb = ttk.Scrollbar(canvas_wrap, orient="horizontal",
                             command=self._swatch_canvas.xview)
        self._swatch_canvas.configure(xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        self._swatch_canvas.pack(fill="both", expand=True)

        # Status pills
        pill_row = tk.Frame(body, bg=T.BG_PANEL)
        pill_row.pack(fill="x", padx=6, pady=(0, 8))
        for label, key, color in [
            ("IN-SPEC",     "In-Spec",     T.GREEN_HMI),
            ("MARGINAL",    "Marginal",    T.AMBER),
            ("OUT-OF-SPEC", "Out-of-Spec", T.RED_HMI),
        ]:
            pill = tk.Frame(pill_row, bg=T.BG_RAISED,
                            highlightbackground=color, highlightthickness=1)
            pill.pack(side="left", padx=6)
            tk.Label(pill, textvariable=self._pill_vars[key],
                     bg=T.BG_RAISED, fg=color,
                     font=("Courier New", 18, "bold"),
                     padx=16, pady=6).pack()
            tk.Label(pill, text=label,
                     bg=T.BG_RAISED, fg=T.TEXT_SEC,
                     font=T.FONT_SMALL, padx=6).pack(pady=(0, 4))

        section(p, "Colour Analysis Data")
        cols = ["Batch","R","G","B","Hex","Deviation","Color_Status"]
        self._table = SearchableTable(p, columns=cols, height=14)
        self._table.pack(fill="both", expand=True, padx=12)

    def refresh(self):
        preds = self.app.color_preds
        if preds is None:
            return

        for status in self._pill_vars:
            self._pill_vars[status].set(
                str(int((preds["Color_Status"] == status).sum())))

        # Draw swatches
        self._swatch_canvas.delete("all")
        sw, sh, pad = 55, 80, 7
        for i, (_, row) in enumerate(preds.iterrows()):
            x0 = pad + i * (sw + pad)
            x1 = x0 + sw
            self._swatch_canvas.create_rectangle(
                x0, pad, x1, sh - 22,
                fill=row["Hex"], outline=T.BORDER)
            sc = T.STATUS_COLORS.get(str(row.get("Color_Status", "")), T.TEXT_DIM)
            self._swatch_canvas.create_oval(
                x0 + 2, pad + 2, x0 + 10, pad + 10,
                fill=sc, outline="")
            self._swatch_canvas.create_text(
                x0 + sw // 2, sh - 12,
                text=str(row["Hex"]),
                fill=T.TEXT_SEC, font=("Courier New", 7))
            self._swatch_canvas.create_text(
                x0 + sw // 2, sh - 2,
                text=str(row["Batch"])[:5],
                fill=T.TEXT_DIM, font=("Courier New", 7))
        total_w = pad + len(preds) * (sw + pad)
        self._swatch_canvas.configure(scrollregion=(0, 0, total_w, sh))

        # Table with status colour coding
        status_tag = {
            "In-Spec":     "ok",
            "Marginal":    "warn",
            "Out-of-Spec": "crit",
        }
        rows = []
        for _, row in preds.iterrows():
            rows.append([str(row[c]) for c in
                         ["Batch","R","G","B","Hex","Deviation","Color_Status"]])

        def colour_tag(i, row):
            return status_tag.get(row[6], "odd" if i % 2 else "even")

        self._table.load(rows, colour_tag)


# ══════════════════════════════════════════════════════════════════════════════
# Equipment
# ══════════════════════════════════════════════════════════════════════════════

class EquipmentTab(ScrollableTab):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app         = app
        self._risk_cards = {}
        self._gauges     = {}
        self._build()

    def _build(self):
        p = self.inner

        section(p, "Equipment Alarm Console", color=T.RED_HMI)
        self._alarm_panel = HMIPanel(
            p, title="Active Alarms",
            title_color=T.RED_HMI, led_color=T.GREEN_HMI)
        self._alarm_panel.pack(fill="x", padx=12, pady=(0, 4))
        self._alarm_body = self._alarm_panel.get_body()
        tk.Label(self._alarm_body,
                 text="[ NO ACTIVE ALARMS ]",
                 bg=T.BG_PANEL, fg=T.TEXT_DIM,
                 font=T.FONT_HMI_SM, padx=10, pady=8).pack(anchor="w")

        section(p, "Risk Distribution")
        risk_row = tk.Frame(p, bg=T.BG_BASE)
        risk_row.pack(fill="x", padx=12, pady=(0, 6))
        for col, (level, color) in enumerate([
            ("Low",      T.GREEN_HMI),
            ("Medium",   T.AMBER),
            ("High",     T.RED_HMI),
            ("Critical", T.MAGENTA),
        ]):
            card = KPICard(risk_row, label=level, unit="batches", color=color)
            card.grid(row=0, column=col, padx=4, pady=2, sticky="nsew")
            risk_row.columnconfigure(col, weight=1)
            self._risk_cards[level] = card

        section(p, "Sensor Averages")
        gauge_row = tk.Frame(p, bg=T.BG_BASE)
        gauge_row.pack(fill="x", padx=12, pady=(0, 6))
        for col, (label, key) in enumerate([
            ("Vibration",     "vib"),
            ("Motor Current", "motor"),
            ("Dryer Temp",    "dryer"),
            ("Runtime Hrs",   "runtime"),
        ]):
            gp = HMIPanel(gauge_row, title=label)
            gp.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")
            gauge_row.columnconfigure(col, weight=1)
            g = ArcGauge(gp.get_body(), label=label, size=115)
            g.pack(pady=(4, 8))
            self._gauges[key] = g

        section(p, "Equipment Risk Log")
        cols = ["Batch","MotorCurrent","Vibration","RuntimeHours",
                "DryerTemp","FailLabel","Risk_Score","Risk_Level"]
        self._table = SearchableTable(p, columns=cols, height=12)
        self._table.pack(fill="both", expand=True, padx=12)

    def refresh(self):
        preds = self.app.equip_preds
        if preds is None:
            return

        for level, card in self._risk_cards.items():
            card.set(str(int((preds["Risk_Level"] == level).sum())))

        vib_max   = max(float(preds["Vibration"].max()),     1.0)
        motor_max = max(float(preds["MotorCurrent"].max()),  1.0)
        run_max   = max(float(preds["RuntimeHours"].max()),  1.0)

        self._gauges["vib"].set_value(
            float(preds["Vibration"].mean())    / vib_max   * 100)
        self._gauges["motor"].set_value(
            float(preds["MotorCurrent"].mean()) / motor_max * 100)
        self._gauges["dryer"].set_value(
            (float(preds["DryerTemp"].mean()) - 100) / 100 * 100)
        self._gauges["runtime"].set_value(
            float(preds["RuntimeHours"].mean()) / run_max   * 100)

        # Alarm console
        for w in self._alarm_body.winfo_children():
            w.destroy()
        critical = preds[preds["Risk_Level"].isin(["High", "Critical"])]
        if critical.empty:
            LED(self._alarm_body, color=T.GREEN_HMI, size=9,
                bg=T.BG_PANEL).pack(side="left", padx=(10, 4), pady=8)
            tk.Label(self._alarm_body,
                     text="ALL SYSTEMS NOMINAL — NO ACTIVE ALARMS",
                     bg=T.BG_PANEL, fg=T.GREEN_HMI,
                     font=T.FONT_HMI_SM).pack(side="left", pady=8)
        else:
            for _, row in critical.iterrows():
                color = T.MAGENTA if row["Risk_Level"] == "Critical" else T.RED_HMI
                af = tk.Frame(self._alarm_body, bg=T.BG_PANEL)
                af.pack(fill="x", padx=8, pady=2)
                LED(af, color=color, size=9, blink=True,
                    bg=T.BG_PANEL).pack(side="left", padx=(0, 6), pady=3)
                txt = (f"[{str(row['Risk_Level']).upper():>8}]  "
                       f"BATCH {str(row['Batch']):<8}  "
                       f"SCORE:{str(row['Risk_Score']):>6}  "
                       f"VIB:{float(row['Vibration']):.3f}  "
                       f"MOTOR:{float(row['MotorCurrent']):.1f}A")
                tk.Label(af, text=txt, bg=T.BG_PANEL, fg=color,
                         font=T.FONT_HMI_SM).pack(side="left")

        # Table
        level_tags = {
            "Low":      "ok",
            "Medium":   "warn",
            "High":     "crit",
            "Critical": "critical",
        }
        cols = ["Batch","MotorCurrent","Vibration","RuntimeHours",
                "DryerTemp","FailLabel","Risk_Score","Risk_Level"]
        rows = [[str(row[c]) for c in cols] for _, row in preds.iterrows()]

        def equip_tag(i, row):
            return level_tags.get(row[7], "odd" if i % 2 else "even")

        self._table.load(rows, equip_tag)


# ══════════════════════════════════════════════════════════════════════════════
# Delivery
# ══════════════════════════════════════════════════════════════════════════════

class DeliveryTab(ScrollableTab):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app        = app
        self._stat_vars = {}
        self._build()

    def _build(self):
        p = self.inner

        section(p, "Dispatch & Delivery Monitoring")
        stat_row = tk.Frame(p, bg=T.BG_BASE)
        stat_row.pack(fill="x", padx=12, pady=(0, 8))

        for col, (key, label, color) in enumerate([
            ("on_track", "On Track",  T.GREEN_HMI),
            ("due_soon", "Due Soon",  T.AMBER),
            ("overdue",  "Overdue",   T.RED_HMI),
            ("total",    "Total",     T.CYAN),
        ]):
            var = tk.StringVar(value="--")
            self._stat_vars[key] = var
            card = HMIPanel(stat_row, title=label, title_color=color)
            card.grid(row=0, column=col, padx=4, sticky="nsew")
            stat_row.columnconfigure(col, weight=1)
            b = card.get_body()
            b.configure(padx=20, pady=12)
            tk.Label(b, textvariable=var,
                     bg=T.BG_PANEL, fg=color,
                     font=("Courier New", 26, "bold")).pack()
            tk.Label(b, text="batches",
                     bg=T.BG_PANEL, fg=T.TEXT_DIM,
                     font=T.FONT_SMALL).pack()

        section(p, "Delivery Schedule")
        cols = ["Batch","Destination","DueDate","Quantity","Days_Until_Due","Status"]
        self._table = SearchableTable(p, columns=cols, height=18)
        self._table.pack(fill="both", expand=True, padx=12)

    def refresh(self):
        df = self.app.df
        if df is None:
            return

        today = pd.Timestamp.now().normalize()
        del_df = df[["Batch","Destination","DueDate","Quantity"]].copy()
        del_df["Days_Until_Due"] = (del_df["DueDate"] - today).dt.days
        del_df["Status"] = del_df["Days_Until_Due"].apply(
            lambda d: "Overdue"   if pd.notna(d) and d < 0
            else     ("Due Soon"  if pd.notna(d) and d <= 3
            else      "On Track"))

        self._stat_vars["on_track"].set(str((del_df["Status"] == "On Track").sum()))
        self._stat_vars["due_soon"].set(str((del_df["Status"] == "Due Soon").sum()))
        self._stat_vars["overdue"].set( str((del_df["Status"] == "Overdue").sum()))
        self._stat_vars["total"].set(str(len(del_df)))

        status_tags = {"On Track": "ok", "Due Soon": "warn", "Overdue": "crit"}
        rows = []
        for _, row in del_df.iterrows():
            due  = (row["DueDate"].strftime("%Y-%m-%d")
                    if pd.notna(row["DueDate"]) else "N/A")
            days = (int(row["Days_Until_Due"])
                    if pd.notna(row["Days_Until_Due"]) else "N/A")
            rows.append([row["Batch"], row["Destination"], due,
                         int(row["Quantity"]), days, row["Status"]])

        def del_tag(i, row):
            return status_tags.get(str(row[5]), "odd" if i % 2 else "even")

        self._table.load(rows, del_tag)
