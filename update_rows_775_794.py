#!/usr/bin/env python3
"""Update rows 775-794 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "775": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Sakai LocaleService centralization blast radius",
        "outreach_message": (
            "Hey Sam,\n\n"
            "Centralizing LocaleService in the Sakai kernel reduces "
            "drift, but raises the blast radius \u2014 a locale "
            "regression now propagates to every tool simultaneously. "
            "Was the migration purely additive, or did some tools "
            "have divergent locale logic that had to be reconciled?"
            "\n\nSeverin"
        ),
    },
    "776": {
        "done": "YES",
        "status": "",
        "outreach_subject": "MosaicSplitOverlay keyboard accessibility pattern",
        "outreach_message": (
            "Hey Nathan,\n\n"
            "Keyboard-accessible split handles need to announce the "
            "current split ratio for screen readers \u2014 arrow-key "
            "increment size also matters or resizing feels too "
            "coarse. Did the fix use role=separator with "
            "aria-valuenow, or a different ARIA pattern?"
            "\n\nSeverin"
        ),
    },
    "777": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SOGS seqno check: duplicate vs dropped message tradeoff",
        "outreach_message": (
            "Hey Ryan,\n\n"
            "A wrong seqno check in SOGS can either accept "
            "duplicate messages or drop valid ones \u2014 the failure "
            "mode depends on whether the boundary is >= vs > "
            "against the stored cursor. Was the bug rejecting "
            "in-order messages as replays, or letting out-of-order "
            "ones through?\n\nSeverin"
        ),
    },
    "778": {
        "done": "YES",
        "status": "",
        "outreach_subject": "WatermelonDB for conversation storage in starter-agent",
        "outreach_message": (
            "Hey Denis,\n\n"
            "WatermelonDB suits relational queries but conversation "
            "histories need recency-sorted pagination \u2014 fetching "
            "the last N messages in order is not the access pattern "
            "it optimizes for. Did you hit friction with the query "
            "API for ordered message retrieval?\n\nSeverin"
        ),
    },
    "779": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "780": {
        "done": "YES",
        "status": "",
        "outreach_subject": "/New vs /Clear context reset semantics in picoclaw",
        "outreach_message": (
            "Hey Jaron,\n\n"
            "In an LLM CLI, /New and /Clear diverge once tool state "
            "accumulates \u2014 /Clear might wipe message history "
            "while /New should also reset loaded files or cached "
            "context. Does the implementation distinguish clearing "
            "history from resetting the full session state?"
            "\n\nSeverin"
        ),
    },
    "781": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Calibre Plugin cancel deadlock when cache DB fails to open",
        "outreach_message": (
            "Hey Will,\n\n"
            "A stuck cancel on DB open failure means the cancel "
            "signal is not reaching the error path \u2014 the task "
            "waits on cleanup that assumes a successful init. Was "
            "the fix threading cancel through the exception handler, "
            "or restructuring cleanup to not depend on the open?"
            "\n\nSeverin"
        ),
    },
    "782": {
        "done": "YES",
        "status": "",
        "outreach_subject": "GWT candidate retirement after goal satisfaction",
        "outreach_message": (
            "Hey Eduardo,\n\n"
            "In a GWT agent, retiring candidates on goal "
            "satisfaction prevents broadcasting stale goals, but "
            "early retirement drops plans still needed for post-goal "
            "cleanup. Was the fix gating retirement on full "
            "resolution, or adding an explicit satisfied state "
            "distinct from retired?\n\nSeverin"
        ),
    },
    "783": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Maestro worktree default: monorepo subdirectory edge case",
        "outreach_message": (
            "Hey Jonathan,\n\n"
            "Defaulting the worktree to the parent of the agent cwd "
            "assumes agents run from a repo subdirectory \u2014 in a "
            "monorepo, the parent is a package dir, not the "
            "workspace root. Did you test against agents spawned "
            "from the repo root itself?\n\nSeverin"
        ),
    },
    "784": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Word template customization in CISO Assistant Pro",
        "outreach_message": (
            "Hey Abder,\n\n"
            "Word template customization breaks when injected "
            "content disrupts conditional sections or nested "
            "tables \u2014 python-docx handles structure but behaves "
            "differently across template Word versions. Did you use "
            "python-docx natively or add a Jinja pre-processing "
            "pass?\n\nSeverin"
        ),
    },
    "785": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Scalextric lap event threading fix",
        "outreach_message": (
            "Hey Juhana,\n\n"
            "Lap sensor events need interrupt-safe handoff \u2014 "
            "shared mutable state between the interrupt handler and "
            "processing thread produces missed or double-counted "
            "laps that only appear under load. Was the fix a "
            "thread-safe queue, or explicit locking around the "
            "shared state?\n\nSeverin"
        ),
    },
    "786": {
        "done": "YES",
        "status": "",
        "outreach_subject": "BACnet/SC Win32 event race on client shutdown",
        "outreach_message": (
            "Hey Dveamer,\n\n"
            "Win32 BACnet/SC shutdown hangs from event races "
            "usually mean a thread blocked on "
            "WaitForMultipleObjects does not see the stop signal "
            "before WSACleanup closes the sockets underneath it. "
            "Was the fix signaling stop before socket teardown, or "
            "adding a wait timeout?\n\nSeverin"
        ),
    },
    "787": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "788": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Static state wrong reset in Playgama bridge-unity",
        "outreach_message": (
            "Hey TonyMax,\n\n"
            "Static state in a Unity bridge reset at the wrong "
            "lifecycle event either carries stale state into new "
            "sessions or wipes state platform code expects to "
            "persist across play mode. Was the wrong reset firing "
            "in a static constructor instead of an explicit reinit "
            "hook?\n\nSeverin"
        ),
    },
    "789": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "790": {
        "done": "YES",
        "status": "",
        "outreach_subject": "isCreatingUser defer timing race in sign-in catch block",
        "outreach_message": (
            "Hey Pete,\n\n"
            "A defer inside a catch executes before the catch body "
            "finishes \u2014 if isCreatingUser is cleared by defer on "
            "any throw, the catch cleanup sees the flag already "
            "false and can leave auth state inconsistent. Was the "
            "fix moving the reset outside defer, or restructuring "
            "the auth flow?\n\nSeverin"
        ),
    },
    "791": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "792": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AndBible infinite scroll busy loop at end of book",
        "outreach_message": (
            "Hey Tuomas,\n\n"
            "Infinite scroll busy loops at end of content usually "
            "mean the load-more trigger never gets a no-more-content "
            "signal \u2014 it keeps firing because the flag only "
            "clears after a successful fetch. Was the fix capping "
            "the observer, or adding an explicit end-of-book state?"
            "\n\nSeverin"
        ),
    },
    "793": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "794": {
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
