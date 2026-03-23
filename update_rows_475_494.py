#!/usr/bin/env python3
"""Update rows 475-494 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "475": {
        "done": "YES",
        "status": "",
        "outreach_subject": "UDP stack usage in verilog-ethernet",
        "outreach_message": (
            "Hey Sina,\n\n"
            "The verilog-ethernet UDP stack is powerful but underdocumented \u2014 figuring "
            "out the AXI-Stream handshake and IP/ARP configuration from RTL alone is "
            "rough. Did you get the UDP TX/RX path working for your robotics "
            "application, and what FPGA target did you use?\n\n"
            "Severin"
        ),
    },
    "476": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "477": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Verilator warnings in verilog-arbiter",
        "outreach_message": (
            "Hey Christian,\n\n"
            "Verilator flags priority logic issues in Verilog arbiters that behavioral "
            "simulators silently accept \u2014 catching these typically requires formal tools "
            "or exhaustive case coverage. With your SRE background, do you apply formal "
            "reasoning to your hardware side projects?\n\n"
            "Severin"
        ),
    },
    "478": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Rotate operator fix in your SV project",
        "outreach_message": (
            "Hey Stephen,\n\n"
            "Rotate operators look simple until bit-width inference and sign-extension "
            "behavior diverge between simulation and synthesis. Was the fix addressing "
            "how the rotate amount gets masked to log2(width) bits, or a more "
            "fundamental implementation issue?\n\n"
            "Severin"
        ),
    },
    "479": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Verilator version requirements for vroom",
        "outreach_message": (
            "Hey Mark,\n\n"
            "Verilator\u2019s newer versions introduced --timing support and deprecated "
            "several legacy options \u2014 the kind of changes that silently break builds "
            "unless explicitly documented. Is vroom using --timing for SystemVerilog "
            "async semantics, or primarily running structural RTL?\n\n"
            "Severin"
        ),
    },
    "480": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Async FIFO high-priority bug fixes",
        "outreach_message": (
            "Hey Haiyang,\n\n"
            "High-priority bugs in async FIFO RTL almost always trace to gray-code "
            "pointer synchronization or reset sequencing across clock domains. Were "
            "the fixes addressing pointer comparison edge cases causing false-full or "
            "false-empty, or was it a reset release ordering issue?\n\n"
            "Severin"
        ),
    },
    "481": {
        "done": "YES",
        "status": "",
        "outreach_subject": "NCS36510 I2C write state machine bug",
        "outreach_message": (
            "Hey Dan,\n\n"
            "The 0x13 special-case in NCS36510 I2C write is a state machine bug that "
            "surfaces only under specific byte sequences \u2014 a missing write++ silently "
            "skips a byte. Did you catch it with a logic analyzer trace or by diffing "
            "the code against the datasheet?\n\n"
            "Severin"
        ),
    },
    "482": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CDC in jfpjc JPEG trimmer",
        "outreach_message": (
            "Hey John,\n\n"
            "Unhandled CDC in an image pipeline trimmer is exactly where metastability "
            "shows up as rare, irreproducible frame artifacts \u2014 the kind of failure "
            "that passes simulation. Does jfpjc connect to your Ka Moamoa mobile "
            "computing research?\n\n"
            "Severin"
        ),
    },
    "483": {
        "done": "YES",
        "status": "",
        "outreach_subject": "LiteX CSR modularization proposal",
        "outreach_message": (
            "Hey George,\n\n"
            "LiteX CSR maps become a regeneration bottleneck at scale \u2014 full map "
            "rebuilds on every peripheral change slow SoC iteration. Are you targeting "
            "a specific peripheral set with this, or designing for general use across "
            "different LiteX boards?\n\n"
            "Severin"
        ),
    },
    "484": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "485": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "486": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CIRCT and your HDL middle layer proposal",
        "outreach_message": (
            "Hey Anton,\n\n"
            "CIRCT \u2014 the LLVM/MLIR-based hardware compiler project \u2014 is now building "
            "essentially what you proposed in f4pga/ideas: an LLVM-like language as an "
            "HDL middle layer. Have you looked at it since filing that issue, and does "
            "it match what you had in mind?\n\n"
            "Severin"
        ),
    },
    "487": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "488": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "489": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "490": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "491": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "492": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "493": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "494": {
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
        continue
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
