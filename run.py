import subprocess
import threading
import sys
import os
from colorama import init as colorama_init
from dotenv import load_dotenv

load_dotenv()
colorama_init()
port = os.getenv("ENV_PORT", "8000")
# ANSI colors
COLORS = {
    "api": "\033[96m",     # cyan
    "reset": "\033[0m"
}

def stream_output(process, name, color):
    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(f"{color}[{name}]{COLORS['reset']} {line.decode(errors='replace')}")
    process.stdout.close()

def run_concurrently():
    try:
        api_cmd = [
            "uvicorn",
            "app.main:app",
            "--reload",
            "--log-level", "debug",
            "--port", port
        ]

        print("...Starting API and Worker...\n")

        # Starting processes
        api_proc = subprocess.Popen(api_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Starting threaded output streaming
        threading.Thread(target=stream_output, args=(api_proc, "api", COLORS["api"]), daemon=True).start()

        api_proc.wait()

    except KeyboardInterrupt:
        print("\nShutting down processes...")

        if api_proc and api_proc.poll() is None:
            api_proc.terminate()
            try:
                api_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_proc.kill()

        print("Clean exit.")

if __name__ == "__main__":
    run_concurrently()
