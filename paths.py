
import os, sys
BASE_PATH = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

def rp(*parts: str) -> str:
    return os.path.join(BASE_PATH, *parts)
