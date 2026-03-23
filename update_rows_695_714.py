#!/usr/bin/env python3
"""Update rows 695-714 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "695": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "696": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Subscription migration loop and HPOS state tracking in WooCommerce",
        "outreach_message": (
            "Hey Aman,\n\n"
            "Migration loops that also add HPOS support have a specific "
            "risk \u2014 if failed items get re-queued without being marked "
            "in-progress, the loop detector gets bypassed on retry. Did "
            "the state tracking gate on idempotency, or track which "
            "subscriptions had already processed?\n\n"
            "Severin"
        ),
    },
    "697": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Stagnation detection for AI agent loops in oh-my-openagent",
        "outreach_message": (
            "Hey ToToKr,\n\n"
            "Stagnation detection that also triggers a token-limit "
            "cooldown has a false-positive risk \u2014 an agent making slow "
            "progress on a hard subproblem looks identical to one "
            "cycling. What signal did you use to distinguish actual "
            "stagnation from slow convergence?\n\n"
            "Severin"
        ),
    },
    "698": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Session reset time display in CCometixLine",
        "outreach_message": (
            "Hey Jesse,\n\n"
            "Showing Claude usage session reset time has a subtle "
            "problem \u2014 the API reset window is UTC-midnight but users "
            "local clocks aren\u2019t, so the countdown can be visually "
            "wrong even when numerically correct. Did you normalize to "
            "local time or display UTC explicitly?\n\n"
            "Severin"
        ),
    },
    "699": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Panel-reviewed plan in openclaw learning pipeline",
        "outreach_message": (
            "Hey Peleke,\n\n"
            "Panel-reviewed planning has a specific failure mode \u2014 all "
            "panel members share the same upstream context, so they "
            "tend to confirm each other\u2019s blind spots rather than "
            "catch them. Did you isolate the panel agents\u2019 reasoning, "
            "or let them see prior evaluations?\n\n"
            "Severin"
        ),
    },
    "700": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "701": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Signal masking during CHAIN_AT_START in sentry-native Android",
        "outreach_message": (
            "Hey J-P,\n\n"
            "Masking signals during CHAIN_AT_START to survive Mono "
            "re-raises creates a window where your own handler can\u2019t "
            "be interrupted \u2014 but if the unmask never runs cleanly "
            "after a double-fault, you end up with permanently blocked "
            "signals. Did you add a guard for the unmask path?\n\n"
            "Severin"
        ),
    },
    "702": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Rate limiting interval calculation in SOGo UIxMailEditor",
        "outreach_message": (
            "Hey Tobias,\n\n"
            "Rate limiting interval calculations in mail editors go "
            "wrong when intervals span DST transitions \u2014 the next "
            "allowed send time can jump backward. Was the bug in how "
            "the interval end was computed, or in the reference "
            "timestamp used as the starting point?\n\n"
            "Severin"
        ),
    },
    "703": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Factory reset permission denied on startup in openrag",
        "outreach_message": (
            "Hey Mike,\n\n"
            "Factory reset triggering permission denied on startup "
            "usually means the reset clears config but leaves a data "
            "directory owned by a service account \u2014 the fresh config "
            "tries to create files in a path it no longer owns. Was it "
            "a directory ownership issue or a stale socket path?\n\n"
            "Severin"
        ),
    },
    "704": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "705": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Exponential backoff and log dedup interaction in Sentry Spotlight",
        "outreach_message": (
            "Hey Matt,\n\n"
            "Backoff with log deduplication in Spotlight has an "
            "interaction \u2014 two identical errors during a backoff window "
            "can have the second suppressed by dedup after backoff "
            "resolves, making the error look like it stopped. Did you "
            "deduplicate before or after the backoff window check?\n\n"
            "Severin"
        ),
    },
    "706": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "707": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "708": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Edge table state in bundled/unbundled transforms in neug",
        "outreach_message": (
            "Hey Zhang Lei,\n\n"
            "Edge table state corruption on bundled/unbundled "
            "transitions often comes from stale references not "
            "recomputed when the representation changes \u2014 the edge "
            "exists in one form but isn\u2019t visible in the other. Was "
            "the root cause a missing invalidation pass or a "
            "structural mismatch?\n\n"
            "Severin"
        ),
    },
    "709": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "710": {
        "done": "YES",
        "status": "",
        "outreach_subject": "ListView string comparison and adapter notifications in App Inventor",
        "outreach_message": (
            "Hey Nitin,\n\n"
            "String comparison in ListView selection can silently fail "
            "when == is used instead of .equals() \u2014 reference equality "
            "works by accident due to string interning, making it hard "
            "to reproduce. Was it an equality operator issue, or "
            "something in how the adapter tracks selection state?\n\n"
            "Severin"
        ),
    },
    "711": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SSH BMC reset fallback in BMCReconciler (metal-operator)",
        "outreach_message": (
            "Hey Stefan,\n\n"
            "SSH-based BMC reset fallback in a reconciler has an "
            "ordering problem \u2014 if the primary reset times out and "
            "the reconciler retries via SSH, the BMC might still be "
            "mid-reset when the SSH session connects. Did you add a "
            "state guard before attempting the SSH fallback?\n\n"
            "Severin"
        ),
    },
    "712": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "713": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "714": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AgentHealthMonitor heartbeat counter reset timing",
        "outreach_message": (
            "Hey Gyasi,\n\n"
            "MissedHeartbeat counter reset timing is tricky \u2014 if you "
            "reset on receipt of any heartbeat rather than on "
            "successful acknowledgment, a lost ack still clears the "
            "counter and the monitor thinks the agent is healthy. Was "
            "the fix in when the reset fires or what event triggers "
            "it?\n\n"
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
