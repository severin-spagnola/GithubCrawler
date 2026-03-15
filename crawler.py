import os
import sys
import json
import csv
import time
import threading
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError

import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Startup validation
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not GITHUB_TOKEN:
    print(
        "ERROR: GITHUB_TOKEN environment variable is not set or is empty.\n"
        "  Export it before running:  export GITHUB_TOKEN=ghp_...",
        file=sys.stderr,
    )
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

RATE_LIMIT_DELAY  = 2.1   # seconds between every API call
REQUEST_TIMEOUT   = 30    # seconds before requests.get() gives up
ENRICH_TIMEOUT    = 60    # seconds before a per-lead enrichment future is abandoned

# ---------------------------------------------------------------------------
# Logging to crawl.log
# ---------------------------------------------------------------------------

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawl.log")
_log_lock = threading.Lock()


def _ts():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def log_line(msg):
    """Append a timestamped line to crawl.log (thread-safe) and echo to stdout."""
    line = f"[{_ts()}] {msg}"
    print(line, flush=True)
    with _log_lock:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")


# ---------------------------------------------------------------------------
# Thread-safe rate limiter
# ---------------------------------------------------------------------------

_rate_lock = threading.Lock()
_next_call_at = 0.0  # monotonic time before which no new call may fire


def rate_limited_get(url, params=None, extra_headers=None):
    """GET with a global 2.1 s floor between calls, handling 403 rate limits.

    Each thread atomically reserves the next available time slot and then
    sleeps *outside* the lock so that threads don't pile up blocking one
    another while sleeping.

    Raises requests.exceptions.Timeout or requests.exceptions.ConnectionError
    to callers — do not swallow them here so individual functions can decide
    how to handle them.
    """
    global _next_call_at

    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)

    while True:
        # Reserve a slot without sleeping under the lock.
        with _rate_lock:
            now = time.monotonic()
            fire_at = max(now, _next_call_at)
            _next_call_at = fire_at + RATE_LIMIT_DELAY

        wait = fire_at - time.monotonic()
        if wait > 0:
            time.sleep(wait)

        resp = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)

        if resp.status_code == 403:
            reset_ts = resp.headers.get("X-RateLimit-Reset")
            if reset_ts:
                sleep_secs = max(int(reset_ts) - int(time.time()), 0) + 5
                print(f"  [rate limit] 403 received. Sleeping {sleep_secs}s until reset …")
                time.sleep(sleep_secs)
                continue
            else:
                print(f"  [warn] 403 with no X-RateLimit-Reset header for {url}")
                return resp

        return resp


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

BOT_PATTERN = re.compile(
    r"(bot|ci|auto|dependabot|renovate|github-actions)",
    re.IGNORECASE,
)

CSV_FIELDS = [
    "query", "source_type", "repo", "repo_name", "org", "org_type",
    "contributor_count", "language", "stars", "username", "display_name",
    "email", "company", "bio", "location", "github_profile", "linkedin",
    "twitter", "blog", "commit_message", "commit_url", "commit_date",
]


