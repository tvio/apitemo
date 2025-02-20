from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
import sys

class CodeChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"\n🔄 File {os.path.basename(event.src_path)} has been modified")
            print("⚡ Restarting menu.py...\n")
            subprocess.run([sys.executable, 'menu.py'])

def main():
    # Initial run
    print("🚀 Starting menu.py...\n")
    subprocess.run([sys.executable, 'menu.py'])
    
    # Set up the observer
    observer = Observer()
    observer.schedule(CodeChangeHandler(), path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping auto-reload...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()