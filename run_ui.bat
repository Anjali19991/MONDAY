@echo off
REM Start Ollama in the background (if not already running)
echo Starting Ollama with tinyllama...
start "" cmd /c "ollama run tinyllama"

REM Wait a moment for Ollama to start
timeout /t 3 /nobreak

REM Activate virtual environment and run Flask app
call .venv\Scripts\activate
echo.
echo Starting JARVIS Web UI...
echo.
echo Open your browser at: http://localhost:5000
echo.
python app.py
pause
