@echo off
echo ========================================================
echo Running SkillSwap 16-Test Automated Verification Suite...
echo ========================================================

cd /d "%~dp0..\server"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "%~dp0test_suite.py"
) else (
    python "%~dp0test_suite.py"
)
pause
