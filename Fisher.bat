@echo off
setlocal

REM Obtiene el directorio donde se encuentra el archivo .bat
set SCRIPT_DIR=%~dp0

REM Cambia al directorio del script
cd /d %SCRIPT_DIR%

REM Ejecuta el script de Python
python Fisher.py

endlocal
