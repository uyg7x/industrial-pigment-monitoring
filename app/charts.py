"""
Charts Tab — Industrial HMI matplotlib views.
8 chart types. All safe — no deprecated pandas calls, no invalid rcParams.
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import numpy as np

from app import theme as T

# ── Global matplotlib style ────────────────────────────────────────────────────
# NOTE: "legend.labelcolor" removed — not valid in matplotlib 3.7
matplotlib.rcParams.update({
    "figure.facecolor":   T.BG_BASE,
    "axes.facecolor":     T.BG_PANEL,
    "axes.edgecolor":     T.BORDER,
    "axes.labelcolor":    T.TEXT_PRI,
    "text.color":         T.TEXT_PRI,
    "xtick.color":        T.TEXT_SEC,
    "ytick.color":        T.TEXT_SEC,
    "grid.color":         T.BORDER,
    "grid.linestyle":     "--",
    "grid.linewidth":     0.5,
    "font.family":        "monospace",
    "font.size":          9,
    "axes.titlepad":      10,
    "axes.titlecolor":    T.CYAN,
    "axes.titleweight":   "bold",
    "axes.titlesize":     10,
    "legend.facecolor":   T.BG_RAISED,
    "legend.edgecolor":   T.BORDER,
    "legend.fontsize":    8,
})

C_CYAN    = T.CYAN
C_BLUE    = "#2980B9"
C_GREEN   = T.GREEN_HMI
C_AMBER   = T.AMBER
C_RED     = T.RED_HMI
C_MAGENTA = T.MAGENTA
C_WHITE   = T.TEXT_SEC   # use muted text instead of bright white on light bg
C_DIM     = T.TEXT_DIM


def _embed(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas


def _style_ax(ax):
    ax.grid(True, alpha=0.4)
    for spine in ax.spines.values():
        spine.set_edgecolor(T.BORDER)


def _legend(ax):
    """Add a legend with manually coloured text (works in all mpl versions)."""
    leg = ax.legend()
    if leg:
        leg.get_frame().set_facecolor(T.BG_RAISED)
        leg.get_frame().set_edgecolor(T.BORDER)
        for text in leg.get_texts():
            text.set_color(T.TEXT_PRI)


CHART_LIST = [
    ("COD/BOD Trends",     "cod_bod"),
    ("Temp vs COD",        "temp_cod"),
    ("Equipment Risk",     "equip_risk"),
    ("Colour Analysis",    "colour_dist"),
    ("Correlation",        "correlation"),
    ("Process Overview",   "process_overview"),
    ("pH & Flow",          "ph_flow"),
    ("Delivery Chart",     "delivery_gantt"),
]


class ChartsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="HMI.TFrame")
        self.app      = app
        self._canvas  = None
        self._current = tk.StringVar(value="cod_bod")
        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Scrollable toolbar (in case window is narrow)
        tb_outer = tk.Frame(self, bg=T.BG_RAISED,
                            highlightbackground=T.BORDER,
                            highlightthickness=1)
        tb_outer.pack(fill="x")

        tk.Frame(tb_outer, bg=T.CYAN, width=3).pack(side="left", fill="y")
        tk.Label(tb_outer, text="  VIEW:", bg=T.BG_RAISED, fg=T.TEXT_SEC,
                 font=T.FONT_HMI_SM).pack(side="left", padx=(8, 4), pady=8)

        # Use a Canvas + frame so buttons scroll horizontally if needed
        btn_canvas = tk.Canvas(tb_outer, bg=T.BG_RAISED,
                               highlightthickness=0, height=40)
        tb_hsb = ttk.Scrollbar(tb_outer, orient="horizontal",
                               command=btn_canvas.xview)
        btn_canvas.configure(xscrollcommand=tb_hsb.set)
        tb_hsb.pack(side="bottom", fill="x")
        btn_canvas.pack(side="left", fill="both", expand=True)

        btn_frame = tk.Frame(btn_canvas, bg=T.BG_RAISED)
        btn_win   = btn_canvas.create_window((0, 0), window=btn_frame, anchor="nw")

        for label, key in CHART_LIST:
            btn = tk.Radiobutton(
                btn_frame, text=label,
                variable=self._current, value=key,
                command=self._draw,
                bg=T.BG_RAISED, fg=T.TEXT_SEC,
                selectcolor=T.BG_PANEL,
                activebackground=T.BG_RAISED,
                activeforeground=T.CYAN,
                font=("Courier New", 9),
                indicatoron=False,
                padx=10, pady=5,
                relief="flat", bd=0,
                cursor="hand2",
            )
            btn.pack(side="left", padx=2, pady=4)

        def _resize_btn_canvas(e):
            btn_canvas.configure(scrollregion=btn_canvas.bbox("all"))
        btn_frame.bind("<Configure>", _resize_btn_canvas)

        tk.Frame(self, bg=T.CYAN, height=1).pack(fill="x")

        self.canvas_frame = tk.Frame(self, bg=T.BG_BASE)
        self.canvas_frame.pack(fill="both", expand=True)

        tk.Label(self.canvas_frame,
                 text="[ LOAD CSV TO RENDER PROCESS CHARTS ]",
                 bg=T.BG_BASE, fg=T.TEXT_DIM,
                 font=("Courier New", 12, "bold")).pack(expand=True)

    # ── Public ────────────────────────────────────────────────────────────────

    def refresh(self):
        self._draw()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _clear(self):
        for w in self.canvas_frame.winfo_children():
            w.destroy()
        if self._canvas:
            plt.close("all")
            self._canvas = None

    def _draw(self):
        if self.app.df is None:
            return
        self._clear()
        key = self._current.get()
        try:
            {
                "cod_bod":          self._chart_cod_bod,
                "temp_cod":         self._chart_temp_cod,
                "equip_risk":       self._chart_equip_risk,
                "colour_dist":      self._chart_colour_dist,
                "correlation":      self._chart_correlation,
                "process_overview": self._chart_process_overview,
                "ph_flow":          self._chart_ph_flow,
                "delivery_gantt":   self._chart_delivery_gantt,
            }[key]()
        except Exception:
            import traceback
            msg = traceback.format_exc()
            tk.Label(self.canvas_frame,
                     text=f"Chart error:\n{msg}",
                     bg=T.BG_BASE, fg=C_RED,
                     font=("Courier New", 9),
                     justify="left").pack(expand=True, padx=20, pady=10)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 1 — COD / BOD Actual vs Predicted
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_cod_bod(self):
        df    = self.app.df
        preds = self.app.cod_bod_preds
        fig   = Figure(figsize=(12, 5.5), tight_layout=True)
        ax1, ax2 = fig.subplots(1, 2)

        x = list(range(len(df)))
        for ax, target, color in [
            (ax1, "COD", C_CYAN),
            (ax2, "BOD", C_BLUE),
        ]:
            actual   = df[target].fillna(0).values
            pred_col = f"{target}_Pred"
            predicted = (preds[pred_col].fillna(0).values
                         if preds is not None and pred_col in preds.columns
                         else actual)

            ax.fill_between(x, actual, alpha=0.15, color=color)
            ax.plot(x, actual,    color=color,   lw=2.0, label="Actual",    zorder=3)
            ax.plot(x, predicted, color=C_WHITE, lw=1.2, ls="--",
                    alpha=0.8, label="Predicted", zorder=2)

            residual = np.abs(actual - predicted)
            high_idx = np.where(residual > 30)[0]
            if len(high_idx) > 0:
                ax.scatter([x[i] for i in high_idx],
                           [actual[i] for i in high_idx],
                           color=C_RED, s=45, zorder=5, label="High Residual")

            ax.set_title(f"{target} — ACTUAL vs PREDICTED")
            ax.set_xlabel("Batch Index")
            ax.set_ylabel(f"{target} (mg/L)")
            _legend(ax)
            _style_ax(ax)

        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 2 — Temperature/Flow scatter
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_temp_cod(self):
        df  = self.app.df
        fig = Figure(figsize=(12, 5.5), tight_layout=True)
        ax1, ax2 = fig.subplots(1, 2)

        sc1 = ax1.scatter(df["Temperature"], df["COD"],
                          c=df["pH"], cmap="plasma",
                          s=55, alpha=0.85, edgecolors="none", zorder=3)
        cbar1 = fig.colorbar(sc1, ax=ax1)
        cbar1.set_label("pH", color=T.TEXT_PRI)
        cbar1.ax.yaxis.set_tick_params(color=T.TEXT_PRI)
        for lbl in cbar1.ax.yaxis.get_ticklabels():
            lbl.set_color(T.TEXT_PRI)
        ax1.set_title("TEMPERATURE vs COD  (colour = pH)")
        ax1.set_xlabel("Temperature (°C)")
        ax1.set_ylabel("COD (mg/L)")
        _style_ax(ax1)

        sc2 = ax2.scatter(df["Flow"], df["BOD"],
                          c=df["Viscosity"], cmap="viridis",
                          s=55, alpha=0.85, edgecolors="none", zorder=3)
        cbar2 = fig.colorbar(sc2, ax=ax2)
        cbar2.set_label("Viscosity", color=T.TEXT_PRI)
        cbar2.ax.yaxis.set_tick_params(color=T.TEXT_PRI)
        for lbl in cbar2.ax.yaxis.get_ticklabels():
            lbl.set_color(T.TEXT_PRI)
        ax2.set_title("FLOW vs BOD  (colour = Viscosity)")
        ax2.set_xlabel("Flow (L/min)")
        ax2.set_ylabel("BOD (mg/L)")
        _style_ax(ax2)

        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 3 — Equipment Risk
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_equip_risk(self):
        preds = self.app.equip_preds
        fig   = Figure(figsize=(14, 5.5), tight_layout=True)
        ax1, ax2, ax3 = fig.subplots(1, 3)

        scores = preds["Risk_Score"].dropna().values
        ax1.hist(scores, bins=16, color=C_CYAN,
                 edgecolor=T.BG_BASE, alpha=0.85, zorder=3)
        for thresh, col, lbl in [
            (30, C_GREEN, "LOW"),
            (55, C_AMBER, "MED"),
            (75, C_RED,   "HIGH"),
        ]:
            ax1.axvline(thresh, color=col, lw=1.5, ls="--", label=lbl)
        ax1.set_title("RISK SCORE DISTRIBUTION")
        ax1.set_xlabel("Risk Score")
        ax1.set_ylabel("Batch Count")
        _legend(ax1)
        _style_ax(ax1)

        levels = ["Low", "Medium", "High", "Critical"]
        colors = [C_GREEN, C_AMBER, C_RED, C_MAGENTA]
        counts = [int((preds["Risk_Level"] == lv).sum()) for lv in levels]
        bars = ax2.bar(levels, counts, color=colors,
                       edgecolor=T.BG_BASE, width=0.5, zorder=3)
        for bar, count in zip(bars, counts):
            if count > 0:
                ax2.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.3, str(count),
                         ha="center", va="bottom",
                         color=C_WHITE, fontsize=9, fontweight="bold")
        ax2.set_title("BATCHES BY RISK LEVEL")
        ax2.set_ylabel("Count")
        _style_ax(ax2)

        cmap = {"Low": C_GREEN, "Medium": C_AMBER,
                "High": C_RED, "Critical": C_MAGENTA}
        for level, col in cmap.items():
            sub = preds[preds["Risk_Level"] == level]
            if not sub.empty:
                ax3.scatter(sub["Vibration"], sub["MotorCurrent"],
                            color=col, s=50, alpha=0.85,
                            edgecolors="none", label=level, zorder=3)
        ax3.set_title("VIBRATION vs MOTOR CURRENT")
        ax3.set_xlabel("Vibration")
        ax3.set_ylabel("Motor Current (A)")
        _legend(ax3)
        _style_ax(ax3)

        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 4 — Colour Analysis
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_colour_dist(self):
        preds = self.app.color_preds
        fig   = Figure(figsize=(14, 5.5), tight_layout=True)
        ax1, ax2, ax3 = fig.subplots(1, 3)

        x = list(range(len(preds)))

        for ch, col in [("R", "#FF2442"), ("G", C_GREEN), ("B", C_BLUE)]:
            ax1.plot(x, preds[ch], color=col, lw=1.6, label=ch, alpha=0.9)
            ax1.fill_between(x, preds[ch], alpha=0.08, color=col)
        ax1.set_title("RGB CHANNEL VALUES PER BATCH")
        ax1.set_xlabel("Batch Index")
        ax1.set_ylabel("Value (0–255)")
        _legend(ax1)
        _style_ax(ax1)

        status_c = preds["Color_Status"].map({
            "In-Spec":     C_GREEN,
            "Marginal":    C_AMBER,
            "Out-of-Spec": C_RED,
        }).fillna(C_DIM)
        ax2.scatter(x, preds["Deviation"],
                    c=status_c.tolist(), s=55,
                    edgecolors="none", alpha=0.9, zorder=3)
        ax2.axhline(1.5, color=C_AMBER, lw=1.2, ls="--", label="Marginal 1.5σ")
        ax2.axhline(2.5, color=C_RED,   lw=1.2, ls="--", label="Out-Spec 2.5σ")
        ax2.set_title("COLOUR DEVIATION PER BATCH")
        ax2.set_xlabel("Batch Index")
        ax2.set_ylabel("Deviation (σ)")
        _legend(ax2)
        _style_ax(ax2)

        labels = ["In-Spec", "Marginal", "Out-of-Spec"]
        colors = [C_GREEN, C_AMBER, C_RED]
        sizes  = [int((preds["Color_Status"] == lb).sum()) for lb in labels]
        nonzero = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
        if nonzero:
            sz, lb, cl = zip(*nonzero)
            wedges, texts, autotexts = ax3.pie(
                sz, labels=lb, colors=cl,
                autopct="%1.0f%%", startangle=90,
                wedgeprops={"edgecolor": T.BG_BASE, "linewidth": 2},
            )
            for t in list(texts) + list(autotexts):
                t.set_color(T.TEXT_PRI)
                t.set_fontsize(9)
        ax3.set_title("COLOUR STATUS BREAKDOWN")

        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 5 — Correlation Matrix
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_correlation(self):
        df   = self.app.df
        cols = ["Temperature","Pressure","pH","Flow",
                "COD","BOD","Vibration","MotorCurrent","DryerTemp","RuntimeHours"]
        sub  = df[cols].dropna()
        corr = sub.corr().values

        fig = Figure(figsize=(9, 7.5), tight_layout=True)
        ax  = fig.add_subplot(111)
        im  = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)

        ax.set_xticks(range(len(cols)))
        ax.set_yticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=40, ha="right", fontsize=8)
        ax.set_yticklabels(cols, fontsize=8)

        for i in range(len(cols)):
            for j in range(len(cols)):
                val     = corr[i, j]
                txt_col = "#FFFFFF" if abs(val) > 0.6 else T.TEXT_PRI
                ax.text(j, i, f"{val:.2f}",
                        ha="center", va="center",
                        color=txt_col, fontsize=7.5, fontweight="bold")

        ax.set_title("PROCESS VARIABLE CORRELATION MATRIX")
        _style_ax(ax)
        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 6 — Process Overview (6-panel)
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_process_overview(self):
        df  = self.app.df
        # Use tight_layout=False here and manage spacing via GridSpec
        fig = Figure(figsize=(14, 6.5))
        gs  = GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.38,
                       left=0.06, right=0.97, top=0.93, bottom=0.09)

        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[0, 2])
        ax4 = fig.add_subplot(gs[1, 0])
        ax5 = fig.add_subplot(gs[1, 1])
        ax6 = fig.add_subplot(gs[1, 2])

        x = list(range(len(df)))

        ax1.plot(x, df["Temperature"], color=C_AMBER, lw=1.5)
        ax1.fill_between(x, df["Temperature"], alpha=0.12, color=C_AMBER)
        ax1.set_title("TEMPERATURE (°C)")
        _style_ax(ax1)

        ax2.plot(x, df["Pressure"], color=C_CYAN, lw=1.5)
        ax2.fill_between(x, df["Pressure"], alpha=0.12, color=C_CYAN)
        ax2.set_title("PRESSURE (bar)")
        _style_ax(ax2)

        ax3.plot(x, df["pH"], color=C_GREEN, lw=1.5)
        ax3.axhspan(6.5, 7.5, color=C_GREEN, alpha=0.08)
        ax3.axhline(6.5, color=C_GREEN, lw=0.8, ls=":")
        ax3.axhline(7.5, color=C_GREEN, lw=0.8, ls=":")
        ax3.set_title("pH LEVEL")
        _style_ax(ax3)

        ax4.hist(df["Viscosity"].dropna(), bins=14, color=C_MAGENTA,
                 edgecolor=T.BG_BASE, alpha=0.85)
        ax4.set_title("VISCOSITY DISTRIBUTION")
        ax4.set_xlabel("cP")
        _style_ax(ax4)

        ax5.scatter(df["COD"], df["BOD"],
                    color=C_CYAN, s=35, alpha=0.7, edgecolors="none")
        valid = df[["COD","BOD"]].dropna()
        if len(valid) > 3:
            z  = np.polyfit(valid["COD"].values, valid["BOD"].values, 1)
            xf = np.linspace(float(valid["COD"].min()),
                             float(valid["COD"].max()), 100)
            ax5.plot(xf, np.polyval(z, xf), color=C_RED, lw=1.5, ls="--")
        ax5.set_title("COD vs BOD")
        ax5.set_xlabel("COD (mg/L)")
        ax5.set_ylabel("BOD (mg/L)")
        _style_ax(ax5)

        ax6.scatter(df["DryerTemp"], df["MotorCurrent"],
                    c=df["FailLabel"].values.astype(float),
                    cmap="RdYlGn_r",
                    s=40, alpha=0.8, edgecolors="none")
        ax6.set_title("DRYER TEMP vs MOTOR (red=fail)")
        ax6.set_xlabel("Dryer Temp (°C)")
        ax6.set_ylabel("Motor Current (A)")
        _style_ax(ax6)

        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 7 — pH & Flow Trends
    # FIX: removed deprecated fillna(method="ffill") — use .ffill() instead
    # FIX: removed tight_layout + subplots_adjust conflict
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_ph_flow(self):
        df  = self.app.df
        # Do NOT use tight_layout=True when manually calling subplots_adjust
        fig = Figure(figsize=(12, 5.5))
        fig.subplots_adjust(left=0.08, right=0.97, top=0.92,
                            bottom=0.10, hspace=0.08)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212, sharex=ax1)

        x = list(range(len(df)))

        # FIX: use .ffill() not fillna(method="ffill") — deprecated in pandas 2.x
        ph        = df["pH"].ffill().fillna(df["pH"].mean())
        win       = max(3, len(df) // 10)
        ph_roll   = ph.rolling(window=win, min_periods=1).mean()

        ax1.plot(x, ph.values,      color=C_GREEN, lw=1.0, alpha=0.5, label="pH Raw")
        ax1.plot(x, ph_roll.values, color=C_GREEN, lw=2.0, label="Rolling Avg")
        ax1.axhspan(6.5, 7.5, color=C_GREEN, alpha=0.07)
        ax1.axhline(6.5, color=C_GREEN, lw=0.7, ls=":", label="Spec Band")
        ax1.axhline(7.5, color=C_GREEN, lw=0.7, ls=":")
        ax1.set_ylabel("pH")
        ax1.set_title("pH & FLOW TRENDS WITH ROLLING AVERAGE")
        _legend(ax1)
        _style_ax(ax1)
        ax1.tick_params(labelbottom=False)

        flow      = df["Flow"].ffill().fillna(df["Flow"].mean())
        flow_roll = flow.rolling(window=win, min_periods=1).mean()

        ax2.bar(x, flow.values,      color=C_CYAN,  alpha=0.35, width=1.0, label="Flow Raw")
        ax2.plot(x, flow_roll.values, color=C_AMBER, lw=2.0,  label="Rolling Avg")
        ax2.set_ylabel("Flow (L/min)")
        ax2.set_xlabel("Batch Index")
        _legend(ax2)
        _style_ax(ax2)

        self._canvas = _embed(fig, self.canvas_frame)

    # ══════════════════════════════════════════════════════════════════════════
    # Chart 8 — Delivery Bubble + Stacked Bar
    # ══════════════════════════════════════════════════════════════════════════

    def _chart_delivery_gantt(self):
        df    = self.app.df
        today = np.datetime64("today", "D")

        del_df = df[["Batch","Destination","DueDate","Quantity"]].copy()
        del_df = del_df.dropna(subset=["DueDate"])

        # Compute days_left safely
        due_days = del_df["DueDate"].values.astype("datetime64[D]")
        del_df["days_left"] = (due_days - today).astype(int)

        del_df["Status"] = del_df["days_left"].apply(
            lambda d: "Overdue"  if d < 0
            else     ("Due Soon" if d <= 3 else "On Track"))

        status_colors = {
            "On Track": C_GREEN,
            "Due Soon": C_AMBER,
            "Overdue":  C_RED,
        }

        fig = Figure(figsize=(13, 6), tight_layout=True)
        ax1, ax2 = fig.subplots(1, 2)

        # Bubble chart
        dest_list = sorted(del_df["Destination"].unique().tolist())
        dest_idx  = {d: i for i, d in enumerate(dest_list)}
        y_vals    = [dest_idx[d] for d in del_df["Destination"]]
        x_vals    = del_df["days_left"].values
        max_qty   = float(del_df["Quantity"].max()) or 1.0
        sizes     = (del_df["Quantity"].values / max_qty * 400)
        colors_   = [status_colors.get(s, C_DIM) for s in del_df["Status"]]

        ax1.scatter(x_vals, y_vals, s=sizes, c=colors_,
                    alpha=0.8, edgecolors=T.BORDER, linewidth=0.5, zorder=3)
        ax1.axvline(0, color=C_RED,   lw=1.5, ls="--", label="Today")
        ax1.axvline(3, color=C_AMBER, lw=1.0, ls=":",  label="+3 days")
        ax1.set_yticks(range(len(dest_list)))
        ax1.set_yticklabels(dest_list, fontsize=8)
        ax1.set_xlabel("Days Until Due Date")
        ax1.set_title("DELIVERY SCHEDULE BY DESTINATION\n(bubble size = quantity)")
        _legend(ax1)
        _style_ax(ax1)

        # Stacked bar
        dest_status = (del_df.groupby(["Destination","Status"])
                       .size().unstack(fill_value=0))
        bottom = np.zeros(len(dest_status))
        for status, col in status_colors.items():
            if status in dest_status.columns:
                vals    = dest_status[status].values.astype(float)
                ax2.bar(range(len(dest_status)), vals, bottom=bottom,
                        color=col, label=status,
                        edgecolor=T.BG_BASE, width=0.6)
                bottom += vals
        ax2.set_xticks(range(len(dest_status)))
        ax2.set_xticklabels(dest_status.index, rotation=30,
                            ha="right", fontsize=8)
        ax2.set_ylabel("Batch Count")
        ax2.set_title("DELIVERY STATUS BY DESTINATION")
        _legend(ax2)
        _style_ax(ax2)

        self._canvas = _embed(fig, self.canvas_frame)
