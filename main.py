import uvicorn
import subprocess
import threading
import os
import sys
import time

def run_backend():
    print("[Backend] Starting FastAPI server...")
    # Add the current directory to sys.path so 'backend' can be found
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)

def run_frontend():
    print("[Frontend] Starting Vite development server...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

    # Handle different npm command for Windows/Linux
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    try:
        subprocess.run([npm_cmd, "run", "dev"], cwd=frontend_dir, check=True)
    except Exception as e:
        print(f"[Frontend] Error starting Vite: {e}")

if __name__ == "__main__":
    print("========================================")
    print("   MTG Collection App - Unified Startup")
    print("========================================")

    # Start Backend Thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Wait a moment for backend to initialize
    time.sleep(2)

    print("\n----------------------------------------")
    print("   App is starting up!")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:5173")
    print("----------------------------------------\n")

    # Start Frontend (in main thread to handle Ctrl+C easily)
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
