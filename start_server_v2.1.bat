@echo off
chcp 65001 >nul
title Windows Process API Server v2.1

echo.
echo =========================================
echo Windows Process API Server v2.1 Starter
echo =========================================
echo.

REM Pr¸fe Python-Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python ist nicht installiert oder nicht im PATH
    echo Bitte installiere Python 3.7+ von https://python.org
    pause
    exit /b 1
)

REM Pr¸fe ob die erweiterte API-Datei existiert
if not exist "enhanced_api_server_v2.1.py" (
    if exist "enhanced_api_server.py" (
        echo HINWEIS: Alte enhanced_api_server.py gefunden
        echo Verwende die neue enhanced_api_server_v2.1.py f¸r Duplikation-Schutz
        set PYTHON_FILE=enhanced_api_server.py
    ) else (
        echo ERROR: enhanced_api_server_v2.1.py nicht gefunden!
        echo Bitte stellen Sie sicher, dass die Datei im aktuellen Verzeichnis ist.
        pause
        exit /b 1
    )
) else (
    set PYTHON_FILE=enhanced_api_server_v2.1.py
)

echo Python gefunden. Installiere/aktualisiere benˆtigte Pakete...
echo.

REM Installiere erforderliche Pakete (falls nicht vorhanden)
pip install flask psutil waitress >nul 2>&1

echo.
echo Konfiguriere Umgebungsvariablen...

REM Setze Umgebungsvariablen
set API_SECRET_TOKEN=YOUR_API_TOKEN
set ALLOWED_TERMINATION_PROCESSES=vanitysearch.exe,BitcrackRandomiser.exe
set ALLOWED_START_PROGRAMS=BitcrackRandomiser.exe
set API_HOST=0.0.0.0
set API_PORT=8080
set ALLOWED_IPS=192.168.178.10,127.0.0.1
set BITCRACK_EXE_PATH=C:\Users\Miner\bitcrackrandomiser\BitcrackRandomiser.exe
set LOG_LEVEL=INFO

echo.
echo ==========================================
echo Windows Process API Server v2.1 gestartet
echo ==========================================
echo Host: %API_HOST%:%API_PORT%
echo Erlaubte IPs: %ALLOWED_IPS%
echo BitCrack-Pfad: %BITCRACK_EXE_PATH%
echo.
echo NEUE FEATURES v2.1:
echo [+] Prozess-Duplikation-Schutz
echo [+] ‹berpr¸fung bereits laufender Prozesse
echo [+] HTTP 409 Conflict f¸r Duplikate
echo [+] Erweiterte Prozess-Statistiken
echo.
echo API-Features: GUI-Support + Duplikation-Schutz
echo Creation Flags: CREATE_NEW_CONSOLE
echo.
echo Druecke Ctrl+C zum Beenden
echo.

REM Starte den Server
python %PYTHON_FILE%

echo.
echo Server wurde beendet.
pause
