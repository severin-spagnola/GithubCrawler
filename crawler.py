import os
import sys
import json
import csv
import time
import threading
import re
import argparse
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Startup validation (deferred so imports work without GITHUB_TOKEN)
# ---------------------------------------------------------------------------

RATE_LIMIT_DELAY = 2.5  # seconds between API calls per token
MAX_SEARCH_RESULTS = 1000  # GitHub hard cap per query
SEARCH_PER_PAGE = 100      # max allowed by GitHub search API

# ---------------------------------------------------------------------------
# Token pool with round-robin rotation
# ---------------------------------------------------------------------------

_token_pool = []
_token_index = 0
_token_lock = threading.Lock()


def _load_tokens():
    """Load all available GitHub tokens from environment."""
    global _token_pool
    tokens = []
    # Primary token
    t = os.environ.get("GITHUB_TOKEN", "").strip()
    if t:
        tokens.append(t)
    # Numbered tokens (GITHUB_TOKEN2, GITHUB_TOKEN3, ...)
    for i in range(2, 20):
        t = os.environ.get(f"GITHUB_TOKEN{i}", "").strip()
        if t and t not in tokens:
            tokens.append(t)
    _token_pool = tokens


def _next_token():
    """Round-robin to the next token. Returns auth headers."""
    global _token_index
    with _token_lock:
        token = _token_pool[_token_index % len(_token_pool)]
        _token_index += 1
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }


def _init_token():
    """Validate and set up token pool. Call before any API usage."""
    _load_tokens()
    if not _token_pool:
        print(
            "ERROR: No GITHUB_TOKEN environment variables found.\n"
            "  Export at least one:  export GITHUB_TOKEN=ghp_...",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"  [tokens] loaded {len(_token_pool)} GitHub token(s)")


def configure_token(token):
    """Set the GitHub token programmatically (used by RunPod workers)."""
    global _token_pool
    _token_pool = [token]


# ---------------------------------------------------------------------------
# Thread-safe rate limiter
# ---------------------------------------------------------------------------

_rate_lock = threading.Lock()
# Per-token rate limiting: each token gets its own next-fire time
_token_next_call = {}  # token_index -> monotonic time


MAX_RETRIES = 3


def rate_limited_get(url, params=None, extra_headers=None):
    """GET with per-token rate limiting and round-robin rotation."""
    retries = 0
    while True:
        # Pick token and get per-token rate limit
        with _token_lock:
            global _token_index
            ti = _token_index % len(_token_pool)
            token = _token_pool[ti]
            _token_index += 1

        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        if extra_headers:
            headers.update(extra_headers)

        with _rate_lock:
            now = time.monotonic()
            token_fire = _token_next_call.get(ti, 0.0)
            fire_at = max(now, token_fire)
            _token_next_call[ti] = fire_at + RATE_LIMIT_DELAY

        wait = fire_at - time.monotonic()
        if wait > 0:
            time.sleep(wait)

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=(10, 30))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            retries += 1
            if retries > MAX_RETRIES:
                raise
            backoff = 10 * retries
            print(f"  [retry] {type(exc).__name__}, attempt {retries}/{MAX_RETRIES}, "
                  f"waiting {backoff}s …")
            time.sleep(backoff)
            continue

        if resp.status_code == 403:
            remaining = resp.headers.get("X-RateLimit-Remaining")
            retry_after = resp.headers.get("Retry-After")
            reset_ts = resp.headers.get("X-RateLimit-Reset")

            # Secondary rate limit (abuse detection) — use Retry-After or short backoff
            if retry_after:
                sleep_secs = int(retry_after) + 5
                print(f"  [secondary limit] 403 + Retry-After. Sleeping {sleep_secs}s …")
                time.sleep(sleep_secs)
                continue

            # Primary rate limit exhausted (remaining == 0)
            if remaining == "0" and reset_ts:
                sleep_secs = max(int(reset_ts) - int(time.time()), 0) + 5
                print(f"  [primary limit] exhausted. Sleeping {sleep_secs}s until reset …")
                time.sleep(sleep_secs)
                continue

            # Secondary limit without Retry-After — use escalating backoff, max 5 min
            retries += 1
            if retries > MAX_RETRIES:
                print(f"  [warn] 403 after {MAX_RETRIES} retries for {url}")
                return resp
            backoff = min(60 * retries, 300)
            print(f"  [secondary limit] 403, attempt {retries}/{MAX_RETRIES}, backoff {backoff}s …")
            time.sleep(backoff)
            continue

        return resp


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

