import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and getattr(sys, '_MEIPASS', None):
    BASE_DIR = Path(sys._MEIPASS)  # noqa
    PROJECT_DIR = Path(sys._MEIPASS)  # noqa
else:
    BASE_DIR = Path(__file__).parent.parent
    PROJECT_DIR = Path(BASE_DIR).parent
