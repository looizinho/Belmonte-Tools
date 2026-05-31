@echo off
setlocal

set "PACKAGE_ROOT=%~dp0src"
set "PYTHONPATH=%PACKAGE_ROOT%;%PYTHONPATH%"
set "PYTHON=%~dp0venv\Scripts\python.exe"
if exist "%PYTHON%" (
    "%PYTHON%" -m belmonte_tools %*
) else (
    py -3 -m belmonte_tools %*
)
