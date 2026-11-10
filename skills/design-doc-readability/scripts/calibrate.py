#!/usr/bin/env python3
"""Print the scanner's index and score for each axis over a set of docs.

Usage:
    calibrate.py <file>...

Use it to set the thresholds in patterns.json: run it over a corpus of
RFCs and a corpus of docs you consider LLM-heavy, and put each axis's "good"
threshold near the top of the RFC range. See references/calibration.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan  # noqa: E402

PATTERNS = Path(__file__).resolve().parent / "patterns.json"


def main():
    files = sys.argv[1:]
    if not files:
        sys.exit(__doc__.strip())
    head = " ".join(f"{a[:5]:>6}" for a in scan.AXES)
    print(f"{'file':<36}{'words':>7}  index: {head}  | score: {head}  subtotal")
    for f in files:
        r = scan.scan(f, PATTERNS, 0)
        idx = " ".join(f"{r['index'][a]:>6}" for a in scan.AXES)
        sc = " ".join(f"{r['mechanical_scores'][a]!s:>6}" for a in scan.AXES)
        print(f"{Path(f).name[:35]:<36}{r['metrics']['words_total']:>7}         {idx}  |        {sc}  {r['mechanical_subtotal']:>8}")


if __name__ == "__main__":
    main()
