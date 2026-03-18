"""
seed_work_units.py — Clear work_units and re-seed from queries.txt.

Schema used (no tier/priority columns exist):
  id, mode, query, search_type, page, payload, status,
  worker_id, assigned_at, completed_at, result_count, total_count
"""

import os
import sqlite3

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(SCRIPT_DIR, "orchestrator.db")
QUERIES_FILE = os.path.join(SCRIPT_DIR, "queries.txt")


def parse_queries(path):
    """
    Return list of (query_str, tier_label) tuples.
    Tier is derived from the most-recently-seen '# TIER N' header.
    Lines that are blank or start with '#' are skipped.
    Surrounding double-quotes are stripped (queries.txt style).
    """
    results = []
    current_tier = "unknown"

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                # e.g.  "# TIER 1 — Direct Pain"
                upper = line.upper()
                for n in ("1", "2", "3", "4", "5"):
                    if f"TIER {n}" in upper:
                        current_tier = f"tier{n}"
                        break
                continue
            # Strip surrounding quotes
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            results.append((line, current_tier))

    return results


def main():
    queries = parse_queries(QUERIES_FILE)
    print(f"Parsed {len(queries)} queries from {QUERIES_FILE}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Delete all existing rows
    cur.execute("DELETE FROM work_units")
    deleted = cur.rowcount
    print(f"Deleted {deleted} existing work_units rows")

    # Insert new rows
    tier_counts = {}
    rows_inserted = 0
    for query_str, tier in queries:
        # search_type: 'code' if query contains 'language:', else 'commits'
        search_type = "code" if "language:" in query_str else "commits"

        cur.execute(
            """
            INSERT INTO work_units (mode, query, search_type, status)
            VALUES ('search', ?, ?, 'pending')
            """,
            (query_str, search_type),
        )
        rows_inserted += 1
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    conn.commit()
    conn.close()

    print(f"\nInserted {rows_inserted} work_units:")
    for tier in sorted(tier_counts):
        print(f"  {tier}: {tier_counts[tier]} rows")
    print("\nDone.")


if __name__ == "__main__":
    main()
