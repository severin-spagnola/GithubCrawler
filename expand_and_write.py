#!/usr/bin/env python3
"""Expand outreach CSV with remaining enriched leads, then write outreach for next 150."""

import csv

ENRICHED = "fpga_enriched.csv"
OUTREACH = "fpga_outreach_leads.csv"

# Read existing
with open(OUTREACH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    existing = list(reader)

existing_usernames = set(r.get("username", "") for r in existing)
print(f"Existing rows: {len(existing)}")

# Read all enriched and grab new unique leads from row 3200+
with open(ENRICHED, newline="", encoding="utf-8") as f:
    enriched = list(csv.DictReader(f))

new_leads = []
for row in enriched[3200:]:
    has_email = bool((row.get("email") or "").strip())
    has_linkedin = bool((row.get("linkedin") or "").strip())
    username = row.get("username", "")
    if (has_email or has_linkedin) and username not in existing_usernames:
        existing_usernames.add(username)
        channel = "email" if has_email else "linkedin"
        row["done"] = "NO"
        row["outreach_channel"] = channel
        row["outreach_subject"] = ""
        row["outreach_message"] = ""
        new_leads.append(row)

# Combine and renumber
combined = existing + new_leads
for i, r in enumerate(combined):
    r["number"] = i + 1

# Write
with open(OUTREACH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(combined)

total = len(combined)
email_count = sum(1 for r in combined if bool((r.get("email") or "").strip()))
linkedin_count = sum(1 for r in combined if bool((r.get("linkedin") or "").strip()))
both_count = sum(1 for r in combined if bool((r.get("email") or "").strip()) and bool((r.get("linkedin") or "").strip()))

print(f"New leads added: {len(new_leads)}")
print(f"Total rows: {total}")
print(f"Email: {email_count}, LinkedIn: {linkedin_count}, Both: {both_count}")

# Print leads 51-200 for message writing
print("\n\n=== LEADS NEEDING OUTREACH (51-200) ===\n")
count = 0
for i, r in enumerate(combined):
    if (r.get("outreach_message") or "").strip():
        continue
    if count >= 150:
        break
    print(f"=== ROW {i} | {r.get('username','')} ===")
    print(f"display_name: {r.get('display_name','')}")
    print(f"email: {r.get('email','')}")
    print(f"linkedin: {r.get('linkedin','')}")
    print(f"company: {r.get('company','')}")
    print(f"bio: {r.get('bio','')}")
    print(f"repo: {r.get('repo','')}")
    print(f"language: {r.get('language','')}")
    print(f"stars: {r.get('stars','')}")
    print(f"contributors: {r.get('contributor_count','')}")
    print(f"location: {r.get('location','')}")
    print(f"channel: {r.get('outreach_channel','')}")
    print()
    count += 1
