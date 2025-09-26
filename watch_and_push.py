import os
import time
import shutil
import subprocess
import json
import pdfplumber
import re
from datetime import datetime

# Paths
WATCH_FILE = r"D:\bill\BILL.pdf"
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

# ✅ Extract BillNo + Mobile + Net Amount
def extract_bill_data(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

        # Bill No
        bill_match = re.search(r"INV\s*NO[:\-]?\s*(\d+)", text, re.IGNORECASE)
        bill_no = bill_match.group(1) if bill_match else None

        # Mobile
        mob_match = re.search(r"MOB[:\-]?\s*(\d{10})", text, re.IGNORECASE)
        mobile = mob_match.group(1) if mob_match else None

        # Net Amount (PAYABLE or TOTAL)
        amt_match = re.search(r"PAYABLE\s*[₹` ]?\s*([\d,]+\.\d{2}|\d+)", text, re.IGNORECASE)
        if not amt_match:
            amt_match = re.search(r"TOTAL\s*[₹` ]?\s*([\d,]+\.\d{2}|\d+)", text, re.IGNORECASE)
        amount = amt_match.group(1) if amt_match else None

        log(f"✅ Extracted Bill Data → No: {bill_no}, Mobile: {mobile}, Amount: {amount}")
        return {"billNo": bill_no, "mobile": mobile, "amount": amount}

    except Exception as e:
        log(f"Error reading PDF: {e}")
        return None

# ✅ Update bills.json
def update_bills_json(bill_data):
    try:
        if not bill_data or not bill_data["billNo"]:
            log("⚠️ Invalid bill data, skipping JSON update")
            return

        if os.path.exists(BILLS_JSON):
            with open(BILLS_JSON, "r") as f:
                data = json.load(f)
        else:
            data = {"bills": []}

        # check duplicate
        exists = any(b["billNo"] == bill_data["billNo"] for b in data["bills"])
        if not exists:
            data["bills"].append(bill_data)
            with open(BILLS_JSON, "w") as f:
                json.dump(data, f, indent=2)
            log(f"✅ Added Bill {bill_data['billNo']} to bills.json")
        else:
            log("ℹ️ Bill already exists, not adding again")

    except Exception as e:
        log(f"Error updating bills.json: {e}")

def push_changes():
    if os.path.exists(WATCH_FILE):
        shutil.copy2(WATCH_FILE, TARGET_FILE)
        log("Copied latest BILL.pdf into repo")

        # extract bill data and update json
        bill_data = extract_bill_data(WATCH_FILE)
        if bill_data:
            update_bills_json(bill_data)
    else:
        log("⚠️ WATCH_FILE missing, cannot copy")
        return

    run(f'"{GIT}" add -A')
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(f'"{GIT}" commit -m "Auto update BILL.pdf and bills.json at {ts}" --allow-empty')
    run(f'"{GIT}" push origin main')
    log("✅ Last update successful")
    log("Public URL: https://bill-4rh.pages.dev/BILL.pdf")
    log("Public JSON: https://bill-4rh.pages.dev/bills.json")

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
