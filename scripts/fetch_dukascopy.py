"""Download Dukascopy XAUUSD ticks -> monthly 1m bid/ask parquet + manifest entry.

  python scripts/fetch_dukascopy.py --start 2015-01-01 --end 2026-07-01
Requires network access to datafeed.dukascopy.com (blocked in the current environment).
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tbot.data.dukascopy import download_range  # noqa: E402
from tbot.data.quality import sha256_file  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    a = ap.parse_args()
    outs = download_range(a.symbol, a.start, a.end, ROOT / "data/raw/dukascopy", ROOT / "data/processed")
    man_path = ROOT / "DATA_MANIFEST.json"
    man = json.loads(man_path.read_text())
    files = [{"path": str(p.relative_to(ROOT)), "sha256": sha256_file(p)} for p in outs]
    for s in man["sources"]:
        if s["id"] == "dukascopy_xauusd_1m":
            s.update({"status": "downloaded", "period": [a.start, a.end], "files": files,
                      "downloaded_utc": datetime.now(timezone.utc).isoformat()})
    man_path.write_text(json.dumps(man, indent=1))
    print(f"{len(outs)} monthly files written; manifest updated")


if __name__ == "__main__":
    main()
