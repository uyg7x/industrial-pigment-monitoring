"""
Reusable HMI widgets — Pigment Process Control System.
- No 8-digit hex colors (tkinter only supports #RRGGBB)
- ScrollableTab: base class for all tabs with a proper vertical scrollbar
"""

import tkinter as tk
from tkinter import ttk
import math

from app import theme as T


# ══════════════════════════════════════════════════════════════════════════════
# ScrollableTab — base class for every tab that needs vertical scrolling
# ══════════════════════════════════════════════════════════════════════════════

class ScrollableTab(ttk.Frame):
    """
    A ttk.Frame that embeds a Canvas + vertical Scrollbar.
    Subclasses should add widgets to self.inner (a plain tk.Frame).
    Mouse-wheel scrolling is bound automatically on Windows, Mac, Linux.
    """

    def __init__(self, parent, **kw):
        super().__init__(parent, style="HMI.TFrame", **kw)

        # Outer layout: canvas on left, scrollbar on right
        self._canvas = tk.Canvas(self, bg=T.BG_BASE,
                                 highlightthickness=0)
        self._vsb    = ttk.Scrollbar(self, orient="vertical",
                                     command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # Inner frame — add all content here
        self.inner = tk.Frame(self._canvas, bg=T.BG_BASE)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")

        # Resize inner frame to canvas width
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self.inner.bind("<Configure>",   self._on_inner_resize)

        # Mouse-wheel bindings
        self._canvas.bind("<Enter>", self._bind_wheel)
        self._canvas.bind("<Leave>", self._unbind_wheel)

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _on_inner_resize(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _bind_wheel(self, event):
        self._canvas.bind_all("<MouseWheel>",        self._on_wheel_win)
        self._canvas.bind_all("<Button-4>",          self._on_wheel_up)
        self._canvas.bind_all("<Button-5>",          self._on_wheel_down)

    def _unbind_wheel(self, event):
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_wheel_win(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_wheel_up(self, event):
        self._canvas.yview_scroll(-1, "units")

    def _on_wheel_down(self, event):
        self._canvas.yview_scroll(1, "units")


# ══════════════════════════════════════════════════════════════════════════════
# LED Indicator
# ══════════════════════════════════════════════════════════════════════════════

class LED(tk.Canvas):
    """Circular LED indicator with optional blink."""

    def __init__(self, parent, color=None, size=12, blink=False, **kw):
        color = color or T.GREEN_HMI
        bg    = kw.pop("bg", T.BG_PANEL)
        super().__init__(parent, width=size + 6, height=size + 6,
                         bg=bg, highlightthickness=0, **kw)
        self._color = color
        self._size  = size
        self._blink = blink
        self._on    = True
        self._draw()
        if blink:
            self._blink_loop()

    def _draw(self):
        self.delete("all")
        p, s = 3, self._size
        c = self._color if self._on else T.TEXT_DIM
        self.create_oval(p - 2, p - 2, p + s + 2, p + s + 2,
                         fill=T.BG_PANEL, outline=c, width=1)
        self.create_oval(p, p, p + s, p + s, fill=c, outline=c)
        sp = max(2, s // 4)
        self.create_oval(p + 2, p + 2, p + 2 + sp, p + 2 + sp,
                         fill="#FFFFFF", outline="")

    def set_color(self, color, blink=False):
        self._color = color
        self._blink = blink
        self._on    = True
        self._draw()

    def _blink_loop(self):
        if not self._blink:
            return
        self._on = not self._on
        self._draw()
        self.after(600, self._blink_loop)


# ══════════════════════════════════════════════════════════════════════════════
# HMI Panel
# ══════════════════════════════════════════════════════════════════════════════

class HMIPanel(tk.Frame):
    """Dark bordered panel with accent title bar."""

    def __init__(self, parent, title="", title_color=None, led_color=None, **kw):
        title_color = title_color or T.CYAN
        super().__init__(parent, bg=T.BG_PANEL,
                         highlightbackground=T.BORDER,
                         highlightthickness=1, **kw)
        if title:
            bar = tk.Frame(self, bg=T.BG_RAISED)
            bar.pack(fill="x", side="top")
            tk.Frame(bar, bg=title_color, width=3).pack(side="left", fill="y")
            if led_color:
                LED(bar, color=led_color, size=8,
                    bg=T.BG_RAISED).pack(side="left", padx=(6, 2), pady=5)
            tk.Label(bar, text=title.upper(),
                     bg=T.BG_RAISED, fg=title_color,
                     font=T.FONT_HMI).pack(side="left", padx=8, pady=5)
            tk.Label(bar, text="◈",
                     bg=T.BG_RAISED, fg=T.TEXT_DIM,
                     font=("Courier New", 8)).pack(side="right", padx=8)
        self.body = tk.Frame(self, bg=T.BG_PANEL)
        self.body.pack(fill="both", expand=True, padx=1, pady=1)

    def get_body(self):
        return self.body


# ══════════════════════════════════════════════════════════════════════════════
# KPI Card
# ══════════════════════════════════════════════════════════════════════════════

class KPICard(tk.Frame):
    """Large monospace KPI readout card."""

    def __init__(self, parent, label="", unit="", color=None, **kw):
        color = color or T.CYAN
        super().__init__(parent, bg=T.BG_PANEL,
                         highlightbackground=T.BORDER,
                         highlightthickness=1, **kw)
        self._var = tk.StringVar(value="--")
        tk.Frame(self, bg=color, height=2).pack(fill="x")
        inner = tk.Frame(self, bg=T.BG_PANEL, padx=12, pady=10)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, textvariable=self._var,
                 bg=T.BG_PANEL, fg=color,
                 font=("Courier New", 20, "bold")).pack()
        bot = tk.Frame(inner, bg=T.BG_PANEL)
        bot.pack(fill="x")
        tk.Label(bot, text=label.upper(),
                 bg=T.BG_PANEL, fg=T.TEXT_SEC,
                 font=T.FONT_SMALL).pack(side="left")
        if unit:
            tk.Label(bot, text=unit,
                     bg=T.BG_PANEL, fg=T.TEXT_DIM,
                     font=T.FONT_SMALL).pack(side="right")

    def set(self, value):
        self._var.set(str(value))


# ══════════════════════════════════════════════════════════════════════════════
# Arc Gauge
# ══════════════════════════════════════════════════════════════════════════════

class ArcGauge(tk.Canvas):
    """Semicircular donut gauge 0–100."""

    def __init__(self, parent, label="", size=130, **kw):
        super().__init__(parent, width=size, height=int(size * 0.72),
                         bg=T.BG_PANEL, highlightthickness=0, **kw)
        self._size  = size
        self._label = label
        self._value = 0.0
        self._redraw()

    def set_value(self, v):
        self._value = max(0.0, min(100.0, float(v)))
        self._redraw()

    def _redraw(self):
        self.delete("all")
        w  = self._size
        h  = int(w * 0.72)
        cx = w // 2
        cy = int(h * 0.90)
        ro = int(w * 0.43)
        ri = int(w * 0.30)
        self._donut(cx, cy, ro, ri, 220, -280, T.BORDER)
        sweep = -(self._value / 100.0) * 280
        color = (T.GREEN_HMI if self._value < 40
                 else T.AMBER if self._value < 70 else T.RED_HMI)
        if abs(sweep) > 1:
            self._donut(cx, cy, ro, ri, 220, sweep, color)
        self.create_text(cx, cy - int(ri * 0.05),
                         text=f"{self._value:.0f}",
                         font=("Courier New", int(w * 0.11), "bold"),
                         fill=color)
        self.create_text(cx, cy + int(w * 0.09),
                         text=self._label[:10].upper(),
                         font=("Courier New", int(w * 0.063)),
                         fill=T.TEXT_SEC)

    def _donut(self, cx, cy, ro, ri, start, extent, color):
        steps = max(36, int(abs(extent)))
        outer, inner = [], []
        for i in range(steps + 1):
            a = math.radians(start + extent * i / steps)
            outer += [cx + ro * math.cos(a), cy - ro * math.sin(a)]
            inner += [cx + ri * math.cos(a), cy - ri * math.sin(a)]
        self.create_polygon(outer + list(reversed(inner)),
                            fill=color, outline="", smooth=False)


# ══════════════════════════════════════════════════════════════════════════════
# Treeview helper
# ══════════════════════════════════════════════════════════════════════════════

def hmi_tree(parent, columns, height=14):
    """Styled Treeview with both scrollbars, packed into parent."""
    wrap = tk.Frame(parent, bg=T.BG_BASE)
    wrap.pack(fill="both", expand=True)
    vsb = ttk.Scrollbar(wrap, orient="vertical")
    hsb = ttk.Scrollbar(wrap, orient="horizontal")
    tv  = ttk.Treeview(wrap, columns=columns, show="headings",
                       height=height,
                       yscrollcommand=vsb.set,
                       xscrollcommand=hsb.set)
    vsb.config(command=tv.yview)
    hsb.config(command=tv.xview)
    vsb.pack(side="right",  fill="y")
    hsb.pack(side="bottom", fill="x")
    tv.pack(fill="both", expand=True)
    for col in columns:
        tv.heading(col, text=col)
        tv.column(col, width=110, anchor="center", minwidth=60)
    tv.tag_configure("odd",      background=T.BG_PANEL,   foreground=T.TEXT_PRI)
    tv.tag_configure("even",     background=T.BG_BASE,    foreground=T.TEXT_PRI)
    tv.tag_configure("ok",       background="#D4EDDA",    foreground="#0F5533")
    tv.tag_configure("warn",     background="#FFF3CD",    foreground="#7A4800")
    tv.tag_configure("crit",     background="#FDDCDA",    foreground="#8C1F1A")
    tv.tag_configure("critical", background="#EDD5F5",    foreground="#5C1F6E")
    return tv


def populate_tree(tv, rows, tag_fn=None):
    tv.delete(*tv.get_children())
    for i, row in enumerate(rows):
        tag = tag_fn(i, row) if tag_fn else ("odd" if i % 2 else "even")
        tv.insert("", "end", values=[str(v) for v in row], tags=(tag,))


# ══════════════════════════════════════════════════════════════════════════════
# SearchableTable  — search + MULTI-COLUMN sort + live filter
# ══════════════════════════════════════════════════════════════════════════════

_PLACEHOLDER = "type to filter any column…"

# Colour palette for sort priority badges (up to 8 levels)
_PRIORITY_COLORS = [
    "#B86A00",   # 1st  — amber
    "#1A6FA8",   # 2nd  — steel blue
    "#1A7A4A",   # 3rd  — green
    "#8B35A0",   # 4th  — purple
    "#C0302A",   # 5th  — red
    "#B07D00",   # 6th  — dark yellow
    "#5C5AA0",   # 7th  — indigo
    "#C0506A",   # 8th  — rose
]


class SearchableTable(tk.Frame):
    """
    Full-featured HMI table widget with MULTI-COLUMN SORT:

      SEARCH:
        • Live filter on every keystroke (AND multi-token logic)
        • ESC or ✕ CLEAR to reset
        • Match counter shows "12 / 100 MATCHES"

      MULTI-COLUMN SORT:
        • Click any column button to ADD it to the sort queue (1st, 2nd, 3rd…)
        • Each button shows a coloured priority badge [1], [2], [3]…
        • Click an active column button again to flip its direction (▲ / ▼)
        • Click a third time to REMOVE it from the sort queue
        • Click column headings in the table to do the same
        • Priority queue strip shows the live sort order
        • ↺ RESET SORT clears all sort levels at once
        • Smart numeric sort — numbers sort as numbers, text alphabetically

    Usage:
        tbl = SearchableTable(parent, columns=[...], height=14)
        tbl.pack(fill="both", expand=True)
        tbl.load(rows, tag_fn=fn)
    """

    def __init__(self, parent, columns, height=14, **kw):
        super().__init__(parent, bg=T.BG_BASE, **kw)
        self._columns  = columns
        self._height   = height
        self._all_rows = []
        self._tag_fn   = None

        # Multi-sort state:
        # _sort_keys = list of (col_idx, asc:bool) in priority order
        self._sort_keys = []

        self._build()

    # ─────────────────────────────────────────────────────────────────────────
    # Build UI
    # ─────────────────────────────────────────────────────────────────────────

    def _build(self):
        # ── ROW 1: Search bar ─────────────────────────────────────────────────
        sb = tk.Frame(self, bg=T.BG_RAISED,
                      highlightbackground=T.BORDER, highlightthickness=1)
        sb.pack(fill="x", pady=(0, 1))

        tk.Frame(sb, bg=T.CYAN, width=3).pack(side="left", fill="y")
        tk.Label(sb, text="  ⌕ SEARCH:",
                 bg=T.BG_RAISED, fg=T.CYAN,
                 font=("Courier New", 9, "bold")).pack(
                     side="left", padx=(6, 4), pady=6)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_type)
        self._entry = tk.Entry(
            sb, textvariable=self._search_var,
            bg=T.BG_FIELD, fg=T.CYAN,
            font=("Courier New", 10, "bold"),
            insertbackground=T.CYAN, relief="flat",
            highlightbackground=T.BORDER, highlightcolor=T.CYAN,
            highlightthickness=1, width=32,
        )
        self._entry.pack(side="left", padx=(0, 4), pady=5, ipady=3)
        self._entry.insert(0, _PLACEHOLDER)
        self._entry.config(fg=T.TEXT_DIM)
        self._entry.bind("<FocusIn>",  self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._entry.bind("<Escape>",   lambda _: self._clear_search())

        tk.Button(sb, text="✕ CLEAR", command=self._clear_search,
                  bg=T.BG_PANEL, fg=T.AMBER,
                  font=("Courier New", 8, "bold"),
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  activebackground=T.BG_RAISED, activeforeground=T.AMBER,
                  ).pack(side="left", padx=(0, 10))

        self._count_var = tk.StringVar(value="")
        tk.Label(sb, textvariable=self._count_var,
                 bg=T.BG_RAISED, fg=T.GREEN_HMI,
                 font=("Courier New", 8, "bold")).pack(side="left")

        # ── ROW 2: Sort column selector ───────────────────────────────────────
        sort_bar = tk.Frame(self, bg=T.BG_PANEL,
                            highlightbackground=T.BORDER, highlightthickness=1)
        sort_bar.pack(fill="x", pady=(0, 1))

        tk.Frame(sort_bar, bg=T.AMBER, width=3).pack(side="left", fill="y")
        tk.Label(sort_bar, text="  ⇅ SORT:",
                 bg=T.BG_PANEL, fg=T.AMBER,
                 font=("Courier New", 9, "bold")).pack(
                     side="left", padx=(6, 4), pady=5)

        # One button per column
        self._sort_btns = {}   # idx -> tk.Button
        btn_frame = tk.Frame(sort_bar, bg=T.BG_PANEL)
        btn_frame.pack(side="left", fill="x", expand=True)

        for idx, col in enumerate(self._columns):
            btn = tk.Button(
                btn_frame, text=col,
                command=lambda i=idx: self._toggle_col(i),
                bg=T.BG_RAISED, fg=T.TEXT_SEC,
                font=("Courier New", 8),
                relief="flat", padx=8, pady=3, cursor="hand2",
                activebackground=T.BG_PANEL, activeforeground=T.AMBER,
            )
            btn.pack(side="left", padx=2, pady=4)
            self._sort_btns[idx] = btn

        tk.Frame(sort_bar, bg=T.BORDER, width=1).pack(
            side="left", fill="y", padx=6, pady=4)

        # Reset button
        tk.Button(sort_bar, text="↺ RESET",
                  command=self._reset_sort,
                  bg=T.BG_PANEL, fg=T.TEXT_DIM,
                  font=("Courier New", 8),
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  activebackground=T.BG_RAISED, activeforeground=T.TEXT_SEC,
                  ).pack(side="right", padx=8, pady=4)

        # ── ROW 3: Active sort priority queue display ─────────────────────────
        self._queue_bar = tk.Frame(self, bg=T.BG_DEEP,
                                   highlightbackground=T.BORDER,
                                   highlightthickness=1)
        self._queue_bar.pack(fill="x", pady=(0, 2))
        tk.Frame(self._queue_bar, bg=T.MAGENTA, width=3).pack(
            side="left", fill="y")
        tk.Label(self._queue_bar, text="  SORT ORDER:",
                 bg=T.BG_DEEP, fg=T.MAGENTA,
                 font=("Courier New", 8, "bold")).pack(
                     side="left", padx=(4, 6), pady=4)
        # Chips will be rendered here dynamically
        self._queue_chips_frame = tk.Frame(self._queue_bar, bg=T.BG_DEEP)
        self._queue_chips_frame.pack(side="left", fill="x", expand=True)

        self._queue_hint = tk.Label(
            self._queue_chips_frame,
            text="click column buttons above to add sort levels",
            bg=T.BG_DEEP, fg=T.TEXT_DIM,
            font=("Courier New", 7, "italic"))
        self._queue_hint.pack(side="left", padx=4)

        # Instructions label on right
        tk.Label(self._queue_bar,
                 text="[1st click=ADD ▲]  [2nd click=FLIP ▼]  [3rd click=REMOVE]  |  click heading to sort",
                 bg=T.BG_DEEP, fg=T.TEXT_DIM,
                 font=("Courier New", 7)).pack(side="right", padx=8)

        # ── Treeview ──────────────────────────────────────────────────────────
        self._tv = hmi_tree(self, self._columns, self._height)

        # Bind column heading clicks → same toggle logic
        for idx, col in enumerate(self._columns):
            self._tv.heading(col, text=col,
                             command=lambda i=idx: self._toggle_col(i))

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def load(self, rows, tag_fn=None):
        """Load new data. Preserves current search and sort state."""
        self._all_rows = [[str(v) for v in row] for row in rows]
        self._tag_fn   = tag_fn
        self._refresh()

    def get_tree(self):
        return self._tv

    # ─────────────────────────────────────────────────────────────────────────
    # Multi-sort logic
    # ─────────────────────────────────────────────────────────────────────────

    def _toggle_col(self, col_idx):
        """
        3-state cycle per column:
          Not in queue  → add as ASCENDING  (1st click)
          In queue, ASC → flip to DESCENDING (2nd click)
          In queue, DESC → REMOVE from queue (3rd click)
        """
        existing = [(i, (ci, asc))
                    for i, (ci, asc) in enumerate(self._sort_keys)
                    if ci == col_idx]

        if not existing:
            # Add ascending
            self._sort_keys.append((col_idx, True))
        else:
            pos, (_, asc) = existing[0]
            if asc:
                # Flip to descending
                self._sort_keys[pos] = (col_idx, False)
            else:
                # Remove from queue
                self._sort_keys.pop(pos)

        self._update_sort_ui()
        self._refresh()

    def _reset_sort(self):
        self._sort_keys.clear()
        self._update_sort_ui()
        self._refresh()

    def _update_sort_ui(self):
        """Refresh column button badges, header arrows, and queue strip."""
        # Build a lookup: col_idx → (priority_1based, asc)
        active = {ci: (pri + 1, asc)
                  for pri, (ci, asc) in enumerate(self._sort_keys)}

        for idx, btn in self._sort_btns.items():
            col = self._columns[idx]
            if idx in active:
                pri, asc  = active[idx]
                badge_col = _PRIORITY_COLORS[(pri - 1) % len(_PRIORITY_COLORS)]
                arrow     = "▲" if asc else "▼"
                btn.config(
                    text=f"[{pri}] {col} {arrow}",
                    bg=badge_col,
                    fg=T.BG_DEEP,
                    font=("Courier New", 8, "bold"),
                )
                self._tv.heading(col, text=f"{col} [{pri}]{arrow}")
            else:
                btn.config(
                    text=col,
                    bg=T.BG_RAISED,
                    fg=T.TEXT_SEC,
                    font=("Courier New", 8),
                )
                self._tv.heading(col, text=col)

        # Rebuild queue chip strip
        for w in self._queue_chips_frame.winfo_children():
            w.destroy()

        if not self._sort_keys:
            tk.Label(self._queue_chips_frame,
                     text="click column buttons above to add sort levels",
                     bg=T.BG_DEEP, fg=T.TEXT_DIM,
                     font=("Courier New", 7, "italic")).pack(
                         side="left", padx=4, pady=3)
        else:
            for pri, (ci, asc) in enumerate(self._sort_keys):
                badge_col = _PRIORITY_COLORS[pri % len(_PRIORITY_COLORS)]
                col_name  = self._columns[ci]
                arrow     = "▲" if asc else "▼"
                chip      = tk.Frame(self._queue_chips_frame, bg=badge_col,
                                     padx=1, pady=1)
                chip.pack(side="left", padx=3, pady=3)
                inner = tk.Frame(chip, bg=T.BG_DEEP)
                inner.pack()
                # Priority number badge
                tk.Label(inner, text=f" {pri+1} ",
                         bg=badge_col, fg=T.BG_DEEP,
                         font=("Courier New", 8, "bold")).pack(side="left")
                # Column name + direction
                tk.Label(inner, text=f" {col_name} {arrow} ",
                         bg=T.BG_DEEP, fg=badge_col,
                         font=("Courier New", 8, "bold")).pack(side="left")
                # ✕ remove button inline on chip
                tk.Button(inner, text="✕",
                          command=lambda i=ci: self._remove_col(i),
                          bg=T.BG_DEEP, fg=badge_col,
                          font=("Courier New", 7, "bold"),
                          relief="flat", padx=2, pady=0,
                          cursor="hand2",
                          activebackground=badge_col,
                          activeforeground=T.BG_DEEP,
                          ).pack(side="left", padx=(0, 2))

                # Arrow separator (not after last)
                if pri < len(self._sort_keys) - 1:
                    tk.Label(self._queue_chips_frame, text=" → ",
                             bg=T.BG_DEEP, fg=T.TEXT_DIM,
                             font=("Courier New", 8)).pack(side="left")

    def _remove_col(self, col_idx):
        """Remove a specific column from sort queue."""
        self._sort_keys = [(ci, asc) for ci, asc in self._sort_keys
                           if ci != col_idx]
        self._update_sort_ui()
        self._refresh()

    # ─────────────────────────────────────────────────────────────────────────
    # Search controls
    # ─────────────────────────────────────────────────────────────────────────

    def _get_query(self):
        raw = self._search_var.get()
        return "" if raw == _PLACEHOLDER else raw.strip().lower()

    def _on_type(self, *_):
        self._refresh()

    def _on_focus_in(self, _):
        if self._entry.get() == _PLACEHOLDER:
            self._entry.delete(0, "end")
            self._entry.config(fg=T.CYAN)

    def _on_focus_out(self, _):
        if not self._entry.get().strip():
            self._entry.insert(0, _PLACEHOLDER)
            self._entry.config(fg=T.TEXT_DIM)

    def _clear_search(self):
        self._search_var.set("")
        self._entry.delete(0, "end")
        self._entry.insert(0, _PLACEHOLDER)
        self._entry.config(fg=T.TEXT_DIM)
        self._refresh()

    # ─────────────────────────────────────────────────────────────────────────
    # Core: filter → multi-sort → render
    # ─────────────────────────────────────────────────────────────────────────

    def _refresh(self):
        query = self._get_query()

        # 1. Filter
        if query:
            tokens  = query.split()
            visible = [row for row in self._all_rows
                       if all(t in " ".join(row).lower() for t in tokens)]
        else:
            visible = list(self._all_rows)

        # 2. Multi-column sort (applied right-to-left so primary key wins)
        if self._sort_keys and visible:
            def _val(row, ci):
                v = row[ci]
                try:
                    return (0, float(v))
                except (ValueError, TypeError):
                    return (1, v.lower())

            # Sort from lowest priority to highest so Python's stable sort
            # keeps the primary key dominant
            for ci, asc in reversed(self._sort_keys):
                visible.sort(key=lambda row: _val(row, ci),
                             reverse=not asc)

        # 3. Counter
        total, matched = len(self._all_rows), len(visible)
        self._count_var.set(
            f"  {matched} / {total} MATCH{'ES' if matched != 1 else ''}"
            if query else f"  {total} ROWS")

        # 4. Render
        tv = self._tv
        tv.delete(*tv.get_children())
        for i, row in enumerate(visible):
            tag = (self._tag_fn(i, row) if self._tag_fn
                   else ("odd" if i % 2 else "even"))
            tv.insert("", "end", values=row, tags=(tag,))


# ══════════════════════════════════════════════════════════════════════════════
# Section divider
# ══════════════════════════════════════════════════════════════════════════════

def section(parent, text, color=None):
    color = color or T.CYAN
    f = tk.Frame(parent, bg=T.BG_BASE)
    f.pack(fill="x", padx=12, pady=(12, 4))
    tk.Frame(f, bg=color, width=3, height=18).pack(side="left")
    tk.Label(f, text=f"  {text.upper()}",
             bg=T.BG_BASE, fg=color,
             font=T.FONT_HMI_SM).pack(side="left")
    tk.Frame(f, bg=T.BORDER, height=1).pack(
        side="left", fill="x", expand=True, padx=(6, 0), pady=9)
    tk.Label(f, text="◆",
             bg=T.BG_BASE, fg=T.TEXT_DIM,
             font=("Courier New", 7)).pack(side="right")
