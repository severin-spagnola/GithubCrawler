#!/usr/bin/env python3
"""Trim outreach_message for rows 395, 400, 412 to ≤300 chars."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "395": {
        "outreach_message": "Hey Enrico,\n\nCircumSpect on a compact in-order core like CROC differs from a superscalar — fewer microarchitectural side channels but also fewer places to add masking without destroying area efficiency. What leakage model does CircumSpect target for CROC — power, timing, or both?\n\nSeverin",
    },
    "400": {
        "outreach_message": "Hey Bekzat,\n\nQuesta and VCS diverge on X-propagation and SystemVerilog scheduling — both are spec-compliant but make different choices that expose assumptions baked into one simulator. Were the Ibex failures in specific categories like CSR or debug mode, or scattered across the regression?\n\nSeverin",
    },
    "412": {
        "outreach_message": "Hey Ingo,\n\nAn incomplete sensitivity list in a VHDL decode process makes simulation treat it as edge-triggered while synthesis infers combinational logic — hardware is correct but simulation diverges. Did the ZPUFlex fix change synthesized behavior, or was it purely a sim correctness issue?\n\nSeverin",
    },
}

# Verify lengths before applying
for row_num, update in UPDATES.items():
    msg = update["outreach_message"]
    length = len(msg)
    status = "OK" if length <= 300 else "OVER"
    print(f"Row {row_num}: {length} chars [{status}]")
    if length > 300:
        raise ValueError(f"Row {row_num} message is {length} chars, exceeds 300 limit")

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

print(f"Updated {updated_count} rows")

# Write back
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

print("Done. CSV written with QUOTE_ALL.")
