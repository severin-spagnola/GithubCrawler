#!/usr/bin/env python3
"""
Step 3: Execute approved merges on Polaris-Classifier training data.
Operations: dedup, reclassify, drop linker_error, generate synthetic api_breaking.
"""

import json
import os
import hashlib
import difflib
import sys
import time

# ── 0. Dependencies ──────────────────────────────────────────────────────────
try:
    import anthropic
except ImportError:
    print("Installing anthropic...")
    os.system(f"{sys.executable} -m pip install anthropic -q")
    import anthropic

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    os.system(f"{sys.executable} -m pip install python-dotenv -q")
    from dotenv import load_dotenv

# ── Constants ────────────────────────────────────────────────────────────────
EXAMPLES_DIR = "/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/"
SUMMARY_PATH = "/Users/severinspagnola/Desktop/GithubCrawler/training_data/summary.json"
ENV_PATH = "/Users/severinspagnola/Desktop/CIRCA/.env"

RECLASSIFY_MAP = {
    "latch_inferred": "sensitivity_list",
    "reset_logic": "clock_domain",
    "combinational_loop": "sensitivity_list",
    "build_regression": "synthesis_error",
    "merge_conflict": "synthesis_error",
}
DROP_CATEGORIES = {"linker_error"}


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_file_patch_hash(data: dict) -> str:
    """Compute a stable hash for a JSON file by combining all nested example patches."""
    examples = data.get("examples", [])
    if examples:
        combined = "".join(ex.get("patch", "") for ex in examples)
    else:
        combined = data.get("patch", "")
    return sha256_of(combined) if combined else sha256_of(json.dumps(data, sort_keys=True))


# ── 1. LOAD ──────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Loading examples...")
files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".json")]
all_data = {}  # filename -> parsed dict
for fn in sorted(files):
    path = os.path.join(EXAMPLES_DIR, fn)
    with open(path) as f:
        all_data[fn] = json.load(f)

n_loaded = len(all_data)
print(f"  Loaded {n_loaded} JSON files")

# ── 2. COMPUTE patch_hash for missing ────────────────────────────────────────
print("\nSTEP 2: Computing patch_hashes...")
n_computed = 0
for fn, data in all_data.items():
    if "patch_hash" not in data:
        data["patch_hash"] = compute_file_patch_hash(data)
        n_computed += 1
print(f"  Computed patch_hash for {n_computed} files (rest already had it)")

# ── 3. DEDUP by patch_hash ───────────────────────────────────────────────────
print("\nSTEP 3: Deduplicating by patch_hash...")
seen_hashes = {}
dedup_keep = {}
dedup_drop = []  # filenames to delete

for fn, data in all_data.items():
    ph = data["patch_hash"]
    if ph in seen_hashes:
        dedup_drop.append(fn)
    else:
        seen_hashes[ph] = fn
        dedup_keep[fn] = data

n_dedup_dropped = len(dedup_drop)
print(f"  Dropped {n_dedup_dropped} duplicates")
print(f"  Kept {len(dedup_keep)} unique examples")

# Working set is now dedup_keep
working_set = dedup_keep

# ── 4. RECLASSIFY ────────────────────────────────────────────────────────────
print("\nSTEP 4: Reclassifying...")
reclassify_counts = {}   # old_cat -> count reclassified
linker_drop = []         # filenames to drop (linker_error)

for fn, data in list(working_set.items()):
    cat = data.get("bug_category", "")

    if cat in DROP_CATEGORIES:
        linker_drop.append(fn)
        del working_set[fn]
        continue

    if cat in RECLASSIFY_MAP:
        new_cat = RECLASSIFY_MAP[cat]
        data["bug_category"] = new_cat
        # Also update nested examples
        for ex in data.get("examples", []):
            if ex.get("bug_category") == cat:
                ex["bug_category"] = new_cat
        reclassify_counts[cat] = reclassify_counts.get(cat, 0) + 1

