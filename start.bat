@echo off
title DL Query Helper
cd /d "%~dp0"

echo ========================================
echo   Deep Learning Query Helper Launcher
echo ========================================
echo.

REM Try to find Python
set PYTHON_CMD=
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    goto :check_db
)

REM Try conda base
if exist "%USERPROFILE%\miniconda3\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\miniconda3\python.exe
    goto :check_db
)
if exist "%USERPROFILE%\anaconda3\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\anaconda3\python.exe
    goto :check_db
)
if exist "%USERPROFILE%\Miniconda3\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\Miniconda3\python.exe
    goto :check_db
)
if exist "%USERPROFILE%\Anaconda3\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\Anaconda3\python.exe
    goto :check_db
)

REM Try conda command
where conda >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Creating conda environment 'dl_helper'...
    call conda create -n dl_helper python=3.9 -y >nul 2>nul
    call conda run -n dl_helper pip install -r requirements.txt -q
    echo [INFO] Starting with conda...
    call conda run -n dl_helper python src/main.py
    goto :end
)

echo [ERROR] Python not found! Please install Python or conda first.
pause
exit /b 1

:check_db
echo [INFO] Checking database...
if not exist "data\functions.json" (
    echo [INFO] Building database first...
    %PYTHON_CMD% src/data/data_builder.py
)

echo [INFO] Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt -q 2>nul

echo [INFO] Starting GUI...
start "" "%PYTHON_CMD%" src/main.py

:end
echo Done.
