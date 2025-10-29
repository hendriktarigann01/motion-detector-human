@echo off
chcp 65001 >nul
color 0C
title MJ Solution Kiosk - Uninstaller

REM ========================================
REM MJ Solution Kiosk - Uninstaller
REM Remove shortcuts and optional cleanup
REM ========================================

cls
echo.
echo ════════════════════════════════════════════════════════════════
echo          MJ SOLUTION KIOSK - UNINSTALLER
echo ════════════════════════════════════════════════════════════════
echo.
echo  This will remove:
echo   • Desktop shortcut
echo   • Taskbar shortcut (if pinned)
echo   • Startup shortcut (auto-start)
echo   • Launch scripts (optional)
echo.
echo  ⚠️  WARNING: This action cannot be undone!
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set /p CONFIRM="Are you sure you want to uninstall? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo.
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo ════════════════════════════════════════════════════════════════
echo Uninstalling MJ Solution Kiosk...
echo ════════════════════════════════════════════════════════════════
echo.

REM Remove desktop shortcut
echo [1/4] Removing desktop shortcut...
if exist "%USERPROFILE%\Desktop\MJ Solution Kiosk.lnk" (
    del "%USERPROFILE%\Desktop\MJ Solution Kiosk.lnk" /f /q
    echo ✓ Desktop shortcut removed
) else (
    echo ℹ️  Desktop shortcut not found
)
echo.

REM Remove startup shortcut
echo [2/4] Removing auto-start shortcut...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MJ Solution Kiosk.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MJ Solution Kiosk.lnk" /f /q
    echo ✓ Auto-start shortcut removed
) else (
    echo ℹ️  Auto-start shortcut not found
)
echo.

REM Remove taskbar pin instruction
echo [3/4] Taskbar shortcut...
echo ℹ️  If pinned to taskbar, please unpin manually:
echo    1. Right-click the taskbar icon
echo    2. Select "Unpin from taskbar"
echo.

REM Ask about launch scripts
echo [4/4] Launch scripts...
set /p DELETE_SCRIPTS="Delete launch scripts (Launch-Kiosk.vbs/bat)? (y/n): "
if /i "%DELETE_SCRIPTS%"=="y" (
    if exist "Launch-Kiosk.vbs" (
        del "Launch-Kiosk.vbs" /f /q
        echo ✓ Launch-Kiosk.vbs removed
    )
    if exist "Launch-Kiosk.bat" (
        del "Launch-Kiosk.bat" /f /q
        echo ✓ Launch-Kiosk.bat removed
    )
) else (
    echo ℹ️  Launch scripts kept
)
echo.

echo ════════════════════════════════════════════════════════════════
echo          UNINSTALL COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.
echo  ✓ Shortcuts removed
echo.
echo  📝 Note: 
echo     • Project files are still intact
echo     • Python packages are still installed
echo     • Configuration files are preserved
echo.
echo  💡 To completely remove:
echo     1. Delete this project folder
echo     2. Uninstall Python packages (optional):
echo        pip uninstall opencv-python torch ultralytics pygame selenium
echo.
echo ════════════════════════════════════════════════════════════════
echo.
pause
exit /b 0