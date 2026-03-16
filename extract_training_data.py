"""
Backfill training data from crawler output.

Takes the crawler CSV (with commit_url fields), hits the GitHub API to extract:
  - Full diff of the fix commit/PR
  - Parent commit SHA (the "before" state with the bug)
  - Changed files and their before/after contents
  - Bug category (inferred from query + diff)

Outputs a training dataset: (buggy_code, fix_code, bug_category, metadata)

Usage:
    python extract_training_data.py leads.csv training_data/

    # Resume from where you left off (skips already-processed URLs):
    python extract_training_data.py leads.csv training_data/ --resume

    # Only process FPGA/hardware leads:
    python extract_training_data.py leads.csv training_data/ --filter-hardware

    # Limit to N entries (for testing):
    python extract_training_data.py leads.csv training_data/ --limit 50
"""

import os
import sys
import csv
import json
import time
import re
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# Import rate limiting and token management from crawler
from crawler import (
    rate_limited_get as _crawler_rate_limited_get,
    _init_token as _crawler_init_token,
    configure_token,
)

# File extensions we care about for training data
CODE_EXTENSIONS = {
    # Hardware
    ".vhd", ".vhdl", ".v", ".sv", ".svh",
    # Systems
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    # Rust
    ".rs",
    # Config/build
    ".ld", ".dts", ".dtsi", ".cfg", ".def", ".mk",
    # Kconfig
    "Kconfig",
    # Python (for build scripts, test harnesses)
    ".py",
    # Makefiles
    "Makefile", "CMakeLists.txt",
}

# Hardware-specific extensions for --filter-hardware
HARDWARE_EXTENSIONS = {".vhd", ".vhdl", ".v", ".sv", ".svh", ".dts", ".dtsi", ".ld"}

# Bug categories inferred from query + diff content
BUG_CATEGORIES = [
    ("port_mismatch",       [r"port\s*mismatch", r"port\s*map", r"signal\s*width", r"instantiation"]),
    ("sensitivity_list",    [r"sensitivity\s*list", r"process\s*\(", r"always\s*@"]),
    ("clock_domain",        [r"clock\s*domain", r"CDC", r"metastab", r"synchroniz"]),
    ("reset_logic",         [r"reset\s*logic", r"async\s*reset", r"sync\s*reset"]),
    ("latch_inferred",      [r"latch\s*infer", r"incomplete\s*case", r"missing\s*else"]),
    ("api_breaking",        [r"breaking\s*(api|change)", r"api\s*contract", r"function\s*signature"]),
    ("merge_conflict",      [r"merge\s*conflict", r"conflicting\s*change", r"revert\s*merge"]),
    ("dependency_conflict", [r"dependency\s*conflict", r"version\s*mismatch", r"broken\s*import"]),
    ("linker_error",        [r"linker\s*(script|error)", r"undefined\s*symbol", r"multiple\s*definition"]),
    ("build_regression",    [r"build\s*error", r"regression\s*introduced", r"fix\s*build"]),
    ("parameter_mismatch",  [r"parameter\s*mismatch", r"argument\s*mismatch", r"wrong\s*number"]),
    ("synthesis_error",     [r"synthesis\s*(error|failure)", r"fix\s*(rtl|entity|module)"]),
    ("config_conflict",     [r"config\s*conflict", r"register\s*map", r"driver\s*conflict"]),
    ("stale_reference",     [r"stale\s*import", r"accidentally\s*removed", r"forgot\s*to\s*update", r"out\s*of\s*sync"]),
]


def _init_token():
    _crawler_init_token()


def rate_limited_get(url, params=None, extra_headers=None):
    return _crawler_rate_limited_get(url, params=params, extra_headers=extra_headers)


# ---------------------------------------------------------------------------
# Bug category classification
# ---------------------------------------------------------------------------

def classify_bug(query, diff_text, commit_message):
    """Classify the bug type from query, diff content, and commit message."""
    combined = f"{query} {commit_message} {diff_text[:2000]}".lower()

    matches = []
    for category, patterns in BUG_CATEGORIES:
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                matches.append(category)
                break

    if not matches:
        return "other"
    return matches[0]  # primary category


