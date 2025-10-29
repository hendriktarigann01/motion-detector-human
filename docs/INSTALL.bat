@echo off
chcp 65001 >nul
color 0B
title MJ Solution Kiosk - Installer

REM ========================================
REM MJ Solution Kiosk - Auto Installer
REM Setup shortcuts, dependencies, dan config
REM ========================================

cls
echo.
echo ════════════════════════════════════════════════════════════════
echo          MJ SOLUTION KIOSK - AUTO INSTALLER
echo ════════════════════════════════════════════════════════════════
echo.
echo  This installer will:
echo   ✓ Check Python installation
echo   ✓ Install required packages
echo   ✓ Create desktop shortcut
echo   ✓ Create taskbar shortcut (optional)
echo   ✓ Setup auto-start (optional)
echo   ✓ Test system components
echo.
echo ════════════════════════════════════════════════════════════════
echo.

pause

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ════════════════════════════════════════════════════════════════
echo [1/8] Checking Python Installation...
echo ════════════════════════════════════════════════════════════════

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo ⚠️  IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
python --version
echo.

echo ════════════════════════════════════════════════════════════════
echo [2/8] Installing Required Packages...
echo ════════════════════════════════════════════════════════════════
echo.

REM Install dependencies
echo Installing packages (this may take a few minutes)...
echo.

pip install --upgrade pip >nul 2>&1

echo [1/7] Installing opencv-python...
pip install opencv-python --quiet
if errorlevel 1 (
    echo ⚠️  Warning: opencv-python installation had issues
) else (
    echo ✓ opencv-python installed
)

echo [2/7] Installing torch...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo ⚠️  Warning: torch installation had issues
) else (
    echo ✓ torch installed
)

echo [3/7] Installing ultralytics (YOLO)...
pip install ultralytics --quiet
if errorlevel 1 (
    echo ⚠️  Warning: ultralytics installation had issues
) else (
    echo ✓ ultralytics installed
)

echo [4/7] Installing pygame (audio)...
pip install pygame --quiet
if errorlevel 1 (
    echo ⚠️  Warning: pygame installation had issues
) else (
    echo ✓ pygame installed
)

echo [5/7] Installing selenium (web)...
pip install selenium --quiet
if errorlevel 1 (
    echo ⚠️  Warning: selenium installation had issues
) else (
    echo ✓ selenium installed
)

echo [6/7] Installing Pillow...
pip install Pillow --quiet
if errorlevel 1 (
    echo ⚠️  Warning: Pillow installation had issues
) else (
    echo ✓ Pillow installed
)

echo [7/7] Installing numpy...
pip install numpy --quiet
if errorlevel 1 (
    echo ⚠️  Warning: numpy installation had issues
) else (
    echo ✓ numpy installed
)

echo.
echo ✓ Package installation complete!
echo.

echo ════════════════════════════════════════════════════════════════
echo [3/8] Creating Launch Scripts...
echo ════════════════════════════════════════════════════════════════
echo.

REM Create VBScript launcher
echo Creating silent launcher...
(
echo Set objShell = CreateObject^("WScript.Shell"^)
echo Set objFSO = CreateObject^("Scripting.FileSystemObject"^)
echo strCurrentDir = objFSO.GetParentFolderName^(WScript.ScriptFullName^)
echo objShell.CurrentDirectory = strCurrentDir
echo objShell.Run "pythonw main_launcher.py", 0, False
) > "Launch-Kiosk.vbs"

echo ✓ Launch-Kiosk.vbs created
echo.

REM Create batch launcher (backup)
(
echo @echo off
echo title MJ Solution Kiosk Launcher
echo cd /d "%%~dp0"
echo pythonw main_launcher.py
echo if errorlevel 1 python main_launcher.py
echo exit
) > "Launch-Kiosk.bat"

echo ✓ Launch-Kiosk.bat created (backup)
echo.

echo ════════════════════════════════════════════════════════════════
echo [4/8] Creating Desktop Shortcut...
echo ════════════════════════════════════════════════════════════════
echo.

REM Create VBS script to make shortcut (more reliable)
echo Creating shortcut maker script...
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo Set oShortcut = WshShell.CreateShortcut^(WshShell.SpecialFolders^("Desktop"^) ^& "\MJ Solution Kiosk.lnk"^)
echo oShortcut.TargetPath = "%SCRIPT_DIR%Launch-Kiosk.vbs"
echo oShortcut.WorkingDirectory = "%SCRIPT_DIR%"
echo oShortcut.IconLocation = "%SCRIPT_DIR%assets\icon-c-merch-color.ico"
echo oShortcut.Description = "MJ Solution Kiosk Control Center"
echo oShortcut.Save
) > "%TEMP%\create_shortcut.vbs"

REM Run the VBS script
cscript //nologo "%TEMP%\create_shortcut.vbs"

REM Clean up temp file
del "%TEMP%\create_shortcut.vbs" >nul 2>&1

REM Verify shortcut created
if exist "%USERPROFILE%\Desktop\MJ Solution Kiosk.lnk" (
    echo ✓ Desktop shortcut created successfully!
) else (
    echo ⚠️  Desktop shortcut creation failed
    echo    You can manually create shortcut from Launch-Kiosk.vbs
)
echo.

