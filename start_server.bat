@echo off
chcp 65001 >nul
title Windows Process API Server

echo.
echo ===================================
echo Startet Windows Process API Server
echo ===================================

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python nicht installiert oder nicht im PATH!
    pause
    exit /b 1
)

if not exist "enhanced_api_server.py" (
    echo ERROR: enhanced_api_server.py nicht gefunden!
    pause
    exit /b 1
)

echo Host: 0.0.0.0:8080
echo Erlaubte IPs: Homeassistant-IP,127.0.0.1
echo Bitcrack-Pfad: C:\Users\Miner\bitcrackrandomiser\BitcrackRandomiser.exe
echo.
echo API-Features: GUI-Support aktiviert
echo Creation Flags: CREATE_NEW_CONSOLE
echo.
echo Druecke Ctrl+C zum Beenden
echo.

set API_SECRET_TOKEN=Your_API_Key
set BITCRACK_EXE_PATH=C:\Users\Miner\bitcrackrandomiser\BitcrackRandomiser.exe
set ALLOWED_IPS=192.168.178.10,127.0.0.1
set ALLOWED_TERMINATION_PROCESSES=vanitysearch.exe,BitcrackRandomiser.exe
set ALLOWED_START_PROGRAMS=BitcrackRandomiser.exe

python enhanced_api_server.py

echo.
echo Server wurde beendet
pause