BOT_PATTERN = re.compile(
    r"(bot|ci|auto|dependabot|renovate|github-actions)",
    re.IGNORECASE,
)

CSV_FIELDS = [
    "query", "query_tier", "source_type", "repo", "repo_name", "org", "org_type",
    "contributor_count", "language", "stars", "username", "display_name",
    "email", "company", "bio", "location", "github_profile", "linkedin",
    "twitter", "blog", "commit_message", "commit_url", "commit_date",
]

# Query string → tier lookup (strips language qualifiers for matching)
TIER_1_QUERIES = {"merge conflict", "fix merge conflict", "revert breaking change",
                  "api breaking change", "port mismatch", "synthesis error",
                  "linker script conflict"}
TIER_2_QUERIES = {"fix function signature", "broken import", "fix broken import",
                  "dependency conflict", "fix header", "accidentally removed",
                  "forgot to update", "out of sync", "stale import",
                  "parameter mismatch", "argument mismatch",
                  "wrong number of arguments", "fix api contract", "breaking api change"}
TIER_3_QUERIES = {"fix build error", "config conflict", "version mismatch",
                  "fix linker error", "regression introduced", "conflicting changes",
                  "revert merge", "fix driver conflict", "fix register map"}
TIER_4_QUERIES = {"fix entity", "fix module", "signal width mismatch", "fix port map",
                  "fix instantiation", "synthesis failure", "fix rtl"}
TIER_5_QUERIES = {"fix sensitivity list", "fix clock domain crossing", "fix reset logic",
                  "latch inferred", "fix simulation mismatch", "fix testbench",
                  "fix timing violation", "fix state machine", "missing case statement",
                  "fix always block", "fix process block", "fix constraint",
                  "fix timing constraint", "simulation synthesis mismatch",
                  "fix combinational loop", "fix race condition", "behavioral mismatch",
                  "fix assertion", "incomplete case"}


HDL_LANGUAGES = ["VHDL", "Verilog", "SystemVerilog"]

# Queries that already have a language: qualifier — don't add another
_HAS_LANG_QUALIFIER = re.compile(r'\blanguage:\w+')


def _query_tier(query):
    """Return the tier number (1-5) for a query string."""
    # Strip language qualifiers like 'language:vhdl' for matching
    base = re.sub(r'\s+language:\w+', '', query).strip().strip('"').lower()
    if base in TIER_1_QUERIES:
        return 1
    if base in TIER_2_QUERIES:
        return 2
    if base in TIER_3_QUERIES:
        return 3
    if base in TIER_4_QUERIES:
        return 4
    if base in TIER_5_QUERIES:
        return 5
    return 0


def _expand_with_language_filter(queries):
    """Expand unqualified Tier 4 queries into per-HDL-language variants.

    e.g. "fix entity" → ["fix entity language:VHDL", "fix entity language:Verilog", ...]
    Queries that already have a language: qualifier are left untouched.
    """
    expanded = []
    for q in queries:
        tier = _query_tier(q)
        if tier == 4 and not _HAS_LANG_QUALIFIER.search(q):
            for lang in HDL_LANGUAGES:
                expanded.append(f"{q} language:{lang}")
        else:
            expanded.append(q)
    return expanded


def _parse_commit_items(items, query):
    """Parse commit search items into lead dicts."""
    leads = []
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
            "query_tier": _query_tier(query),
            "source_type": "commit",
            "repo": repo_full,
            "username": username,
            "commit_message": message,
            "commit_url": commit_url,
            "commit_date": commit_date,
        })
    return leads


def _parse_issue_items(items, query):
    """Parse issue/PR search items into lead dicts."""
    leads = []
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
            "query_tier": _query_tier(query),
            "source_type": source_type,
            "repo": repo_full,
            "username": username,
            "commit_message": item.get("title", "")[:200],
            "commit_url": html_url,
            "commit_date": item.get("created_at", ""),
        })
    return leads


