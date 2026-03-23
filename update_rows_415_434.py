#!/usr/bin/env python3
"""Update rows 415-434 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "415": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CLINT/PLIC clock domain isolation in Rocket Chip",
        "outreach_message": (
            "Hey Jerry,\n\n"
            "Routing CLINT and PLIC interrupts through separate clock domains in Rocket Chip "
            "means the CDC path directly affects interrupt latency guarantees. Was the original "
            "crossing causing metastability on FPGA, or was this caught through timing analysis?\n\n"
            "Severin"
        ),
    },
    "416": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CDC in valentyusb eptri USB core",
        "outreach_message": (
            "Hey Sean,\n\n"
            "Clock domain crossing in a USB PHY is unforgiving — one metastable flip and the host "
            "resets the device. The eptri CDC patch was marked untested at the time — did you "
            "validate it against real host controllers, or did the Fomu community catch edge cases "
            "in the field?\n\n"
            "Severin"
        ),
    },
    "417": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CDC fix in pymosa MAPS detector readout",
        "outreach_message": (
            "Hey Jens,\n\n"
            "A CDC bug in MAPS readout can corrupt hit data silently — the detector keeps running "
            "but physics analysis downstream gets garbage. Was the pymosa fix triggered by data "
            "corruption during beam tests, or did simulation catch the crossing violation first?\n\n"
            "Severin"
        ),
    },
    "418": {
        "done": "YES",
        "status": "",
        "outreach_subject": "PokeReg CDC violation in CMV12000 S7 PHY",
        "outreach_message": (
            "Hey Thomas,\n\n"
            "A CDC violation in PokeReg means sensor register writes could glitch during "
            "configuration — intermittent corruption that mimics a sensor fault. Was this showing "
            "up as pixel artifacts on the AXIOM camera, or did timing analysis flag it before real "
            "frames were affected?\n\n"
            "Severin"
        ),
    },
    "419": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CDC stability in VMM readout firmware at CERN",
        "outreach_message": (
            "Hey Paris,\n\n"
            "CDC instability in VMM readout can cause trigger-correlated data drops that mimic "
            "detector inefficiency — hard to separate from physics. Were the stability fixes "
            "driven by data quality issues during beam runs, or caught during commissioning with "
            "test pulses?\n\n"
            "Severin"
        ),
    },
    "420": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SDRAM fast input registers in PCXT MiSTer core",
        "outreach_message": (
            "Hey Aitor,\n\n"
            "Fast input registers for SDRAM in the PCXT MiSTer core buy real timing margin "
            "on the 8088 bus interface, and removing unnecessary clock domain logic simplifies "
            "the design. After these changes, did you see measurable improvement in SDRAM "
            "reliability at speed?\n\n"
            "Severin"
        ),
    },
    "421": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "422": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AXI bus snooping for print_stat in BSG manycore",
        "outreach_message": (
            "Hey Borna,\n\n"
            "Snooping loader_link for print_stat on the AXI-to-MCL bridge avoids adding a "
            "dedicated debug side channel. Did this pattern generalize to other packet types in "
            "the BSG manycore, or was print_stat uniquely suited to bus snooping over a dedicated "
            "path?\n\n"
            "Severin"
        ),
    },
    "423": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Multi-clock domain partitioning in Chisel2",
        "outreach_message": (
            "Hey Jim,\n\n"
            "Partitioning a Chisel2 design across clock domains at the top-level dot file means "
            "CDC boundaries become a graph-cut problem. Did the monolithic cpp fallback exist "
            "because multi-clock partitioning broke Verilator compatibility?\n\n"
            "Severin"
        ),
    },
    "424": {
        "done": "YES",
        "status": "",
        "outreach_subject": "pixhdl signed/unsigned type support gap",
        "outreach_message": (
            "Hey Damien,\n\n"
            "The signed/unsigned gap in pixhdl means any image processing pipeline needing "
            "negative coefficients — like convolution kernels — won't synthesize correctly from "
            "pixel art. Are you looking at this from a DSP perspective, or more general pixel "
            "manipulation?\n\n"
            "Severin"
        ),
    },
    "425": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "426": {
        "done": "YES",
        "status": "",
        "outreach_subject": "OSVVM testbench refactoring for SoC verification",
        "outreach_message": (
            "Hey Amine,\n\n"
            "Refactoring OSVVM testbenches well is underrated — most SoC teams inherit messy "
            "verification environments and just bolt on more tests. Were you restructuring the "
            "template to support a specific SoC verification workflow, or making it more reusable "
            "across different FPGA projects?\n\n"
            "Severin"
        ),
    },
    "427": {
        "done": "YES",
        "status": "",
        "outreach_subject": "MRISC32 video timing mismatch between tb and RTL",
        "outreach_message": (
            "Hey,\n\n"
            "The timing mismatch between video_tb.vhd and mc1.vhd in MRISC32 means the "
            "testbench was validating against wrong timing — simulation passes but real hardware "
            "could show tearing or blanking. Was this caught on actual FPGA output or through "
            "waveform inspection?\n\n"
            "Severin"
        ),
    },
    "428": {
        "done": "YES",
        "status": "",
        "outreach_subject": "verilog-ethernet port to KR260",
        "outreach_message": (
            "Hey Victor,\n\n"
            "Porting verilog-ethernet to the KR260 involves bridging the AXI-Stream Ethernet "
            "MAC with the PS-PL interconnect and the SFP+ transceiver — nontrivial given the "
            "Kria's clock architecture. Are you targeting bare-metal networking or integrating "
            "with a Linux-side network stack?\n\n"
            "Severin"
        ),
    },
    "429": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Quartus out-of-box compilation for md5cracker",
        "outreach_message": (
            "Hey Alexandre,\n\n"
            "Quartus compilation issues on Verilog projects often come down to missing pin "
            "assignments or IP core version mismatches that the original environment handled "
            "implicitly. Did the md5cracker fail at synthesis or during fitter placement?\n\n"
            "Severin"
        ),
    },
    "430": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AXIS DownSample line buffer empty edge case",
        "outreach_message": (
            "Hey Bowei,\n\n"
            "The DownSample AXIS fix when the line buffer is empty suggests the module was "
            "outputting stale data on buffer underrun — a classic streaming pipeline edge case. "
            "Was this triggered by a specific frame size that drained the buffer mid-line, or a "
            "reset-sequence corner case?\n\n"
            "Severin"
        ),
    },
    "431": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Illegal GTP clock connections in SCROD Ethernet",
        "outreach_message": (
            "Hey,\n\n"
            "Illegal GTP clock connections can pass synthesis but fail in hardware — Xilinx GTP "
            "transceivers have strict clock routing rules that Vivado doesn't always enforce at "
            "the RTL level. Did this cause link-up failures on actual hardware, or was it caught "
            "during bitstream generation?\n\n"
            "Severin"
        ),
    },
    "432": {
        "done": "YES",
        "status": "",
        "outreach_subject": "MARK-II custom CPU from ISA to physical board",
        "outreach_message": (
            "Hey Vladislav,\n\n"
            "Taking MARK-II from custom ISA to a physical board means bus timing and IO "
            "constraints become real problems the toolchain can't abstract away. What drove "
            "designing a new instruction set rather than extending RISC-V — a specific "
            "architectural tradeoff you wanted to explore?\n\n"
            "Severin"
        ),
    },
    "433": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "434": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Top module naming in Tiny Tapeout testbench",
        "outreach_message": (
            "Hey Anton,\n\n"
            "A wrong top module name in the testbench means simulation runs against the wrong "
            "hierarchy — tests pass but don't exercise the tapeout design. Was this caught during "
            "the Tiny Tapeout submission flow, or did the CI miss it because the sim still "
            "elaborated without error?\n\n"
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
