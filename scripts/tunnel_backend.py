import subprocess
import re
import sys
import time

print("Starting public tunnel for FastAPI backend (port 8000)...")

cmd = [
    'ssh',
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'ServerAliveInterval=30',
    '-R', '80:127.0.0.1:8000',
    'nokey@localhost.run'
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

url_found = None

for _ in range(70):
    line = proc.stdout.readline()
    if not line:
        time.sleep(0.3)
        continue
    sys.stdout.write(line)
    sys.stdout.flush()
    match = re.search(r'(https://[a-zA-Z0-9\-\.]+\.lhr\.life)', line)
    if match:
        url_found = match.group(1)
        with open("BACKEND_PUBLIC_URL.txt", "w") as f:
            f.write(url_found)
        print(f"\n==========================================")
        print(f"BACKEND PUBLIC TUNNEL: {url_found}")
        print(f"==========================================\n")
        break

try:
    while True:
        line = proc.stdout.readline()
        if not line:
            time.sleep(1)
            continue
        sys.stdout.write(line)
except KeyboardInterrupt:
    proc.terminate()
