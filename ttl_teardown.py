#!/usr/bin/env python3
import time
import subprocess
import sys
import os

# Time-to-live in seconds (e.g. 30 minutes)
TTL_SECONDS = int(os.environ.get("EPHEMERAL_TTL", 1800))

NGINX_SERVICE = "nginx"

def shutdown():
    print("[EphemeralProxy] TTL expired. Initiating teardown.")

    # Stop nginx
    subprocess.run(
        ["systemctl", "stop", NGINX_SERVICE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Optional: clear temp directories
    subprocess.run(
        ["rm", "-rf", "/tmp/*"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Shutdown the machine
    subprocess.run(
        ["shutdown", "-h", "now"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def main():
    print(f"[EphemeralProxy] Starting TTL countdown: {TTL_SECONDS} seconds")
    time.sleep(TTL_SECONDS)
    shutdown()

if __name__ == "__main__":
    main()
