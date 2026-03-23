#!/usr/bin/env python3
"""Update rows 575-594 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "575": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "576": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "577": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "578": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Speech state reset in Textream NotchOverlayController",
        "outreach_message": (
            "Hey Fatih,\n\n"
            "When a notch overlay teleprompter doesn't reset speech state between "
            "sessions, the next run inherits partial transcriptions from the previous. "
            "Was the stale reference in NotchOverlayController, or was MarqueeTextView "
            "not signaling teardown to the recognizer?\n\n"
            "Severin"
        ),
    },
    "579": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "580": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "581": {
        "done": "YES",
        "status": "",
        "outreach_subject": "tmux dynamic background reset in .zshrc",
        "outreach_message": (
            "Hey Rob,\n\n"
            "A dynamic background in tmux that doesn't reset cleanly usually means "
            "precmd/preexec hooks fire but the terminal sequence doesn't land on "
            "session detach. Is this for color-coding panes by environment at "
            "Google Cloud, or something else?\n\n"
            "Severin"
        ),
    },
    "582": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "583": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "584": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "585": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "586": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "587": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "588": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "589": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "590": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "591": {
        "done": "YES",
        "status": "",
        "outreach_subject": "WiFi reset state machine on ESP32-S3",
        "outreach_message": (
            "Hey zfkun,\n\n"
            "ESP32 WiFi reconnection state machines are hard when STA disconnect "
            "events and provisioning fallback can race each other. Was the root issue "
            "a race between the event handler and the reset call, or a disconnect "
            "reason code the state machine wasn't accounting for?\n\n"
            "Severin"
        ),
    },
    "592": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "593": {
        "done": "YES",
        "status": "",
        "outreach_subject": "F8 scoring reset bug in contest_trainer",
        "outreach_message": (
            "Hey Chad,\n\n"
            "Scoring bugs in a live ham radio contest trainer are the worst kind "
            "\u2014 the log looks clean in the moment but the uploaded result disagrees. "
            "Was F8 state persisting across QSO boundaries, or was the reset firing "
            "at the wrong point in the exchange sequence?\n\n"
            "Severin"
        ),
    },
    "594": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Collator externals reset on genesis in Tycho",
        "outreach_message": (
            "Hey SmaGMan,\n\n"
            "If externals aren't cleared on genesis, the collator includes pre-genesis "
            "messages in the first block and the node silently diverges. Did the test "
            "verify that in-flight externals drain before the genesis transition, or "
            "does it focus on post-reset consistency?\n\n"
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