def search_commits(query, page=None, per_page=SEARCH_PER_PAGE):
    """Return list of raw lead dicts from commit search.

    If page is specified, fetch only that single page (for worker mode).
    If page is None, paginate through all available pages (standalone mode).
    Returns (leads, total_count) when page is specified, or just leads when paginating all.
    """
    url = "https://api.github.com/search/commits"
    extra = {"Accept": "application/vnd.github.cloak-preview+json"}

    if page is not None:
        # Single-page mode for workers
        params = {"q": query, "per_page": per_page, "page": page}
        print(f"  [commits] searching: {query} (page {page})")
        resp = rate_limited_get(url, params=params, extra_headers=extra)
        if not resp.ok:
            print(f"  [warn] commit search failed ({resp.status_code}): {resp.text[:200]}")
            return [], 0
        data = resp.json()
        total_count = data.get("total_count", 0)
        items = data.get("items", [])
        print(f"  [commits] page {page}: {len(items)} results (total: {total_count})")
        return _parse_commit_items(items, query), total_count

    # Full pagination mode
    leads = []
    max_pages = MAX_SEARCH_RESULTS // per_page
    current_page = 1

    while current_page <= max_pages:
        params = {"q": query, "per_page": per_page, "page": current_page}
        print(f"  [commits] searching: {query} (page {current_page})")
        resp = rate_limited_get(url, params=params, extra_headers=extra)
        if not resp.ok:
            print(f"  [warn] commit search failed ({resp.status_code}): {resp.text[:200]}")
            break

        data = resp.json()
        total_count = data.get("total_count", 0)
        items = data.get("items", [])
        print(f"  [commits] page {current_page}: {len(items)} results (total: {total_count})")

        leads.extend(_parse_commit_items(items, query))

        if len(items) < per_page:
            break
        if len(leads) >= min(total_count, MAX_SEARCH_RESULTS):
            break
        current_page += 1

    return leads


def search_issues(query, page=None, per_page=SEARCH_PER_PAGE):
    """Return list of raw lead dicts from issues/PR search.

    If page is specified, fetch only that single page (for worker mode).
    If page is None, paginate through all available pages (standalone mode).
    Returns (leads, total_count) when page is specified, or just leads when paginating all.
    """
    url = "https://api.github.com/search/issues"

    if page is not None:
        # Single-page mode for workers
        params = {"q": query, "per_page": per_page, "page": page}
        print(f"  [issues]  searching: {query} (page {page})")
        resp = rate_limited_get(url, params=params)
        if not resp.ok:
            print(f"  [warn] issue search failed ({resp.status_code}): {resp.text[:200]}")
            return [], 0
        data = resp.json()
        total_count = data.get("total_count", 0)
        items = data.get("items", [])
        print(f"  [issues]  page {page}: {len(items)} results (total: {total_count})")
        return _parse_issue_items(items, query), total_count

    # Full pagination mode
    leads = []
    max_pages = MAX_SEARCH_RESULTS // per_page
    current_page = 1

    while current_page <= max_pages:
        params = {"q": query, "per_page": per_page, "page": current_page}
        print(f"  [issues]  searching: {query} (page {current_page})")
        resp = rate_limited_get(url, params=params)
        if not resp.ok:
            print(f"  [warn] issue search failed ({resp.status_code}): {resp.text[:200]}")
            break

        data = resp.json()
        total_count = data.get("total_count", 0)
        items = data.get("items", [])
        print(f"  [issues]  page {current_page}: {len(items)} results (total: {total_count})")

        leads.extend(_parse_issue_items(items, query))

        if len(items) < per_page:
            break
        if len(leads) >= min(total_count, MAX_SEARCH_RESULTS):
            break
        current_page += 1

    return leads


# ---------------------------------------------------------------------------
# Enrichment helpers
# ---------------------------------------------------------------------------

def enrich_user(username):
    """Fetch GitHub profile data for a username."""
    url = f"https://api.github.com/users/{username}"
    resp = rate_limited_get(url)
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
    """Use the Link header rel=last trick to get contributor count."""
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
    """Fetch repo metadata and contributor count."""
    repo_url = f"https://api.github.com/repos/{repo_full}"
    resp = rate_limited_get(repo_url)
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

    contrib_url = f"https://api.github.com/repos/{repo_full}/contributors"
    contrib_resp = rate_limited_get(contrib_url, params={"per_page": 30, "anon": "true"})
    contributor_count = 0
    if contrib_resp.ok:
        contributor_count = _parse_contributor_count(contrib_resp)

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
    try:
        contributor_count = int(lead.get("contributor_count", 0) or 0)
    except (ValueError, TypeError):
        contributor_count = 0

    if BOT_PATTERN.search(username):
        return True
    if contributor_count < 1 or contributor_count > 500:
        return True
    return False