# ---------------------------------------------------------------------------
# GitHub API: extract commit data
# ---------------------------------------------------------------------------

def parse_commit_url(commit_url):
    """Extract (owner, repo, commit_sha) or (owner, repo, 'pull', pr_number) from URL."""
    # https://github.com/owner/repo/commit/sha
    # https://github.com/owner/repo/pull/123
    # https://github.com/owner/repo/issues/456
    parts = commit_url.rstrip("/").split("/")

    if len(parts) < 5:
        return None

    # Find github.com in the URL
    try:
        gh_idx = parts.index("github.com")
    except ValueError:
        return None

    owner = parts[gh_idx + 1]
    repo = parts[gh_idx + 2]
    resource_type = parts[gh_idx + 3] if len(parts) > gh_idx + 3 else None
    resource_id = parts[gh_idx + 4] if len(parts) > gh_idx + 4 else None

    return {
        "owner": owner,
        "repo": repo,
        "type": resource_type,  # "commit", "pull", "issues"
        "id": resource_id,      # SHA or PR/issue number
    }


def get_commit_data(owner, repo, sha):
    """Fetch commit details including diff."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    resp = rate_limited_get(url)
    if not resp.ok:
        return None
    return resp.json()


def get_pr_commits(owner, repo, pr_number):
    """Get the merge commit or head commit of a PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    resp = rate_limited_get(url)
    if not resp.ok:
        return None
    data = resp.json()
    return {
        "merge_commit_sha": data.get("merge_commit_sha"),
        "head_sha": data.get("head", {}).get("sha"),
        "base_sha": data.get("base", {}).get("sha"),
        "title": data.get("title", ""),
        "body": data.get("body", ""),
    }


def get_pr_files(owner, repo, pr_number):
    """Get the list of files changed in a PR with diffs."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    files = []
    page = 1
    while True:
        resp = rate_limited_get(url, params={"per_page": 100, "page": page})
        if not resp.ok:
            break
        batch = resp.json()
        if not batch:
            break
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return files


def get_file_at_ref(owner, repo, path, ref):
    """Get file contents at a specific commit ref.

    Uses the Contents API (works for files up to 1MB).
    Falls back to the Git Blobs API for larger files (up to 100MB).
    """
    import base64

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = rate_limited_get(url, params={"ref": ref})
    if not resp.ok:
        return None

    data = resp.json()

    # Standard base64 response (< 1MB)
    if data.get("encoding") == "base64" and data.get("content"):
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None

    # File too large for Contents API — fall back to Git Blobs API
    sha = data.get("sha")
    if sha:
        blob_url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs/{sha}"
        blob_resp = rate_limited_get(blob_url)
        if blob_resp.ok:
            blob_data = blob_resp.json()
            if blob_data.get("encoding") == "base64" and blob_data.get("content"):
                try:
                    return base64.b64decode(blob_data["content"]).decode("utf-8", errors="replace")
                except Exception:
                    return None

    return None


# ---------------------------------------------------------------------------
# Core extraction logic
# ---------------------------------------------------------------------------

def is_relevant_file(filename):
    """Check if a file is relevant code we want training data from."""
    name = os.path.basename(filename)
    ext = os.path.splitext(filename)[1].lower()
    return ext in CODE_EXTENSIONS or name in CODE_EXTENSIONS


def is_hardware_file(filename):
    """Check if a file is hardware-specific."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in HARDWARE_EXTENSIONS


def extract_from_commit(owner, repo, sha, query, commit_message):
    """Extract training data from a direct commit URL."""
    commit_data = get_commit_data(owner, repo, sha)
    if not commit_data:
        return None

    files = commit_data.get("files", [])
    parent_sha = None
    parents = commit_data.get("parents", [])
    if parents:
        parent_sha = parents[0].get("sha")

    return _process_files(owner, repo, files, parent_sha, sha, query, commit_message)


