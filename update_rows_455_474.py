#!/usr/bin/env python3
"""Update rows 455-474 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "455": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AXI per-ID completion queue ordering rules",
        "outreach_message": (
            "Hey Damien,\n\n"
            "AXI per-ID queues enforce in-order completion within each ID while allowing "
            "different IDs to reorder \u2014 without them, a reordering interconnect silently "
            "violates the spec for same-ID issuers. Was the root cause interconnect-side "
            "or a master assuming globally ordered completions?\n\n"
            "Severin"
        ),
    },
    "456": {
        "done": "YES",
        "status": "",
        "outreach_subject": "PTE read timing fix on Nexys A7 FPGA",
        "outreach_message": (
            "Hey Micha\u0142,\n\n"
            "BRAM-backed page tables introduce read latency that stalls the hardware "
            "walker \u2014 a common failure mode on FPGA MMUs where timing differs from the "
            "DRAM model. Was the Nexys A7 fix a timing issue in the walker pipeline, or "
            "a structural addressing problem?\n\n"
            "Severin"
        ),
    },
    "457": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "458": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "459": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Vivado 2020.1 elaboration crash behavior",
        "outreach_message": (
            "Hey Kawazome,\n\n"
            "Vivado 2020.1 tightened elaboration in ways that crash without pointing at "
            "the offending construct \u2014 code clean in 2019.x broke silently. Did the crash "
            "trace to a specific RTL pattern, or did it surface during IP integration?\n\n"
            "Severin"
        ),
    },
    "460": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "461": {
        "done": "YES",
        "status": "",
        "outreach_subject": "IODDR_STYLE removal from ssio_sdr_in",
        "outreach_message": (
            "Hey Lucas,\n\n"
            "Removing IODDR_STYLE lets the tool infer the IODDR primitive rather than "
            "hard-instantiating it \u2014 synthesis may choose different variants across device "
            "families. Does Clash\u2019s I/O abstraction handle SDR inference transparently, "
            "or does it still require per-target annotation?\n\n"
            "Severin"
        ),
    },
    "462": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "463": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "464": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "465": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "466": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Metrics DSim support in verification flow",
        "outreach_message": (
            "Hey Taichi,\n\n"
            "DSim\u2019s DPI-C and VPI support lags behind local simulators \u2014 HPC IP with C "
            "behavioral models often needs adjustments that aren\u2019t obvious until the run "
            "fails. At pezy-computing, does your flow use DPI-C for cycle-accurate models, "
            "or is DSim purely for SV regression?\n\n"
            "Severin"
        ),
    },
    "467": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AC bit result in SUBB instruction",
        "outreach_message": (
            "Hey Jos\u00e9,\n\n"
            "The AC flag in SUBB reflects borrow from bit 3 to bit 4, not the MSB \u2014 the "
            "8080 manual is ambiguous on direction, so most implementations get it subtly "
            "wrong. Was the bug in the borrow direction, or in DAA behavior reading AC "
            "afterward?\n\n"
            "Severin"
        ),
    },
    "468": {
        "done": "YES",
        "status": "",
        "outreach_subject": "RTL correction for Yosys synthesis compatibility",
        "outreach_message": (
            "Hey Jonathan,\n\n"
            "Yosys rejects patterns that Vivado silently accepts \u2014 multi-driven nets and "
            "certain generate scopes pass commercial elaboration but halt Yosys synthesis. "
            "Was the correction structural RTL changes or synthesis attribute adjustments?\n\n"
            "Severin"
        ),
    },
    "469": {
        "done": "YES",
        "status": "",
        "outreach_subject": "RTL folder exclusion for broadcast IP scanning",
        "outreach_message": (
            "Hey Nitheesh,\n\n"
            "Folder exclusion in RTL scanners typically targets third-party IP that floods "
            "false positives. At NEP Group, is the scanner catching CDC violations in "
            "broadcast hardware, or used mainly for lint-style quality gates?\n\n"
            "Severin"
        ),
    },
    "470": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "471": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "472": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "473": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Byte and half-word write fix in RISC-V core",
        "outreach_message": (
            "Hey Graeme,\n\n"
            "Byte and half-word write bugs in RISC-V usually trace to byte-enable "
            "masking \u2014 wrong mask computation writes a full word with only target lanes "
            "active, silently corrupting adjacent bytes. Was the issue in the bus fabric "
            "strobe logic or the CPU-side enable generation?\n\n"
            "Severin"
        ),
    },
    "474": {
        "done": "YES",
        "status": "",
        "outreach_subject": "First formal property findings",
        "outreach_message": (
            "Hey Angelo,\n\n"
            "Formal verification shifts discovery from corner-case simulation to proof of "
            "absence \u2014 but the first property set usually exposes implicit RTL assumptions "
            "about reset or enable sequencing. What was the first property that formal "
            "flagged that simulation had missed?\n\n"
            "Severin"
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
