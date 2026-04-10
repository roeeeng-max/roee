"""
מתכנן פיננסי - רועי וניקול
לחץ פעמיים על קובץ זה להפעלה
"""
import subprocess
import sys
import os
import time
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(HERE, "backend")
REQS = os.path.join(BACKEND, "requirements.txt")

print("=" * 40)
print("  מתכנן פיננסי - רועי וניקול")
print("=" * 40)
print()

# התקנת חבילות
print("מתקין חבילות (פעם ראשונה לוקח כמה דקות)...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", REQS, "-q"],
    cwd=BACKEND
)
if result.returncode != 0:
    print()
    print("*** שגיאה בהתקנת חבילות ***")
    input("לחץ Enter לסגירה...")
    sys.exit(1)

print("החבילות הותקנו בהצלחה!")
print()
print("מפעיל שרת...")

# הפעלת השרת
server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app",
     "--host", "127.0.0.1", "--port", "8000"],
    cwd=BACKEND
)

print("ממתין שהשרת יעלה...")
time.sleep(4)

if server.poll() is not None:
    print()
    print("*** השרת נכשל בהפעלה ***")
    input("לחץ Enter לסגירה...")
    sys.exit(1)

print()
print("=" * 40)
print("  האפליקציה פועלת!")
print("  http://localhost:8000")
print("=" * 40)
print()
print("פותח דפדפן...")
webbrowser.open("http://localhost:8000")

print()
print("אל תסגור חלון זה בזמן השימוש!")
print("לסגירה - לחץ Ctrl+C")
print()

try:
    server.wait()
except KeyboardInterrupt:
    print()
    print("סוגר שרת...")
    server.terminate()
    print("להתראות!")
