#!/usr/bin/env python3
"""Town Crier run tools. Usage: ``python3 tc.py <command> --help``."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # find the towncrier package

from towncrier.cli import main  # noqa: E402

if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # output closed early (e.g. piped to head): stop quietly, as Python's docs advise
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
