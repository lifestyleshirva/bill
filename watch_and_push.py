import os
import time
import shutil
import subprocess
import json
import pdfplumber
import re
from datetime import datetime

# Paths
WATCH_FILE = r"D:\bill\BILL.pdf"       # Software creates here
REPO_FOLDER = r"C:\Repos\bill"
TARGET_FILE = os.path.join(REPO_FOLDER, "BILL.pdf")
BILLS_JSON = os.path.join(REPO_FOLDER, "bills.json")
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

def extract_bill_number(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        match = re.search(r"INV\s*NO[:\-]?\s*(\d+)", text, re.IGNORECASE)
        if match:
            bill_no = match.group(1)
            log(f"✅ Extracted Bill Number: {bill_no}")
            return bill_no
        else:
            log("⚠️ Bill Number not found in PDF")
            return None
    except Exception as e:
        log(f"Error reading PDF: {e}")
        return None

def update_bills_json(bill_no):
    try:
        if os.path.exists(BILLS_JSON):
            with open(BILLS_JSON, "r") as f:
                data = json.load(f)
        else:
            data = {"validBills": []}

        if bill_no and bill_no not in data["validBills"]:
            data["validBills"].append(bill_no)
            with open(BILLS_JSON, "w") as f:
                json.dump(data, f, indent=2)
            log(f"✅ Added Bill Number {bill_no} into bills.json")
        else:
            log("Bill already exists or invalid, not updating JSON")
    except Exception as e:
        log(f"Error updating bills.json: {e}")

def push_changes():
    if os.path.exists(WATCH_FILE):
        shutil.copy2(WATCH_FILE, TARGET_FILE)   # always copy fresh
        log("Copied latest BILL.pdf into repo")

        # Extract Bill Number & update bills.json
        bill_no = extract_bill_number(WATCH_FILE)
        if bill_no:
            update_bills_json(bill_no)
    else:
        log("⚠️ WATCH_FILE missing, cannot copy")
        return

    run(f'"{GIT}" add -A')
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(f'"{GIT}" commit -m "Auto update BILL.pdf and bills.json at {ts}" --allow-empty')
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
