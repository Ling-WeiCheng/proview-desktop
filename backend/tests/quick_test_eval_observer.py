import os
import subprocess
import sys


def main():
    test_file = os.path.join(os.path.dirname(__file__), "test_eval_observer.py")
    return subprocess.call([sys.executable, test_file])


if __name__ == "__main__":
    raise SystemExit(main())
