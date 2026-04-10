"""
מתכנן פיננסי - רועי וניקול
לחץ פעמיים על קובץ זה להפעלה
"""
import subprocess
import sys
import os
import time
import webbrowser

def main():
    HERE = os.path.dirname(os.path.abspath(__file__))
    BACKEND = os.path.join(HERE, "backend")
    REQS = os.path.join(BACKEND, "requirements.txt")

    print("=" * 40)
    print("  מתכנן פיננסי - רועי וניקול")
    print("=" * 40)
    print()
    print(f"Python: {sys.executable}")
    print(f"תיקיה: {HERE}")
    print()

    # התקנת חבילות
    print("שלב 1: מתקין חבילות (יכול לקחת כמה דקות)...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", REQS, "-q"],
        cwd=BACKEND
    )
    if result.returncode != 0:
        print()
        print("*** שגיאה בהתקנת חבילות ***")
        return

    print("החבילות הותקנו!")
    print()
    print("שלב 2: מפעיל שרת...")

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    print("ממתין 5 שניות...")
    time.sleep(5)

    if server.poll() is not None:
        out, _ = server.communicate()
        print()
        print("*** השרת נכשל ***")
        print(out.decode("utf-8", errors="ignore"))
        return

    print()
    print("=" * 40)
    print("  האפליקציה פועלת!")
    print("  http://localhost:8000")
    print("=" * 40)
    print()
    webbrowser.open("http://localhost:8000")
    print("הדפדפן נפתח!")
    print()
    print("אל תסגור חלון זה!")
    print("לסגירה - לחץ Ctrl+C")
    print()

    try:
        server.wait()
    except KeyboardInterrupt:
        server.terminate()
        print("נסגר. להתראות!")

try:
    main()
except Exception as e:
    print()
    print(f"*** שגיאה: {e} ***")
    import traceback
    traceback.print_exc()

print()
input("לחץ Enter לסגירה...")
