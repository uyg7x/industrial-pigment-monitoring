# Pigment Process Control System — Build Guide
## Converting the Python Project into a Windows .exe Application

---

## What You'll Get

| Output | Description |
|---|---|
| `dist\PigmentPCS\PigmentPCS.exe` | Standalone executable (no Python needed) |
| `Output\PigmentPCS_Setup.exe` | Professional Windows installer |

---

## Prerequisites — Install These First

### 1. Python 3.10+
Download from https://python.org  
✅ During install, check **"Add Python to PATH"**

### 2. Inno Setup 6 (for the installer)
Download from https://jrsoftware.org/isinfo.php  
Install with default settings.

---

## Build Steps

### Step 1 — Open PowerShell in your project folder

Right-click on `D:\pigment_v8_steel\pigment_app\`  
→ Open in Terminal (or PowerShell)

### Step 2 — Copy build files into the project folder

Copy these 3 files from `build_tools\` into your `pigment_app\` folder:
```
build_tools\build.bat        →  pigment_app\build.bat
build_tools\PigmentPCS.spec  →  pigment_app\PigmentPCS.spec
build_tools\installer.iss    →  pigment_app\installer.iss
```

### Step 3 — Run the build script

Double-click `build.bat`   
OR in PowerShell run:
```powershell
.\build.bat
```

The script will:
1. Check Python is installed
2. Install/upgrade all dependencies (pandas, matplotlib, openpyxl, pyinstaller)
3. Generate sample_data.csv
4. Create a default icon
5. Build the .exe with PyInstaller (~3-5 minutes)
6. Build the installer with Inno Setup

### Step 4 — Find your outputs

```
pigment_app\
├── dist\
│   └── PigmentPCS\
│       └── PigmentPCS.exe   ← double-click to run (no Python needed)
└── Output\
    └── PigmentPCS_Setup.exe  ← share this to install on any PC
```

---

## Distributing the App

### Option A — Share the installer (recommended)
Send `PigmentPCS_Setup.exe` to colleagues.  
They double-click it → next → next → finish → app is installed with Start Menu shortcut.

### Option B — Share the folder
Zip `dist\PigmentPCS\` and send it.  
Recipient unzips and double-clicks `PigmentPCS.exe`.  
**Do not move PigmentPCS.exe out of its folder** — it needs the other files.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pyinstaller not found` | Run: `pip install pyinstaller` |
| Build fails with missing module | Add the module name to `hiddenimports` in `PigmentPCS.spec` |
| App crashes on launch | Run from cmd: `dist\PigmentPCS\PigmentPCS.exe` — read the error |
| `app_icon.ico` error | Delete the icon line from spec: `icon='app_icon.ico'` → `icon=None` |
| Antivirus flags the exe | Add an exclusion — common with PyInstaller builds, not a real virus |
| Inno Setup not found | Install from jrsoftware.org then re-run build.bat |

---

## Customising the Installer

Edit `installer.iss` before building:

```ini
#define AppName      "Your Company — Pigment Monitor"   ; ← change this
#define AppPublisher "Your Company Name"                  ; ← change this
#define AppVersion   "3.1"                               ; ← version number
```

---

## Adding a Custom Icon

1. Create a 256×256 `.ico` file with your company logo
2. Name it `app_icon.ico`
3. Place it in `pigment_app\`
4. The build script will use it automatically

Free online converter: https://convertio.co/png-ico/

---

## File Size Reference

| Component | Approximate Size |
|---|---|
| Python runtime | ~8 MB |
| pandas + numpy | ~25 MB |
| matplotlib | ~15 MB |
| Total app folder | ~60-80 MB |
| Installer (.exe) | ~30-40 MB (compressed) |
