# Windows Process API Server - Enhanced Version
# Erweiterte Version für direkte BitcrackRandomiser.exe Ausführung

r"""
             _   ___                
            (_) /   |               
  __ _ _ __  _ / /| |_ __ ___   ___ 
 / _` | '_ \| / /_| | '_ ` _ \ / _ \
| (_| | |_) | \___  | | | | | |  __/
 \__,_| .__/|_|   |_/_| |_| |_|\___|
      | |                           
      |_|

Windows Process API Server v2.0
Sichere HTTP-API für Prozesssteuerung
"""

import os
import subprocess
import time
import logging
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import psutil
import sys
import ipaddress

# Configuration constants - Diese können über Umgebungsvariablen überschrieben werden
API_SECRET_TOKEN = os.getenv("API_SECRET_TOKEN", "YOUR_API_KEY")
ALLOWED_TERMINATION_PROCESSES = os.getenv("ALLOWED_TERMINATION_PROCESSES", "BitcrackRandomiser.exe,vanitysearch.exe,process.exe").split(",")
ALLOWED_START_PROGRAMS = os.getenv("ALLOWED_START_PROGRAMS", "BitcrackRandomiser.exe").split(",")
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "Homeassistant-IP,127.0.0.1").split(",")

# NEU: Direkter Pfad zur BitcrackRandomiser.exe
BITCRACK_EXE_PATH = os.getenv("BITCRACK_EXE_PATH", r"C:\Users\Miner\bitcrackrandomiser\BitcrackRandomiser.exe")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("process_api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("process_api")

# Security Logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)
security_handler = logging.FileHandler("security.log")
security_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
security_logger.addHandler(security_handler)

# Statistics tracking
start_time = datetime.now()
statistics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "process_kills": 0,
    "process_starts": 0,
    "unauthorized_attempts": 0
}

# Initialize Flask app
app = Flask(__name__)

