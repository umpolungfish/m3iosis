import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOX = ROOT.parents[2] / "Vox"
os.environ.setdefault("VOX_BAKED_TARGET_DIR", str(ROOT / "target"))
sys.path.insert(0, str(VOX))

from baked_case import main


if __name__ == "__main__":
    raise SystemExit(main())
