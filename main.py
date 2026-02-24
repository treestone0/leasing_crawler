#!/usr/bin/env python3
"""Entry point: python main.py input.json"""

import sys
from pathlib import Path

# Ensure project root is on path for src imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli import main

if __name__ == "__main__":
    sys.exit(main())
