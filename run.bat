@echo off
REM Переход в директорию, где лежит этот BAT-файл
cd /d "%~dp0"

REM Проверка наличия папки виртуального окружения
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] The virtual environment is activated
    
    REM Запуск вашего Python-скрипта
    python main.py
) else (
    echo [ERROR] The venv folder was not found! Okay, we'll fix it now.
    call python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    python.exe -m pip install --upgrade pip
    python main.py
)

pause