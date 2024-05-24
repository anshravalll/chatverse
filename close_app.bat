@echo off
REM Find the PID of the pythonw.exe process and terminate it

for /F "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq pythonw.exe" /NH') do taskkill /F /PID %%i
