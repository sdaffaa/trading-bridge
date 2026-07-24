"""Durable persistence — SQLite (stdlib, no external dependency).

One store for everything that must survive restarts: idempotency keys, the
decision log, recorded outcomes (the feedback loop), and run metrics
(observability). Single-writer + threads is fine with a lock and WAL; for
multi-host you would point this at Redis/Postgres, but the interface stays.
"""
import os
import time
import sqlite3
import threading

from . import config
from .logging_setup import jlog

_lock = threading.Lock()
_conn = None


def _connect():
    global _conn
    if _conn is None:
        os.makedirs(config.STATE_DIR, exist_ok=True)
        _conn = sqlite3.connect(os.path.join(config.STATE_DIR, "bridge.db"),
                                check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.executescript("""
            CREATE TABLE IF NOT EXISTS processed (
                key TEXT PRIMARY KEY, ts REAL);
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY, run TEXT, symbol TEXT, action TEXT,
                confidence REAL, reason TEXT, ts REAL, dry_run INTEGER,
                outcome TEXT, outcome_ts REAL, pnl REAL);
            CREATE TABLE IF NOT EXISTS metrics (
                ts REAL, kind TEXT, ok INTEGER, detail TEXT);
        """)
        _conn.commit()
    return _conn


def reset_for_tests():
    """Drop the in-process connection so a new STATE_DIR takes effect."""
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
        _conn = None


# --- idempotency ----------------------------------------------------------
def seen(key: str) -> bool:
    with _lock:
        c = _connect()
        return c.execute("SELECT 1 FROM processed WHERE key=?", (key,)).fetchone() is not None


def mark(key: str) -> None:
    with _lock:
        c = _connect()
        c.execute("INSERT OR IGNORE INTO processed(key, ts) VALUES(?, ?)", (key, time.time()))
        c.commit()


# --- decision log + outcomes (feedback loop) ------------------------------
def record_decision(event_id, run, symbol, decision, dry_run):
    if not decision:
        return
    with _lock:
        c = _connect()
        c.execute(
            "INSERT OR REPLACE INTO decisions"
            "(id, run, symbol, action, confidence, reason, ts, dry_run,"
            " outcome, outcome_ts, pnl) VALUES(?,?,?,?,?,?,?,?,"
            " COALESCE((SELECT outcome FROM decisions WHERE id=?), NULL),"
            " (SELECT outcome_ts FROM decisions WHERE id=?),"
            " (SELECT pnl FROM decisions WHERE id=?))",
            (event_id, run, symbol, decision.get("action"),
             decision.get("confidence"), decision.get("reason"), time.time(),
             1 if dry_run else 0, event_id, event_id, event_id))
        c.commit()


def record_outcome(event_id, outcome, pnl=None) -> bool:
    with _lock:
        c = _connect()
        cur = c.execute("UPDATE decisions SET outcome=?, outcome_ts=?, pnl=? WHERE id=?",
                        (outcome, time.time(), pnl, event_id))
        c.commit()
        return cur.rowcount > 0


def stats() -> dict:
    with _lock:
        c = _connect()
        total = c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        by_action = {r["action"]: r["n"] for r in c.execute(
            "SELECT action, COUNT(*) n FROM decisions GROUP BY action")}
        graded = c.execute(
            "SELECT COUNT(*) FROM decisions WHERE outcome IS NOT NULL").fetchone()[0]
        wins = c.execute(
            "SELECT COUNT(*) FROM decisions WHERE outcome='win'").fetchone()[0]
        pnl = c.execute(
            "SELECT COALESCE(SUM(pnl),0) FROM decisions WHERE pnl IS NOT NULL").fetchone()[0]
    accuracy = (wins / graded) if graded else None
    return {"total_decisions": total, "by_action": by_action, "graded": graded,
            "wins": wins, "accuracy": accuracy, "total_pnl": pnl}


def recent_decisions(limit=20) -> list:
    with _lock:
        c = _connect()
        rows = c.execute(
            "SELECT id, symbol, action, confidence, reason, ts, dry_run, outcome, pnl"
            " FROM decisions ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


# --- metrics (observability) ----------------------------------------------
def record_metric(kind: str, ok: bool, detail: str = "") -> None:
    with _lock:
        c = _connect()
        c.execute("INSERT INTO metrics(ts, kind, ok, detail) VALUES(?,?,?,?)",
                  (time.time(), kind, 1 if ok else 0, detail))
        c.commit()


def last_success_ts(kind: str = "run"):
    with _lock:
        c = _connect()
        row = c.execute("SELECT MAX(ts) FROM metrics WHERE kind=? AND ok=1",
                        (kind,)).fetchone()
    return row[0] if row and row[0] else None


def open_positions_count() -> int:
    """Decisions that acted (executed a directional trade) and aren't closed."""
    with _lock:
        c = _connect()
        n = c.execute(
            "SELECT COUNT(*) FROM decisions WHERE dry_run=0 AND action IN('long','short')"
            " AND outcome IS NULL").fetchone()[0]
    return n
