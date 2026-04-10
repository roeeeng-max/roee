@echo off
chcp 65001 >nul
title מתכנן פיננסי

echo.
echo ================================
echo  מתכנן פיננסי - רועי וניקול
echo ================================
echo.

:: בדיקה שPython מותקן
echo [1/5] בודק Python...
python --version
if errorlevel 1 (
    echo.
    echo *** שגיאה: Python לא מותקן ***
    echo.
    echo הורד מ: https://www.python.org/downloads/
    echo חשוב: סמן "Add Python to PATH" בזמן ההתקנה!
    echo.
    pause
    exit /b 1
)

:: בדיקה שNode.js מותקן
echo [2/5] בודק Node.js...
node --version
if errorlevel 1 (
    echo.
    echo *** שגיאה: Node.js לא מותקן ***
    echo.
    echo הורד מ: https://nodejs.org/ - לחץ על LTS
    echo.
    pause
    exit /b 1
)

echo.
echo [3/5] מתקין תלויות Backend - אנא המתן...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo *** שגיאה בהתקנת Backend ***
    pause
    exit /b 1
)

echo.
echo [4/5] מתקין תלויות Frontend - אנא המתן...
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 (
    echo.
    echo *** שגיאה בהתקנת Frontend ***
    pause
    exit /b 1
)

echo.
echo [5/5] מפעיל שרתים...
cd /d "%~dp0backend"
start "Backend" python -m uvicorn main:app --host 127.0.0.1 --port 8000

cd /d "%~dp0frontend"
start "Frontend" npm run dev

echo.
echo ממתין 8 שניות שהשרתים יעלו...
timeout /t 8 /nobreak

echo.
echo פותח דפדפן...
start http://localhost:5173

echo.
echo ================================
echo  האפליקציה פועלת!
echo  אם הדפדפן לא נפתח - גש ל:
echo  http://localhost:5173
echo ================================
echo.
echo אל תסגור חלון זה בזמן השימוש!
echo לסגירה - לחץ על X כאן
echo.
pause