n_linker_dropped = len(linker_drop)
print(f"  Dropped {n_linker_dropped} linker_error files")
print(f"  Reclassifications:")
for old_cat, count in sorted(reclassify_counts.items()):
    print(f"    {old_cat} -> {RECLASSIFY_MAP[old_cat]}: {count}")

# ── 5. GENERATE SYNTHETIC api_breaking ──────────────────────────────────────
print("\nSTEP 5: Generating 50 synthetic api_breaking examples...")

# Load API key
load_dotenv(ENV_PATH)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    # Manual parse fallback
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    print("  ERROR: Could not read ANTHROPIC_API_KEY from", ENV_PATH)
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

SYNTH_PROMPT_TEMPLATE = """Generate exactly 10 diverse C/C++ firmware API breaking change examples. Each example shows a realistic API break in embedded/firmware code.

Return ONLY a JSON array of 10 objects with no extra text. Each object must have exactly these fields:
- "before_code": string, the original C/C++ code (10-40 lines)
- "after_code": string, the modified C/C++ code with a breaking API change

Make the examples varied across these change types: function signature changes (added/removed/reordered parameters, changed return type), removed exported functions, struct layout changes (added/removed/reordered fields), enum value shifts (changed integer values), macro redefinitions that break callers.

Focus on realistic embedded/firmware patterns: HAL APIs, driver interfaces, RTOS APIs, peripheral register structs, communication protocol handlers. Use realistic C firmware style with typedefs, uint8_t/uint16_t/uint32_t types, function pointers in structs, etc.

Batch {batch_num} of 5 — use different change types and domains than previous batches.

Return only the JSON array, no markdown fences."""


def make_unified_diff(before: str, after: str) -> str:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(
        before_lines, after_lines,
        fromfile="a/firmware.c", tofile="b/firmware.c"
    ))
    return "".join(diff_lines)


synthetics = []
existing_patch_hashes = {data["patch_hash"] for data in working_set.values()}

