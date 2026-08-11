#!/usr/bin/env python3
"""
analyze_insights.py — turn an Instagram insights export into an account read.

Instagram is unreachable from a sandboxed environment, so the data has to be
exported by the account owner. This reads whatever they export and does the
analysis, tolerating the fact that Meta renames these columns constantly and
that a hand-typed table will not match any official header at all.

    python3 scripts/analyze_insights.py insights.csv
    python3 scripts/analyze_insights.py insights.csv --json

Accepts CSV or TSV. Column names are matched loosely (case, spacing and
wording are ignored), and both English and Arabic headers are recognised.
Anything missing is simply skipped — a file with only views and saves still
produces the parts of the report that data supports.
"""

import csv
import json
import re
import sys
from statistics import median

# Loose aliases. Matching is done on a normalised key, so "Average watch time",
# "avg_watch_time" and "متوسط وقت المشاهدة" all land on the same field.
FIELDS = {
    "title":     ["description", "caption", "title", "post", "name", "الوصف", "العنوان"],
    "kind":      ["posttype", "type", "format", "mediatype", "النوع"],
    "date":      ["date", "publishtime", "published", "التاريخ"],
    "views":     ["views", "plays", "videoviews", "impressions", "المشاهدات"],
    "reach":     ["reach", "accountsreached", "الوصول"],
    "watch":     ["averagewatchtime", "avgwatchtime", "watchtime", "متوسطوقتالمشاهدة"],
    "duration":  ["duration", "length", "videoduration", "المدة"],
    "saves":     ["saves", "saved", "bookmarks", "الحفظ", "المحفوظات"],
    "shares":    ["shares", "sends", "المشاركات"],
    "comments":  ["comments", "التعليقات"],
    "likes":     ["likes", "الإعجابات", "الاعجابات"],
    "follows":   ["follows", "followsgained", "newfollowers", "المتابعات"],
}

norm = lambda s: re.sub(r"[^a-z؀-ۿ]", "", str(s).lower())


def to_num(v):
    """Numbers arrive as '1,234', '12.5%', '0:08', '8s' or blank."""
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("%", "")
    if not s or s in {"-", "—", "N/A"}:
        return None
    if ":" in s:                                   # 0:08 → 8 seconds
        try:
            parts = [float(p) for p in s.split(":")]
        except ValueError:
            return None
        out = 0.0
        for p in parts:
            out = out * 60 + p
        return out
    s = re.sub(r"[a-z؀-ۿ]+$", "", s)     # trailing "s", "ث"
    try:
        return float(s)
    except ValueError:
        return None


def load(path):
    raw = open(path, encoding="utf-8-sig").read()
    dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t") if raw.strip() else csv.excel
    rows = list(csv.DictReader(raw.splitlines(), dialect=dialect))
    if not rows:
        sys.exit("no rows found in that file")

    mapping = {}
    for field, aliases in FIELDS.items():
        for header in rows[0]:
            if header is None:
                continue
            h = norm(header)
            if any(h == a or (len(a) > 4 and a in h) for a in aliases):
                mapping.setdefault(field, header)
                break

    posts = []
    for r in rows:
        p = {}
        for field, header in mapping.items():
            val = r.get(header)
            p[field] = val if field in ("title", "kind", "date") else to_num(val)
        if p.get("views") or p.get("reach"):
            posts.append(p)
    return posts, mapping


def rate(a, b):
    return (a / b * 100) if (a and b) else None


def enrich(p):
    base = p.get("reach") or p.get("views")
    p["save_rate"] = rate(p.get("saves"), base)
    p["share_rate"] = rate(p.get("shares"), base)
    p["follow_rate"] = rate(p.get("follows"), base)
    p["comment_rate"] = rate(p.get("comments"), base)
    # Retention only means something when both numbers are present.
    if p.get("watch") and p.get("duration"):
        p["retention"] = p["watch"] / p["duration"] * 100
        p["skip_rate"] = 100 - p["retention"]
    return p


