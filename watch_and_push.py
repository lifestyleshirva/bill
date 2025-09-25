import os
import time
import shutil
import subprocess
from datetime import datetime

WATCH_FILE = r"D:\bill\bill.pdf"   # always same file from your software
REPO_FOLDER = r"C:\Repos\bill"
TARGET_FILE = os.path.join(REPO_FOLDER, "bill.pdf")

def run(cmd):
    result = subprocess.run(cmd, cwd=REPO_FOLDER, shell=True,
                            capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

def push_changes():
    run("git add bill.pdf")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(f'git commit -m "Auto update bill.pdf at {ts}" || echo "No changes"')
    run("git push origin main")

def watch_file():
    print(f"[{datetime.now()}] Watching: {WATCH_FILE}")
    last_mtime = None
    while True:
        if os.path.exists(WATCH_FILE):
            mtime = os.path.getmtime(WATCH_FILE)
            if mtime != last_mtime:
                last_mtime = mtime
                print(f"[{datetime.now()}] Detected update in bill.pdf, pushing...")
                shutil.copy2(WATCH_FILE, TARGET_FILE)
                push_changes()
                print(f"[{datetime.now()}] Public URL: https://bill-4rh.pages.dev/bill.pdf")
        time.sleep(5)

if __name__ == "__main__":
    watch_file()
