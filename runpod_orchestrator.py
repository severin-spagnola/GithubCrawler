"""
Local orchestrator for distributed GitHub crawling via RunPod workers.

Supports three modes:
    search  — distribute search queries across workers (original)
    enrich  — distribute lead enrichment across workers
    extract — distribute training data extraction across workers

Runs on your machine, exposes an HTTP API via ngrok tunnel.
Workers on RunPod pull work units, execute them, and POST results back.

Usage:
    # Search mode (original)
    python runpod_orchestrator.py search

    # Enrich FPGA leads (resumes automatically)
    python runpod_orchestrator.py enrich --input-csv fpga_leads.csv --enriched-csv fpga_enriched.csv

    # Extract training data from enriched leads
    python runpod_orchestrator.py extract --enriched-csv fpga_enriched.csv --output-dir training_data/

Requires .env with:
    NGROK_AUTH_TOKEN=...
    QUERIES_FILE=./queries.txt    (for search mode)
    OUTPUT_FILE=./final_leads.csv (for search mode)
"""

import os
import sys
import json
import time
import csv
import sqlite3
import signal
import argparse
import threading
from datetime import datetime
from contextlib import contextmanager

from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

QUERIES_FILE = os.environ.get("QUERIES_FILE", "./queries.txt").strip()
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "./final_leads.csv").strip()
DB_FILE = os.environ.get("ORCHESTRATOR_DB", "./orchestrator.db").strip()
SEED_LEADS_FILE = os.environ.get("SEED_LEADS_FILE", "./seed_leads.csv").strip()

SEARCH_PER_PAGE = 100
MAX_PAGES = 10  # 1000 results / 100 per page
STALE_TIMEOUT = 300  # seconds before in_progress units are reclaimed
REAPER_INTERVAL = 60  # seconds between reaper runs

# Track current mode globally so export knows what to do
_current_mode = "search"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

_db_lock = threading.Lock()


