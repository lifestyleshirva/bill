import os
import time
import shutil
import subprocess
from datetime import datetime

# File paths
WATCH_FILE = r"D:\bill\BILL.pdf"    # Your software always generates BILL.pdf here
REPO_FOLDER = r"C:\Repos\bill"      # GitHub repo local clone
TARGET_FILE = os.path.join(REPO_FOLDER, "BILL.pdf")

def run(cmd):
    result = subprocess.run(cmd, cwd=REPO_FOLDER, shell=True,
                            capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

def push_changes():
    # Stage everything just in case
    run("git add -A")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Always commit, even if Git thinks nothing changed
    run(f'git commit -m "Auto update BILL.pdf at {ts}" --allow-empty')
    run("git push origin main")

def watch_file():
    print(f"[{datetime.now()}] Watching: {WATCH_FILE}")
    last_mtime = None
    while True:
        if os.path.exists(WATCH_FILE):
            mtime = os.path.getmtime(WATCH_FILE)
            if mtime != last_mtime:
                last_mtime = mtime
                print(f"[{datetime.now()}] Detected update in BILL.pdf, pushing...")
                shutil.copy2(WATCH_FILE, TARGET_FILE)
                push_changes()
                print(f"[{datetime.now()}] Public URL: https://bill-4rh.pages.dev/BILL.pdf")
        time.sleep(5)

if __name__ == "__main__":
    watch_file()
