#!/usr/bin/env python3
"""Update rows 595-614 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "595": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Blocking settimeofday resets on ESP32 weather monitor",
        "outreach_message": (
            "Hey Arunkumar,\n\n"
            "Blocking settimeofday when NTP isn't ready is the right call — an "
            "errant SNTP callback can zero out your RTC and corrupt all downstream "
            "timestamps. Was the spurious reset in the SNTP callback, or something "
            "earlier in the boot sequence?\n\n"
            "Severin"
        ),
    },
    "596": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "597": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "598": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "599": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "600": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "601": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "602": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Git reset for path sync in IndiVoice Colab workflow",
        "outreach_message": (
            "Hey Purvansh,\n\n"
            "Path sync errors in Colab-based ASR pipelines usually hit after a "
            "runtime reconnect when the working directory diverges from the cloned "
            "repo root. Was the git reset guarding against a dirty state from a "
            "failed run, or a Colab Drive mount path mismatch?\n\n"
            "Severin"
        ),
    },
    "603": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "604": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Fingerprint reset on casting start in wod-wiki",
        "outreach_message": (
            "Hey Sergei,\n\n"
            "Structural fingerprinting to diff exercise blocks without re-rendering "
            "is clever — resetting it on cast start prevents the receiver from "
            "applying a stale diff that never recovers. Was the fingerprint the only "
            "shared state needing a clear on the cast handshake?\n\n"
            "Severin"
        ),
    },
    "605": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Timezone streak reset fix in Market-Rover backend",
        "outreach_message": (
            "Hey Sankar,\n\n"
            "Timezone-shifted midnight boundaries that silently drop streaks only "
            "surface when someone in a +5 offset complains at 12:01 AM. Was the fix "
            "normalizing to UTC at the evaluation point, or storing the user's local "
            "offset at action time?\n\n"
            "Severin"
        ),
    },
    "606": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "607": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Stats reset and test logic fix in ProxySQL",
        "outreach_message": (
            "Hey Miro,\n\n"
            "False-passing tests in a production query router can mask real "
            "regressions in connection pooling or query rule accounting. Was the "
            "test asserting against stale stats counters that hadn't been flushed, "
            "or was the reset not propagating across all hostgroups?\n\n"
            "Severin"
        ),
    },
    "608": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Obsidian-style forgot password UI in StreamHub",
        "outreach_message": (
            "Hey Protyush,\n\n"
            "An Obsidian-style forgot password UI suggests rethinking the default "
            "reset UX — the email reset fix likely means the link was validating "
            "before the new password was set. Is this for StreamHub, or something "
            "you're refining at Hasura?\n\n"
            "Severin"
        ),
    },
    "609": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "610": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "611": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Async autosuggest ghost text cleanup in zsh-conf",
        "outreach_message": (
            "Hey Aditya,\n\n"
            "Transient prompt swaps and async autosuggestion clearing race when the "
            "async worker returns after the prompt has already transitioned. With "
            "138 stars on zsh-conf, were you seeing ghost text on fast keystrokes, "
            "or specifically when the transient prompt triggered a redraw?\n\n"
            "Severin"
        ),
    },
    "612": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "613": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "614": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Turn race and trick-lead reset in six-poker",
        "outreach_message": (
            "Hey Hao,\n\n"
            "A race between single-player turn progression and trick-lead reset "
            "usually means trick completion and dealer assignment are firing in the "
            "same event loop tick. Was it a timing issue in your state machine, or "
            "two handlers both trying to advance the turn?\n\n"
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
