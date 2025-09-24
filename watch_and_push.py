"""
watch_and_push.py
Watches D:\bill for new/changed PDF files and pushes them to a local git clone of your repo,
then writes the public GitHub Pages URL to Generated_URLs.txt.
"""

import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from git import Repo, GitCommandError
import urllib.parse

# --- CONFIGURE THESE ---
WATCH_FOLDER = r"D:\bill"                  # Folder where billing software saves PDFs
LOCAL_REPO = r"C:\Repos\bill"              # Local clone of your GitHub repo
GITHUB_USERNAME = "lifestyleshirva"        # Your GitHub username
REPO_NAME = "bill"                         # Repo name
PAGES_BASE = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/"
GENERATED_FILE = os.path.join(WATCH_FOLDER, "Generated_URLs.txt")
# -----------------------

repo = Repo(LOCAL_REPO)

def push_file_to_repo(src_path):
    filename = os.path.basename(src_path)
    dest_path = os.path.join(LOCAL_REPO, filename)
    shutil.copy2(src_path, dest_path)
    print(f"Copied to repo: {dest_path}")

    try:
        repo.index.add([filename])
        commit_message = f"Add/Update bill file {filename}"
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        print("Pushing to remote...")
        origin.push()
        print("Push finished.")
    except GitCommandError as e:
        print("Git error:", e)
        return None

    enc_name = urllib.parse.quote(filename)
    public_url = PAGES_BASE + enc_name
    update_generated_urls(filename, public_url)
    return public_url

def update_generated_urls(filename, url):
    lines = []
    if os.path.exists(GENERATED_FILE):
        with open(GENERATED_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    prefix = filename + " -> "
    lines = [ln for ln in lines if not ln.startswith(prefix)]
    from datetime import datetime
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_line = f"{filename} -> {url}    [{t}]"
    lines.insert(0, new_line)
    with open(GENERATED_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Updated Generated_URLs.txt")

class NewPDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        self.handle(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self.handle(event.src_path)

    def handle(self, path):
        _, ext = os.path.splitext(path)
        if ext.lower() != ".pdf":
            return
        print("Detected PDF:", path)
        time.sleep(1)
        url = push_file_to_repo(path)
        if url:
            print("Public URL:", url)

if __name__ == "__main__":
    print("Watching folder:", WATCH_FOLDER)
    if not os.path.isdir(WATCH_FOLDER):
        raise SystemExit(f"Watch folder not found: {WATCH_FOLDER}")
    event_handler = NewPDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

