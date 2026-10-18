"""Run the current CLI directly from a complete unpacked bundle."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hs_dev.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
