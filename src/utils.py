import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def path(*paths):
    return os.path.join(PROJECT_ROOT, *paths)

def ensure_directories():
    os.makedirs(path("data"), exist_ok=True)
    os.makedirs(path("outputs"), exist_ok=True)
    os.makedirs(path("dashboard"), exist_ok=True)
