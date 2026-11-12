"""
run_app.py — Unified launcher for InfraSense Backend (FastAPI) and Frontend (Vite).
Usage:
    python run_app.py
"""
import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--app-dir", "backend", "--port", "8000", "--host", "127.0.0.1"]
    frontend_cmd = ["npm", "--prefix", "frontend", "run", "dev"]

    print("=" * 60)
    print("InfraSense — Karnataka Analytics Application Launcher")
    print("=" * 60)
    print("[1] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=root_dir)

    time.sleep(2)

    print("[2] Starting React Vite frontend on http://localhost:3000 ...")
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=root_dir, shell=True)

    print("\nInfraSense platform is live:")
    print("  • Frontend Dashboard: http://localhost:3000")
    print("  • Backend API Docs:   http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to terminate both servers.")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down InfraSense servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
