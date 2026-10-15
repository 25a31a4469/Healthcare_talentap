import sys
import os

# Ensure backend directory is in sys.path so 'app.*' imports always resolve
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