# ---------------------------------------------------------------------------
# Core enrichment worker (with caching)
# ---------------------------------------------------------------------------

_user_cache = {}
_repo_cache = {}
_cache_lock = threading.Lock()


def enrich_lead(lead):
    """Enrich a single lead with user + repo data. Returns updated lead dict."""
    username = lead["username"]
    repo = lead["repo"]

    with _cache_lock:
        user_cached = _user_cache.get(username)
        repo_cached = _repo_cache.get(repo)

    if user_cached is None:
        user_cached = enrich_user(username)
        with _cache_lock:
            _user_cache[username] = user_cached

    if repo_cached is None:
        repo_cached = enrich_repo(repo)
        with _cache_lock:
            _repo_cache[repo] = repo_cached

    lead.update(user_cached)
    lead.update(repo_cached)
    return lead


# ---------------------------------------------------------------------------
# Incremental CSV writer
# ---------------------------------------------------------------------------

class IncrementalCSV:
    """Append-mode CSV writer that flushes after each batch."""

    def __init__(self, path, fields, resume=False):
        self.path = path
        self.fields = fields
        self._count = 0
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        if resume and os.path.isfile(path):
            # Count existing rows (don't overwrite)
            with open(path, newline="", encoding="utf-8") as f:
                self._count = sum(1 for _ in f) - 1  # minus header
            print(f"  [resume] keeping {self._count} existing leads in {path}")
        else:
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=fields, extrasaction="ignore").writeheader()

    def write_leads(self, leads):
        """Append leads to the CSV file."""
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields, extrasaction="ignore")
            for lead in leads:
                writer.writerow({field: lead.get(field, "") for field in self.fields})
        self._count += len(leads)

    @property
    def count(self):
        return self._count


# ---------------------------------------------------------------------------
# Main — search-only mode
# ---------------------------------------------------------------------------

