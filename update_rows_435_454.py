#!/usr/bin/env python3
"""Update rows 435-454 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "435": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Replication operator syntax fix in HDLBits Verilog",
        "outreach_message": (
            "Hey Shiva,\n\n"
            "The concatenation braces in Verilog's replication operator interact in ways that "
            "silently produce the wrong bit-width \u2014 no error, just wrong bits routed. Was the bug "
            "a synthesis width mismatch, or a simulation case where outputs looked valid but "
            "used the wrong slice?\n\n"
            "Severin"
        ),
    },
    "436": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Control matrix issues in Neptune CPU",
        "outreach_message": (
            "Hey Shreyas,\n\n"
            "A control matrix bug hits every instruction sharing a control bit simultaneously "
            "\u2014 not one failing test, but correlated failures across an instruction group. Was "
            "the issue in the microcode encoding itself, or in how control signals propagated "
            "through pipeline registers?\n\n"
            "Severin"
        ),
    },
    "437": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "438": {
        "done": "YES",
        "status": "",
        "outreach_subject": "ISERDESE2 reset sequence in OpenHBMC",
        "outreach_message": (
            "Hey Mohammad,\n\n"
            "ISERDESE2 reset is poorly documented \u2014 get the sequence wrong and the "
            "deserializer locks onto the wrong bit alignment without flagging an error. Did the "
            "issue manifest as corrupted data reads, or was the ISERDES producing no valid "
            "output at all?\n\n"
            "Severin"
        ),
    },
    "439": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SVO raycaster compatibility with Xilinx ISE 10.1",
        "outreach_message": (
            "Hey David,\n\n"
            "Xilinx ISE 10.1 had fragile support for parameterized generate blocks in complex "
            "procedural Verilog \u2014 the toolchain would silently discard synthesis paths rather "
            "than error. Did this cause functional differences between simulation and "
            "bitstream, or fail at elaboration?\n\n"
            "Severin"
        ),
    },
    "440": {
        "done": "YES",
        "status": "",
        "outreach_subject": "RTLGen macro-hardening with nangate45",
        "outreach_message": (
            "Hey Yohei,\n\n"
            "Macro-hardening Layer1 seed candidates against nangate45 surfaces placement and "
            "routing issues before the RTL is committed \u2014 issues that behavioral simulation "
            "never catches. Are you evaluating RTLGen output across multiple PDKs, or is "
            "nangate45 the primary target for this pass?\n\n"
            "Severin"
        ),
    },
    "441": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "442": {
        "done": "YES",
        "status": "",
        "outreach_subject": "TED chip colour palette accuracy in Plus/4 FPGA core",
        "outreach_message": (
            "Hey Ramon,\n\n"
            "The TED chip colour palette used analog DAC levels that don't map cleanly to "
            "standard RGB encoding, and Commodore's documentation on the exact values was "
            "sparse. Did you derive the palette from measured hardware output, or from "
            "community-documented values?\n\n"
            "Severin"
        ),
    },
    "443": {
        "done": "YES",
        "status": "",
        "outreach_subject": "PnR fix on AES-128 FPGA accelerator",
        "outreach_message": (
            "Hey,\n\n"
            "PnR failures on a crypto accelerator usually come down to S-box critical path "
            "timing or routing congestion from the wide key-expansion buses. Was the breakage "
            "from a tool constraint format change, or did the updated synthesizer change "
            "placement enough to require re-floorplanning?\n\n"
            "Severin"
        ),
    },
    "444": {
        "done": "YES",
        "status": "",
        "outreach_subject": "BLDC speed control module in SystemVerilog",
        "outreach_message": (
            "Hey Sergei,\n\n"
            "Implementing BLDC speed control in SystemVerilog after server-side async C++ "
            "means the feedback loop timing is now a hardware constraint rather than a "
            "scheduler decision. Did you implement closed-loop PID with the speed module, or "
            "open-loop PWM for now?\n\n"
            "Severin"
        ),
    },
    "445": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "446": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Metastability handling in HardwareModules",
        "outreach_message": (
            "Hey Sonya,\n\n"
            "An async input without a synchronizer fails probabilistically \u2014 and the failure "
            "rate shifts with temperature and voltage in ways bench testing misses. Does this "
            "connect to signal acquisition timing in your neural instrumentation work at Allen "
            "Institute?\n\n"
            "Severin"
        ),
    },
    "447": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Unpacked array concatenation fix for Vivado in xr-series",
        "outreach_message": (
            "Hey Dennis,\n\n"
            "Vivado rejects unpacked array concatenation that Questa and Cadence accept \u2014 it "
            "enforces a stricter SystemVerilog interpretation that most teams discover the hard "
            "way. Was this blocking synthesis of the xsip module, or only showing up in "
            "simulation?\n\n"
            "Severin"
        ),
    },
    "448": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Cadence parameter ordering in Ibex super system",
        "outreach_message": (
            "Hey Sundar,\n\n"
            "Cadence enforces parameter declaration ordering that VCS and Verilator silently "
            "waive \u2014 code that passes both tools fails in Cadence without a clear spec "
            "violation. How often do you hit these vendor-specific SystemVerilog "
            "interpretation gaps in your verification flows?\n\n"
            "Severin"
        ),
    },
    "449": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CWE-1239 hardware register clearing in SystemVerilog SHA256",
        "outreach_message": (
            "Hey M2kar,\n\n"
            "CWE-1239 in RTL is almost never audited \u2014 open-source crypto rarely clears "
            "sensitive registers on reset, and the vulnerability is invisible until netlist "
            "inspection. How do you approach systematic hardware CWE discovery at ISCAS \u2014 "
            "static analysis or formal property checking?\n\n"
            "Severin"
        ),
    },
    "450": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AES S-box implementation in SystemVerilog",
        "outreach_message": (
            "Hey Ryan,\n\n"
            "The AES S-box is where composite-field arithmetic wins at high frequencies \u2014 "
            "LUT-based lookup hits routing bottlenecks that arithmetic factoring distributes "
            "across stages. Did you use ROM lookup or composite-field arithmetic, and how did "
            "that affect timing closure?\n\n"
            "Severin"
        ),
    },
    "451": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Rescaled multiply module in PHIvs metrics pipeline",
        "outreach_message": (
            "Hey Abraham,\n\n"
            "A rescaled multiply in the metrics pipeline suggests post-multiply scaling to "
            "prevent accumulator overflow \u2014 the question is how many bits you're dropping and "
            "whether edge cases need saturation. Did the bit-width budget work out cleanly, or "
            "did you add saturation logic?\n\n"
            "Severin"
        ),
    },
    "452": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Instruction memory bug fix in RISC-V SoC",
        "outreach_message": (
            "Hey Matias,\n\n"
            "Instruction memory bugs in a RISC-V SoC are often read-before-write hazards \u2014 a "
            "fetch that reads before the write completes looks correct in simulation but fails "
            "on real memory latency. Was this a combinational read hazard, or something in the "
            "memory-mapped access path?\n\n"
            "Severin"
        ),
    },
    "453": {
        "done": "YES",
        "status": "",
        "outreach_subject": "BMU verification RTL file connections",
        "outreach_message": (
            "Hey Osaid,\n\n"
            "Mismatched port connections when wiring RTL files fail silently \u2014 the testbench "
            "elaborates but drives signals that go nowhere. Were you integrating the branch "
            "management unit against a full RISC-V decode stage, or isolating it with "
            "constrained random stimulus first?\n\n"
            "Severin"
        ),
    },
    "454": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Removing defines from parameterized up-down counter",
        "outreach_message": (
            "Hey Saransh,\n\n"
            "`define-based widths create silent scoping issues \u2014 tool invocations can pick up "
            "stale defines without warning when a codebase spans multiple projects. At Google, "
            "do parameterized modules go through lint and CDC checks in a way that "
            "`define-based ones bypass?\n\n"
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
