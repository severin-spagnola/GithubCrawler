#!/usr/bin/env python3
"""Update rows 535-554 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "535": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "536": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "537": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "538": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Per-bin phase offset correction in souk PSB",
        "outreach_message": (
            "Hey Sam,\n\n"
            "Per-bin phase offsets in a PSB are deterministic \u2014 filter-design "
            "artifacts, not noise \u2014 so correcting them requires per-bin lookup "
            "rather than a single phase rotation. Did the fix live in the PSB "
            "itself or in downstream detector readout?\n\n"
            "Severin"
        ),
    },
    "539": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "540": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "541": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "542": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "543": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "544": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "545": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "546": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "547": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "548": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "549": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "550": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "551": {
        "done": "YES",
        "status": "",
        "outreach_subject": "FPGA driver rewrite for Kaman eddy current sensor (AMDC)",
        "outreach_message": (
            "Hey Nathan,\n\n"
            "Kaman eddy current sensors have a nonlinear output that needs "
            "calibration \u2014 rewriting the FPGA driver at the AMDC layer raises "
            "whether the linearization sits in the FPGA fabric or gets pushed "
            "to the host. Where did the rewrite land on that tradeoff?\n\n"
            "Severin"
        ),
    },
    "552": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Trigger-source logging in RNO-G RADIANT firmware",
        "outreach_message": (
            "Hey Steffen,\n\n"
            "In RNO-G multi-board setup, wrong trigger-source logging corrupts "
            "coincidence filtering between RADIANTs during event reconstruction "
            "\u2014 not just bookkeeping. Was it a register readout ordering issue, "
            "or did the firmware mispack the trigger ID into the event header?\n\n"
            "Severin"
        ),
    },
    "553": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "554": {
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
