import os
import time
import shutil
import subprocess
from datetime import datetime

# Paths
WATCH_FILE = r"D:\bill\BILL.pdf"       # Software creates here
REPO_FOLDER = r"C:\Repos\bill"
TARGET_FILE = os.path.join(REPO_FOLDER, "BILL.pdf")
LOG_FILE = os.path.join(REPO_FOLDER, "log.txt")

# Full git path
GIT = r"C:\Program Files\Git\cmd\git.exe"

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run(cmd):
    log(f"Running: {cmd}")
    result = subprocess.run(cmd, cwd=REPO_FOLDER, shell=True,
                            capture_output=True, text=True)
    if result.stdout.strip():
        log(result.stdout.strip())
    if result.stderr.strip():
        log(result.stderr.strip())

def push_changes():
    if os.path.exists(WATCH_FILE):
        shutil.copy2(WATCH_FILE, TARGET_FILE)   # always copy fresh
        log("Copied latest BILL.pdf into repo")
    else:
        log("⚠️ WATCH_FILE missing, cannot copy")
        return

    run(f'"{GIT}" add -A')
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(f'"{GIT}" commit -m "Auto update BILL.pdf at {ts}" --allow-empty')
    run(f'"{GIT}" push origin main')
    log("✅ Last update successful")
    log("Public URL: https://bill-4rh.pages.dev/BILL.pdf")

def watch_file():
    log(f"Watching: {WATCH_FILE}")
    last_mtime = None
    while True:
        if os.path.exists(WATCH_FILE):
            mtime = os.path.getmtime(WATCH_FILE)
            if mtime != last_mtime:
                last_mtime = mtime
                log("Detected update in BILL.pdf, pushing...")
                push_changes()
        time.sleep(5)

if __name__ == "__main__":
    watch_file()
