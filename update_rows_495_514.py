#!/usr/bin/env python3
"""Update rows 495-514 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "495": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "496": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "497": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Node architecture docs in bittide-hardware",
        "outreach_message": (
            "Hey Nathan,\n\n"
            "Bittide\u2019s elastic node architecture is novel \u2014 clock "
            "domain flexibility through elastic buffers instead of rigid "
            "synchronous interconnect is hard to explain without the full "
            "timing model. What parts of the node architecture were most "
            "underdocumented before your update?\n\n"
            "Severin"
        ),
    },
    "498": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "499": {
        "done": "YES",
        "status": "",
        "outreach_subject": "GPIB applet for Glasgow",
        "outreach_message": (
            "Hey Aaron,\n\n"
            "GPIB\u2019s three-wire handshake and controller-in-charge state "
            "machine make a clean applet interface tricky \u2014 especially "
            "mapping Talk/Listen addressing to Glasgow\u2019s bitbang-friendly "
            "FPGA architecture. What test equipment are you targeting "
            "with this applet?\n\n"
            "Severin"
        ),
    },
    "500": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "501": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Pulse sampling issues in FluxEngine",
        "outreach_message": (
            "Hey David,\n\n"
            "Dropped pulses during floppy sampling usually trace to USB "
            "bulk transfer latency or timer capture overflow on the PSoC "
            "\u2014 the gap between consecutive flux transitions can be shorter "
            "than the sampling pipeline\u2019s worst-case path. Was this a "
            "capture-side or host-side issue?\n\n"
            "Severin"
        ),
    },
    "502": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "503": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "504": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "505": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "506": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "507": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "508": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "509": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "510": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "511": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "512": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "513": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "514": {
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
