@echo off
echo ===================================================
echo Starting InfraSense Karnataka Analytics Platform
echo ===================================================
echo [1/2] Launching FastAPI Backend on http://localhost:8000 ...
start "InfraSense Backend (Port 8000)" cmd /k "python -m uvicorn main:app --app-dir backend --port 8000 --host 127.0.0.1"

echo [2/2] Launching React Vite Frontend on http://localhost:3000 ...
start "InfraSense Frontend (Port 3000)" cmd /k "npm --prefix frontend run dev"

echo.
echo ===================================================
echo Application successfully launched in separate windows!
echo • Frontend Dashboard: http://localhost:3000
echo • Backend OpenAPI Docs: http://localhost:8000/docs
echo ===================================================
