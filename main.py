import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.main_window import run

if __name__ == "__main__":
    run()
