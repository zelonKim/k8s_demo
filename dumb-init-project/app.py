import time
import subprocess
import os

def spawn_child():
    global child
    print("Spawning child process...")
    child = subprocess.Popen(["python", "-c", "import time; time.sleep(1000)"])
    print(f"Child PID: {child.pid}")

if __name__ == "__main__":
    print("Starting main process...")
    spawn_child()
    while True:
        print(f"Main process running... PID: {os.getpid()}")
        time.sleep(10)