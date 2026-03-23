#!/usr/bin/env python3
"""Update rows 735-754 in fpga_outreach_leads.csv in-place."""

import csv

CSV_PATH = "fpga_outreach_leads.csv"

UPDATES = {
    "735": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Twitter UsageCapExceeded flag-file persistence",
        "outreach_message": (
            "Hey Clawdia,\n\n"
            "Flag-file early-exit for UsageCapExceeded avoids "
            "redundant API calls, but the flag persists across "
            "restarts — if the cap resets server-side, the local "
            "file keeps the client locked out. Did you add a TTL "
            "or staleness check on the flag file?\n\n"
            "Severin"
        ),
    },
    "736": {
        "done": "YES",
        "status": "",
        "outreach_subject": "WASM OOB buffer alignment in Fallout2 object preload",
        "outreach_message": (
            "Hey Vasilii,\n\n"
            "WASM memory OOB in the object preload path usually "
            "means the native pointer arithmetic assumed contiguous "
            "allocation that the linear memory model doesn't "
            "guarantee at page boundaries. Was the fix an alignment "
            "guard, or did the preload buffer need explicit bounds "
            "checks?\n\n"
            "Severin"
        ),
    },
    "737": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "738": {
        "done": "YES",
        "status": "",
        "outreach_subject": "MySQL auto_increment counter bleed in TestCase",
        "outreach_message": (
            "Hey Ni,\n\n"
            "Resetting auto_increment in TestCase stops counter "
            "bleed between tests, but TRUNCATE vs ALTER TABLE "
            "differ under InnoDB — TRUNCATE resets implicitly "
            "while ALTER TABLE preserves data. Which did you "
            "pick, and did foreign key constraints complicate "
            "the reset?\n\n"
            "Severin"
        ),
    },
    "739": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Daily/weekly accumulation reset in WoW addon",
        "outreach_message": (
            "Hey Darren,\n\n"
            "Accumulation reset bugs in WoW addons usually come "
            "from comparing server time against saved timestamps "
            "that used local time — the daily boundary drifts if "
            "the player changes timezones. Was the fix normalizing "
            "to server time, or anchoring resets to a fixed UTC "
            "offset?\n\n"
            "Severin"
        ),
    },
    "740": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Transcript debounce corruption after context compaction",
        "outreach_message": (
            "Hey Samuel,\n\n"
            "Debounce logic that caches pending writes will "
            "permanently skip future flushes if context compaction "
            "invalidates the cached state without clearing the "
            "debounce timer. Was the root cause a stale reference "
            "in the debounce closure, or did compaction not signal "
            "downstream consumers?\n\n"
            "Sev"
        ),
    },
    "741": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "742": {
        "done": "YES",
        "status": "",
        "outreach_subject": "pgbackrest RPO precision on streaming lag fallback",
        "outreach_message": (
            "Hey Mayank,\n\n"
            "Falling back to pgbackrest when streaming lag check "
            "fails changes the RPO guarantee — streaming gives "
            "near-zero lag, but pgbackrest restore points depend "
            "on backup frequency. Did the fallback expose the "
            "degraded RPO to the operator, or does it silently "
            "switch?\n\n"
            "Severin"
        ),
    },
    "743": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Inbox count triggering hidden column reset",
        "outreach_message": (
            "Hey Sherv,\n\n"
            "Hidden column state resetting when inbox count "
            "changes suggests the column visibility is derived "
            "from a render cycle that re-evaluates on count "
            "updates rather than being stored independently. "
            "Was the fix decoupling visibility state from the "
            "count-dependent render path?\n\n"
            "Severin"
        ),
    },
    "744": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "745": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "746": {
        "done": "YES",
        "status": "",
        "outreach_subject": "React Activity state preservation on link navigation",
        "outreach_message": (
            "Hey James,\n\n"
            "React Activity preserving state after link navigation "
            "means the component tree stays mounted when it should "
            "unmount — stale state from the previous route leaks "
            "into the new one. Was the workaround a key reset on "
            "route change, or did you patch the Activity boundary "
            "itself?\n\n"
            "Severin"
        ),
    },
    "747": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "748": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "749": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Stale resource table on cluster switch",
        "outreach_message": (
            "Hey Nitin,\n\n"
            "Resource table state persisting across cluster "
            "switches means the UI shows the previous cluster's "
            "resources until the new fetch completes — or worse, "
            "merges both if the response races. Did the fix clear "
            "state on switch, or cancel in-flight requests for "
            "the old cluster?\n\n"
            "Severin"
        ),
    },
    "750": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Frontend gating vs server-side subscription enforcement",
        "outreach_message": (
            "Hey Aaron,\n\n"
            "Frontend gating for subscriptions without matching "
            "server-side enforcement means any API call that "
            "bypasses the UI gets ungated access — feature flags "
            "in the client are hints, not controls. Did the PR "
            "add server-side middleware, or is the frontend gate "
            "the sole enforcement point?\n\n"
            "Sev"
        ),
    },
    "751": {
        "done": "YES",
        "status": "",
        "outreach_subject": "CallbackRequestID idempotency for CHASM Schedules",
        "outreach_message": (
            "Hey Sean,\n\n"
            "Adding CallbackRequestID gives CHASM Schedules a "
            "dedup key, but idempotency depends on where the ID "
            "is generated — if derived from schedule time, clock "
            "skew between schedulers creates duplicates. Is the "
            "ID deterministic from schedule input, or minted at "
            "dispatch?\n\n"
            "Severin"
        ),
    },
    "752": {
        "done": "YES",
        "status": "SKIP",
        "outreach_subject": "",
        "outreach_message": "",
    },
    "753": {
        "done": "YES",
        "status": "",
        "outreach_subject": "PIA iOS reconnection on server reboot vs disappearance",
        "outreach_message": (
            "Hey Diego,\n\n"
            "Server reboot and disappearance look identical from "
            "the client until TCP timeout fires — but reconnect "
            "strategy should differ. Reboots warrant fast retry "
            "to the same endpoint; disappearance needs failover. "
            "Does the new mechanism distinguish the two, or use "
            "a single backoff?\n\n"
            "Severin"
        ),
    },
    "754": {
        "done": "YES",
        "status": "",
        "outreach_subject": "Raw SQL to Drizzle migration edge cases",
        "outreach_message": (
            "Hey Jackson,\n\n"
            "Migrating raw SQL to Drizzle usually surfaces edge "
            "cases where the ORM generates subtly different SQL "
            "— especially around NULL handling, implicit casts, "
            "and JOIN ordering. Did you find cases where Drizzle "
            "diverged from raw queries in behavior, not just "
            "syntax?\n\n"
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