def write_snapshot(leads, output_path):
    """Persist an incremental CSV snapshot for live monitoring."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for lead in leads:
            writer.writerow({field: lead.get(field, "") for field in CSV_FIELDS})


def search_commits(query):
    """Return list of raw lead dicts from commit search."""
    leads = []
    url = "https://api.github.com/search/commits"
    params = {"q": query, "per_page": 30, "page": 1}
    extra = {"Accept": "application/vnd.github.cloak-preview+json"}

    print(f"  [commits] searching: {query}")
    try:
        resp = rate_limited_get(url, params=params, extra_headers=extra)
    except requests.exceptions.Timeout:
        print(f"  [warn] commit search timed out for query: {query}")
        return leads
    except requests.exceptions.ConnectionError as exc:
        print(f"  [warn] commit search connection error for query '{query}': {exc}")
        return leads

    if not resp.ok:
        print(f"  [warn] commit search failed ({resp.status_code}): {resp.text[:200]}")
        return leads

    items = resp.json().get("items", [])
    print(f"  [commits] got {len(items)} results")

    for item in items:
        repo_full = item.get("repository", {}).get("full_name", "")
        author = (item.get("author") or {}).get("login", "")
        committer = (item.get("committer") or {}).get("login", "")
        username = author or committer
        if not username or not repo_full:
            continue

        commit_data = item.get("commit", {})
        message = commit_data.get("message", "")[:200]
        commit_url = item.get("html_url", "")
        commit_date = (commit_data.get("author") or {}).get("date", "")

        leads.append({
            "query": query,
            "source_type": "commit",
            "repo": repo_full,
            "username": username,
            "commit_message": message,
            "commit_url": commit_url,
            "commit_date": commit_date,
        })

    return leads


def search_issues(query):
    """Return list of raw lead dicts from issues/PR search."""
    leads = []
    url = "https://api.github.com/search/issues"
    params = {"q": query, "per_page": 30, "page": 1}

    print(f"  [issues]  searching: {query}")
    try:
        resp = rate_limited_get(url, params=params)
    except requests.exceptions.Timeout:
        print(f"  [warn] issue search timed out for query: {query}")
        return leads
    except requests.exceptions.ConnectionError as exc:
        print(f"  [warn] issue search connection error for query '{query}': {exc}")
        return leads

    if not resp.ok:
        print(f"  [warn] issue search failed ({resp.status_code}): {resp.text[:200]}")
        return leads

    items = resp.json().get("items", [])
    print(f"  [issues]  got {len(items)} results")

    for item in items:
        html_url = item.get("html_url", "")
        repo_url = item.get("repository_url", "")
        repo_full = "/".join(repo_url.split("/")[-2:]) if repo_url else ""
        username = (item.get("user") or {}).get("login", "")
        if not username or not repo_full:
            continue

        source_type = "pr" if "/pull/" in html_url else "issue"

        leads.append({
            "query": query,
            "source_type": source_type,
            "repo": repo_full,
            "username": username,
            "commit_message": item.get("title", "")[:200],
            "commit_url": html_url,
            "commit_date": item.get("created_at", ""),
        })

    return leads


# ---------------------------------------------------------------------------
# Enrichment helpers
# ---------------------------------------------------------------------------

def enrich_user(username):
    """Fetch GitHub profile data for a username. Returns {} on any network error."""
    url = f"https://api.github.com/users/{username}"
    try:
        resp = rate_limited_get(url)
    except requests.exceptions.Timeout:
        print(f"  [warn] user enrich timed out: {username}")
        return {}
    except requests.exceptions.ConnectionError as exc:
        print(f"  [warn] user enrich connection error for {username}: {exc}")
        return {}

    if not resp.ok:
        print(f"  [warn] user enrichment failed for {username} ({resp.status_code})")
        return {}

    data = resp.json()
    blog = data.get("blog") or ""
    linkedin = blog if "linkedin.com" in blog.lower() else ""

    return {
        "display_name": data.get("name") or "",
        "email": data.get("email") or "",
        "company": data.get("company") or "",
        "bio": data.get("bio") or "",
        "location": data.get("location") or "",
        "github_profile": data.get("html_url") or "",
        "twitter": data.get("twitter_username") or "",
        "blog": blog,
        "linkedin": linkedin,
    }


def _parse_contributor_count(resp):
    """
    Use the Link header rel=last trick to get contributor count.
    Falls back to counting the returned list if Link header is absent.
    """
    link_header = resp.headers.get("Link", "")
    if link_header:
        match = re.search(r'page=(\d+)>;\s*rel="last"', link_header)
        if match:
            last_page = int(match.group(1))
            return last_page * 30

    try:
        return len(resp.json())
    except Exception:
        return 0


def enrich_repo(repo_full):
    """Fetch repo metadata and contributor count. Returns {} on any network error."""
    repo_url = f"https://api.github.com/repos/{repo_full}"
    try:
        resp = rate_limited_get(repo_url)
    except requests.exceptions.Timeout:
        print(f"  [warn] repo enrich timed out: {repo_full}")
        return {}
    except requests.exceptions.ConnectionError as exc:
        print(f"  [warn] repo enrich connection error for {repo_full}: {exc}")
        return {}

    if not resp.ok:
        print(f"  [warn] repo enrichment failed for {repo_full} ({resp.status_code})")
        return {}

    data = resp.json()
    owner = data.get("owner") or {}
    org = owner.get("login") or ""
    org_type = owner.get("type") or ""
    repo_name = data.get("name") or ""
    description = data.get("description") or ""
    language = data.get("language") or ""
    stars = data.get("stargazers_count") or 0

    contributor_count = 0
    contrib_url = f"https://api.github.com/repos/{repo_full}/contributors"
    try:
        contrib_resp = rate_limited_get(contrib_url, params={"per_page": 30, "anon": "true"})
        if contrib_resp.ok:
            contributor_count = _parse_contributor_count(contrib_resp)
    except requests.exceptions.Timeout:
        print(f"  [warn] contributor fetch timed out: {repo_full}")
    except requests.exceptions.ConnectionError as exc:
        print(f"  [warn] contributor fetch connection error for {repo_full}: {exc}")

    return {
        "repo_name": repo_name,
        "org": org,
        "org_type": org_type,
        "language": language,
        "stars": stars,
        "description": description,
        "contributor_count": contributor_count,
    }


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def should_filter_out(lead):
    username = lead.get("username", "")
    contributor_count = lead.get("contributor_count", 0)

    if BOT_PATTERN.search(username):
        return True
    if contributor_count < 3 or contributor_count > 500:
        return True
    return False


# ---------------------------------------------------------------------------
# Core enrichment worker
# ---------------------------------------------------------------------------

def enrich_lead(lead):
    """Enrich a single lead with user + repo data. Returns updated lead dict."""
    username = lead["username"]
    repo = lead["repo"]

    print(f"  [enrich] {username} @ {repo}")

    user_data = enrich_user(username)
    repo_data = enrich_repo(repo)

    lead.update(user_data)
    lead.update(repo_data)
    return lead


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python crawler.py '<json_query_array>' <output_csv>", file=sys.stderr)
        sys.exit(1)

    try:
        queries = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse queries JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path = sys.argv[2]

    print(f"=== GitHub Crawler starting ===")
    print(f"  Queries : {len(queries)}")
    print(f"  Output  : {output_path}")
    print(f"  Log     : {LOG_PATH}")
    print()

    # ------------------------------------------------------------------
    # Phase 1: Search — log after every query completes
    # ------------------------------------------------------------------
    raw_leads = []
    for query in queries:
        commit_leads = search_commits(query)
        issue_leads  = search_issues(query)
        raw_leads.extend(commit_leads)
        raw_leads.extend(issue_leads)
        write_snapshot(raw_leads, output_path)
        log_line(
            f'query="{query}" commits={len(commit_leads)} issues={len(issue_leads)}'
        )

    print(f"\n[phase 1] collected {len(raw_leads)} raw leads")

    # ------------------------------------------------------------------
    # Phase 2: Deduplicate by (username, repo)
    # ------------------------------------------------------------------
    seen = {}
    for lead in raw_leads:
        key = (lead["username"], lead["repo"])
        if key not in seen:
            seen[key] = lead

    unique_leads = list(seen.values())
    print(f"[phase 2] {len(unique_leads)} unique leads after deduplication\n")

    # ------------------------------------------------------------------
    # Phase 3: Enrich (threaded, rate-limited, per-future timeout)
    # ------------------------------------------------------------------
    print("[phase 3] enriching leads …")
    enriched = []
    skipped  = 0

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(enrich_lead, lead): lead for lead in unique_leads}
        for future in as_completed(futures):
            lead = futures[future]
            try:
                result = future.result(timeout=ENRICH_TIMEOUT)
                enriched.append(result)
                filtered_snapshot = [item for item in enriched if not should_filter_out(item)]
                write_snapshot(filtered_snapshot, output_path)
            except FutureTimeoutError:
                skipped += 1
                print(
                    f"  [warn] enrichment timed out after {ENRICH_TIMEOUT}s — "
                    f"skipping {lead.get('username')} @ {lead.get('repo')}"
                )
            except Exception as exc:
                skipped += 1
                print(f"  [error] enrichment exception: {exc}")

    print(f"\n[phase 3] enriched {len(enriched)} leads, skipped {skipped}")

    # ------------------------------------------------------------------
    # Phase 4: Filter
    # ------------------------------------------------------------------
    filtered = [l for l in enriched if not should_filter_out(l)]
    print(f"[phase 4] {len(filtered)} leads after filtering "
          f"(removed {len(enriched) - len(filtered)})\n")

    # ------------------------------------------------------------------
    # Phase 5: Write CSV
    # ------------------------------------------------------------------
    write_snapshot(filtered, output_path)

    print(f"[done] wrote {len(filtered)} leads to {output_path}")

    # ------------------------------------------------------------------
    # Final log entry
    # ------------------------------------------------------------------
    log_line(f"CRAWL COMPLETE total_leads={len(filtered)}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        print("=== TEST MODE: single query 'fix merge conflict' → /tmp/test_output.csv ===")
        sys.argv = [sys.argv[0], '["fix merge conflict"]', "/tmp/test_output.csv"]
    main()
