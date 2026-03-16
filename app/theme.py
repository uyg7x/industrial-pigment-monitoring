"""
Steel Professional Theme — Pigment Process Control System
Light industrial palette. Easy on eyes for all-day factory use.
ALL colors are valid 6-digit hex (#RRGGBB) — safe for tkinter.
"""

# ── Backgrounds ───────────────────────────────────────────────────────────────
BG_DEEP   = "#DDE4EE"   # deepest surface  (tab bar bg, status bar)
BG_BASE   = "#F0F4F8"   # main window background
BG_PANEL  = "#FFFFFF"   # card / panel surface
BG_RAISED = "#E8EDF2"   # slightly raised surface (headers, toolbars)
BG_FIELD  = "#EEF3F7"   # input field background

# ── Accent colors (6-digit only) ──────────────────────────────────────────────
CYAN      = "#1A6FA8"   # primary accent — steel blue
CYAN_DIM  = "#0D4F7A"   # darker blue (hover, active states)
CYAN_MID  = "#C8D6E0"   # muted blue for dividers / borders
AMBER     = "#B86A00"   # warning — rich amber
AMBER_DIM = "#8A4E00"   # darker amber
GREEN_HMI = "#1A7A4A"   # ok / in-spec — forest green
GREEN_DIM = "#0F5533"   # darker green
RED_HMI   = "#C0302A"   # alarm / critical — deep red
RED_DIM   = "#8C1F1A"   # darker red
MAGENTA   = "#8B35A0"   # critical / special — purple-magenta
MAGENTA_DIM = "#5C1F6E" # darker magenta

# ── Text ──────────────────────────────────────────────────────────────────────
TEXT_PRI  = "#1C2B3A"   # primary text    (dark navy)
TEXT_SEC  = "#4A6070"   # secondary text  (muted slate)
TEXT_DIM  = "#8A9BA8"   # disabled / hint (light grey-blue)

# ── Borders ───────────────────────────────────────────────────────────────────
BORDER    = "#C8D6E0"   # standard border
BORDER2   = "#B0C0CC"   # stronger border (hover / focus)

# ── Fonts (Courier New — always available on Windows) ─────────────────────────
FONT_DISPLAY = ("Courier New", 28, "bold")
FONT_HMI     = ("Courier New", 11, "bold")
FONT_HMI_SM  = ("Courier New",  9)
FONT_TITLE   = ("Courier New", 13, "bold")
FONT_BODY    = ("Courier New", 10)
FONT_SMALL   = ("Courier New",  8)
FONT_LABEL   = ("Courier New",  9)

# ── Semantic maps ─────────────────────────────────────────────────────────────
RISK_COLORS = {
    "Low":      GREEN_HMI,
    "Medium":   AMBER,
    "High":     RED_HMI,
    "Critical": MAGENTA,
}
STATUS_COLORS = {
    "In-Spec":     GREEN_HMI,
    "Marginal":    AMBER,
    "Out-of-Spec": RED_HMI,
}
DELIVERY_COLORS = {
    "On Track": GREEN_HMI,
    "Due Soon": AMBER,
    "Overdue":  RED_HMI,
}