echo ════════════════════════════════════════════════════════════════
echo [5/8] Taskbar Shortcut (Optional)
echo ════════════════════════════════════════════════════════════════
echo.

set /p PIN_TASKBAR="Do you want to pin to taskbar? (y/n): "
if /i "%PIN_TASKBAR%"=="y" (
    echo.
    echo ℹ️  To pin to taskbar:
    echo    1. Find "MJ Solution Kiosk" on your Desktop
    echo    2. Right-click the shortcut
    echo    3. Select "Pin to taskbar"
    echo.
    echo Press any key to continue...
    pause >nul
)
echo.

echo ════════════════════════════════════════════════════════════════
echo [6/8] Auto-Start Setup (Optional)
echo ════════════════════════════════════════════════════════════════
echo.

set /p AUTO_START="Enable auto-start on Windows boot? (y/n): "
if /i "%AUTO_START%"=="y" (
    echo.
    echo Creating startup shortcut...
    
    REM Create VBS for startup shortcut
    (
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo Set oShortcut = WshShell.CreateShortcut^("%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MJ Solution Kiosk.lnk"^)
    echo oShortcut.TargetPath = "%SCRIPT_DIR%Launch-Kiosk.vbs"
    echo oShortcut.WorkingDirectory = "%SCRIPT_DIR%"
    echo oShortcut.IconLocation = "%SCRIPT_DIR%assets\icon-c-merch-color.ico"
    echo oShortcut.Save
    ) > "%TEMP%\create_startup.vbs"
    
    cscript //nologo "%TEMP%\create_startup.vbs"
    del "%TEMP%\create_startup.vbs" >nul 2>&1
    
    if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MJ Solution Kiosk.lnk" (
        echo ✓ Auto-start enabled!
        echo    Kiosk will launch automatically on Windows boot
    ) else (
        echo ⚠️  Auto-start setup failed
    )
) else (
    echo ✓ Auto-start skipped
)
echo.

echo ════════════════════════════════════════════════════════════════
echo [7/8] Creating Default Configuration...
echo ════════════════════════════════════════════════════════════════
echo.

REM Create config directory
if not exist "config" mkdir config

REM Create default kiosk_config.json if not exists
if not exist "config\kiosk_config.json" (
    echo Creating default configuration...
    (
    echo {
    echo     "camera_index": 1,
    echo     "distance_far": 150,
    echo     "distance_near": 450,
    echo     "distance_very_near": 700,
    echo     "stage2_countdown": 10,
    echo     "stage3_timeout": 15,
    echo     "stage4_idle_timeout": 15,
    echo     "stage4_countdown": 60,
    echo     "web_url": "http://localhost:5173/test",
    echo     "fullscreen": false,
    echo     "debug_mode": true
    echo }
    ) > "config\kiosk_config.json"
    echo ✓ Default configuration created
) else (
    echo ✓ Configuration already exists
)
echo.

echo ════════════════════════════════════════════════════════════════
echo [8/8] Running System Test...
echo ════════════════════════════════════════════════════════════════
echo.

set /p RUN_TEST="Do you want to run component test now? (y/n): "
if /i "%RUN_TEST%"=="y" (
    echo.
    echo Starting component test...
    echo.
    if exist "utility\test_components.py" (
        python utility\test_components.py
    ) else (
        echo ⚠️  Test script not found: utility\test_components.py
        echo    You can run it manually later
    )
) else (
    echo ✓ Test skipped (you can run it later from the launcher)
)
echo.

echo ════════════════════════════════════════════════════════════════
echo          INSTALLATION COMPLETE! 🎉
echo ════════════════════════════════════════════════════════════════
echo.
echo  ✓ All components installed successfully!
echo.
echo  📁 Files created:
echo     • Launch-Kiosk.vbs (silent launcher)
echo     • Launch-Kiosk.bat (backup launcher)
echo     • Desktop shortcut
if /i "%AUTO_START%"=="y" (
    echo     • Startup shortcut
)
echo     • config\kiosk_config.json
echo.
echo  🚀 How to use:
echo     1. Double-click "MJ Solution Kiosk" on Desktop
echo     2. Or run "Launch-Kiosk.vbs" from this folder
echo     3. Or use "Launch-Kiosk.bat" if VBS doesn't work
echo.
echo  📋 Next steps:
echo     • Run CALIBRATION to setup distance thresholds
echo     • Run TEST to verify all components
echo     • Click START KIOSK to launch the application
echo.
echo  💡 Tips:
echo     • Pin Desktop shortcut to Taskbar for quick access
echo     • Run calibration in your actual deployment location
echo     • Check config\kiosk_config.json for settings
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Open launcher
set /p OPEN_NOW="Open MJ Solution Kiosk Launcher now? (y/n): "
if /i "%OPEN_NOW%"=="y" (
    echo.
    echo Launching...
    start "" "Launch-Kiosk.vbs"
)

echo.
echo Thank you for installing MJ Solution Kiosk! 🙏
echo.
pause
exit /b 0