#!/usr/bin/env python3
"""Update rows 655-674 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "655": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Maintenance cancellation reset edge cases in AsenovoBackend",
        "outreach_message": (
            "Hey Sadik,\n\n"
            "Nullable plannedDate on cancellation can trip downstream "
            "queries that assume non-null when status != NOT_PLANNED "
            "\u2014 a filter like `WHERE plannedDate > NOW()` silently drops "
            "cancelled rows instead of including them. Did the fix add "
            "a null-check path or a sentinel date?\n\n"
            "Severin"
        ),
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
        "status": "",
        "outreach_subject": "TCP reset rate percentage shift in sharkclaw severity logic",
        "outreach_message": (
            "Hey David,\n\n"
            "Switching TCP resets to percentage-based rates changes "
            "severity boundary meaning \u2014 a 5% threshold on a low-traffic "
            "link fires on a handful of packets while the same threshold "
            "stays silent on a saturated one. Was the severity update "
            "tied to absolute minimums or purely relative?\n\n"
            "Severin"
        ),
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
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "664": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Connection reset handling tradeoffs in kungfu",
        "outreach_message": (
            "Hey yinheli,\n\n"
            "Connection reset fixes in proxy layers have a subtle "
            "tradeoff \u2014 retrying on RST can mask upstream failures, but "
            "propagating it immediately drops in-flight streams that "
            "could have landed on a healthy backend. Did the fix add "
            "retry logic or just clean up the teardown path?\n\n"
            "Severin"
        ),
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
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
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
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
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
