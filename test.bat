@echo off
REM Test Monday File Management Agent

echo.
echo ========================================
echo Monday - Test Suite
echo ========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate

REM Run tests
echo Starting comprehensive tests...
echo.

python test_agent.py

if errorlevel 1 (
    echo.
    echo Tests FAILED
    pause
    exit /b 1
) else (
    echo.
    echo All tests PASSED!
    pause
    exit /b 0
)