def top(posts, key, n=5):
    have = [p for p in posts if p.get(key) is not None]
    return sorted(have, key=lambda p: p[key], reverse=True)[:n]


def label(p):
    t = (p.get("title") or "").strip().replace("\n", " ")
    return (t[:52] + "…") if len(t) > 53 else (t or "(untitled)")


def report(posts):
    posts = [enrich(p) for p in posts]
    out = {"count": len(posts)}
    print(f"\n{len(posts)} posts\n" + "=" * 64)

    def med(key):
        vals = [p[key] for p in posts if p.get(key) is not None]
        return median(vals) if vals else None

    print("\nMEDIANS")
    for key, lab, unit in [
        ("views", "views", ""), ("reach", "reach", ""),
        ("retention", "retention", "%"), ("skip_rate", "skip rate", "%"),
        ("save_rate", "save rate", "%"), ("share_rate", "share rate", "%"),
        ("follow_rate", "follow rate", "%"), ("comment_rate", "comment rate", "%"),
    ]:
        m = med(key)
        out[f"median_{key}"] = m
        if m is not None:
            print(f"  {lab:<14} {m:,.1f}{unit}")

    # The ranking that matters depends on the goal, so rank by each separately:
    # reach, saving, and following are three different behaviours.
    for key, heading in [("views", "MOST VIEWED"), ("save_rate", "MOST SAVED (rate)"),
                         ("follow_rate", "BEST FOLLOW CONVERSION"),
                         ("retention", "BEST RETENTION")]:
        rows = top(posts, key)
        if not rows:
            continue
        print(f"\n{heading}")
        for i, p in enumerate(rows, 1):
            v = p[key]
            unit = "" if key == "views" else "%"
            extra = f"  ({p['views']:,.0f} views)" if key != "views" and p.get("views") else ""
            print(f"  {i}. {v:,.1f}{unit}{extra}  — {label(p)}")
        out[heading] = [{"value": p[key], "title": label(p)} for p in rows]

    # Does length actually matter for this account? Split at the benchmark
    # boundary rather than assuming the published 15–30s optimum transfers.
    dur = [p for p in posts if p.get("duration") and p.get("retention") is not None]
    if len(dur) >= 4:
        short = [p for p in dur if p["duration"] <= 30]
        long_ = [p for p in dur if p["duration"] > 30]
        if short and long_:
            s, l = median([p["retention"] for p in short]), median([p["retention"] for p in long_])
            print(f"\nDURATION")
            print(f"  ≤30s  n={len(short):<3} median retention {s:.1f}%")
            print(f"  >30s  n={len(long_):<3} median retention {l:.1f}%")
            print(f"  → {'shorter holds better' if s > l else 'longer holds better'} "
                  f"by {abs(s - l):.1f} points on this account")
            out["duration_split"] = {"short_n": len(short), "short_retention": s,
                                     "long_n": len(long_), "long_retention": l}

    # Format comparison, when the export distinguishes reels from carousels.
    kinds = {}
    for p in posts:
        k = (p.get("kind") or "").strip().lower()
        if k:
            kinds.setdefault(k, []).append(p)
    if len(kinds) > 1:
        print(f"\nBY FORMAT")
        for k, group in sorted(kinds.items()):
            sv = [p["save_rate"] for p in group if p.get("save_rate") is not None]
            vw = [p["views"] for p in group if p.get("views")]
            print(f"  {k:<12} n={len(group):<3}"
                  + (f" median views {median(vw):,.0f}" if vw else "")
                  + (f"  median save rate {median(sv):.2f}%" if sv else ""))
        out["formats"] = {k: len(v) for k, v in kinds.items()}

    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    posts, mapping = load(args[0])
    missing = [f for f in FIELDS if f not in mapping]
    print(f"matched columns: {', '.join(sorted(mapping))}")
    if missing:
        print(f"not found (skipped): {', '.join(sorted(missing))}")
    out = report(posts)
    if "--json" in sys.argv:
        print("\n" + json.dumps(out, ensure_ascii=False, indent=2, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
