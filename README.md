<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white"/>
<img src="https://img.shields.io/badge/UI-Tkinter-FF6B35?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge"/>

# ⬡ Pigment Process Control System

### Industrial Analytics Platform for Pigment Manufacturing & Packing

*A professional desktop application that brings factory-floor intelligence to pigment production — COD/BOD prediction, colour quality analysis, equipment health monitoring, and delivery tracking, all in one Steel Professional HMI interface.*

---

[Features](#-features) · [Quick Start](#-quick-start) · [Data Format](#-data-format) · [Build EXE](#-build-as-windows-exe) · [Project Structure](#-project-structure) · [Contributing](#-contributing)

</div>

---

## 🏭 Overview

The **Pigment Process Control System (PCS)** is a full-featured industrial desktop application built for pigment manufacturing companies. It replaces manual spreadsheet tracking with a real-time analytics dashboard that monitors batch quality, predicts process outcomes, tracks equipment health, and manages delivery schedules — all without needing any cloud infrastructure or internet connection.

> Designed for **plant operators, quality engineers, and production managers** who need immediate insight into every batch that comes off the line.

---

## ✨ Features

### 📊 Dashboard
- **7 live KPI cards** — Total Batches, Avg COD, Avg BOD, Failures, Fail Rate, Destinations, Total Quantity
- **5 arc gauges** — real-time visual indicators for Fail Rate, Vibration, Runtime, Temperature, COD Load
- **Live batch table** with search and multi-column sort
- **Inline Quick Entry form** — add batch data directly from the dashboard without switching tabs

### ✏️ Data Entry Tab
- **Full form** with validation for all 19 batch fields
- **Auto-increment Batch ID** — B0001 → B0002 automatically
- **Double-click to edit** any entered row, **Delete key** to remove rows
- **Export to CSV** — save entered batches for future use
- **One-click Analyse** — pushes all batches to all analysis tabs instantly

### ⚗️ COD / BOD Prediction
- **OLS linear regression** model trained on your own batch data (no sklearn required)
- **Single-batch predictor** — enter process parameters and get instant COD/BOD predictions
- **Batch log** — actual vs predicted vs residual, colour-coded by error magnitude

### 🎨 Colour Analysis
- **Pigment RGB deviation scoring** — detects colour drift from the batch mean
- **3-tier classification** — In-Spec / Marginal / Out-of-Spec
- **Scrollable swatch array** — visual colour preview for every batch

### 🔧 Equipment Health
- **Weighted risk scoring** — Vibration (35%), Motor Current (30%), Runtime Hours (20%), Dryer Temp (15%)
- **4-level risk classification** — Low / Medium / High / Critical
- **Blinking alarm console** — highlights High and Critical batches with live LED indicators

### 🚚 Delivery Tracking
- **Real-time due-date status** — On Track / Due Soon / Overdue per batch
- **Full delivery schedule** with days-until-due counter

### 📈 Charts — 8 Types

| # | Chart | What it shows |
|---|---|---|
| 1 | COD/BOD Trends | Actual vs predicted with residual highlights |
| 2 | Temp vs COD | Scatter with pH colour scale |
| 3 | Equipment Risk | Histogram + bar chart + sensor scatter |
| 4 | Colour Analysis | RGB channels + deviation + status pie |
| 5 | Correlation Matrix | 10-variable heatmap |
| 6 | Process Overview | 6-panel production dashboard |
| 7 | pH & Flow Trends | Dual time-series with rolling averages |
| 8 | Delivery Gantt | Bubble chart by destination |

### 🔍 Search & Sort on Every Table
- **Live search** — filters all columns on every keystroke (AND multi-token logic)
- **Multi-column sort** — up to 8 sort levels with coloured priority badges `[1] [2] [3]`
- **3-click cycle per column** — Add ▲ → Flip ▼ → Remove
- **Smart numeric sort** — numbers sort as numbers, not as text

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher — [python.org](https://python.org)
- Windows 10/11 (macOS and Linux also work)

### Run from source

```bash
# 1. Clone the repository
git clone https://github.com/uyg7x/pigment-pcs.git
cd pigment-pcs/pigment_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate sample data
python generate_sample.py

# 4. Launch the app
python run.py
```

Click **LOAD FILE** in the header to load `sample_data.csv` or your own data file.

---

## 📋 Data Format

The app accepts both **CSV** and **Excel (.xlsx)** files.

### Required columns

| Column | Type | Range | Description |
|---|---|---|---|
| `Batch` | Text | — | Unique batch ID (e.g. B0001) |
| `Temperature` | Float | 40–110 | Reactor temperature °C |
| `Pressure` | Float | 0.5–6.0 | Pressure bar |
| `pH` | Float | 4.0–10.0 | pH level |
| `Flow` | Float | 30–200 | Flow rate L/min |
| `COD` | Float | 20–300 | Chemical Oxygen Demand mg/L |
| `BOD` | Float | 5–120 | Biological Oxygen Demand mg/L |
| `Pigment_R` | Integer | 0–255 | Red channel |
| `Pigment_G` | Integer | 0–255 | Green channel |
| `Pigment_B` | Integer | 0–255 | Blue channel |
| `Viscosity` | Float | 5–150 | Viscosity cP |
| `DryerTemp` | Float | 100–200 | Dryer temperature °C |
| `MotorCurrent` | Float | 10–60 | Motor current A |
| `Vibration` | Float | 0–8 | Vibration sensor reading |
| `RuntimeHours` | Float | 0–8760 | Equipment runtime hours |
| `FailLabel` | Integer | 0 or 1 | Equipment failure flag |
| `Destination` | Text | — | Shipping destination city |
| `DueDate` | Date | YYYY-MM-DD | Delivery due date |
| `Quantity` | Integer | 1–99999 | Batch quantity units |

### Example row
```csv
B0001,75.0,2.5,7.0,100.0,155.0,58.0,180,60,90,48.0,140.0,25.0,0.8,2400.0,0,Mumbai,2026-04-01,1500
```

> 💡 An Excel batch entry template (`Pigment_Batch_Entry_Template.xlsx`) with dropdowns, validation rules, and conditional formatting is included in the repository.

---

## 🏗️ Build as Windows EXE

Convert the app into a standalone `.exe` that runs on any Windows PC — **no Python required**.

```powershell
# From inside pigment_app\ — double-click or run in terminal:
quick_build.bat
```

**Output:** `dist\PigmentPCS.exe` — a single portable file (~60–80 MB)

The build script will:
1. Install PyInstaller automatically
2. Bundle Python + all libraries + your app into one file
3. Open the `dist\` folder when complete

For a professional installer wizard, install [Inno Setup 6](https://jrsoftware.org/isinfo.php) and compile `installer.iss` — produces `Output\PigmentPCS_Setup.exe`.

---

## 📁 Project Structure

```
pigment_app/
│
├── run.py                             # Entry point
├── generate_sample.py                 # Generates 100-row test data
├── requirements.txt                   # pandas, matplotlib, openpyxl
├── quick_build.bat                    # One-click Windows EXE builder
├── installer.iss                      # Inno Setup installer script
├── Pigment_Batch_Entry_Template.xlsx  # Excel data entry template
│
└── app/
    ├── __init__.py
    ├── main.py           # MainApp window, header, notebook, status bar
    ├── tabs.py           # All 7 tab classes including DataEntryTab
    ├── charts.py         # 8 matplotlib chart types
    ├── widgets.py        # SearchableTable, ArcGauge, LED, HMIPanel, KPICard
    ├── theme.py          # Steel Professional colour palette
    ├── data_loader.py    # CSV + Excel loading and validation
    ├── predictor.py      # OLS regression, colour deviation, risk scoring
    └── exporter.py       # 6-sheet colour-coded Excel export
```

---

## 🛠️ Tech Stack

| Component | Library | Version |
|---|---|---|
| GUI Framework | tkinter + ttk | Built-in (Python) |
| Data Processing | pandas | ≥ 2.0 |
| Charts | matplotlib | ≥ 3.7 |
| Excel Export/Import | openpyxl | ≥ 3.1 |
| Numerical Models | numpy | via pandas |
| EXE Packaging | PyInstaller | ≥ 6.0 |

> **No machine learning libraries required.** All prediction models (OLS regression, risk scoring) are implemented from scratch using NumPy only — keeping the dependency list minimal.

---

## 🎨 UI Theme — Steel Professional

Custom light industrial palette designed for all-day factory use:

```python
Background   #F0F4F8   soft blue-grey    — easy on eyes
Panel        #FFFFFF   white             — clean surfaces
Accent       #1A6FA8   steel blue        — primary actions
OK           #1A7A4A   forest green      — in-spec / on track
Warning      #B86A00   amber             — marginal / due soon
Critical     #C0302A   deep red          — failure / overdue
Font         Courier New monospace       — HMI aesthetic
```

---

## 📦 Dependencies

```
pandas>=2.0,<2.3
matplotlib>=3.7,<3.9
openpyxl>=3.1,<4.0
```

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add: description of feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

**Ideas for contributions:**
- New chart types in `charts.py`
- Additional prediction models in `predictor.py`
- Alternative colour themes in `theme.py`
- Multi-language support
- Database backend (SQLite) instead of CSV

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Free to use, modify, and distribute with attribution.

---

## 👤 Author

**Dharmendra**

- GitHub: [@uyg7x](https://github.com/uyg7x)
- Project: [github.com/uyg7x/pigment-pcs](https://github.com/uyg7x/pigment-pcs)

---

<div align="center">

**Built for the pigment manufacturing industry**

*If this project helped you, please consider giving it a ⭐*

</div>
