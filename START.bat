@echo off
chcp 65001 >nul
title Tutorly - Запуск
color 0A

echo ================================
echo    Tutorly - Запуск
echo ================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python 3.10+ с python.org
    echo.
    pause
    exit /b 1
)

echo [OK] Python найден
echo.

REM Проверка зависимостей
echo Проверка зависимостей...
cd backend
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Устанавливаю зависимости...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить зависимости
        pause
        exit /b 1
    )
)

echo [OK] Зависимости установлены
echo.

REM Установка переменных окружения из .env.local
if exist ..\.env.local (
    echo Загрузка конфигурации...
    for /f "usebackq tokens=1,2 delims==" %%a in ("..\.env.local") do (
        set "%%a=%%b"
    )
    echo [OK] Конфигурация загружена
) else (
    echo [ВНИМАНИЕ] Файл .env.local не найден
    echo Используются настройки по умолчанию
    set DATABASE_URL=sqlite:///./tutorly.db
    set SECRET_KEY=local-development-key
    set CORS_ORIGINS=http://localhost:5173
)

echo.
echo ================================
echo    Запуск Tutorly...
echo ================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo [!] НЕ ЗАКРЫВАЙТЕ это окно
echo [!] Для остановки нажмите Ctrl+C
echo.

REM Запуск backend
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

REM Ждем запуска backend
timeout /t 3 /nobreak >nul

REM Запуск frontend
cd ..\frontend

REM Проверка node_modules
if not exist node_modules (
    echo Устанавливаю зависимости frontend...
    call npm install
)

REM Установка API URL
set VITE_API_URL=http://localhost:8000

REM Запуск frontend dev server
start /B npm run dev

REM Ждем запуска frontend
timeout /t 3 /nobreak >nul

REM Открываем браузер
start http://localhost:5173

echo.
echo ================================
echo    Tutorly запущен!
echo ================================
echo.

REM Держим окно открытым
pause