def verify_auth_token(auth_header):
    """Verify the authorization token in the request header"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split('Bearer ')[1].strip()
    # Use constant time comparison to prevent timing attacks
    return hmac.compare_digest(token, API_SECRET_TOKEN)

def is_ip_allowed(ip):
    """Check if the IP is in the allowed list"""
    if not ip:
        return False
    
    try:
        client_ip = ipaddress.ip_address(ip)
        for allowed_ip in ALLOWED_IPS:
            if '/' in allowed_ip:  # CIDR notation
                if client_ip in ipaddress.ip_network(allowed_ip):
                    return True
            else:  # Single IP
                if client_ip == ipaddress.ip_address(allowed_ip):
                    return True
        return False
    except ValueError:
        security_logger.error(f"Invalid IP format: {ip}")
        return False

@app.before_request
def validate_request():
    """Middleware to validate all requests"""
    # Skip validation for health endpoint
    if request.path == '/health':
        return None
    
    # Get client IP (consider X-Forwarded-For for proxied requests)
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # IP whitelist check
    if not is_ip_allowed(client_ip):
        security_logger.warning(f"Unauthorized access attempt from {client_ip} to {request.path}")
        statistics["unauthorized_attempts"] += 1
        return jsonify({"error": "Access denied"}), 403

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - no authentication required"""
    uptime = datetime.now() - start_time
    return jsonify({
        "status": "healthy",
        "uptime_seconds": uptime.total_seconds(),
        "version": "2.0.0",
        "features": ["process_management", "security", "monitoring", "gui_support"]
    })

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint - returns detailed information about the API"""
    # Auth token validation
    auth_header = request.headers.get('Authorization')
    if not verify_auth_token(auth_header):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        security_logger.warning(f"Invalid authentication from {client_ip} to {request.path}")
        statistics["unauthorized_attempts"] += 1
        return jsonify({"error": "Unauthorized"}), 401

    uptime = datetime.now() - start_time
    
    # Get system information
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Prepare response
    response = {
        "server_info": {
            "uptime": str(uptime),
            "uptime_seconds": uptime.total_seconds(),
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "system_resources": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "memory_total_mb": memory.total / (1024 * 1024)
        },
        "statistics": statistics,
        "configuration": {
            "allowed_termination_processes": ALLOWED_TERMINATION_PROCESSES,
            "allowed_start_programs": ALLOWED_START_PROGRAMS,
            "allowed_ips": ALLOWED_IPS,
            "bitcrack_exe_path": BITCRACK_EXE_PATH  # NEU: Zeigt den konfigurierten Pfad
        }
    }
    
    return jsonify(response)

@app.route('/kill-process', methods=['POST'])
def kill_process():
    """Endpoint to kill a specific process by name"""
    # Auth token validation
    auth_header = request.headers.get('Authorization')
    if not verify_auth_token(auth_header):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        security_logger.warning(f"Invalid authentication from {client_ip} to {request.path}")
        statistics["unauthorized_attempts"] += 1
        return jsonify({"error": "Unauthorized"}), 401

    start_request_time = time.time()
    data = request.json
    
    if not data or 'process_name' not in data:
        statistics["total_requests"] += 1
        statistics["failed_requests"] += 1
        return jsonify({"error": "Missing process_name parameter"}), 400

    process_name = data['process_name']
    logger.info(f"Request to kill process: {process_name}")

    # Check if process is in the allowed list
    if process_name not in ALLOWED_TERMINATION_PROCESSES:
        security_logger.warning(f"Attempt to kill non-allowed process: {process_name}")
        statistics["total_requests"] += 1
        statistics["failed_requests"] += 1
        return jsonify({"error": f"Process {process_name} is not allowed to be terminated"}), 403

    terminated_count = 0
    terminated_pids = []

    # Find and terminate all instances of the process
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if process name matches
            if proc.info['name'].lower() == process_name.lower():
                pid = proc.info['pid']
                logger.info(f"Terminating process {process_name} with PID {pid}")
                
                # Terminate the process
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait for process to terminate, kill if it doesn't respond
                try:
                    process.wait(timeout=3)
                except psutil.TimeoutExpired:
                    logger.warning(f"Process {pid} did not terminate gracefully, killing it")
                    process.kill()
                
                terminated_count += 1
                terminated_pids.append(pid)
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.error(f"Error terminating process: {e}")

    # Update statistics
    statistics["total_requests"] += 1
    statistics["process_kills"] += terminated_count
    
    if terminated_count > 0:
        statistics["successful_requests"] += 1
        execution_time = time.time() - start_request_time
        
        return jsonify({
            "success": True,
            "message": f"Successfully terminated {terminated_count} instance(s) of {process_name}",
            "terminated_processes": terminated_count,
            "terminated_pids": terminated_pids,
            "execution_time_seconds": execution_time
        })
    else:
        statistics["failed_requests"] += 1
        return jsonify({
            "success": False,
            "message": f"No running instances of {process_name} found"
        }), 404

@app.route('/start-from-shortcut', methods=['POST'])
def start_from_shortcut():
    """DEPRECATED: Use /start-direct instead"""
    return jsonify({
        "error": "This endpoint has been deprecated. Use /start-direct instead.",
        "new_endpoint": "/start-direct"
    }), 410

@app.route('/start-direct', methods=['POST'])
def start_direct():
    """Endpoint to start BitcrackRandomiser.exe directly from its specified path"""
    # Auth token validation
    auth_header = request.headers.get('Authorization')
    if not verify_auth_token(auth_header):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        security_logger.warning(f"Invalid authentication from {client_ip} to {request.path}")
        statistics["unauthorized_attempts"] += 1
        return jsonify({"error": "Unauthorized"}), 401

    start_request_time = time.time()
    data = request.json
    
    if not data or 'program_name' not in data:
        statistics["total_requests"] += 1
        statistics["failed_requests"] += 1
        return jsonify({"error": "Missing program_name parameter"}), 400

    program_name = data['program_name']
    logger.info(f"Request to start program directly: {program_name}")

    # Check if program is in the allowed list
    if program_name not in ALLOWED_START_PROGRAMS:
        security_logger.warning(f"Attempt to start non-allowed program: {program_name}")
        statistics["total_requests"] += 1
        statistics["failed_requests"] += 1
        return jsonify({"error": f"Program {program_name} is not allowed to be started"}), 403

    # Check if the specified path exists
    if not os.path.exists(BITCRACK_EXE_PATH):
        logger.error(f"Program path does not exist: {BITCRACK_EXE_PATH}")
        statistics["total_requests"] += 1
        statistics["failed_requests"] += 1
        return jsonify({
            "success": False,
            "message": f"Program path not found: {BITCRACK_EXE_PATH}"
        }), 404

    try:
        # Prepare working directory - extract directory from full path
        working_dir = os.path.dirname(BITCRACK_EXE_PATH)
        logger.info(f"Starting {BITCRACK_EXE_PATH} in working directory {working_dir}")

        # KORRIGIERT: Für GUI-Anwendungen verwenden wir CREATE_NEW_CONSOLE statt DETACHED_PROCESS
        # Windows Creation Flags:
        # CREATE_NEW_CONSOLE = 0x00000010 (Erstellt neue Console für GUI-Apps)
        # CREATE_NEW_PROCESS_GROUP = 0x00000200 (Neue Prozessgruppe)
        # Combined flags = 0x00000210
        process = subprocess.Popen(
            [BITCRACK_EXE_PATH],
            cwd=working_dir,
            creationflags=0x00000210,  # CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP
            shell=False,
            # Entfernt: stdin/stdout/stderr Redirection für GUI-Apps
            # GUI-Anwendungen benötigen ihre Standard-Handles
        )

        # Wait a short moment to check if process started successfully
        time.sleep(0.5)
        
        # Check if process is still running
        if process.poll() is None:
            # Process is still running - success!
            statistics["total_requests"] += 1
            statistics["successful_requests"] += 1
            statistics["process_starts"] += 1
            execution_time = time.time() - start_request_time

            logger.info(f"Successfully started {program_name} with PID {process.pid}")
            
            return jsonify({
                "success": True,
                "message": f"Successfully started {program_name}",
                "pid": process.pid,
                "executable_path": BITCRACK_EXE_PATH,
                "working_directory": working_dir,
                "execution_time_seconds": execution_time,
                "note": "Process is running with new console and will persist independently",
                "creation_flags": "CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP"
            })
        else:
            # Process exited immediately - error
            exit_code = process.poll()
            logger.error(f"Process {program_name} exited immediately with code {exit_code}")
            statistics["total_requests"] += 1
            statistics["failed_requests"] += 1
            
            return jsonify({
                "success": False,
                "message": f"Process {program_name} started but exited immediately",
                "exit_code": exit_code,
                "executable_path": BITCRACK_EXE_PATH,
                "suggestion": "Check if the program requires specific arguments or dependencies"
            }), 500

    except Exception as e:
        logger.error(f"Error starting program: {e}")
        statistics["total_requests"] += 1
        statistics["failed_requests"] += 1
        
        return jsonify({
            "success": False,
            "message": f"Failed to start {program_name}: {str(e)}",
            "executable_path": BITCRACK_EXE_PATH
        }), 500

# Main entry point
if __name__ == "__main__":
    # Print ASCII Art and startup info
    print(r"""
             _   ___                
            (_) /   |               
  __ _ _ __  _ / /| |_ __ ___   ___ 
 / _` | '_ \| / /_| | '_ ` _ \ / _ \\
