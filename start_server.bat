@echo off
echo ========================================================
echo Starting SkillSwap Application Server...
echo URL: http://localhost:8000/
echo Swagger API Docs: http://localhost:8000/docs
echo ========================================================

cd /d "%~dp0server"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000
) else (
    python -m uvicorn main:app --reload --port 8000
)
pause
