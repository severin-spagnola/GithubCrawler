#!/usr/bin/env python3
"""Update rows 715-734 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "715": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Setup edge cases vs documented onboarding flow in xmtp",
        "outreach_message": (
            "Hey Saul,\n\n"
            "Onboarding docs written post-refinement tend to document "
            "the clean path \u2014 the edge cases that prompted the fix "
            "rarely make it in. Did the flow updates capture the "
            "failure modes, or primarily the happy path?\n\n"
            "Severin"
        ),
    },
    "716": {
        "done": "YES",
        "status": "",
        "outreach_subject": "State transition validation gap in Erlang-to-Python patterns",
        "outreach_message": (
            "Hey Gavin,\n\n"
            "Erlang gen_statem makes invalid transitions explicit \u2014 "
            "migrating that intuition to Python means the gaps tend "
            "to surface late. Was the bug a missing guard or an "
            "implicit transition that looked valid?\n\n"
            "Severin"
        ),
    },
    "717": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Inconsistent validation strength across Sentinel paths",
        "outreach_message": (
            "Hey DaVoe,\n\n"
            "Password validation inconsistency across paths usually "
            "means the strength check lives in more than one place, "
            "and they drifted. Was the root cause duplicated logic, "
            "or a path that bypassed the central validator entirely?\n\n"
            "Severin"
        ),
    },
    "718": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "719": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "720": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Sync source fallback and cursor alignment in envio indexer",
        "outreach_message": (
            "Hey Dmitry,\n\n"
            "Switching back to sync sources as fallback creates a "
            "re-indexing window \u2014 if the cursor doesn\u2019t resume where "
            "the failed async source left off, you get duplicates or "
            "gaps. Did the recovery align cursors before resuming?\n\n"
            "Severin"
        ),
    },
    "721": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "722": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Cumulative commitment accounting at mid-period upgrades in Flexprice",
        "outreach_message": (
            "Hey Pratham,\n\n"
            "Cumulative commitment logic breaks at upgrade "
            "boundaries \u2014 usage accrued under the old commitment "
            "tier can get double-counted when a subscription upgrades "
            "mid-period. Did the implementation handle prorated "
            "resets, or treat upgrades as period boundaries?\n\n"
            "Severin"
        ),
    },
    "723": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Signal handler conflict between test framework and blocking buzzer",
        "outreach_message": (
            "Hey Aven,\n\n"
            "Test frameworks install signal handlers that compete "
            "with blocking hardware calls \u2014 the buzzer crash on test "
            "framework setup is a classic symptom. Was it a SIGALRM "
            "conflict, or a threading model mismatch with the "
            "blocking I/O?\n\n"
            "Severin"
        ),
    },
    "724": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Accepted flag reset atomicity for WiiU request retry",
        "outreach_message": (
            "Hey Criso,\n\n"
            "Resetting an accepted flag to allow resending has a "
            "race \u2014 if the flag clears before the request state "
            "resets, a retry looks like a new request to the "
            "receiver. Was the fix an atomic reset, or a sequencing "
            "change on the send path?\n\n"
            "Severin"
        ),
    },
    "725": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "726": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Retry counter reset timing relative to epoch validation",
        "outreach_message": (
            "Hey Albert,\n\n"
            "Resetting the retry counter on epoch completion rather "
            "than on validation success masks mid-epoch failures \u2014 "
            "the counter looks clean even if a retry happened inside "
            "the epoch. Was the reset gated on epoch finish or the "
            "validation step?\n\n"
            "Severin"
        ),
    },
    "727": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Selection UI gap during keyboard style changes in tldraw",
        "outreach_message": (
            "Hey Steve,\n\n"
            "Hiding selection UI during keyboard style changes "
            "creates an asymmetry \u2014 remote collaborators see the "
            "style update without the selection context that gives "
            "local users visual confirmation. Was the hide intentional "
            "to cut noise, or a side effect of the shortcut path?\n\n"
            "Severin"
        ),
    },
    "728": {
        "done": "YES",
        "status": "",
        "outreach_subject": "failurerate.Tracker interface boundary in FSMv2 extraction",
        "outreach_message": (
            "Hey Jeremy,\n\n"
            "Extracting a failure rate tracker as a standalone "
            "package means its internal state can diverge from the "
            "FSM's view if they don't share the same event source. "
            "Did the extraction define the interface boundary first, "
            "or derive it from FSM state?\n\n"
            "Severin"
        ),
    },
    "729": {
        "done": "YES",
        "status": "",
        "outreach_subject": "num_images persistence across EPICS AD triggers in ophyd",
        "outreach_message": (
            "Hey Thomas,\n\n"
            "Not resetting num_images per trigger means counts "
            "persist across calls \u2014 correct for multi-trigger "
            "sequences but wrong for modes that expect a fresh count "
            "each time. Was this gated on acquisition mode, or a "
            "general policy change?\n\n"
            "Severin"
        ),
    },
    "730": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Disk-based prompt customization write-access attack surface",
        "outreach_message": (
            "Hey Peter,\n\n"
            "Disk-based prompts with user customization create a "
            "write-access attack surface \u2014 any process that can write "
            "to that directory can inject into the prompt without "
            "going through the UI. Was the storage path scoped to "
            "user-owned directories, or is there an integrity check?\n\n"
            "Severin"
        ),
    },
    "731": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "732": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Low-voltage reboot hang after App config on RAK WisMeshTag",
        "outreach_message": (
            "Hey Ethac,\n\n"
            "Low-voltage hangs after App config usually mean radio "
            "init fires before the supply stabilizes \u2014 brownout "
            "detection won't catch it if the threshold is set below "
            "the radio's minimum operating voltage. Was the fix a "
            "voltage gate, or a config persistence change?\n\n"
            "Severin"
        ),
    },
    "733": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "734": {
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
