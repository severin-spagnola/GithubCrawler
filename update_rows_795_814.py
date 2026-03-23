#!/usr/bin/env python3
"""Update rows 795-814 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "795": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Worktree session handling: root vs path keying in slayzone",
        "outreach_message": (
            "Hey Marco,\n\n"
            "Worktree session bugs that also affect cleanup usually "
            "mean session state is keyed on repo root instead of "
            "worktree path \u2014 root-keyed state mutates the wrong "
            "session when two worktrees coexist. Was the bug stale "
            "handles surviving cleanup, or cross-worktree state "
            "collisions?\n\nSeverin"
        ),
    },
    "796": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Dynamic reset time coupling consistency in MOOSE",
        "outreach_message": (
            "Hey Zachary,\n\n"
            "Dynamic time resets in MOOSE must propagate to every "
            "coupled physics \u2014 if one MultiApp resets while "
            "another doesn't, the residual evaluates across "
            "inconsistent time states. Did the fix push reset "
            "through the MultiApp hierarchy, or add a "
            "synchronization barrier?\n\nSeverin"
        ),
    },
    "797": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Controlled cursor and selection sync in MetaMask bridge input",
        "outreach_message": (
            "Hey Bryan,\n\n"
            "Controlled cursor in React Native requires text and "
            "selection state to update atomically \u2014 if the bridge "
            "input reformats on value change, selection lags and "
            "the cursor jumps. Did you track cursor position via a "
            "ref, or explicitly pass the selection back on each "
            "update?\n\nSeverin"
        ),
    },
    "798": {
        "done": "YES",
        "status": "",
        "outreach_subject": "NEORV32 on XC6SLX9: LUT budget at minimum config",
        "outreach_message": (
            "Hey Alirio,\n\n"
            "At absolute minimum config \u2014 RV32I only, no debug "
            "unit, IMEM as BRAM \u2014 NEORV32 barely clears the "
            "XC6SLX9 LUT budget, leaving almost nothing for "
            "peripherals. Did you use BRAM for instruction memory "
            "to free up LUTs, or switch to a smaller core?"
            "\n\nSeverin"
        ),
    },
    "799": {
        "done": "YES",
        "status": "",
        "outreach_subject": "GHDL vs Vivado BRAM: RTL vs primitive read-during-write semantics",
        "outreach_message": (
            "Hey Carl-Johannes,\n\n"
            "GHDL models read-during-write as generic RTL; Vivado "
            "models the BRAM's READ_FIRST/WRITE_FIRST mode \u2014 "
            "they will always disagree unless your VHDL explicitly "
            "encodes the access policy. Did the fix use a BRAM "
            "attribute, or restructure to avoid same-cycle "
            "collisions?\n\nSeverin"
        ),
    },
    "800": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "801": {
        "done": "YES",
        "status": "",
        "outreach_subject": "GateMate IO primitive requirement for keyboard ports in openCologne",
        "outreach_message": (
            "Hey Goran,\n\n"
            "GateMate's toolchain needs explicit CC_IBUF/CC_OBUF "
            "on IO ports rather than inferring them \u2014 plain "
            "logic driving a top-level port skips the IO cell "
            "wrapper and usually errors at placement. Was Error 10 "
            "the missing IO primitive, or a constraint pin "
            "assignment?\n\nSeverin"
        ),
    },
    "802": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Inference shape fallback masking checkpoint weight errors",
        "outreach_message": (
            "Hey Hi\u1ec3n,\n\n"
            "A fallback on shape mismatch prevents chart crashes, "
            "but silently hides cases where the model loaded wrong "
            "weights \u2014 the shape error might be a checkpoint "
            "mismatch, not just a batch size issue. Does the "
            "fallback log the mismatch, or just substitute zeros?"
            "\n\nSeverin"
        ),
    },
    "803": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "804": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Float32Array/Wasm worker boundary type loss in openclo",
        "outreach_message": (
            "Hey Samuel,\n\n"
            "Float32Array passed through a transferable worker "
            "boundary loses its type if the worker reconstructs "
            "from raw ArrayBuffer \u2014 SharedArrayBuffer avoids the "
            "copy but needs COOP/COEP headers. Did you marshal "
            "state per frame, or share the buffer directly?"
            "\n\nSeverin"
        ),
    },
    "805": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "806": {
        "done": "YES",
        "status": "",
        "outreach_subject": "RangeCamera non-organized point cloud color index mapping",
        "outreach_message": (
            "Hey Shin'ichiro,\n\n"
            "Non-organized point clouds drop the image-coordinate "
            "index used to map RGB to depth \u2014 sequential color "
            "assignment misaligns the moment any point is culled "
            "or reordered. Was the mismatch an index offset into "
            "the color buffer, or a stride error?\n\nSeverin"
        ),
    },
    "807": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "808": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "809": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Simu5G MEC uninitialized vars: debug vs release init semantics",
        "outreach_message": (
            "Hey Andras,\n\n"
            "Debug allocators zero-initialize memory; release "
            "allocators leave garbage \u2014 uninitialized vars that "
            "only affect fingerprints in DEBUG mode are taking "
            "different simulation branches on that zero value. Was "
            "the fix explicit init, or dead-code removal?"
            "\n\nSeverin"
        ),
    },
    "810": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "811": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "812": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "813": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SLAM mid-simulation init: EKF covariance P0 vs dead-reckoning pose",
        "outreach_message": (
            "Hey Yongkyun,\n\n"
            "Initializing EKF with the dead-reckoning pose fixes "
            "state mismatch, but P0 also needs to reflect "
            "accumulated drift uncertainty \u2014 a tight default P0 "
            "will reject sensor updates that disagree with the "
            "pose. Did you set P0 based on elapsed time, or use a "
            "fixed default?\n\nSeverin"
        ),
    },
    "814": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Optical-only Celeritas: decoupled EM and optical physics stacks",
        "outreach_message": (
            "Hey Amanda,\n\n"
            "Optical-only mode needs optical photons to bypass the "
            "EM step limiter \u2014 Cherenkov and EM tracks share "
            "the same transport loop in Celeritas. Does the "
            "optical core params carry a separate process manager, "
            "or disable EM steps via a flag?\n\nSeverin"
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
