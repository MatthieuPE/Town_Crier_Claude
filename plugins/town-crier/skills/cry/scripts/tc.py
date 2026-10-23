#!/usr/bin/env python3
"""Town Crier run tools. Usage: ``python3 tc.py <command> --help``."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # find the towncrier package

from towncrier.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