def extract_from_pr(owner, repo, pr_number, query, commit_message):
    """Extract training data from a PR URL."""
    pr_data = get_pr_commits(owner, repo, pr_number)
    if not pr_data:
        return None

    files = get_pr_files(owner, repo, pr_number)
    base_sha = pr_data.get("base_sha")
    head_sha = pr_data.get("head_sha")

    # Use PR title/body for better classification
    full_message = f"{pr_data.get('title', '')} {pr_data.get('body', '')}"
    if commit_message:
        full_message = f"{commit_message} {full_message}"

    return _process_files(owner, repo, files, base_sha, head_sha, query, full_message)


def _process_files(owner, repo, files, before_ref, after_ref, query, commit_message):
    """Process changed files and extract before/after code pairs."""
    training_examples = []

    relevant_files = [f for f in files if is_relevant_file(f.get("filename", ""))]

    if not relevant_files:
        return None

    diff_text = "\n".join(f.get("patch", "") for f in relevant_files)
    bug_category = classify_bug(query, diff_text, commit_message)

    for file_info in relevant_files:
        filename = file_info.get("filename", "")
        patch = file_info.get("patch", "")
        status = file_info.get("status", "")  # added, removed, modified, renamed

        if status not in ("modified", "renamed"):
            continue  # we want before/after pairs

        if not patch:
            continue

        # Get before/after file contents
        before_code = None
        after_code = None

        if before_ref:
            # For renamed files, use previous_filename
            before_filename = file_info.get("previous_filename", filename)
            before_code = get_file_at_ref(owner, repo, before_filename, before_ref)

        if after_ref:
            after_code = get_file_at_ref(owner, repo, filename, after_ref)

        # Validation: flag examples that are actually usable for training
        has_before = before_code is not None and len(before_code.strip()) > 0
        has_after = after_code is not None and len(after_code.strip()) > 0
        has_meaningful_diff = (file_info.get("additions", 0) + file_info.get("deletions", 0)) >= 2

        if has_before and has_after and has_meaningful_diff:
            validation = "clean"
        elif has_before and has_after:
            validation = "trivial_diff"  # might just be whitespace or rename
        elif has_before or has_after:
            validation = "partial"  # missing one side
        else:
            validation = "no_code"  # couldn't fetch either file

        example = {
            "repo": f"{owner}/{repo}",
            "filename": filename,
            "before_ref": before_ref,
            "after_ref": after_ref,
            "bug_category": bug_category,
            "query": query,
            "commit_message": commit_message[:500],
            "patch": patch,
            "before_code": before_code,
            "after_code": after_code,
            "language": _detect_language(filename),
            "additions": file_info.get("additions", 0),
            "deletions": file_info.get("deletions", 0),
            "validation": validation,
        }
        training_examples.append(example)

    if not training_examples:
        return None

    return {
        "repo": f"{owner}/{repo}",
        "before_ref": before_ref,
        "after_ref": after_ref,
        "bug_category": bug_category,
        "query": query,
        "commit_message": commit_message[:500],
        "file_count": len(training_examples),
        "examples": training_examples,
    }


def _detect_language(filename):
    ext_map = {
        ".vhd": "vhdl", ".vhdl": "vhdl",
        ".v": "verilog", ".sv": "systemverilog", ".svh": "systemverilog",
        ".c": "c", ".h": "c",
        ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
        ".rs": "rust",
        ".py": "python",
        ".ld": "linker_script",
        ".dts": "devicetree", ".dtsi": "devicetree",
    }
    ext = os.path.splitext(filename)[1].lower()
    return ext_map.get(ext, "other")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def _passes_quality_gate(lead):
    """Filter out toy repos and solo student projects before burning API calls."""
    try:
        cc = int(lead.get("contributor_count") or 0)
    except (ValueError, TypeError):
        cc = 0

    try:
        stars = int(lead.get("stars") or 0)
    except (ValueError, TypeError):
        stars = 0

    language = (lead.get("language") or "").strip()
    org_type = (lead.get("org_type") or "").strip()
    company = (lead.get("company") or "").strip()

    # Must have at least 2 contributors (not a solo project)
    if cc < 2:
        return False

    # Must have a detected language (not just READMEs)
    if not language:
        return False

    # Must have at least 2 stars OR be org-owned OR contributor has a company
    if stars < 2 and org_type != "Organization" and not company:
        return False

    return True


