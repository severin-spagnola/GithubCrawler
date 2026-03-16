"""
RunPod serverless worker for distributed GitHub crawling, enrichment, and training data extraction.

Pulls work units from the orchestrator, executes the requested mode, and POSTs results back.

Modes:
    search  — GitHub API search + optional enrichment (original behavior)
    enrich  — enrich a batch of leads with user/repo metadata
    extract — extract training data (diffs, before/after code) from commit URLs

Environment variables (set in RunPod template):
    ORCHESTRATOR_URL  — public URL of the orchestrator (e.g., ngrok tunnel)
    GITHUB_TOKEN      — GitHub personal access token for this worker
    WORKER_ID         — optional, auto-generated if not set
    BATCH_SIZE        — work units per request (default: 3)
    MAX_IDLE_POLLS    — exit after N consecutive empty polls (default: 30 = ~5min)
    ENRICH_LEADS      — set to "1" to enrich leads in search mode (default: "1")
"""

import os
import sys
import json
import time
import uuid
import traceback

import requests as http_requests
from dotenv import load_dotenv

load_dotenv()

# Import crawler functions
from crawler import (
    configure_token,
    search_commits,
    search_issues,
    enrich_lead,
    should_filter_out,
)

# Import extract functions
from extract_training_data import process_lead_batch

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "").strip().rstrip("/")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
WORKER_ID = os.environ.get("WORKER_ID", f"w-{uuid.uuid4().hex[:8]}")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "3"))
MAX_IDLE_POLLS = int(os.environ.get("MAX_IDLE_POLLS", "30"))
DO_ENRICH = os.environ.get("ENRICH_LEADS", "1").strip() == "1"
POLL_SLEEP = 10  # seconds between idle polls


def log(msg):
    print(f"[{WORKER_ID}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Orchestrator HTTP client
# ---------------------------------------------------------------------------

def request_work():
    """Request a batch of work units from the orchestrator."""
    resp = http_requests.post(
        f"{ORCHESTRATOR_URL}/work/request",
        json={"worker_id": WORKER_ID, "batch_size": BATCH_SIZE},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("units", [])


def report_complete(unit_id, leads, total_count, mode="search"):
    """Report a completed work unit with results."""
    resp = http_requests.post(
        f"{ORCHESTRATOR_URL}/work/complete",
        json={
            "worker_id": WORKER_ID,
            "unit_id": unit_id,
            "mode": mode,
            "leads": leads,
            "total_count": total_count,
        },
        timeout=60,
    )
    resp.raise_for_status()


def report_failure(unit_id, error):
    """Report a failed work unit."""
    try:
        http_requests.post(
            f"{ORCHESTRATOR_URL}/work/fail",
            json={
                "worker_id": WORKER_ID,
                "unit_id": unit_id,
                "error": str(error)[:500],
            },
            timeout=15,
        )
    except Exception as exc:
        log(f"  failed to report failure for unit {unit_id}: {exc}")


# ---------------------------------------------------------------------------
# Work execution
# ---------------------------------------------------------------------------

def execute_search(unit):
    """Execute a search work unit (original behavior)."""
    query = unit["query"]
    search_type = unit["search_type"]
    page = unit["page"]

    if search_type == "commits":
        leads, total_count = search_commits(query, page=page)
    else:
        leads, total_count = search_issues(query, page=page)

    if DO_ENRICH and leads:
        enriched = []
        for lead in leads:
            try:
                enriched.append(enrich_lead(lead))
            except Exception as exc:
                log(f"  enrich failed for {lead.get('username', '?')}: {exc}")
                enriched.append(lead)
        leads = enriched

    return leads, total_count


def execute_enrich(unit):
    """Enrich a batch of leads with user/repo metadata."""
    leads = unit.get("payload", [])
    enriched = []
    for lead in leads:
        try:
            result = enrich_lead(lead)
            if not should_filter_out(result):
                enriched.append(result)
        except Exception as exc:
            log(f"  enrich failed for {lead.get('username', '?')}: {exc}")
    return enriched, len(enriched)


def execute_extract(unit):
    """Extract training data from a batch of leads."""
    leads = unit.get("payload", [])
    results = process_lead_batch(leads)
    return results, len(results)


def execute_unit(unit):
    """Route work unit to the correct executor based on mode."""
    mode = unit.get("mode", "search")

    if mode == "search":
        return execute_search(unit), mode
    elif mode == "enrich":
        return execute_enrich(unit), mode
    elif mode == "extract":
        return execute_extract(unit), mode
    else:
        raise ValueError(f"Unknown work unit mode: {mode}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def worker_loop():
    """Main worker loop: pull work, execute, report, repeat."""
    if not ORCHESTRATOR_URL:
        log("ERROR: ORCHESTRATOR_URL not set")
        return {"status": "error", "reason": "ORCHESTRATOR_URL not set"}

    if not GITHUB_TOKEN:
        log("ERROR: GITHUB_TOKEN not set")
        return {"status": "error", "reason": "GITHUB_TOKEN not set"}

    # Configure the crawler with our token
    configure_token(GITHUB_TOKEN)

    log(f"Starting worker loop (orchestrator: {ORCHESTRATOR_URL})")
    log(f"  batch_size={BATCH_SIZE}, enrich={DO_ENRICH}, max_idle={MAX_IDLE_POLLS}")

    idle_count = 0
    units_done = 0
    total_leads = 0

    while idle_count < MAX_IDLE_POLLS:
        try:
            batch = request_work()
        except Exception as exc:
            log(f"  failed to request work: {exc}")
            idle_count += 1
            time.sleep(POLL_SLEEP)
            continue

        if not batch:
            idle_count += 1
            if idle_count % 5 == 0:
                log(f"  no work available (idle {idle_count}/{MAX_IDLE_POLLS})")
            time.sleep(POLL_SLEEP)
            continue

        idle_count = 0

        for unit in batch:
            unit_id = unit["id"]
            mode = unit.get("mode", "search")
            log(f"  executing [{mode}]: unit {unit_id}")

            try:
                (results, count), result_mode = execute_unit(unit)
                report_complete(unit_id, results, count, mode=result_mode)
                units_done += 1
                total_leads += count
                log(f"  completed unit {unit_id} [{mode}]: {count} results "
                    f"(total: {units_done} units, {total_leads} results)")
            except Exception as exc:
                log(f"  unit {unit_id} failed: {exc}")
                traceback.print_exc()
                report_failure(unit_id, str(exc))

    log(f"Worker done: {units_done} units completed, {total_leads} results collected")
    return {
        "status": "done",
        "units_completed": units_done,
        "results_collected": total_leads,
        "reason": "no more work" if idle_count >= MAX_IDLE_POLLS else "finished",
    }


# ---------------------------------------------------------------------------
# RunPod entry point
# ---------------------------------------------------------------------------

def handler(event):
    """RunPod serverless handler."""
    return worker_loop()


# Support both RunPod serverless and direct execution
if __name__ == "__main__":
    try:
        import runpod
        runpod.serverless.start({"handler": handler})
    except ImportError:
        # Direct execution without RunPod SDK (for local testing)
        log("Running without RunPod SDK (direct mode)")
        result = worker_loop()
        print(json.dumps(result, indent=2))
