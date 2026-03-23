#!/usr/bin/env python3
"""Update rows 675-694 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "675": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Stale waiting state after completed turns in t3code",
        "outreach_message": (
            "Hey Fabian,\n\n"
            "Clearing waiting state on turn completion has a race \u2014 if "
            "the server streams a partial response and the client marks "
            "the turn done before the final chunk arrives, the UI resets "
            "mid-render. Did the fix gate on stream close or on a "
            "completion flag from the backend?\n\n"
            "Severin"
        ),
    },
    "676": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Dead retry wiring in ChatController send path",
        "outreach_message": (
            "Hey Saurav,\n\n"
            "Dead retry code that\u2019s wired up but never invoked tends to "
            "rot \u2014 when it finally fires, timeouts and backoff curves "
            "are stale relative to the current API contract. Was the "
            "SmartRetry logic already tested in isolation, or did wiring "
            "it in also surface config drift?\n\n"
            "Severin"
        ),
    },
    "677": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "678": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "679": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "680": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "681": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Newline preservation in CopilotKit markdown code blocks",
        "outreach_message": (
            "Hey Giulio,\n\n"
            "Newline stripping in markdown code blocks usually means "
            "the renderer collapses whitespace before the syntax "
            "highlighter runs \u2014 so the raw content is intact but the "
            "display pass flattens it. Was the fix in the markdown "
            "parser or the React rendering layer?\n\n"
            "Severin"
        ),
    },
    "682": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "683": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "684": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Anthropic rate limit pause-until-reset in ai-social",
        "outreach_message": (
            "Hey Joshua,\n\n"
            "Detecting Anthropic rate limits and pausing until reset "
            "is clean, but the reset timestamp from 429 headers can "
            "drift if the client clock is skewed \u2014 you\u2019d resume too "
            "early or too late. Did you fall back to a retry-after "
            "delta or trust the absolute reset time?\n\n"
            "Severin"
        ),
    },
    "685": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "686": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "687": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "688": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "689": {
        "done": "YES",
        "status": "",
        "outreach_subject": "NONE production control reset for RC master groups in OPM",
        "outreach_message": (
            "Hey H\u00e5kon,\n\n"
            "NONE production control on RC master groups is tricky "
            "\u2014 if the reset path doesn\u2019t propagate to child wells, "
            "they keep their old control mode while the group thinks "
            "it\u2019s unconstrained. Was the fix in the group-level reset "
            "or the well-level inheritance logic?\n\n"
            "Severin"
        ),
    },
    "690": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Wall-clock gap reset vs offline render in kingdubby",
        "outreach_message": (
            "Hey Nathan,\n\n"
            "Wall-clock gap reset during offline render is subtle "
            "\u2014 if the gap detector fires on real-time deltas, an "
            "offline bounce processes the entire buffer as one giant "
            "gap and inserts silence or skips. Did you gate the reset "
            "on a render-mode flag or clamp the gap threshold?\n\n"
            "Severin"
        ),
    },
    "691": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Model selection lost on hydration in background-agents",
        "outreach_message": (
            "Hey Cole,\n\n"
            "Model selection lost on hydration usually means the "
            "persisted value loads after the default initializer "
            "runs \u2014 the store hydrates with the saved model, then the "
            "component mounts and overwrites it. Was the fix a "
            "load-order guard or a merge strategy?\n\n"
            "Severin"
        ),
    },
    "692": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Lease renewal retry backoff in k8s leader election",
        "outreach_message": (
            "Hey Valentin,\n\n"
            "Lease renewal with exponential backoff in leader election "
            "has a ceiling problem \u2014 if the backoff grows past the "
            "lease TTL, the leader loses its lease before the next "
            "renewal attempt and a second node promotes. Did you cap "
            "the backoff at a fraction of the TTL?\n\n"
            "Severin"
        ),
    },
    "693": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Neo Connect menu reset on Chromebooks in App Inventor",
        "outreach_message": (
            "Hey Surbhi,\n\n"
            "Chromebook-specific menu reset bugs often trace to how "
            "Chrome OS handles window focus events differently from "
            "desktop Chrome \u2014 a blur/focus cycle on tab switch can "
            "re-trigger the menu init. Was the Neo Connect reset tied "
            "to a focus event or a USB reconnect path?\n\n"
            "Severin"
        ),
    },
    "694": {
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
