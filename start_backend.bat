@echo off
cd /d "%~dp0"
echo Starting Smart AI Code Studio FastAPI backend...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
