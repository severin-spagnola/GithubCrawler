#!/usr/bin/env python3
"""Expand outreach CSV: add next 500 filtered leads from enriched, dedupe."""

import csv

ENRICHED = "fpga_enriched.csv"
OUTREACH = "fpga_outreach_leads.csv"
SKIP_ROWS = 1000  # already processed first 1000 of enriched
NEW_LEADS_TARGET = 500

# Read existing outreach leads
with open(OUTREACH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    outreach_fields = reader.fieldnames
    existing = list(reader)

print(f"Existing outreach rows: {len(existing)}")

# Track existing by (username, repo, email) to dedupe
existing_keys = set()
for r in existing:
    key = (r.get("username", ""), r.get("repo", ""), r.get("email", ""))
    existing_keys.add(key)

# Read enriched starting from row SKIP_ROWS, collect next 500 with email/linkedin
new_leads = []
with open(ENRICHED, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i < SKIP_ROWS:
            continue
        if len(new_leads) >= NEW_LEADS_TARGET:
            break
        has_email = bool((row.get("email") or "").strip())
        has_linkedin = bool((row.get("linkedin") or "").strip())
        if has_email or has_linkedin:
            key = (row.get("username", ""), row.get("repo", ""), row.get("email", ""))
            if key not in existing_keys:
                existing_keys.add(key)
                channel = "email" if has_email else "linkedin"
                row["outreach_channel"] = channel
                row["outreach_subject"] = ""
                row["outreach_message"] = ""
                new_leads.append(row)

print(f"New leads found: {len(new_leads)}")

# Also dedupe existing rows
seen = set()
deduped_existing = []
dupes_removed = 0
for r in existing:
    key = (r.get("username", ""), r.get("repo", ""), r.get("email", ""))
    if key not in seen:
        seen.add(key)
        deduped_existing.append(r)
    else:
        dupes_removed += 1

print(f"Duplicates removed from existing: {dupes_removed}")

# Combine and renumber
combined = deduped_existing + new_leads
for i, row in enumerate(combined):
    row["number"] = i + 1

# Write
with open(OUTREACH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=outreach_fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(combined)

# Stats
email_count = sum(1 for r in combined if bool((r.get("email") or "").strip()))
linkedin_count = sum(1 for r in combined if bool((r.get("linkedin") or "").strip()))
both_count = sum(1 for r in combined if bool((r.get("email") or "").strip()) and bool((r.get("linkedin") or "").strip()))
outreach_written = sum(1 for r in combined if (r.get("outreach_message") or "").strip())

print(f"\n{'='*60}")
print(f"Final row count: {len(combined)}")
print(f"  From original batch (first 1000): {len(deduped_existing)}")
print(f"  New from rows 1001+: {len(new_leads)}")
print(f"  With email: {email_count}")
print(f"  With linkedin: {linkedin_count}")
print(f"  With both: {both_count}")
print(f"  With outreach written: {outreach_written}")
print(f"{'='*60}")