| (_| | |_) | \\___  | | | | | |  __/
 \\__,_| .__/|_|   |_/_| |_| |_|\\___|
      | |                           
      |_|

Windows Process API Server v2.0
================================
Sichere HTTP-API für Prozesssteuerung
    """)
    
    logger.info(f"Process API Server starting...")
    logger.info(f"BitCrack executable path: {BITCRACK_EXE_PATH}")
    logger.info(f"Allowed IPs: {ALLOWED_IPS}")
    logger.info(f"Allowed termination processes: {ALLOWED_TERMINATION_PROCESSES}")
    logger.info(f"Allowed start programs: {ALLOWED_START_PROGRAMS}")

    # Import waitress for production server
    try:
        from waitress import serve
        logger.info("Starting production server with Waitress...")
        logger.info("Werkzeug development server warning eliminated!")
        logger.info("GUI process support: CREATE_NEW_CONSOLE enabled")
        
        # Serve on all interfaces but IP is restricted by validation middleware
        serve(app, host="0.0.0.0", port=8080, threads=6, connection_limit=100)
    except ImportError:
        logger.warning("Waitress not installed, using Flask development server")
        logger.warning("INSTALLING WAITRESS IS RECOMMENDED FOR PRODUCTION USE")
        logger.warning("Use: pip install waitress")
        app.run(host="0.0.0.0", port=8080, debug=False)
