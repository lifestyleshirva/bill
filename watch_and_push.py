import os
import time
import shutil
import subprocess
import pdfplumber
import re
import json
from datetime import datetime

# Paths
WATCH_FILE = r"D:\bill\BILL.pdf"       # Software creates here
REPO_FOLDER = r"C:\Repos\bill"
TARGET_FILE = os.path.join(REPO_FOLDER, "BILL.pdf")
JSON_FILE = os.path.join(REPO_FOLDER, "bills.json")
LOG_FILE = os.path.join(REPO_FOLDER, "log.txt")

# Full git path
GIT = r"C:\Program Files\Git\cmd\git.exe"

def clear_log():
    # ✅ Empty log.txt before each run
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

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

def extract_bill_data():
    try:
        with pdfplumber.open(WATCH_FILE) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        # ✅ Extract Name (stop before MOB)
        name_match = re.search(r"NAME:\s*([A-Za-z\s]+?)(?:MOB:|$)", text, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else None

        # Extract Mobile
        mobile_match = re.search(r"MOB:\s*([0-9]+)", text)
        mobile = mobile_match.group(1) if mobile_match else None

        # Extract Bill Number
        bill_no_match = re.search(r"INV NO:\s*(\d+)", text)
        bill_no = bill_no_match.group(1) if bill_no_match else None

        # Extract Payable Amount
        payable_match = re.search(r"PAYABLE\s+`?\s*([\d.]+)", text)
        payable = payable_match.group(1) if payable_match else None

        if bill_no:
            log(f"✅ Extracted Bill Data → No: {bill_no}, Name: {name}, Mobile: {mobile}, Payable: {payable}")
            return {
                "billNo": bill_no,
                "name": name,
                "mobile": mobile,
                "payable": payable
            }
        else:
            log("⚠️ Bill number not found in PDF")
            return None
    except Exception as e:
        log(f"⚠️ Error extracting bill data: {e}")
        return None

def update_json(bill_data):
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except:
                    data = {"bills": []}
        else:
            data = {"bills": []}

        if "bills" not in data:
            data["bills"] = []

        # Remove old entry with same billNo
        data["bills"] = [b for b in data["bills"] if b.get("billNo") != bill_data["billNo"]]

        # Add new bill
        data["bills"].append(bill_data)

        # ✅ Keep only latest 50 bills
        if len(data["bills"]) > 50:
            data["bills"] = data["bills"][-50:]

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        log(f"✅ Added Bill {bill_data['billNo']} → bills.json now has {len(data['bills'])} entries")

    except Exception as e:
        log(f"Error updating bills.json: {e}")

def push_changes():
    clear_log()  # ✅ clear old log before each run

    if os.path.exists(WATCH_FILE):
        shutil.copy2(WATCH_FILE, TARGET_FILE)   # always copy fresh
        log("Copied latest BILL.pdf into repo")
    else:
        log("⚠️ WATCH_FILE missing, cannot copy")
        return

    bill_data = extract_bill_data()
    if bill_data:
        update_json(bill_data)

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
