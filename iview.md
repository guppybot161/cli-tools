# iview — Python reference implementation

The active version is a bash script. Below is a Python equivalent for reference.

```python
#!/usr/bin/env python3
"""iview — open images in IrfanView from WSL2."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

IRFANVIEW = "/mnt/c/Program Files/IrfanView/i_view64.exe"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open images in IrfanView from WSL2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  iview photo.jpg
  iview *.png
  iview ~/screenshots/grab.bmp
""",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="image file(s) to open",
    )
    return parser.parse_args()


def to_winpath(p: Path) -> str:
    """Convert a WSL path to a Windows path via wslpath."""
    result = subprocess.run(
        ["wslpath", "-w", str(p.resolve())],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"error: cannot convert path: {p}")
    return result.stdout.strip()


def main() -> int:
    args = parse_args()

    if not Path(IRFANVIEW).exists():
        sys.exit(f"error: IrfanView not found at {IRFANVIEW}")

    for f in args.files:
        if not f.exists():
            print(f"warning: {f} not found, skipping", file=sys.stderr)
            continue
        subprocess.Popen(
            [IRFANVIEW, to_winpath(f)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
