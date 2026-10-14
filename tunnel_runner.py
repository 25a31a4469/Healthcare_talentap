import subprocess
import re
import sys
import time

print("Starting public tunnel for H4 Medication Safety System (port 5173)...")

cmd = [
    'ssh',
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'ServerAliveInterval=30',
    '-p', '443',
    '-R0:localhost:5173',
    'a.pinggy.io'
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

url_found = None
lines = []

for _ in range(60):
    line = proc.stdout.readline()
    if not line:
        time.sleep(0.5)
        continue
    lines.append(line)
    sys.stdout.write(line)
    sys.stdout.flush()
    # Look for https://...pinggy.link or similar
    match = re.search(r'(https://[a-zA-Z0-9\-\.]+\.pinggy\.link)', line)
    if match:
        url_found = match.group(1)
        with open("PUBLIC_URL.txt", "w") as f:
            f.write(url_found)
        print(f"\n==========================================")
        print(f"PUBLIC URL GENERATED: {url_found}")
        print(f"==========================================\n")
        break

# Keep the tunnel alive
try:
    while True:
        line = proc.stdout.readline()
        if not line:
            time.sleep(1)
            continue
        sys.stdout.write(line)
except KeyboardInterrupt:
    proc.terminate()
