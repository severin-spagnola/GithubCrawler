#!/usr/bin/env python3
"""Update rows 405–414 in fpga_outreach_leads.csv in-place."""

import csv
import os
import tempfile

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "405": {
        "done": "YES",
        "outreach_subject": "DSim support in Ibex and Silimate's EDA AI",
        "outreach_message": "Hey Akash,\n\nFixing DSim support in Ibex suggests Silimate is targeting simulator-agnostic flows — or using Ibex as a benchmark for AI-assisted debugging. What does the hardest bottleneck look like for AI-assisted chip debugging: catching RTL logic bugs, timing closure, or something further down the flow like DRC sign-off?\n\nSeverin",
    },
    "406": {
        "done": "YES",
        "outreach_subject": "Merge queue CI for OpenTitan's verification scale",
        "outreach_message": "Hey Gary,\n\nMerge queues in OpenTitan's CI hit a verification integrity problem that smaller projects don't face — when batching commits, a test result that passed in one queue state doesn't necessarily hold after a different batch lands first. How did you handle the case where merge queue batching invalidates results that depend on exact commit ordering?\n\nSeverin",
    },
    "407": {
        "done": "YES",
        "outreach_subject": "HMAC key vault slot exposure in Caliptra",
        "outreach_message": "Hey Jeff,\n\nWithout KV slot tagging, HMAC becomes an extraction oracle — firmware can feed chosen inputs through an HMAC keyed with a protected slot and observe outputs, which is a known key derivation attack path in HSMs. Is the threat model here compromised firmware specifically, or hardware-enforced key isolation that holds even if the attestation identity key is exposed?\n\nSeverin",
    },
    "408": {
        "done": "YES",
        "outreach_subject": "OpenTitan PWM smoke test failure root cause",
        "outreach_message": "Hey Christoph,\n\nA failing PWM smoke test looks identical whether the peripheral RTL changed or the test expectation drifted — the failure mode doesn't tell you which side is wrong. Was the failure caused by a change in the PWM RTL, or was the test itself out of sync with the current spec?\n\nSeverin",
    },
    "409": {
        "done": "YES",
        "outreach_subject": "RAT synthesis in Quartus for Ozone out-of-order processor",
        "outreach_message": "Hey Karmanyaah,\n\nGetting a register alias table through Quartus synthesis is where most student out-of-order implementations hit their first hard constraint — the multi-port lookup the RAT needs either bloats to unusable LUT counts or needs structural changes that break the microarchitecture. What ISA does Ozone target, and how far along is the pipeline beyond the RAT?\n\nSeverin",
    },
    "410": {
        "done": "YES",
        "outreach_subject": "Caliptra RTL signal names in integration docs",
        "outreach_message": "Hey Steven,\n\nCaliptra integration docs that reference abstract names instead of RTL signal names create silent mapping errors — and for a hardware root of trust, an integrator building confidential computing attestation needs exact register and signal names to write correct firmware. How does Caliptra fit into Nvidia's broader confidential computing stack?\n\nSeverin",
    },
    "411": {
        "done": "YES",
        "outreach_subject": "Learn FPGA Programming testbench fix",
        "outreach_message": "Hey Niyazi,\n\nBroken testbenches in educational FPGA repos cause more damage than broken testbenches in production code — a student can't distinguish their own mistake from a faulty reference, which means they doubt their understanding before they doubt the book. What was the specific issue in the tb.sv you fixed?\n\nSeverin",
    },
    "412": {
        "done": "YES",
        "outreach_subject": "ZPUFlex decodeControl sensitivity list fix",
        "outreach_message": "Hey Ingo,\n\nAn incomplete sensitivity list in a VHDL decode process causes simulation to treat it as edge-triggered when synthesis infers combinational logic — the synthesized hardware is correct but simulation diverges, so testbenches pass while the actual device behaves differently. Did the ZPUFlex fix change what the synthesized hardware did, or was it purely a simulation correctness issue?\n\nSeverin",
    },
    "413": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "414": {
        "done": "YES",
        "outreach_subject": "TRNG architecture for Betrusted SoC",
        "outreach_message": "Hey Arnaud,\n\nRing-oscillator TRNGs are the default FPGA choice but also the most well-characterized attack target — digital post-processing can mask low entropy if the oscillator sources are correlated. What TRNG approach were you evaluating for Betrusted — ring oscillator jitter, metastability-based, or something else?\n\nSeverin",
    },
}

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