def run_search(queries, output_path, language_filter=False, resume=False):
    """Search-only: collect leads, dedup in-flight, write incrementally."""
    if language_filter:
        queries = _expand_with_language_filter(queries)
        print(f"  [lang-filter] expanded to {len(queries)} queries (Tier 4 → per-HDL-language)")

    writer = IncrementalCSV(output_path, CSV_FIELDS, resume=resume)
    seen = set()  # (username, repo) dedup

    # If resuming, load existing leads into seen set for dedup
    if resume and os.path.isfile(output_path):
        with open(output_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                seen.add((row.get("username", ""), row.get("repo", "")))
        print(f"  [resume] loaded {len(seen)} existing (username, repo) pairs for dedup")

    print(f"\n=== Search Phase ===")
    for qi, query in enumerate(queries, 1):
        query_new = 0
        query_dup = 0

        for search_fn in (search_commits, search_issues):
            leads = search_fn(query)
            new_leads = []
            for lead in leads:
                key = (lead["username"], lead["repo"])
                if key not in seen:
                    seen.add(key)
                    new_leads.append(lead)
                else:
                    query_dup += 1
            if new_leads:
                writer.write_leads(new_leads)
                query_new += len(new_leads)

        print(f"  [{qi}/{len(queries)}] {query}: +{query_new} new, {query_dup} dupes "
              f"(total unique: {writer.count})")

    print(f"\n[done] wrote {writer.count} unique leads to {output_path}")
    return writer.count


# ---------------------------------------------------------------------------
# Main — enrich-only mode
# ---------------------------------------------------------------------------

def run_enrich(input_path, output_path, resume=False):
    """Read an existing CSV, enrich each lead incrementally, and write output.

    Runs single-threaded (rate limit makes threading pointless) and writes
    each enriched lead immediately for crash resilience.  Supports --resume
    to continue from where a previous run left off.
    """
    # Read input
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    print(f"  Read {len(leads)} leads from {input_path}")

    # Deduplicate input
    seen = {}
    for lead in leads:
        key = (lead.get("username", ""), lead.get("repo", ""))
        if key not in seen:
            seen[key] = lead
    unique_leads = list(seen.values())
    print(f"  {len(unique_leads)} unique leads after dedup")

    # Resume support: figure out how many were already enriched
    already_done = set()
    if resume and os.path.isfile(output_path):
        with open(output_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                already_done.add((row.get("username", ""), row.get("repo", "")))
        print(f"  [resume] {len(already_done)} leads already enriched, skipping them")

    # Prepare incremental writer
    writer = IncrementalCSV(output_path, CSV_FIELDS, resume=resume)

    # Enrich one by one (single-threaded — rate limit is the bottleneck)
    total = len(unique_leads)
    written = 0
    filtered_out = 0
    print(f"\n=== Enrich Phase ({total} leads) ===")
    for i, lead in enumerate(unique_leads, 1):
        key = (lead.get("username", ""), lead.get("repo", ""))
        if key in already_done:
            continue
        try:
            enriched = enrich_lead(lead)
        except Exception as exc:
            print(f"  [error] enrichment exception for {key}: {exc}")
            continue
        if should_filter_out(enriched):
            filtered_out += 1
        else:
            writer.write_leads([enriched])
            written += 1
        if i % 50 == 0:
            print(f"  [enrich] {i}/{total} processed, {writer.count} written, {filtered_out} filtered out")

    print(f"\n[done] wrote {writer.count} enriched leads to {output_path} ({filtered_out} filtered out)")


# ---------------------------------------------------------------------------
# Main — full mode (search + enrich, legacy behavior)
# ---------------------------------------------------------------------------

def run_full(queries, output_path, language_filter=False):
    """Full pipeline: search → dedup → enrich → filter → write."""
    if language_filter:
        queries = _expand_with_language_filter(queries)

    # Search with in-flight dedup + incremental writes to a temp file
    tmp_path = output_path + ".search_tmp.csv"
    run_search(queries, tmp_path, language_filter=False)  # already expanded

    # Enrich the search results
    run_enrich(tmp_path, output_path)

    # Clean up temp
    try:
        os.remove(tmp_path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description="GitHub lead crawler with search-only, enrich-only, and full modes",
    )
    sub = p.add_subparsers(dest="mode")

    # --- search ---
    s = sub.add_parser("search", help="Search only — fast collection, no enrichment")
    s.add_argument("queries", help="JSON array of query strings, or path to queries.txt")
    s.add_argument("output", help="Output CSV path")
    s.add_argument("--language-filter", action="store_true",
                   help="Auto-expand unqualified Tier 4 queries with language:VHDL/Verilog/SystemVerilog")
    s.add_argument("--resume", action="store_true",
                   help="Resume a previous run — keep existing CSV rows and dedup against them")

    # --- enrich ---
    e = sub.add_parser("enrich", help="Enrich an existing search-results CSV")
    e.add_argument("input", help="Input CSV from a previous search run")
    e.add_argument("output", help="Output CSV with enriched data")
    e.add_argument("--resume", action="store_true",
                   help="Resume a previous enrichment run (skip already-enriched leads)")

    # --- full ---
    f = sub.add_parser("full", help="Full pipeline: search + enrich + filter")
    f.add_argument("queries", help="JSON array of query strings, or path to queries.txt")
    f.add_argument("output", help="Output CSV path")
    f.add_argument("--language-filter", action="store_true",
                   help="Auto-expand unqualified Tier 4 queries with language:VHDL/Verilog/SystemVerilog")

    return p


def _load_queries(raw):
    """Load queries from a JSON string or a queries.txt file path."""
    # Try as JSON first
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        pass

    # Try as file path
    if os.path.isfile(raw):
        queries = []
        with open(raw, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip surrounding quotes for the search API
                queries.append(line.strip('"'))
        return queries

    print(f"ERROR: Could not parse queries as JSON or find file: {raw}", file=sys.stderr)
    sys.exit(1)


def main():
    _init_token()

    parser = build_parser()
    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        sys.exit(1)

    print(f"=== GitHub Crawler ({args.mode} mode) ===\n")

    if args.mode == "search":
        queries = _load_queries(args.queries)
        print(f"  Queries : {len(queries)}")
        print(f"  Output  : {args.output}")
        run_search(queries, args.output, language_filter=args.language_filter,
                   resume=args.resume)

    elif args.mode == "enrich":
        print(f"  Input   : {args.input}")
        print(f"  Output  : {args.output}")
        run_enrich(args.input, args.output, resume=args.resume)

    elif args.mode == "full":
        queries = _load_queries(args.queries)
        print(f"  Queries : {len(queries)}")
        print(f"  Output  : {args.output}")
        run_full(queries, args.output, language_filter=args.language_filter)


if __name__ == "__main__":
    main()