@contextmanager
def get_db():
    """Thread-safe SQLite connection with WAL mode."""
    with _db_lock:
        conn = sqlite3.connect(DB_FILE, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS work_units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL DEFAULT 'search',
                query TEXT,
                search_type TEXT,
                page INTEGER,
                payload TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                worker_id TEXT,
                assigned_at REAL,
                completed_at REAL,
                result_count INTEGER DEFAULT 0,
                total_count INTEGER
            );

            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_unit_id INTEGER NOT NULL DEFAULT 0,
                username TEXT NOT NULL,
                repo TEXT NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_unit_id INTEGER NOT NULL,
                commit_url TEXT NOT NULL,
                data TEXT NOT NULL,
                UNIQUE(commit_url)
            );

            CREATE TABLE IF NOT EXISTS workers (
                worker_id TEXT PRIMARY KEY,
                last_seen REAL,
                units_completed INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_work_status ON work_units(status);
            CREATE INDEX IF NOT EXISTS idx_work_mode ON work_units(mode);
            CREATE INDEX IF NOT EXISTS idx_leads_key ON leads(username, repo);
        """)


# ---------------------------------------------------------------------------
# Search mode seeding
# ---------------------------------------------------------------------------

def load_queries():
    """Read queries from file."""
    try:
        with open(QUERIES_FILE, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"ERROR: cannot read {QUERIES_FILE}: {exc}", file=sys.stderr)
        sys.exit(1)

    queries = [
        line.strip().strip('"')
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]
    if not queries:
        print(f"ERROR: no queries found in {QUERIES_FILE}", file=sys.stderr)
        sys.exit(1)
    return queries


def seed_search_units(queries):
    """Insert work units for all (query, search_type, page) combos."""
    with get_db() as conn:
        count = 0
        for query in queries:
            for search_type in ("commits", "issues"):
                for page in range(1, MAX_PAGES + 1):
                    try:
                        conn.execute(
                            "INSERT INTO work_units (mode, query, search_type, page, status) "
                            "VALUES ('search', ?, ?, ?, 'pending')",
                            (query, search_type, page),
                        )
                        count += 1
                    except sqlite3.IntegrityError:
                        pass
        return count


def load_seed_leads():
    """Load previously collected leads into the DB to prevent duplication."""
    if not os.path.exists(SEED_LEADS_FILE):
        return 0

    with get_db() as conn:
        existing = conn.execute(
            "SELECT COUNT(*) as c FROM leads WHERE work_unit_id = 0"
        ).fetchone()["c"]
        if existing > 0:
            return existing

        count = 0
        try:
            with open(SEED_LEADS_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    username = row.get("username", "").strip()
                    repo = row.get("repo", "").strip()
                    if not username or not repo:
                        continue
                    conn.execute(
                        "INSERT OR IGNORE INTO leads (work_unit_id, username, repo, data) "
                        "VALUES (0, ?, ?, ?)",
                        (username, repo, json.dumps(row)),
                    )
                    count += 1
        except Exception as exc:
            print(f"  [warn] could not load seed leads: {exc}")
            return 0

    return count


# ---------------------------------------------------------------------------
# Enrich mode seeding
# ---------------------------------------------------------------------------

def seed_enrich_units(input_csv, enriched_csv, chunk_size=50):
    """Read input CSV, subtract already-enriched leads, chunk the rest into work units."""
    # Read all leads
    with open(input_csv, newline="", encoding="utf-8") as f:
        all_leads = list(csv.DictReader(f))
    print(f"  Input leads : {len(all_leads)} from {input_csv}")

    # Deduplicate
    seen = {}
    for lead in all_leads:
        key = (lead.get("username", ""), lead.get("repo", ""))
        if key not in seen:
            seen[key] = lead
    unique_leads = list(seen.values())
    print(f"  Unique leads: {len(unique_leads)}")

    # Subtract already-enriched
    already_done = set()
    if enriched_csv and os.path.isfile(enriched_csv):
        with open(enriched_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                already_done.add((row.get("username", ""), row.get("repo", "")))
        print(f"  Already done: {len(already_done)} in {enriched_csv}")

    remaining = [
        lead for lead in unique_leads
        if (lead.get("username", ""), lead.get("repo", "")) not in already_done
    ]
    print(f"  Remaining   : {len(remaining)} to enrich")

    if not remaining:
        print("  Nothing to enrich!")
        return 0

    # Check what's already in the DB (resume support)
    with get_db() as conn:
        existing = conn.execute(
            "SELECT COUNT(*) as c FROM work_units WHERE mode = 'enrich'"
        ).fetchone()["c"]
        if existing > 0:
            print(f"  [resume] {existing} enrich units already in DB, skipping seeding")
            return 0

    # Chunk into work units
    chunks = [remaining[i:i + chunk_size] for i in range(0, len(remaining), chunk_size)]

    with get_db() as conn:
        for chunk in chunks:
            conn.execute(
                "INSERT INTO work_units (mode, payload, status) "
                "VALUES ('enrich', ?, 'pending')",
                (json.dumps(chunk),),
            )

    print(f"  Created     : {len(chunks)} enrich work units (chunk_size={chunk_size})")
    return len(chunks)


# ---------------------------------------------------------------------------
# Extract mode seeding
# ---------------------------------------------------------------------------

def seed_extract_units(enriched_csv, output_dir, chunk_size=25):
    """Read enriched CSV, apply quality gate, chunk remaining leads for extraction."""
    from extract_training_data import _passes_quality_gate

    with open(enriched_csv, newline="", encoding="utf-8") as f:
        all_leads = list(csv.DictReader(f))
    print(f"  Input leads : {len(all_leads)} from {enriched_csv}")

    # Quality gate
    qualified = [l for l in all_leads if _passes_quality_gate(l)]
    print(f"  Quality gate: {len(qualified)} passed")

    # Deduplicate by commit_url
    seen_urls = {}
    unique_leads = []
    for lead in qualified:
        url = lead.get("commit_url", "").strip()
        if url and url not in seen_urls:
            seen_urls[url] = True
            unique_leads.append(lead)
    print(f"  Unique URLs : {len(unique_leads)}")

    # Check existing extractions (resume)
    examples_dir = os.path.join(output_dir, "examples") if output_dir else None
    processed = set()
    if examples_dir and os.path.isdir(examples_dir):
        processed = {f.replace(".json", "") for f in os.listdir(examples_dir) if f.endswith(".json")}
        print(f"  Already done: {len(processed)} extractions on disk")

    # Filter out already-processed
    from extract_training_data import parse_commit_url
    remaining = []
    for lead in unique_leads:
        parsed = parse_commit_url(lead.get("commit_url", ""))
        if parsed:
            safe = f"{parsed['owner']}__{parsed['repo']}__{parsed['type']}_{parsed['id']}".replace("/", "__")
            if safe not in processed:
                remaining.append(lead)
        else:
            remaining.append(lead)
    print(f"  Remaining   : {len(remaining)} to extract")

    if not remaining:
        print("  Nothing to extract!")
        return 0

    # Check DB resume
    with get_db() as conn:
        existing = conn.execute(
            "SELECT COUNT(*) as c FROM work_units WHERE mode = 'extract'"
        ).fetchone()["c"]
        if existing > 0:
            print(f"  [resume] {existing} extract units already in DB, skipping seeding")
            return 0

    # Chunk
    chunks = [remaining[i:i + chunk_size] for i in range(0, len(remaining), chunk_size)]

    with get_db() as conn:
        for chunk in chunks:
            conn.execute(
                "INSERT INTO work_units (mode, payload, status) "
                "VALUES ('extract', ?, 'pending')",
                (json.dumps(chunk),),
            )

    print(f"  Created     : {len(chunks)} extract work units (chunk_size={chunk_size})")
    return len(chunks)


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)
_shutdown_event = threading.Event()


@app.route("/health", methods=["GET"])
def health():
    with get_db() as conn:
        stats = {}
        for status in ("pending", "in_progress", "done", "failed", "skipped"):
            row = conn.execute(
                "SELECT COUNT(*) as c FROM work_units WHERE status = ?", (status,)
            ).fetchone()
            stats[status] = row["c"]

        total_leads = conn.execute("SELECT COUNT(*) as c FROM leads").fetchone()["c"]
        total_training = conn.execute("SELECT COUNT(*) as c FROM training_data").fetchone()["c"]
        worker_count = conn.execute(
            "SELECT COUNT(*) as c FROM workers WHERE last_seen > ?",
            (time.time() - 120,),
        ).fetchone()["c"]

    stats["total"] = sum(stats.values())
    stats["total_leads"] = total_leads
    stats["total_training_examples"] = total_training
    stats["active_workers"] = worker_count
    return jsonify(stats)


@app.route("/work/request", methods=["POST"])
def request_work_endpoint():
    body = request.get_json(force=True)
    worker_id = body.get("worker_id", "unknown")
    batch_size = min(body.get("batch_size", 3), 10)

    now = time.time()

    with get_db() as conn:
        # Upsert worker
        conn.execute(
            "INSERT INTO workers (worker_id, last_seen, units_completed) "
            "VALUES (?, ?, 0) "
            "ON CONFLICT(worker_id) DO UPDATE SET last_seen = ?",
            (worker_id, now, now),
        )

        # Grab pending units
        rows = conn.execute(
            "SELECT id, mode, query, search_type, page, payload FROM work_units "
            "WHERE status = 'pending' ORDER BY id LIMIT ?",
            (batch_size,),
        ).fetchall()

        if not rows:
            return jsonify({"units": []})

        units = []
        for row in rows:
            conn.execute(
                "UPDATE work_units SET status = 'in_progress', "
                "worker_id = ?, assigned_at = ? WHERE id = ?",
                (worker_id, now, row["id"]),
            )
            unit = {
                "id": row["id"],
                "mode": row["mode"],
            }
            if row["mode"] == "search":
                unit["query"] = row["query"]
                unit["search_type"] = row["search_type"]
                unit["page"] = row["page"]
            else:
                unit["payload"] = json.loads(row["payload"]) if row["payload"] else []
            units.append(unit)

    return jsonify({"units": units})


@app.route("/work/complete", methods=["POST"])
def complete_work():
    body = request.get_json(force=True)
    worker_id = body.get("worker_id", "unknown")
    unit_id = body["unit_id"]
    results = body.get("leads", [])
    total_count = body.get("total_count", 0)
    mode = body.get("mode", "search")

    now = time.time()

    with get_db() as conn:
        # Mark unit done
        conn.execute(
            "UPDATE work_units SET status = 'done', completed_at = ?, "
            "result_count = ?, total_count = ? WHERE id = ?",
            (now, len(results), total_count, unit_id),
        )

        if mode in ("search", "enrich"):
            # Store leads
            for lead in results:
                conn.execute(
                    "INSERT INTO leads (work_unit_id, username, repo, data) "
                    "VALUES (?, ?, ?, ?)",
                    (unit_id, lead.get("username", ""), lead.get("repo", ""),
                     json.dumps(lead)),
                )
        elif mode == "extract":
            # Store training examples
            for result in results:
                commit_url = result.get("commit_url", "")
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO training_data "
                        "(work_unit_id, commit_url, data) VALUES (?, ?, ?)",
                        (unit_id, commit_url, json.dumps(result)),
                    )
                except sqlite3.IntegrityError:
                    pass

        # Update worker stats
        conn.execute(
            "UPDATE workers SET last_seen = ?, "
            "units_completed = units_completed + 1 WHERE worker_id = ?",
            (now, worker_id),
        )

        # Optimization for search mode: skip excess pages
        if mode == "search" and total_count > 0:
            unit_row = conn.execute(
                "SELECT query, search_type FROM work_units WHERE id = ?", (unit_id,)
            ).fetchone()
            if unit_row:
                max_needed = min(
                    (total_count + SEARCH_PER_PAGE - 1) // SEARCH_PER_PAGE,
                    MAX_PAGES,
                )
                conn.execute(
                    "UPDATE work_units SET status = 'skipped', completed_at = ? "
                    "WHERE query = ? AND search_type = ? AND page > ? "
                    "AND status = 'pending'",
                    (now, unit_row["query"], unit_row["search_type"], max_needed),
                )

    return jsonify({"ok": True})


@app.route("/work/fail", methods=["POST"])
def fail_work():
    body = request.get_json(force=True)
    unit_id = body["unit_id"]
    error = body.get("error", "unknown")

    with get_db() as conn:
        row = conn.execute(
            "SELECT status FROM work_units WHERE id = ?", (unit_id,)
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE work_units SET status = 'pending', worker_id = NULL, "
                "assigned_at = NULL WHERE id = ?",
                (unit_id,),
            )
            print(f"  [fail] unit {unit_id} returned to pending: {error}")

    return jsonify({"ok": True})


@app.route("/results/export", methods=["GET"])
def export_results():
    """Trigger export and return stats."""
    if _current_mode == "search":
        stats = _export_search_csv()
    elif _current_mode == "enrich":
        stats = _export_enriched_csv()
    elif _current_mode == "extract":
        stats = _export_training_data()
    else:
        stats = {"error": f"Unknown mode: {_current_mode}"}
    return jsonify(stats)


@app.route("/stop", methods=["POST"])
def stop():
    _shutdown_event.set()
    return jsonify({"ok": True, "message": "shutting down"})


# ---------------------------------------------------------------------------
# Reaper — reclaim stale in_progress units
# ---------------------------------------------------------------------------

def reaper_loop():
    while not _shutdown_event.is_set():
        try:
            with get_db() as conn:
                cutoff = time.time() - STALE_TIMEOUT
                result = conn.execute(
                    "UPDATE work_units SET status = 'pending', worker_id = NULL, "
                    "assigned_at = NULL WHERE status = 'in_progress' AND assigned_at < ?",
                    (cutoff,),
                )
                if result.rowcount > 0:
                    print(f"  [reaper] reclaimed {result.rowcount} stale units")
        except Exception as exc:
            print(f"  [reaper] error: {exc}")

        _shutdown_event.wait(REAPER_INTERVAL)


# ---------------------------------------------------------------------------
# Progress display
# ---------------------------------------------------------------------------

def progress_loop():
    while not _shutdown_event.is_set():
        try:
            with get_db() as conn:
                row = conn.execute(
                    "SELECT "
                    "  SUM(CASE WHEN status IN ('done','skipped') THEN 1 ELSE 0 END) as completed, "
                    "  SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as active, "
                    "  COUNT(*) as total "
                    "FROM work_units"
                ).fetchone()

                leads_row = conn.execute("SELECT COUNT(*) as c FROM leads").fetchone()
                training_row = conn.execute("SELECT COUNT(*) as c FROM training_data").fetchone()
                workers_row = conn.execute(
                    "SELECT COUNT(*) as c FROM workers WHERE last_seen > ?",
                    (time.time() - 120,),
                ).fetchone()

            completed = row["completed"] or 0
            total = row["total"] or 1
            active = row["active"] or 0
            pct = (completed / total) * 100

            ts = datetime.now().strftime("%H:%M:%S")

            if _current_mode == "extract":
                extra = f"|  {training_row['c']} training examples"
            else:
                extra = f"|  {leads_row['c']} leads collected"

            print(
                f"[{ts}] Progress: {completed}/{total} units ({pct:.1f}%)  "
                f"|  {workers_row['c']} workers  |  {active} in-flight  "
                f"{extra}",
                flush=True,
            )

            if completed >= total:
                print(f"\n[{ts}] All work units completed! Exporting results...")
                if _current_mode == "search":
                    _export_search_csv()
                elif _current_mode == "enrich":
                    _export_enriched_csv()
                elif _current_mode == "extract":
                    _export_training_data()
                _shutdown_event.set()
                return

        except Exception as exc:
            print(f"  [progress] error: {exc}")

        _shutdown_event.wait(15)


# ---------------------------------------------------------------------------
# Export functions
# ---------------------------------------------------------------------------

def _export_search_csv():
    """Deduplicate, score, and write the final search CSV."""
    try:
        from merge_results import score_lead, priority_label, OUTPUT_FIELDS
    except ImportError:
        print("  [warn] merge_results not available, writing raw leads")
        return _export_raw_leads_csv()

    with get_db() as conn:
        rows = conn.execute("SELECT data FROM leads").fetchall()

    seen = {}
    for row in rows:
        lead = json.loads(row["data"])
        key = (lead.get("username", ""), lead.get("repo", ""))
        if key not in seen:
            seen[key] = lead

    unique_leads = list(seen.values())

    for lead in unique_leads:
        s = score_lead(lead)
        lead["priority_score"] = s
        lead["priority"] = priority_label(s)

    unique_leads.sort(key=lambda r: int(r["priority_score"]), reverse=True)

    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for lead in unique_leads:
            writer.writerow({field: lead.get(field, "") for field in OUTPUT_FIELDS})

    p1 = sum(1 for l in unique_leads if l.get("priority") == "P1")
    p2 = sum(1 for l in unique_leads if l.get("priority") == "P2")
    p3 = sum(1 for l in unique_leads if l.get("priority") == "P3")

    stats = {"total": len(unique_leads), "p1": p1, "p2": p2, "p3": p3, "output_file": OUTPUT_FILE}
    print(f"\n=== Search Export Complete ===")
    print(f"  Total: {len(unique_leads)}  |  P1: {p1}  |  P2: {p2}  |  P3: {p3}")
    print(f"  Written to: {OUTPUT_FILE}")
    return stats


def _export_raw_leads_csv():
    """Fallback: export leads without scoring."""
    from crawler import CSV_FIELDS

    with get_db() as conn:
        rows = conn.execute("SELECT data FROM leads").fetchall()

    seen = {}
    for row in rows:
        lead = json.loads(row["data"])
        key = (lead.get("username", ""), lead.get("repo", ""))
        if key not in seen:
            seen[key] = lead

    unique_leads = list(seen.values())

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for lead in unique_leads:
            writer.writerow({field: lead.get(field, "") for field in CSV_FIELDS})

    stats = {"total": len(unique_leads), "output_file": OUTPUT_FILE}
    print(f"\n=== Raw Export Complete ===")
    print(f"  Total: {len(unique_leads)}  |  Written to: {OUTPUT_FILE}")
    return stats


def _export_enriched_csv():
    """Export enriched leads from the DB, merged with any pre-existing enriched CSV."""
    from crawler import CSV_FIELDS

    enriched_output = os.environ.get("ENRICHED_OUTPUT", "./fpga_enriched_complete.csv")

    with get_db() as conn:
        rows = conn.execute(
            "SELECT data FROM leads WHERE work_unit_id > 0"
        ).fetchall()

    # Deduplicate
    seen = {}
    for row in rows:
        lead = json.loads(row["data"])
        key = (lead.get("username", ""), lead.get("repo", ""))
        if key not in seen:
            seen[key] = lead

    unique_leads = list(seen.values())

    os.makedirs(os.path.dirname(enriched_output) if os.path.dirname(enriched_output) else ".", exist_ok=True)

    with open(enriched_output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for lead in unique_leads:
            writer.writerow({field: lead.get(field, "") for field in CSV_FIELDS})

    stats = {"total": len(unique_leads), "output_file": enriched_output}
    print(f"\n=== Enriched Export Complete ===")
    print(f"  Total: {len(unique_leads)}  |  Written to: {enriched_output}")
    return stats


def _export_training_data():
    """Export training data from the DB to JSON files."""
    output_dir = os.environ.get("TRAINING_OUTPUT_DIR", "./training_data")
    examples_dir = os.path.join(output_dir, "examples")
    os.makedirs(examples_dir, exist_ok=True)

    with get_db() as conn:
        rows = conn.execute("SELECT commit_url, data FROM training_data").fetchall()

    category_counts = {}
    language_counts = {}
    total_examples = 0

    for row in rows:
        result = json.loads(row["data"])
        commit_url = row["commit_url"]

        # Write JSON file
        from extract_training_data import parse_commit_url
        parsed = parse_commit_url(commit_url)
        if parsed:
            safe = f"{parsed['owner']}__{parsed['repo']}__{parsed['type']}_{parsed['id']}".replace("/", "__")
        else:
            safe = commit_url.replace("/", "__").replace(":", "_")

        out_path = os.path.join(examples_dir, f"{safe}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        cat = result.get("bug_category", "other")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        total_examples += result.get("file_count", 0)

        for ex in result.get("examples", []):
            lang = ex.get("language", "other")
            language_counts[lang] = language_counts.get(lang, 0) + 1

    # Write summary
    summary = {
        "total_repos": len(rows),
        "total_examples": total_examples,
        "category_counts": category_counts,
        "language_counts": language_counts,
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    stats = {
        "repos": len(rows),
        "examples": total_examples,
        "categories": category_counts,
        "output_dir": output_dir,
    }
    print(f"\n=== Training Data Export Complete ===")
    print(f"  Repos: {len(rows)}  |  Examples: {total_examples}")
    print(f"  Categories: {json.dumps(category_counts, indent=2)}")
    print(f"  Written to: {output_dir}/")
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global _current_mode

    parser = argparse.ArgumentParser(description="GitHub Crawler Orchestrator")
    sub = parser.add_subparsers(dest="mode", help="Operating mode")

    # Search mode
    s = sub.add_parser("search", help="Distribute search queries across workers")
    s.add_argument("--max-hours", type=float, default=8)
    s.add_argument("--port", type=int, default=8742)
    s.add_argument("--no-tunnel", action="store_true")

    # Enrich mode
    e = sub.add_parser("enrich", help="Distribute lead enrichment across workers")
    e.add_argument("--input-csv", required=True, help="Raw leads CSV (e.g. fpga_leads.csv)")
    e.add_argument("--enriched-csv", default="", help="Already-enriched CSV to skip (e.g. fpga_enriched.csv)")
    e.add_argument("--chunk-size", type=int, default=50, help="Leads per work unit")
    e.add_argument("--max-hours", type=float, default=8)
    e.add_argument("--port", type=int, default=8742)
    e.add_argument("--no-tunnel", action="store_true")

    # Extract mode
    x = sub.add_parser("extract", help="Distribute training data extraction across workers")
    x.add_argument("--enriched-csv", required=True, help="Enriched leads CSV")
    x.add_argument("--output-dir", default="./training_data", help="Training data output directory")
    x.add_argument("--chunk-size", type=int, default=25, help="Leads per work unit")
    x.add_argument("--max-hours", type=float, default=8)
    x.add_argument("--port", type=int, default=8742)
    x.add_argument("--no-tunnel", action="store_true")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        sys.exit(1)

    _current_mode = args.mode

    print(f"=== GitHub Crawler Orchestrator ({args.mode} mode) ===\n")

    # Init database
    init_db()
    print(f"  Database    : {DB_FILE}")

    # Mode-specific seeding
    if args.mode == "search":
        seed_count = load_seed_leads()
        if seed_count:
            print(f"  Seed leads  : {seed_count}")
        queries = load_queries()
        new_units = seed_search_units(queries)
        print(f"  Queries     : {len(queries)} from {QUERIES_FILE}")
        print(f"  Work units  : {new_units} new")

    elif args.mode == "enrich":
        os.environ["ENRICHED_OUTPUT"] = args.enriched_csv or "./fpga_enriched_complete.csv"
        new_units = seed_enrich_units(args.input_csv, args.enriched_csv, args.chunk_size)

    elif args.mode == "extract":
        os.environ["TRAINING_OUTPUT_DIR"] = args.output_dir
        new_units = seed_extract_units(args.enriched_csv, args.output_dir, args.chunk_size)

    # Show DB state
    with get_db() as conn:
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM work_units WHERE status = 'pending'"
        ).fetchone()["c"]
        done = conn.execute(
            "SELECT COUNT(*) as c FROM work_units WHERE status IN ('done', 'skipped')"
        ).fetchone()["c"]
    print(f"  Pending     : {pending}")
    print(f"  Done        : {done}")
    print(f"  Max runtime : {args.max_hours}h")
    print()

    # Start tunnel
    tunnel = None
    port = args.port
    if not args.no_tunnel:
        try:
            from pyngrok import ngrok, conf

            auth_token = os.environ.get("NGROK_AUTH_TOKEN", "").strip()
            if auth_token:
                conf.get_default().auth_token = auth_token

            tunnel = ngrok.connect(port, "http")
            tunnel_url = tunnel.public_url
            print(f"  Tunnel URL  : {tunnel_url}")
            print(f"\n  Set this as ORCHESTRATOR_URL in your RunPod template env vars.\n")
        except ImportError:
            print("  [warn] pyngrok not installed — pip install pyngrok")
            print(f"  Local URL   : http://localhost:{port}")
        except Exception as exc:
            print(f"  [warn] ngrok tunnel failed: {exc}")
            print(f"  Local URL   : http://localhost:{port}")
    else:
        print(f"  Local URL   : http://localhost:{port}")
    print()

    # Start background threads
    threading.Thread(target=reaper_loop, daemon=True).start()
    threading.Thread(target=progress_loop, daemon=True).start()

    # Max runtime watchdog
    def watchdog():
        _shutdown_event.wait(args.max_hours * 3600)
        if not _shutdown_event.is_set():
            print(f"\n[watchdog] Max runtime of {args.max_hours}h reached. Exporting...")
            if _current_mode == "search":
                _export_search_csv()
            elif _current_mode == "enrich":
                _export_enriched_csv()
            elif _current_mode == "extract":
                _export_training_data()
            _shutdown_event.set()

    threading.Thread(target=watchdog, daemon=True).start()

    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\n\n[interrupt] Ctrl+C received. Exporting results before exit...")
        if _current_mode == "search":
            _export_search_csv()
        elif _current_mode == "enrich":
            _export_enriched_csv()
        elif _current_mode == "extract":
            _export_training_data()
        _shutdown_event.set()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start Flask (blocking)
    try:
        app.run(host="0.0.0.0", port=port, threaded=True)
    except Exception:
        pass
    finally:
        if tunnel:
            try:
                from pyngrok import ngrok
                ngrok.disconnect(tunnel.public_url)
            except Exception:
                pass


if __name__ == "__main__":
    main()
