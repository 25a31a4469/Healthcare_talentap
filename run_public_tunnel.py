import subprocess
import re
import sys
import time

print("Launching localhost.run public tunnel for H4 Medication Safety System...")

cmd = [
    'ssh',
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'ServerAliveInterval=30',
    '-R', '80:127.0.0.1:5173',
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
        with open("PUBLIC_URL.txt", "w") as f:
            f.write(url_found)
        print(f"\n==========================================")
        print(f"ACTIVE PUBLIC TUNNEL LINK: {url_found}")
        print(f"==========================================\n")
        break

# Keep process alive
try:
    while True:
        line = proc.stdout.readline()
        if not line:
            time.sleep(1)
            continue
        sys.stdout.write(line)
except KeyboardInterrupt:
    proc.terminate()
