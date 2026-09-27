@echo off
echo ========================================================
echo Starting MOGG SkillSwap Server on http://localhost:8000
echo ========================================================

cd /d "%~dp0..\server"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) else (
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
)
pause
