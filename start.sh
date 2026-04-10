#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "מתכנן פיננסי - רועי וניקול"
echo "================================"

# Backend - virtualenv
VENV="$SCRIPT_DIR/venv"
if [ ! -d "$VENV" ]; then
  echo "יוצר virtualenv..."
  python3 -m venv "$VENV"
fi

echo "מתקין תלויות Backend..."
"$VENV/bin/pip" install -r "$SCRIPT_DIR/backend/requirements.txt" -q

echo "מפעיל שרת Backend (port 8000)..."
cd "$SCRIPT_DIR/backend"
"$VENV/bin/uvicorn" main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Frontend
echo "מתקין תלויות Frontend..."
cd "$SCRIPT_DIR/frontend"
npm install --silent

echo "מפעיל Frontend (port 5173)..."
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "האפליקציה רצה!"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "לעצור: Ctrl+C"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'עצרנו'" EXIT
wait
