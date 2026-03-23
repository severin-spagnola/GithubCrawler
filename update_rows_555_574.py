#!/usr/bin/env python3
"""Update rows 555-574 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "555": {
        "done": "YES",
        "status": "",
        "outreach_subject": "HasRocketTiles decoupling and BOOM integration",
        "outreach_message": (
            "Hey Andrew,\n\n"
            "Decoupling Rocket-specific assumptions from HasRocketTiles in #1463 "
            "let BOOM reuse the integration layer without forking \u2014 the moment "
            "Rocket Chip became a multi-core platform rather than just a Rocket "
            "vehicle. Was BOOM already in scope, or did it emerge afterward?\n\n"
            "Severin"
        ),
    },
    "556": {
        "done": "YES",
        "status": "",
        "outreach_subject": "dummy_signal removal and initial block migration in Migen",
        "outreach_message": (
            "Hey David,\n\n"
            "PR #127 closes the Migen sim/synthesis gap \u2014 X-state during "
            "simulation masked reset behavior that synthesis would define. "
            "Pre-compiled modules from the old backend needed cache invalidation "
            "to pick up the new Verilog output. Did that regeneration happen "
            "cleanly across users?\n\n"
            "Severin"
        ),
    },
    "557": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "558": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "559": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "560": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "561": {
        "done": "YES",
        "status": "",
        "outreach_subject": "BBF operator discovery and Verilator build coupling in dsptools",
        "outreach_message": (
            "Hey Stevo,\n\n"
            "Automating BBF operator inclusion in Verilator means the build step "
            "needs to know which BlackBox Verilog files the design uses after "
            "FIRRTL compilation \u2014 a coupling problem. Did the fix hook into "
            "FIRRTL annotation output, or track BBF dependencies at the Chisel "
            "module level?\n\n"
            "Severin"
        ),
    },
    "562": {
        "done": "YES",
        "status": "",
        "outreach_subject": "UART failure root cause in MBus ICE debugger",
        "outreach_message": (
            "Hey Ben,\n\n"
            "A UART failure in the ICE debugger is self-concealing \u2014 if the "
            "debug path is broken, you lose the visibility to diagnose what "
            "broke it. How did you close that loop: logic analyzer on the "
            "physical lines, or was there a secondary diagnostic path in the "
            "ICE firmware?\n\n"
            "Severin"
        ),
    },
    "563": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "564": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "565": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "566": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "567": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "568": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "569": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "570": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "571": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "572": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "573": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "574": {
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
