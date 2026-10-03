"""Experiment registry (EXPERIMENTS.csv) and hold-out lock.

Every run — including failed/crashed ones — is appended. Each row links to the code
version (git commit + dirty flag), data fingerprint, config hash and RNG seed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "EXPERIMENTS.csv"
FIELDS = ["exp_id", "utc_time", "git_commit", "git_dirty", "phase", "hypothesis", "params", "split",
          "period", "data_sha256", "config_hash", "seed", "status", "n_trades", "net_profit", "cum_return",
          "max_dd", "sharpe_daily_ann", "profit_factor", "expectancy_R", "pct_profitable_days_active",
          "pct_profitable_days_all", "notes"]


def git_info() -> tuple[str, bool]:
    try:
        c = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "tbot", "configs", "scripts"],
                                             cwd=ROOT, text=True).strip())
        return c, dirty
    except Exception:
        return "unknown", True


def config_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def next_id() -> str:
    if not REGISTRY.exists():
        return "E0001"
    with open(REGISTRY) as f:
        n = sum(1 for _ in f) - 1
    return f"E{n + 1:04d}"


def append(row: dict, path: Path = REGISTRY) -> str:
    new = not path.exists()
    row = dict(row)
    row.setdefault("exp_id", next_id())
    row.setdefault("utc_time", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    if "git_commit" not in row:
        row["git_commit"], row["git_dirty"] = git_info()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow({k: (json.dumps(v, default=str) if isinstance(v, (dict, list)) else v) for k, v in row.items()})
    return row["exp_id"]


# ---------------------------------------------------------------- hold-out lock
FREEZE = ROOT / "FREEZE.json"
OPENED = ROOT / "HOLDOUT_OPENED.json"


def assert_can_open_holdout() -> dict:
    """The final hold-out may be evaluated only from a clean tree whose commit equals
    the frozen commit in FREEZE.json, and only once. Re-use => results are development data."""
    if not FREEZE.exists():
        raise PermissionError("No FREEZE.json: freeze code, params and acceptance criteria first.")
    frz = json.loads(FREEZE.read_text())
    commit, dirty = git_info()
    if dirty or commit != frz["commit"]:
        raise PermissionError(f"Tree is dirty or HEAD {commit[:8]} != frozen {frz['commit'][:8]}")
    if OPENED.exists():
        raise PermissionError("Hold-out already opened once. Any further use is DEVELOPMENT data (see DECISIONS.md).")
    OPENED.write_text(json.dumps({"opened_utc": datetime.now(timezone.utc).isoformat(), "commit": commit}, indent=1))
    return frz
