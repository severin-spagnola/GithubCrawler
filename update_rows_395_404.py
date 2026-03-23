#!/usr/bin/env python3
"""Update rows 395-404 and 413 in fpga_outreach_leads.csv."""

import csv
import os

CSV_PATH = "fpga_outreach_leads.csv"
TMP_PATH = CSV_PATH + ".tmp"

UPDATES = {
    395: {
        "done": "YES",
        "outreach_subject": "CircumSpect leakage model on PULP CROC",
        "outreach_message": "Hey Enrico,\n\nCircumSpect on a compact in-order core like CROC is a different problem from a superscalar — fewer microarchitectural side channels but also fewer places to add masking countermeasures without destroying area efficiency. What leakage model does CircumSpect target for CROC — power side channels, timing-based leakage, or both?\n\nSeverin",
    },
    396: {
        "done": "YES",
        "outreach_subject": "FPU reg0 debug view in Core-V-MCU",
        "outreach_message": "Hey Jeremy,\n\nA frozen FPU register 0 in the debug unit means any GDB session doing floating-point bring-up is working with wrong state — the kind of bug that makes you doubt your toolchain before doubting the hardware. Did this surface during Embecosm's Core-V-MCU bring-up work, or through the OpenHW verification flow?\n\nSeverin",
    },
    397: {
        "done": "YES",
        "outreach_subject": "Three code bugs in pzbcm — systematic audit?",
        "outreach_message": "Hey Josh,\n\nThree bugs caught in pzbcm through a single PR reads more like a structured audit than incidental discovery — the kind of coverage that only comes from running formal tools or a systematic manual review. Were they LEC failures, synthesis-unfriendly constructs, or functional logic errors?\n\nSeverin",
    },
    398: {
        "done": "YES",
        "outreach_subject": "Multi-FPGA enumeration gap in OPAE",
        "outreach_message": "Hey Yifan,\n\nOPAE\u2019s software stack assumed single-FPGA deployments long after the hardware made multi-device setups practical — multi-device enumeration and routing were never first-class citizens in the building blocks. Coming from deep learning inference at Nvidia, were you hitting this while prototyping an FPGA inference cluster, or a different use case?\n\nSeverin",
    },
    399: {
        "done": "YES",
        "outreach_subject": "vmax/vmin op mask fix in vicuna2 vector decoder",
        "outreach_message": "Hey Efe,\n\nWrong vmax/vmin operation masks pass scalar test suites and only surface when vectorized code exercises the actual ALU comparison path — exactly the kind of bug that stays invisible until a real workload runs. Were the masks swapped between signed and unsigned variants, or a broader encoding issue across multiple vector compare ops?\n\nSeverin",
    },
    400: {
        "done": "YES",
        "outreach_subject": "Ibex regression failures on Questa",
        "outreach_message": "Hey Bekzat,\n\nQuesta and VCS diverge most on X-propagation and SystemVerilog scheduling semantics — both are spec-compliant but make different choices that expose test assumptions baked into one simulator\u2019s behavior. Were the Ibex failures concentrated in specific categories like CSR tests or debug mode, or scattered randomly across the regression?\n\nSeverin",
    },
    401: {
        "done": "YES",
        "outreach_subject": "Wally development containers for academic courses",
        "outreach_message": "Hey Dogan,\n\nContainerizing Wally means every student gets the same RISC-V toolchain and simulator versions — in a course environment, debugging environment mismatches eats more lab time than the actual assignments. Is this being used for a digital design course at Bo\u011fazi\u00e7i, or mainly for research reproducibility?\n\nSeverin",
    },
    402: {
        "done": "YES",
        "outreach_subject": "VM_CBO RTL fixes in CORE-V Wally",
        "outreach_message": "Hey Muhammad,\n\nCache block operations interacting with virtual memory is where the RISC-V privileged spec leaves the most room for implementation bugs — especially the permission check distinction between CBO.FLUSH and CBO.CLEAN across privilege levels. Were the fixes mostly around the page-fault logic path, or how the cache controller handled the invalidation sequencing?\n\nSeverin",
    },
    403: {
        "done": "YES",
        "outreach_subject": "RISC-V\u2019s role in Tenstorrent\u2019s AI accelerator",
        "outreach_message": "Hey Sharanesh,\n\nTenstorrent is one of the few architectures integrating RISC-V into the compute tile alongside AI cores rather than just using it as a host controller — a bet that RISC-V programmability belongs in the data path, not just the control plane. What does the RISC-V work look like at Tenstorrent — control plane for the AI matmul engines, or more tightly coupled to the tensor compute pipeline?\n\nSeverin",
    },
    404: {
        "done": "YES",
        "outreach_subject": "SHA3 endianness description fix in Caliptra",
        "outreach_message": "Hey Max,\n\nAn endianness mismatch in a root-of-trust\u2019s SHA3 register documentation is security-relevant in a way most doc fixes aren\u2019t — an integrator configuring the wrong byte order gets silently incorrect hashes from hardware they\u2019ve decided to trust. How did you find the discrepancy — integration testing, or reviewing the RDL against the SHA3 spec?\n\nSeverin",
    },
    413: {
        "done": "YES",
        "status": "SKIP",
    },
}

with open(CSV_PATH, "r", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

for row in rows:
    try:
        n = int(row["number"])
    except (ValueError, KeyError):
        continue
    if n in UPDATES:
        for key, val in UPDATES[n].items():
            row[key] = val

with open(TMP_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

os.replace(TMP_PATH, CSV_PATH)
print("Done. Updated rows:", sorted(UPDATES.keys()))
