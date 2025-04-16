@echo off
echo === SS Steganography Build Script ===
echo.

cd /d "%~dp0"
python build_exe.py %*
set BUILD_RESULT=%ERRORLEVEL%

if %BUILD_RESULT% EQU 0 (
    echo.
    echo Build successful! Press any key to exit...
) else (
    echo.
    echo Build failed with error code %BUILD_RESULT%. Press any key to exit...
    exit /b %BUILD_RESULT%
)

pause
exit /b 0
