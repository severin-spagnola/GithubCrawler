#!/usr/bin/env python3
"""Update rows 635-654 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "635": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "636": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "637": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "638": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "639": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "640": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "641": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Redundant state resets in FANS CourseManager",
        "outreach_message": (
            "Hey,\n\n"
            "Redundant resets in CourseManager can silently diverge what ATC "
            "sees from actual flight plan state \u2014 the second reset clobbers "
            "the first\u2019s intended state rather than resolving both. Was the "
            "auto-open fix related, or a separate behavior that surfaced in "
            "the same pass?\n\n"
            "Severin"
        ),
    },
    "642": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "643": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "644": {
        "done": "YES",
        "status": "",
        "outreach_subject": "vLLM host binding state on provider switch in LightRAG",
        "outreach_message": (
            "Hey Daniel,\n\n"
            "Host binding that doesn\u2019t reset on provider switch means local "
            "mode silently inherits the remote endpoint \u2014 requests succeed "
            "but hit the wrong backend. Did the fix need to track provider "
            "identity per-request, or was a single previous-state flag "
            "enough?\n\n"
            "Severin"
        ),
    },
    "645": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "646": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "647": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "648": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Reset-password prerender fix via token-to-component move",
        "outreach_message": (
            "Hey Suman,\n\n"
            "Moving token logic to the component layer bypasses prerender, "
            "but it also means the token is never available during SSR \u2014 if "
            "any server-side middleware expects it, those paths break "
            "silently. Was the prerender error happening at build time or "
            "at request time?\n\n"
            "Severin"
        ),
    },
    "649": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "650": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "651": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "652": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "653": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "654": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Reset UI logic in token-beam Aseprite plugin",
        "outreach_message": (
            "Hey David,\n\n"
            "In a design token plugin, a reset that clears UI state but not "
            "the underlying token store can leave the canvas out of sync "
            "with what the renderer sees \u2014 a silent divergence until the "
            "next reload. Was the reset scoped to UI only, or does it also "
            "flush the token graph?\n\n"
            "Severin"
        ),
    },
}

# Verify all constraints before applying
for row_num, update in UPDATES.items():
    msg = update.get("outreach_message", "")
    subj = update.get("outreach_subject", "")
    if update.get("status") == "SKIP":
        assert msg == "", f"Row {row_num}: SKIP row must have empty message"
        assert subj == "", f"Row {row_num}: SKIP row must have empty subject"
        print(f"Row {row_num}: SKIP — OK")
    else:
        # Check message length
        msg_len = len(msg)
        if msg_len > 300:
            raise ValueError(f"Row {row_num}: message is {msg_len} chars, exceeds 300 limit")
        # Check subject length
        subj_len = len(subj)
        if subj_len > 80:
            raise ValueError(f"Row {row_num}: subject is {subj_len} chars, exceeds 80 limit")
        # Check no 'I' opener
        body = msg.split("\n\n")[1] if "\n\n" in msg else msg
        if body.lstrip().startswith("I ") or body.lstrip().startswith("I'"):
            raise ValueError(f"Row {row_num}: message starts with 'I'")
        print(f"Row {row_num}: subject={subj_len} chars, message={msg_len} chars — OK")

# Read all rows
with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# Apply updates
updated_count = 0
for row in rows:
    row_num = row["number"]
    if row_num in UPDATES:
        update = UPDATES[row_num]
        for key, value in update.items():
            row[key] = value
        updated_count += 1

print(f"\nUpdated {updated_count} rows")

# Write back
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

print("Done. CSV written with QUOTE_ALL.")