for batch_num in range(1, 6):
    print(f"  Generating synthetics batch {batch_num}/5...")
    prompt = SYNTH_PROMPT_TEMPLATE.format(batch_num=batch_num)

    batch_result = None
    for attempt in range(2):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            batch_result = json.loads(raw)
            if isinstance(batch_result, list):
                break
            else:
                print(f"    Attempt {attempt+1}: unexpected response type, retrying...")
                batch_result = None
        except json.JSONDecodeError as e:
            print(f"    Attempt {attempt+1}: JSON parse error: {e}, retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"    Attempt {attempt+1}: API error: {e}, retrying...")
            time.sleep(5)

    if not batch_result:
        print(f"  Batch {batch_num} failed after 2 attempts, skipping")
        continue

    batch_added = 0
    for item in batch_result:
        before = item.get("before_code", "")
        after = item.get("after_code", "")
        if not before or not after:
            continue
        patch = make_unified_diff(before, after)
        ph = sha256_of(patch)
        if ph in existing_patch_hashes:
            continue  # dedup
        existing_patch_hashes.add(ph)
        synthetics.append({
            "before_code": before,
            "after_code": after,
            "patch": patch,
            "bug_category": "api_breaking",
            "language": "c",
            "before_ref": "synthetic",
            "synthetic": True,
            "patch_hash": ph,
        })
        batch_added += 1

    print(f"    Batch {batch_num}: added {batch_added} new synthetics (total so far: {len(synthetics)})")

n_synthetics = len(synthetics)
print(f"  Total synthetics generated: {n_synthetics}")

# ── 6. WRITE RESULTS BACK ────────────────────────────────────────────────────
print("\nSTEP 6: Writing results back to disk...")

# Delete dedup victims
for fn in dedup_drop:
    path = os.path.join(EXAMPLES_DIR, fn)
    if os.path.exists(path):
        os.remove(path)
print(f"  Deleted {len(dedup_drop)} dedup victim files")

# Delete linker_error files
for fn in linker_drop:
    path = os.path.join(EXAMPLES_DIR, fn)
    if os.path.exists(path):
        os.remove(path)
print(f"  Deleted {n_linker_dropped} linker_error files")

# Write/overwrite remaining files (reclassified + updated patch_hash)
n_written = 0
for fn, data in working_set.items():
    path = os.path.join(EXAMPLES_DIR, fn)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    n_written += 1
print(f"  Wrote/updated {n_written} existing files")

# Write synthetic files
for i, synth in enumerate(synthetics, 1):
    fn = f"synthetic_api_breaking_{i:03d}.json"
    path = os.path.join(EXAMPLES_DIR, fn)
    with open(path, "w") as f:
        json.dump(synth, f, indent=2, ensure_ascii=False)
print(f"  Wrote {n_synthetics} synthetic files")

# ── 7. UPDATE summary.json ───────────────────────────────────────────────────
print("\nSTEP 7: Updating summary.json...")

# Count category distribution in working set
cat_counts = {}
for data in working_set.values():
    cat = data.get("bug_category", "unknown")
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

# Add synthetics
cat_counts["api_breaking"] = cat_counts.get("api_breaking", 0) + n_synthetics

total_final = sum(cat_counts.values())

# Load existing summary and update
with open(SUMMARY_PATH) as f:
    summary = json.load(f)

summary["category_counts"] = cat_counts
summary["total_files"] = total_final
summary["step3_applied"] = True
summary["step3_changes"] = {
    "dedup_dropped": n_dedup_dropped,
    "linker_error_dropped": n_linker_dropped,
    "reclassified": reclassify_counts,
    "synthetics_added": n_synthetics,
}

with open(SUMMARY_PATH, "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"  Updated summary.json")

# ── 8. FINAL REPORT ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)
print(f"  Examples loaded initially:    {n_loaded}")
print(f"  Dropped by dedup:             {n_dedup_dropped}")
print(f"  Dropped (linker_error):       {n_linker_dropped}")
print(f"  Reclassifications:")
for old_cat, count in sorted(reclassify_counts.items()):
    print(f"    {old_cat:25s} -> {RECLASSIFY_MAP[old_cat]}: {count}")
print(f"  Synthetics generated+added:   {n_synthetics}")
print(f"  Total final dataset size:     {total_final}")
print()
print("  Final category distribution:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"    {cat:30s}: {count}")

# ── 9. VERIFICATION ─────────────────────────────────────────────────────────
print("\nSTEP 9: Verification...")
actual_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".json")]
n_actual = len(actual_files)

verify_cats = {}
for fn in actual_files:
    path = os.path.join(EXAMPLES_DIR, fn)
    with open(path) as f:
        d = json.load(f)
    cat = d.get("bug_category", "unknown")
    verify_cats[cat] = verify_cats.get(cat, 0) + 1

print(f"  Files in examples/ dir: {n_actual} (expected {total_final})")
if n_actual == total_final:
    print("  File count: OK")
else:
    print(f"  WARNING: file count mismatch! {n_actual} != {total_final}")

print("  Verified category distribution:")
for cat, count in sorted(verify_cats.items(), key=lambda x: -x[1]):
    print(f"    {cat:30s}: {count}")

match = all(verify_cats.get(c, 0) == cat_counts.get(c, 0) for c in set(list(cat_counts.keys()) + list(verify_cats.keys())))
if match:
    print("  Category counts: CONSISTENT")
else:
    print("  WARNING: category count mismatch between written data and report!")
    for cat in sorted(set(list(cat_counts.keys()) + list(verify_cats.keys()))):
        exp = cat_counts.get(cat, 0)
        got = verify_cats.get(cat, 0)
        if exp != got:
            print(f"    {cat}: expected {exp}, got {got}")

print("\nDone.")
