#!/usr/bin/env python3
"""Update rows 815-834 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "815": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "816": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AI search depth parity: simulation vs live game divergence",
        "outreach_message": (
            "Hey Mihnea,\n\n"
            "Using different AI search depths between simulation and "
            "live game creates a training-reality gap \u2014 the agent "
            "optimizes against a policy it never actually faces. Was "
            "the mismatch a depth parameter not being shared, or the "
            "simulation running a different search budget?\n\nSeverin"
        ),
    },
    "817": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "818": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "819": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "820": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "821": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "822": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Scalability test failures in simulation ecology: emergent network coupling",
        "outreach_message": (
            "Hey Daniel,\n\n"
            "Scalability test failures in active inference networks "
            "often expose emergent coupling \u2014 agents independent at "
            "small N become correlated through shared generative "
            "models at scale. Was the failure a timeout or a state "
            "consistency issue that only appears at higher node "
            "counts?\n\nSeverin"
        ),
    },
    "823": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "824": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "825": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "826": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Model architecture mismatch: training vs inference config in simulation",
        "outreach_message": (
            "Hey Winston,\n\n"
            "Architecture mismatches between training and inference "
            "configs are invisible until simulation \u2014 the model "
            "loads but silently produces garbage because weight "
            "shapes are subtly wrong. Was the mismatch a layer "
            "ordering issue, or a hidden size inconsistency?"
            "\n\nSeverin"
        ),
    },
    "827": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Sensor unit_id string-to-null: downstream strict equality fallthrough",
        "outreach_message": (
            "Hey YongHwan,\n\n"
            "Changing unit_id from string to null fixes the "
            "falsy-check path, but any consumer doing strict "
            "equality against an empty string now falls through "
            "instead of matching. Was the bug an empty-string "
            "sentinel that null replaced, or a missing-sensor case?"
            "\n\nSeverin"
        ),
    },
    "828": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "829": {
        "done": "YES",
        "status": "",
        "outreach_subject": "NB08 round-trip K mismatch: kinematic convention in remap loop",
        "outreach_message": (
            "Hey Maurilio,\n\n"
            "Round-trip K mismatches in kinematic simulation usually "
            "mean forward and inverse models don\u2019t share the same "
            "joint-offset convention. Did the remap loop cell "
            "correct a frame definition mismatch, or compensate for "
            "different K parameterizations between directions?"
            "\n\nSeverin"
        ),
    },
    "830": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "831": {
        "done": "YES",
        "status": "",
        "outreach_subject": "sessionStorage key mismatch: orphaned session forensic artifacts",
        "outreach_message": (
            "Hey Albert,\n\n"
            "Orphaned sessionStorage keys from a mismatch persist "
            "across navigation and appear as active sessions in "
            "browser forensic artifacts. Was the collision between "
            "tabs, or a key rename that wasn\u2019t propagated to all "
            "read paths?\n\nSeverin"
        ),
    },
    "832": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "833": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "834": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
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
