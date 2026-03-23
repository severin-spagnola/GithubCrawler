#!/usr/bin/env python3
"""Update rows 615-634 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "615": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Stale frame_step inheritance in BlenderJPS workers",
        "outreach_message": (
            "Hey Fabian,\n\n"
            "When frame_step persists after stream teardown, workers picking up "
            "the next job inherit a non-1 step and silently skip frames \u2014 no "
            "error, just gaps. Was this surfacing as missing frames in the "
            "output, or causing workers to loop incorrectly?\n\n"
            "Severin"
        ),
    },
    "616": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "617": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "618": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "619": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "620": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "621": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "622": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "623": {
        "done": "YES",
        "status": "",
        "outreach_subject": "OV7670 PCLK/SDRAM/VGA CDC on Artix 7",
        "outreach_message": (
            "Hey Raj,\n\n"
            "SDRAM refresh during active video is the usual culprit for "
            "horizontal tear in OV7670 pipelines \u2014 the burst controller "
            "doesn't know you're mid-scanline. Did the VGA FSM fix gate "
            "refresh requests during display, or restructure the frame "
            "buffer access pattern?\n\n"
            "Severin"
        ),
    },
    "624": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "625": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "626": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Chip-8 timer state in fruitchip reset",
        "outreach_message": (
            "Hey Ivan,\n\n"
            "In a Chip-8 emulator, missing the delay or sound timer from "
            "reset means ROMs that poll them before writing see non-zero "
            "garbage \u2014 behavior that only surfaces on specific titles. Was "
            "the bug causing hangs, or wrong audio/timing?\n\n"
            "Severin"
        ),
    },
    "627": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "628": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "629": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "630": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "631": {
        "done": "YES",
        "status": "",
        "outreach_subject": "LLM plan review testing in llmutils",
        "outreach_message": (
            "Hey Daniel,\n\n"
            "Removing tests from an LLM planning view is often right \u2014 "
            "snapshot tests for non-deterministic output create maintenance "
            "overhead without catching real regressions. At DeviceFlow, are "
            "you seeing the same mismatch between standard test patterns "
            "and agentic workflow validation?\n\n"
            "Severin"
        ),
    },
    "632": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "633": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "634": {
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
