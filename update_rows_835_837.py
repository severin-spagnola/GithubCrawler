#!/usr/bin/env python3
"""Update rows 835-837 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "176": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "177": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Corundum 100G clock period vs MAC framing alignment",
        "outreach_message": (
            "Hey Mario,\n\n"
            "Changing the clock period on Corundum to close timing can "
            "silently shift the MAC-to-PHY clock ratio \u2014 at 100G the "
            "framing depends on exact cycle relationships that don't "
            "tolerate rounding. Was the clock period change on the "
            "transmit side, receive side, or the core crossbar?"
            "\n\nSeverin"
        ),
    },
    "178": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Microwatt Arty A7: Linux PPC ISA assumptions as hard RTL constraints",
        "outreach_message": (
            "Hey Paul,\n\n"
            "The Linux PowerPC port's assumptions about cache line "
            "sizes and TLB invalidation sequences \u2014 things baked in "
            "when you wrote them \u2014 become hard RTL constraints on "
            "Microwatt that a clean-sheet RISC-V core wouldn't "
            "inherit. Did the Arty A7 work surface any of those "
            "tensions, or was it purely a resource and timing exercise?"
            "\n\nSeverin"
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
