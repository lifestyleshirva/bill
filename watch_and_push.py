import os
import time
import shutil
from git import Repo
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === SETTINGS ===
WATCH_FOLDER = r"D:\bill"                  # Billing software PDFs save ಆಗೋ folder
LOCAL_REPO = r"C:\Repos\bill"              # Git repo location
CLOUDFLARE_URL = "https://bill-4rh.pages.dev/"  # Cloudflare Pages site URL

# Git repo open ಮಾಡೋದು
repo = Repo(LOCAL_REPO)

def handle_pdf(file_path):
    filename = os.path.basename(file_path)
    dest_path = os.path.join(LOCAL_REPO, filename)

    # Copy PDF to repo folder
    shutil.copy2(file_path, dest_path)
    print(f"Copied to repo: {dest_path}")

    # Git operations
    try:
        repo.index.add([filename])
        repo.index.commit(f"Add or update PDF: {filename}")
        origin = repo.remote(name="origin")
        print("Pushing to remote...")
        origin.push()
        print("Push finished.")
    except Exception as e:
        print("Error pushing:", e)

    # Public Cloudflare URL
    public_url = CLOUDFLARE_URL + filename
    print(f"Public URL: {public_url}")

    # Save to Generated_URLs.txt
    with open(os.path.join(LOCAL_REPO, "Generated_URLs.txt"), "a") as f:
        f.write(public_url + "\n")
    print("Updated Generated_URLs.txt")

# Watchdog event handler
class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            time.sleep(1)  # wait until file write completes
            handle_pdf(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            time.sleep(1)
            handle_pdf(event.src_path)

if __name__ == "__main__":
    print(f"Watching folder: {WATCH_FOLDER}")
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

