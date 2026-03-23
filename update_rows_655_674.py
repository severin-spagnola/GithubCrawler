#!/usr/bin/env python3
"""Update rows 655-674 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "655": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "656": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "657": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "658": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "659": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "660": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "661": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "662": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "663": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Streak reset simplification tradeoffs in karman",
        "outreach_message": (
            "Hey Suryateja,\n\n"
            "Simplifying streak resets risks masking timezone edge "
            "cases \u2014 a user crossing midnight in their local zone might "
            "see a false reset if retrieval and reset share one code "
            "path. Did the fix unify both operations, or just trim "
            "redundant queries?\n\n"
            "Severin"
        ),
    },
    "664": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "665": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "666": {
        "done": "YES",
        "status": "",
        "outreach_subject": "BIO reset compat divergence in wolfSSL OpenSSL layer",
        "outreach_message": (
            "Hey Roy,\n\n"
            "BIO compat layers tend to diverge on retry semantics "
            "\u2014 OpenSSL BIO_read sets retry flags on -1, but if "
            "wolfSSL doesn\u2019t mirror that state machine, callers "
            "looping on BIO_should_retry will spin or bail. Was the "
            "fix aligning retry flags or the error code mapping?\n\n"
            "Severin"
        ),
    },
    "667": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Worker logic fixes and frame pipeline state in DeepLabCut",
        "outreach_message": (
            "Hey Cyril,\n\n"
            "Worker fixes in a live inference GUI can hide a subtlety "
            "\u2014 if the worker resets mid-frame, stale keypoints display "
            "on the new frame until the next inference cycle. Were the "
            "fixes around worker lifecycle or the data handoff between "
            "worker and renderer?\n\n"
            "Severin"
        ),
    },
    "668": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "669": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "670": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Active/standby line logic on board v3 in PacSatSW",
        "outreach_message": (
            "Hey Corey,\n\n"
            "Active/standby logic that shifts across board revisions "
            "can break failover if the new pin mapping isn\u2019t reflected "
            "in the watchdog reset path \u2014 standby thinks it promoted "
            "but hardware never switched. Was the v3 fix a pin "
            "reassignment or a protocol-level change?\n\n"
            "Severin"
        ),
    },
    "671": {
        "done": "YES",
        "status": "",
        "outreach_subject": "reloadMessages and reset regression in CopilotKit",
        "outreach_message": (
            "Hey Jordan,\n\n"
            "When reloadMessages and reset both stop working, it often "
            "points to a shared state subscription that was refactored "
            "upstream \u2014 the hook still fires but the store it reads "
            "from was replaced. Did this surface after a specific "
            "version bump, or was it a gradual regression?\n\n"
            "Severin"
        ),
    },
    "672": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Silent --phase parameter drop in cadre reset",
        "outreach_message": (
            "Hey Jacob,\n\n"
            "A silently ignored CLI flag is one of the harder bugs to "
            "catch \u2014 users think they\u2019re doing a scoped reset but get "
            "a full rollback to phase 0. Was --phase being parsed but "
            "not forwarded to the reset handler, or dropped at the "
            "arg-parsing layer?\n\n"
            "Severin"
        ),
    },
    "673": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Graph zoom reset on editor resize in studio-json-schema",
        "outreach_message": (
            "Hey Aditya,\n\n"
            "Resetting zoom on every panel resize can fight the user "
            "\u2014 if they\u2019ve zoomed into a deeply nested schema node, a "
            "panel drag snaps them back to the root view. Was the fix "
            "gating the reset on a specific resize threshold, or "
            "preserving the viewport entirely?\n\n"
            "Severin"
        ),
    },
    "674": {
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
