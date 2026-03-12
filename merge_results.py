import os
import sys
import csv
import glob

# ---------------------------------------------------------------------------
# Field definitions
# ---------------------------------------------------------------------------

BASE_FIELDS = [
    "query", "source_type", "repo", "repo_name", "org", "org_type",
    "contributor_count", "language", "stars", "username", "display_name",
    "email", "company", "bio", "location", "github_profile", "linkedin",
    "twitter", "blog", "commit_message", "commit_url", "commit_date",
]

OUTPUT_FIELDS = BASE_FIELDS + ["priority_score", "priority"]

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

HARDWARE_LANG_KEYWORDS = {"vhdl", "verilog", "systemverilog"}
SYSTEMS_LANG_KEYWORDS = {"c", "c++", "cpp", "rust"}
MODERN_LANG_KEYWORDS = {"typescript", "python"}

QUERY_BOOST_PHRASES = {
    "merge conflict",
    "breaking change",
    "port mismatch",
    "synthesis error",
}


def score_lead(lead):
    score = 0

    # contributor_count bands
    try:
        cc = int(lead.get("contributor_count") or 0)
    except (ValueError, TypeError):
        cc = 0

    if 5 <= cc <= 50:
        score += 3
    elif 3 <= cc <= 4:
        score += 1
    elif 51 <= cc <= 200:
        score += 2

    # profile completeness
    if lead.get("email", "").strip():
        score += 2
    if lead.get("linkedin", "").strip():
        score += 2
    if lead.get("company", "").strip():
        score += 1

    # org type
    if (lead.get("org_type") or "").strip() == "Organization":
        score += 2

    # language bonus
    lang = (lead.get("language") or "").strip().lower()
    if lang in HARDWARE_LANG_KEYWORDS:
        score += 3
    elif lang in SYSTEMS_LANG_KEYWORDS:
        score += 2
    elif lang in MODERN_LANG_KEYWORDS:
        score += 1

    # query content bonus
    query_lower = (lead.get("query") or "").lower()
    if any(phrase in query_lower for phrase in QUERY_BOOST_PHRASES):
        score += 2

    return score


def priority_label(score):
    if score >= 8:
        return "P1"
    if score >= 5:
        return "P2"
    return "P3"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python merge_results.py <results_dir> <output_csv>", file=sys.stderr)
        sys.exit(1)

    results_dir = sys.argv[1]
    output_path = sys.argv[2]

    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    if not csv_files:
        print(f"ERROR: no *.csv files found in {results_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Merge Results ===")
    print(f"  Input dir : {results_dir}")
    print(f"  CSV files : {len(csv_files)}")
    print(f"  Output    : {output_path}")
    print()

    # ------------------------------------------------------------------
    # Read & deduplicate
    # ------------------------------------------------------------------
    seen = {}  # (username, repo) -> row dict
    total_read = 0

    for path in sorted(csv_files):
        file_count = 0
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_read += 1
                    file_count += 1
                    key = (row.get("username", ""), row.get("repo", ""))
                    if key not in seen:
                        seen[key] = row
        except Exception as exc:
            print(f"  [warn] could not read {path}: {exc}")
            continue
        print(f"  read {file_count:>5} rows from {os.path.basename(path)}")

    unique_leads = list(seen.values())
    print(f"\n  total read   : {total_read}")
    print(f"  unique leads : {len(unique_leads)}  "
          f"(deduplicated {total_read - len(unique_leads)})\n")

    # ------------------------------------------------------------------
    # Score, label, sort
    # ------------------------------------------------------------------
    for lead in unique_leads:
        s = score_lead(lead)
        lead["priority_score"] = s
        lead["priority"] = priority_label(s)

    unique_leads.sort(key=lambda r: int(r["priority_score"]), reverse=True)

    # ------------------------------------------------------------------
    # Write output
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for lead in unique_leads:
            writer.writerow({field: lead.get(field, "") for field in OUTPUT_FIELDS})

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    p1 = sum(1 for l in unique_leads if l["priority"] == "P1")
    p2 = sum(1 for l in unique_leads if l["priority"] == "P2")
    p3 = sum(1 for l in unique_leads if l["priority"] == "P3")

    print(f"=== Summary ===")
    print(f"  Total leads : {len(unique_leads)}")
    print(f"  P1 (>= 8)   : {p1}")
    print(f"  P2 (>= 5)   : {p2}")
    print(f"  P3 (< 5)    : {p3}")
    print(f"\n  Written to  : {output_path}")


if __name__ == "__main__":
    main()
