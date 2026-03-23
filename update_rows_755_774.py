#!/usr/bin/env python3
"""Update rows 755-774 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "755": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Pairing code rejection: timing race vs platform validation",
        "outreach_message": (
            "Hey Matheus,\n\n"
            "Pairing code rejections from timing AND platform "
            "validation failing together usually means one hides "
            "the other — if platform validation short-circuits, "
            "the timing race never surfaces in isolation. Was the "
            "fix sequencing the checks, or patching each "
            "independently?\n\n"
            "Severin"
        ),
    },
    "756": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Signal as C2 channel for inventory management",
        "outreach_message": (
            "Hey Richie,\n\n"
            "Signal as a C2 channel gives E2E encryption, but "
            "its rate limits aren't designed for high-frequency "
            "command dispatch — inventory sync under load could "
            "get throttled or dropped. Did you add sequence "
            "numbers or a fallback channel?\n\n"
            "Severin"
        ),
    },
    "757": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SCQIndexing seek hardening and cleanup test de-flaking",
        "outreach_message": (
            "Hey Peter,\n\n"
            "Hardening SCQ seek logic and de-flaking cleanup "
            "tests in the same commit suggests the flakiness was "
            "exposing a real seek edge case, not just timing "
            "noise. Did the de-flake reveal incorrect index "
            "state, or were the tests racing a GC pause the seek "
            "fix also covered?\n\n"
            "Severin"
        ),
    },
    "758": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "759": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Segfault in Montezuma Revenge episode boundary",
        "outreach_message": (
            "Hey Joseph,\n\n"
            "Segfaults in RL environments usually come from the "
            "C binding accessing a freed frame buffer after "
            "episode reset — especially when the wrapper resets "
            "while an async step is still in flight. Was the root "
            "cause in the Gym wrapper or a race on episode "
            "boundaries?\n\n"
            "Severin"
        ),
    },
    "760": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "761": {
        "done": "YES",
        "status": "",
        "outreach_subject": "RVV state initialization and hart context switch safety",
        "outreach_message": (
            "Hey Nadime,\n\n"
            "Dynamically initializing RVV registers means "
            "tracking vtype and vl per-hart on context switch — "
            "unzeroed initial state before guest entry leaks "
            "vtype across hart migrations. Was the fix "
            "initializing on first trap-in or on every hart "
            "reset?\n\n"
            "Severin"
        ),
    },
    "762": {
        "done": "YES",
        "status": "",
        "outreach_subject": "idleTimeout semantics after HTTP-to-WebSocket upgrade",
        "outreach_message": (
            "Hey Lachlan,\n\n"
            "After a WebSocket upgrade, HTTP idle timeout fires "
            "on live connections or never fires on dead ones — "
            "the semantics diverge because WebSocket frames "
            "don't reset the HTTP idle counter. Was the fix "
            "disabling the HTTP timeout on upgrade, or replacing "
            "it with ping-based keepalive?\n\n"
            "Severin"
        ),
    },
    "763": {
        "done": "YES",
        "status": "",
        "outreach_subject": "AssumeRoleWithWebIdentity OIDC config error handling",
        "outreach_message": (
            "Hey Jan,\n\n"
            "AssumeRoleWithWebIdentity errors on config usually "
            "surface as STS rejecting the JWT — either the "
            "audience claim doesn't match the role trust policy, "
            "or the JWKS thumbprint is stale. Did the fix update "
            "the trust policy condition, or was it a JWKS "
            "endpoint mismatch?\n\n"
            "Severin"
        ),
    },
    "764": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Adaptive throttle dropping critical timer status transitions",
        "outreach_message": (
            "Hey Sunchan,\n\n"
            "Adaptive throttle on timer-based status updates "
            "risks dropping transitions to terminal states — if "
            "the throttle suppresses a failed or complete event "
            "during backoff, the consumer sees stale status "
            "indefinitely. Did the fix exempt terminal state "
            "changes from throttling?\n\n"
            "Severin"
        ),
    },
    "765": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "766": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "767": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Community-to-official migration impact on copilot-sdk-java consumers",
        "outreach_message": (
            "Hey Ed,\n\n"
            "Rebranding from community to official SDK freezes "
            "the API surface faster than community iteration can "
            "tolerate — contributors who built against the old "
            "package name need a redirect or migration path, not "
            "just a rename. Did the rebrand include a "
            "compatibility layer or deprecation notice?\n\n"
            "Severin"
        ),
    },
    "768": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "769": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "770": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "771": {
        "done": "YES",
        "status": "",
        "outreach_subject": "File upload error recovery on partial write vs session timeout",
        "outreach_message": (
            "Hey Abhilash,\n\n"
            "Poor connection upload errors split into partial "
            "writes that need resumable chunking and session "
            "timeouts that invalidate the multipart ID before "
            "reassembly. Does the fix retry the full upload, or "
            "recover from the last committed chunk?\n\n"
            "Severin"
        ),
    },
    "772": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "773": {
        "done": "YES",
        "status": "",
        "outreach_subject": "SV table checkbox sync with active filter state",
        "outreach_message": (
            "Hey Jatin,\n\n"
            "Checkbox out of sync with active filter usually "
            "means the component derives display state from a "
            "cycle that doesn't subscribe to filter store "
            "updates. Was the fix adding a subscription, or "
            "lifting filter state to a shared store?\n\n"
            "Severin"
        ),
    },
    "774": {
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
