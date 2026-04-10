@echo off
chcp 65001 >nul
title מתכנן פיננסי - רועי וניקול

echo.
echo ================================
echo  מתכנן פיננסי - רועי וניקול
echo ================================
echo.

:: בדיקה שPython מותקן
python --version >nul 2>&1
if errorlevel 1 (
    echo שגיאה: Python לא מותקן!
    echo.
    echo אנא הורד והתקן Python מ:
    echo https://www.python.org/downloads/
    echo.
    echo חשוב: בזמן ההתקנה סמן את "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: בדיקה שNode.js מותקן
node --version >nul 2>&1
if errorlevel 1 (
    echo שגיאה: Node.js לא מותקן!
    echo.
    echo אנא הורד והתקן Node.js מ:
    echo https://nodejs.org/
    echo.
    echo בחר את הגרסה LTS
    echo.
    pause
    exit /b 1
)

echo מתקין תלויות Backend...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo שגיאה בהתקנת תלויות Backend
    pause
    exit /b 1
)

echo מפעיל שרת Backend...
start /b python -m uvicorn main:app --host 127.0.0.1 --port 8000 > "%TEMP%\finance-backend.log" 2>&1

echo מתקין תלויות Frontend...
cd /d "%~dp0frontend"
call npm install --silent
if errorlevel 1 (
    echo שגיאה בהתקנת תלויות Frontend
    pause
    exit /b 1
)

echo מפעיל Frontend...
start /b npm run dev > "%TEMP%\finance-frontend.log" 2>&1

echo.
echo ממתין שהשרתים יעלו...
timeout /t 5 /nobreak >nul

echo.
echo ================================
echo  האפליקציה מוכנה!
echo ================================
echo.
echo פותח דפדפן...
start http://localhost:5173

echo.
echo לעצור את האפליקציה - סגור חלון זה
echo.
pause
