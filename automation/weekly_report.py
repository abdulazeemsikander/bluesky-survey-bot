# automation/weekly_report.py
"""
Generate a simple weekly posting report from logs/post_log.csv.

Usage (from repo root, with venv activated):
    python -m automation.weekly_report
"""

import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT.parent / "logs"
POST_LOG = LOG_DIR / "post_log.csv"


def load_rows():
    if not POST_LOG.exists():
        print("No post_log.csv found yet – nothing to report.")
        return []

    rows = []
    with open(POST_LOG, "r", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            try:
                ts = datetime.fromisoformat(row["utc_time"])
            except Exception:
                # skip malformed lines
                continue
            rows.append(
                {
                    "ts": ts,
                    "dry_run": row.get("dry_run", "true") == "true",
                    "variant": row.get("variant", ""),
                    "length": int(row.get("length", "0") or 0),
                }
            )
    return rows


def main():
    rows = load_rows()
    if not rows:
        return

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    recent = [r for r in rows if r["ts"] >= week_ago]

    if not recent:
        print("No posts in the last 7 days.")
        return

    total = len(recent)
    live = sum(1 for r in recent if not r["dry_run"])
    dry = total - live

    by_day = Counter(r["ts"].date().isoformat() for r in recent)
    by_variant = Counter(r["variant"] for r in recent)
    lengths = [r["length"] for r in recent if r["length"] > 0]
    avg_len = sum(lengths) / len(lengths) if lengths else 0

    print("\n=== Weekly Bluesky posting report ===\n")
    print(f"Time window: {week_ago.date()}  →  {now.date()}")
    print(f"Total posts logged: {total}  (live: {live}, dry-run: {dry})")
    print(f"Average post length: {avg_len:.1f} characters\n")

    print("Posts per day (last 7 days):")
    for day, count in sorted(by_day.items()):
        print(f"  {day}: {count}")

    print("\nTop variants used:")
    for variant, count in by_variant.most_common(5):
        label = variant or "(no label)"
        print(f"  {label}: {count}")

    # also write a text file summary
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = LOG_DIR / f"weekly_summary_{now.date().isoformat()}.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Weekly Bluesky posting report\n")
        f.write(f"Time window: {week_ago.date()}  →  {now.date()}\n")
        f.write(f"Total posts: {total} (live: {live}, dry-run: {dry})\n")
        f.write(f"Average length: {avg_len:.1f} characters\n\n")

        f.write("Posts per day:\n")
        for day, count in sorted(by_day.items()):
            f.write(f"  {day}: {count}\n")

        f.write("\nTop variants:\n")
        for variant, count in by_variant.most_common(5):
            label = variant or "(no label)"
            f.write(f"  {label}: {count}\n")

    print(f"\nSaved summary to: {summary_path}")


if __name__ == "__main__":
    main()