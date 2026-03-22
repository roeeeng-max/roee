#!/bin/bash
set -e

echo "🚀 מתכנן פיננסי - רועי וניקול"
echo "================================"

# Backend
echo "📦 מתקין תלויות Backend..."
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q

echo "▶️  מפעיל שרת Backend (port 8000)..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Frontend
echo "📦 מתקין תלויות Frontend..."
cd "$(dirname "$0")/frontend"
npm install --silent

echo "▶️  מפעיל Frontend (port 5173)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ האפליקציה רצה!"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "לעצור: Ctrl+C"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'עצרנו'" EXIT
wait
