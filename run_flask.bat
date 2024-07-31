@echo off
REM Change directory to your Flask app location
echo Changing directory to your Flask app location...
cd C:\Users\Ansh\Desktop\coding\Chatverse
if %errorlevel% neq 0 (
    echo Failed to change directory. Path not found.
    pause
    exit /b
)

#REM Activate the virtual environment
#echo Activating the virtual environment...
#call C:\Users\Ansh\Desktop\coding\Chatverse\Scripts\activate.bat
#if %errorlevel% neq 0 (
#    echo Failed to activate virtual environment. Path not found or invalid.
#    pause
#    exit /b
#)

REM Run your Flask app
echo Running Flask app...
pythonw main.py > C:\Users\Ansh\Desktop\coding\Chatverse\flask_app.log 2>&1
if %errorlevel% neq 0 (
    echo Failed to start Flask app.
    pause
    exit /b
)

echo Flask app started successfully. Check flask_app.log for details.
pause


