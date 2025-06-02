```
             _   ___                
            (_) /   |               
  __ _ _ __  _ / /| |_ __ ___   ___ 
 / _` | '_ \| / /_| | '_ ` _ \ / _ \
| (_| | |_) | \___  | | | | | |  __/
 \__,_| .__/|_|   |_/_| |_| |_|\___|
      | |                           
      |_|                           
```
# Windows Process API Server v2.1

A secure HTTP API server written in Python (Flask + Waitress) to manage processes on a Windows machine. Designed primarily for integration with Home Assistant to control applications like BitcrackRandomiser and vanitysearch.

**Version:** 2.1

## Features

*   **Remote Process Management:** Start and stop specified Windows processes via HTTP API calls.
*   **Direct Program Execution:** Start programs (e.g., `BitcrackRandomiser.exe`) directly from a specified file path.
*   **Duplicate Process Prevention:** Checks if a process is already running before attempting to start it, preventing multiple instances.
*   **Secure Authentication:** Uses Bearer Token authentication for all sensitive operations.
*   **IP Whitelisting:** Restricts API access to a configurable list of IP addresses.
*   **Production Ready:** Uses Waitress WSGI server, suitable for production environments (eliminates Flask development server warnings).
*   **GUI Application Support:** Correctly starts GUI applications, ensuring they remain visible and active.
*   **Detailed Logging:** Comprehensive logging for API requests, security events, and process actions.
*   **Status Endpoints:** Provides `/health` and `/status` endpoints for monitoring API health and statistics.
*   **Home Assistant Integration:** Easily integrable with Home Assistant using RESTful sensors and commands.

## Prerequisites

*   A Windows machine to host the API server.
*   Python 3.6+ installed on the Windows machine.
*   `pip` (Python package installer).
*   The target applications (e.g., BitcrackRandomiser, vanitysearch) installed on the Windows machine.
*   (Optional) Home Assistant instance for remote control and automation.

## Setup and Installation (Windows API Server)

1.  **Create a Directory:**
    Create a dedicated directory for the API server files on your Windows machine (e.g., `C:\API-Server`).

2.  **Download Files:**
    Place the following files into the directory created above:
    *   `enhanced_api_server_v2.1.py` (the Python API server script)
    *   `start_server_v2.1.bat` (the batch script to run the server)

3.  **Install Python Dependencies:**
    Open a Command Prompt or PowerShell in the server directory and install the required Python packages:
    ```
    pip install Flask psutil waitress
    ```

4.  **Configure Environment Variables:**
    The API server is configured via environment variables. These are set within the `start_server_v2.1.bat` script, or you can set them globally in your Windows system environment variables.

    **Key Environment Variables (Edit in `start_server_v2.1.bat` or set globally):**

    *   `API_SECRET_TOKEN`: **(Required)** A strong, unique secret token for API authentication.
        *Example: Generate a secure token (e.g., using a password manager or online generator).*
        *Replace `YOUR_VERY_SECRET_API_TOKEN_HERE` in the batch file.*
    *   `BITCRACK_EXE_PATH`: **(Required)** The full path to the `BitcrackRandomiser.exe` (or other primary application) you want to start.
        *Example: `C:\Path\To\Your\Application\BitcrackRandomiser.exe`*
    *   `ALLOWED_IPS`: **(Required)** Comma-separated list of IP addresses allowed to access the API.
        *Example: `192.168.1.100,127.0.0.1` (replace `192.168.1.100` with your Home Assistant IP)*
    *   `ALLOWED_TERMINATION_PROCESSES`: Comma-separated list of process names (e.g., `BitcrackRandomiser.exe`, `vanitysearch.exe`) that can be terminated via the API.
    *   `ALLOWED_START_PROGRAMS`: Comma-separated list of program names (from `BITCRACK_EXE_PATH`) that can be started via the API. Usually, this will be the filename part of `BITCRACK_EXE_PATH`.
    *   `API_HOST`: (Optional) Host IP for the server. Defaults to `0.0.0.0` (listens on all interfaces).
    *   `API_PORT`: (Optional) Port for the server. Defaults to `8080`.
    *   `LOG_LEVEL`: (Optional) Logging level. Defaults to `INFO`. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

    **Example `start_server_v2.1.bat` configuration snippet:**
    ```
    REM --- CONFIGURATION ---
    set API_SECRET_TOKEN=YOUR_VERY_SECRET_API_TOKEN_HERE
    set BITCRACK_EXE_PATH=C:\Users\Miner\bitcrackrandomiser\BitcrackRandomiser.exe
    set ALLOWED_IPS=192.168.178.10,127.0.0.1
    set ALLOWED_TERMINATION_PROCESSES=vanitysearch.exe,BitcrackRandomiser.exe
    set ALLOWED_START_PROGRAMS=BitcrackRandomiser.exe
    REM --- END CONFIGURATION ---
    ```

5.  **Adjust Application Path (if needed):**
    Ensure the `BITCRACK_EXE_PATH` variable in `start_server_v2.1.bat` points to the correct location of your `BitcrackRandomiser.exe` or primary application.

## Running the Server

Simply double-click the `start_server_v2.1.bat` file.
It will set the environment variables and then launch the Python API server. A console window will remain open showing server logs. To stop the server, close this console window or press `Ctrl+C`.

*Note: If the applications you are controlling require administrative privileges, you might need to run `start_server_v2.1.bat` as an administrator.*

## API Endpoints

*   **`GET /health`**:
    *   Checks the health of the API server.
    *   No authentication required.
    *   Returns basic server status, version, and features.
*   **`GET /status`**:
    *   Provides detailed server statistics, configuration, and status of managed processes.
    *   Requires Bearer Token authentication.
*   **`POST /kill-process`**:
    *   Terminates a specified process if it's in `ALLOWED_TERMINATION_PROCESSES`.
    *   Requires Bearer Token authentication.
    *   Payload: `{"process_name": "ProcessName.exe"}`
*   **`POST /start-direct`**:
    *   Starts the program defined by `BITCRACK_EXE_PATH` (if its name is in `ALLOWED_START_PROGRAMS`).
    *   Checks if the process is already running to prevent duplicates.
    *   Requires Bearer Token authentication.
    *   Payload: `{"program_name": "ProgramName.exe"}` (must match the filename part of `BITCRACK_EXE_PATH`)

## Home Assistant Integration

Here's how to integrate the Windows Process API Server with Home Assistant:

**Important:**
*   Replace `YOUR_WINDOWS_SERVER_IP` with the actual IP address of the Windows machine running the API server (e.g., `192.168.178.34`).
*   Replace `YOUR_VERY_SECRET_API_TOKEN_HERE` with the exact `API_SECRET_TOKEN` you configured in `start_server_v2.1.bat`.

### `configuration.yaml` Entries

Add the entries from `configuration.yaml` & `automation.yaml` to your corresponding Home Assistant files.
