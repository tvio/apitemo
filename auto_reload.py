from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os
import sys

class CodeChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Ignore changes in logs directory
        if 'logs' in event.src_path:
            return
            
        if event.src_path.endswith('.py'):
            print(f"\n🔄 File {os.path.basename(event.src_path)} has been modified")
            print("⚡ Restarting menu.py...\n")
            # Kill any existing process
            if hasattr(self, 'process') and self.process:
                try:
                    self.process.kill()
                except:
                    pass  # Process might already be dead
            # Start new process
            self.process = subprocess.Popen(
                [sys.executable, 'menu.py'],
                stdout=None,  # Use None to inherit parent's stdout/stderr
                stderr=None,
                shell=True    # Use shell=True for Windows console apps
            )

def main():
    handler = CodeChangeHandler()
    # Initial run
    print("🚀 Starting menu.py...\n")
    handler.process = subprocess.Popen(
        [sys.executable, 'menu.py'],
        stdout=None,  # Use None to inherit parent's stdout/stderr
        stderr=None,
        shell=True    # Use shell=True for Windows console apps
    )
    
    # Set up the observer
    observer = Observer()
    observer.schedule(handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping auto-reload...")
        if hasattr(handler, 'process') and handler.process:
            try:
                handler.process.kill()
            except:
                pass  # Process might already be dead
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()