def process_lead(lead, output_dir, processed_urls):
    """Process a single lead row from the crawler CSV."""
    commit_url = lead.get("commit_url", "").strip()
    if not commit_url:
        return None

    if commit_url in processed_urls:
        return None

    # Quality gate — skip toy repos before hitting the API
    if not _passes_quality_gate(lead):
        return None

    parsed = parse_commit_url(commit_url)
    if not parsed:
        print(f"  [skip] can't parse URL: {commit_url}")
        return None

    owner = parsed["owner"]
    repo = parsed["repo"]
    resource_type = parsed["type"]
    resource_id = parsed["id"]
    query = lead.get("query", "")
    commit_message = lead.get("commit_message", "")

    print(f"  [extract] {owner}/{repo} ({resource_type}/{resource_id})")

    try:
        if resource_type == "commit":
            result = extract_from_commit(owner, repo, resource_id, query, commit_message)
        elif resource_type == "pull":
            result = extract_from_pr(owner, repo, resource_id, query, commit_message)
        elif resource_type == "issues":
            # Issues don't have diffs — skip
            return None
        else:
            return None
    except Exception as exc:
        print(f"  [error] {commit_url}: {exc}")
        return None

    if result:
        # Save to disk immediately (checkpoint)
        safe_name = f"{owner}__{repo}__{resource_type}_{resource_id}".replace("/", "__")
        out_path = os.path.join(output_dir, "examples", f"{safe_name}.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  [saved] {safe_name}: {result['file_count']} files, category={result['bug_category']}")

    return result


