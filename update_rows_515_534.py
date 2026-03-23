#!/usr/bin/env python3
"""Update rows 515-534 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "515": {
        "done": "YES",
        "status": "",
        "outreach_subject": "EMA window tradeoff in BCH difficulty algorithm",
        "outreach_message": (
            "Hey zawy,\n\n"
            "The EMA window that minimizes selfish-mining incentive and the "
            "one that minimizes honest-miner variance under sudden hashrate "
            "drops differ \u2014 forcing a policy choice about which attack to "
            "optimize against. In the BCH EMA proposal, how did you settle "
            "on the window size?\n\n"
            "Severin"
        ),
    },
    "516": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Incremental build restructuring in fiction (cda-tum)",
        "outreach_message": (
            "Hey Marcel,\n\n"
            "Fiction's deep C++ template hierarchies make it ambiguous whether "
            "the CLI restructuring decoupled the layout algorithm specializations "
            "from the frontend or just reorganized headers. Does touching a "
            "placement heuristic now avoid recompiling the full CLI?\n\n"
            "Severin"
        ),
    },
    "517": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "518": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "519": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "520": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "521": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "522": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "523": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "524": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "525": {
        "done": "YES",
        "status": "",
        "outreach_subject": "inout support for VivadoConstraintWriter in SpinalHDL",
        "outreach_message": (
            "Hey Craig,\n\n"
            "Before your fix, SpinalHDL's VivadoConstraintWriter silently "
            "skipped bidirectional ports \u2014 FPGA designs using tristate buffers "
            "or DDR interfaces would have had unconstrained pins that Vivado "
            "couldn't properly assign to I/O banks. What design exposed this "
            "gap?\n\n"
            "Severin"
        ),
    },
    "526": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "527": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "528": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Sparse dispatch sink in TENNLab FPGA neuromorphic framework",
        "outreach_message": (
            "Hey Keegan,\n\n"
            "Cutting fanout with a sparse dispatch sink can move the critical "
            "path from the routing fabric to dispatch arbitration \u2014 trading one "
            "bottleneck for another. After the refactor, did the sparse sink "
            "let you fit larger neuron populations, or was the win mostly in "
            "clock frequency?\n\n"
            "Severin"
        ),
    },
    "529": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "530": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "531": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "532": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "533": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "534": {
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
