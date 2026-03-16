@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  Pigment Process Control System — Windows Build Script
REM  Run this file from inside the pigment_app\ folder
REM  Produces:  dist\PigmentPCS\PigmentPCS.exe   (folder build)
REM             Output\PigmentPCS_Setup.exe        (installer, if Inno Setup installed)
REM ═══════════════════════════════════════════════════════════════════════════

title Pigment PCS — Build Script
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   PIGMENT PROCESS CONTROL SYSTEM — BUILD TOOL           ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

REM ── Step 1: Check Python ─────────────────────────────────────────────────────
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python not found. Install Python 3.10+ from python.org
    pause & exit /b 1
)
python --version

REM ── Step 2: Install / upgrade dependencies ──────────────────────────────────
echo.
echo [2/6] Installing dependencies...
python -m pip install --upgrade pip -q
python -m pip install pandas>=2.0 matplotlib>=3.7 openpyxl>=3.1 pyinstaller -q
if %errorlevel% neq 0 (
    echo  ERROR: pip install failed. Check your internet connection.
    pause & exit /b 1
)
echo  Done.

REM ── Step 3: Generate sample data (optional) ──────────────────────────────────
echo.
echo [3/6] Generating sample data...
if exist generate_sample.py (
    python generate_sample.py --rows 100 --out sample_data.csv
    echo  sample_data.csv created.
) else (
    echo  generate_sample.py not found — skipping.
)

REM ── Step 4: Create a default icon if none exists ─────────────────────────────
echo.
echo [4/6] Checking icon...
if not exist app_icon.ico (
    echo  No app_icon.ico found — creating a default one...
    python -c "
import struct, zlib

def make_ico():
    # 16x16 steel-blue icon (solid fill)
    w = h = 16
    img = bytes([26, 111, 168, 255] * w * h)  # BGRA steel blue #1A6FA8

    # BMP DIB header
    bmp_hdr = struct.pack('<IIIHHIIIIII',
        40, w, -h, 1, 32, 0, len(img), 2835, 2835, 0, 0)
    bmp_data = bmp_hdr + img

    # ICO structure
    ico = struct.pack('<HHH', 0, 1, 1)  # header
    ico += struct.pack('<BBBBHHII',
        w, h, 0, 0, 1, 32, len(bmp_data), 22)  # dir entry
    ico += bmp_data
    with open('app_icon.ico', 'wb') as f:
        f.write(ico)
    print('  app_icon.ico created')

make_ico()
"
)

REM ── Step 5: Run PyInstaller ───────────────────────────────────────────────────
echo.
echo [5/6] Building executable with PyInstaller...
echo  This may take 2-5 minutes — please wait...
echo.

REM Copy spec file from build_tools if it exists there
if exist build_tools\PigmentPCS.spec (
    copy build_tools\PigmentPCS.spec PigmentPCS.spec >nul
)

pyinstaller PigmentPCS.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: PyInstaller build failed.
    echo  Check the output above for details.
    pause & exit /b 1
)

echo.
echo  Build complete!
echo  Executable: dist\PigmentPCS\PigmentPCS.exe

REM ── Step 6: Create installer with Inno Setup (if installed) ──────────────────
echo.
echo [6/6] Checking for Inno Setup...

set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%INNO_PATH%" (
    set INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
)

if exist "%INNO_PATH%" (
    echo  Inno Setup found — building installer...
    if exist build_tools\installer.iss (
        copy build_tools\installer.iss installer.iss >nul
    )
    "%INNO_PATH%" installer.iss
    if %errorlevel% equ 0 (
        echo.
        echo  ╔══════════════════════════════════════════════════════════╗
        echo  ║  INSTALLER READY:  Output\PigmentPCS_Setup.exe          ║
        echo  ╚══════════════════════════════════════════════════════════╝
    ) else (
        echo  Installer build failed — check installer.iss
    )
) else (
    echo  Inno Setup not found.
    echo  To create a proper installer:
    echo    1. Download Inno Setup from: https://jrsoftware.org/isinfo.php
    echo    2. Install it, then run this script again.
    echo.
    echo  For now you can distribute the folder:  dist\PigmentPCS\
    echo  Just zip that folder and share it — users double-click PigmentPCS.exe
)

echo.
echo ════════════════════════════════════════════════════════════
echo  BUILD SUMMARY
echo ════════════════════════════════════════════════════════════
echo  App folder  :  dist\PigmentPCS\
echo  Executable  :  dist\PigmentPCS\PigmentPCS.exe
if exist "Output\PigmentPCS_Setup.exe" (
    echo  Installer   :  Output\PigmentPCS_Setup.exe
)
echo ════════════════════════════════════════════════════════════
echo.
pause