def process_lead_batch(leads):
    """Process a batch of leads and return results (no file I/O).

    Used by RunPod workers — returns list of result dicts.
    """
    results = []
    for lead in leads:
        commit_url = lead.get("commit_url", "").strip()
        if not commit_url:
            continue
        if not _passes_quality_gate(lead):
            continue

        parsed = parse_commit_url(commit_url)
        if not parsed:
            continue

        owner = parsed["owner"]
        repo = parsed["repo"]
        resource_type = parsed["type"]
        resource_id = parsed["id"]
        query = lead.get("query", "")
        commit_message = lead.get("commit_message", "")

        try:
            if resource_type == "commit":
                result = extract_from_commit(owner, repo, resource_id, query, commit_message)
            elif resource_type == "pull":
                result = extract_from_pr(owner, repo, resource_id, query, commit_message)
            else:
                continue
        except Exception as exc:
            print(f"  [error] {commit_url}: {exc}", flush=True)
            continue

        if result:
            result["commit_url"] = commit_url
            results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(description="Extract training data from crawler output")
    parser.add_argument("input_csv", help="Crawler output CSV file")
    parser.add_argument("output_dir", help="Directory to write training data")
    parser.add_argument("--resume", action="store_true",
                        help="Skip already-processed URLs")
    parser.add_argument("--filter-hardware", action="store_true",
                        help="Only process hardware/FPGA leads")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max entries to process (0 = all)")
    parser.add_argument("--no-quality-filter", action="store_true",
                        help="Skip quality gate (include toy repos)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel workers (careful with rate limits)")
    args = parser.parse_args()

    _init_token()

    # Read input CSV
    leads = []
    with open(args.input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)

    print(f"=== Training Data Extraction ===")
    print(f"  Input       : {args.input_csv} ({len(leads)} leads)")
    print(f"  Output      : {args.output_dir}")

    # Filter to hardware if requested
    if args.filter_hardware:
        hw_languages = {"vhdl", "verilog", "systemverilog", "c", "c++", "rust"}
        leads = [l for l in leads if (l.get("language", "").lower() in hw_languages)]
        print(f"  Hardware    : {len(leads)} leads after filter")

    # Quality gate — drop toy repos before API calls
    if not args.no_quality_filter:
        before_qg = len(leads)
        leads = [l for l in leads if _passes_quality_gate(l)]
        dropped = before_qg - len(leads)
        print(f"  Quality gate: {len(leads)} passed, {dropped} dropped (solo/toy/no-language)")

    # Deduplicate by commit_url
    seen_urls = {}
    unique_leads = []
    for lead in leads:
        url = lead.get("commit_url", "").strip()
        if url and url not in seen_urls:
            seen_urls[url] = True
            unique_leads.append(lead)

    print(f"  Unique URLs : {len(unique_leads)}")

    if args.limit > 0:
        unique_leads = unique_leads[:args.limit]
        print(f"  Limited to  : {args.limit}")

    # Check for already-processed (resume mode)
    processed_urls = set()
    examples_dir = os.path.join(args.output_dir, "examples")
    if args.resume and os.path.exists(examples_dir):
        existing = os.listdir(examples_dir)
        print(f"  Existing    : {len(existing)} already processed")
        # We'll check by URL in the processing loop
        for fname in existing:
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(examples_dir, fname), encoding="utf-8") as f:
                        data = json.load(f)
                        # Mark as processed
                        processed_urls.add(fname.replace(".json", ""))
                except Exception:
                    pass

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)

    print()

    # Process leads
    results = []
    category_counts = {}
    language_counts = {}
    validation_counts = {"clean": 0, "trivial_diff": 0, "partial": 0, "no_code": 0}

    for i, lead in enumerate(unique_leads):
        commit_url = lead.get("commit_url", "").strip()
        parsed = parse_commit_url(commit_url)
        if parsed:
            safe_name = f"{parsed['owner']}__{parsed['repo']}__{parsed['type']}_{parsed['id']}".replace("/", "__")
            if safe_name in processed_urls:
                continue

        print(f"[{i+1}/{len(unique_leads)}]", end="")
        result = process_lead(lead, args.output_dir, set())

        if result:
            results.append(result)
            cat = result["bug_category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

            for ex in result["examples"]:
                lang = ex["language"]
                language_counts[lang] = language_counts.get(lang, 0) + 1
                v = ex.get("validation", "no_code")
                validation_counts[v] = validation_counts.get(v, 0) + 1

        # Save progress summary periodically
        if (i + 1) % 25 == 0 or i == len(unique_leads) - 1:
            _write_summary(args.output_dir, results, category_counts, language_counts, validation_counts)

    # Final summary
    _write_summary(args.output_dir, results, category_counts, language_counts, validation_counts)

    total_examples = sum(r['file_count'] for r in results)
    clean = validation_counts.get("clean", 0)

    print(f"\n=== Extraction Complete ===")
    print(f"  Repos processed    : {len(results)}")
    print(f"  Training examples  : {total_examples}")
    print(f"  Clean (trainable)  : {clean} ({(clean/total_examples*100) if total_examples else 0:.0f}%)")
    print(f"  Validation         :")
    for v, count in sorted(validation_counts.items(), key=lambda x: -x[1]):
        print(f"    {v:25s} : {count}")
    print(f"  Bug categories     :")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:25s} : {count}")
    print(f"  Languages          :")
    for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):
        print(f"    {lang:25s} : {count}")
    print(f"\n  Output: {args.output_dir}/")


def _write_summary(output_dir, results, category_counts, language_counts, validation_counts=None):
    """Write a summary JSON for tracking progress."""
    total_examples = sum(r["file_count"] for r in results)
    clean = (validation_counts or {}).get("clean", 0)
    summary = {
        "total_repos": len(results),
        "total_examples": total_examples,
        "clean_examples": clean,
        "clean_pct": round((clean / total_examples * 100) if total_examples else 0, 1),
        "category_counts": category_counts,
        "language_counts": language_counts,
        "validation_counts": validation_counts or {},
        "repos": [
            {
                "repo": r["repo"],
                "bug_category": r["bug_category"],
                "file_count": r["file_count"],
                "query": r["query"],
            }
            for r in results
        ],
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
