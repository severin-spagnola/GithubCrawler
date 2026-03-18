#!/usr/bin/env python3
"""Filter FPGA leads and write outreach for first 10 (messages pre-generated)."""

import csv

INPUT = "fpga_enriched.csv"
OUTPUT = "fpga_outreach_leads.csv"
MAX_ROWS = 1000
OUTREACH_COUNT = 10

# Pre-generated outreach messages for the first 10 filtered leads (by username)
OUTREACH = {
    "Lucretia": {
        "channel": "email",
        "subject": "ghdl and open source VHDL tooling",
        "message": "Hey LA,\n\nCurious what specifically still feels broken to you in the VHDL tooling ecosystem? Like, if you could mass-delete one class of problems from your ghdl workflow tomorrow, what goes first?\n\nAsking because I'm an aero engineering student at SJSU who works in HDL and I keep running into the same walls.\n\nSeverin"
    },
    "nfrancque": {
        "channel": "email",
        "subject": "VUnit and making FPGA life easier",
        "message": "Hey, saw your contributions to VUnit.\n\nHonestly one of the few VHDL tools that actually delivers on making life easier for other designers. What's the biggest gap you still see in the verification workflow that VUnit doesn't cover yet?\n\nBeen thinking about this a lot as a student writing HDL and constantly fighting my own toolchain.\n\nSeverin"
    },
    "sigvef": {
        "channel": "email",
        "subject": "Hyre's stack in Oslo",
        "message": "Hey Sigve,\n\nSaw you're at Hyre in Oslo. Curious what your team's development workflow looks like when multiple people are touching the same services simultaneously. Do you run into cases where someone's local changes silently break another teammate's work before anything gets pushed? That's a problem I keep thinking about from the hardware side but it seems universal.\n\nSeverin"
    },
    "Xiretza": {
        "channel": "email",
        "subject": "ghdl's synthesis backend",
        "message": "Hey,\n\nYou're one of 150 contributors on ghdl. Curious whether you've worked at all on the synthesis side, specifically how it handles mapping to different target architectures. The gap between what ghdl can simulate vs. what it can actually synthesize seems like one of the biggest open problems in open source EDA right now. Is that something the project is actively pushing on?\n\nSeverin"
    },
    "machitgarha": {
        "channel": "email",
        "subject": "ghdl contributions from Qazvin",
        "message": "Hey Mohammad,\n\nContributing to ghdl from Iran is cool. Access to commercial VHDL tools is rough with licensing restrictions over there, right? Curious whether that's part of what drew you to ghdl specifically, or if it was more of a technical interest thing. Open source EDA feels like it matters way more in places where Vivado licenses aren't handed out freely.\n\nSeverin"
    },
    "rugebiker": {
        "channel": "email",
        "subject": "VUnit contributions from NL",
        "message": "Hey Ruben,\n\nSaw your contributions to VUnit. The Netherlands has a pretty deep FPGA scene between ASML, NXP, and the university groups. What's your main use case for VUnit, verification on work projects or personal stuff? Trying to figure out how people actually integrate it into real team workflows.\n\nSeverin"
    },
    "alexmodrono": {
        "channel": "email",
        "subject": "TerosHDL and the EECS double major",
        "message": "Hey Alex,\n\nComputer and electrical engineering plus business analytics in Madrid is a heavy combo. You're contributing to TerosHDL, which is one of the few VS Code extensions that actually tries to make HDL development not painful. What got you involved? Did you find existing VHDL tooling frustrating enough during coursework that you wanted to fix it yourself?\n\nSeverin"
    },
    "obruendl": {
        "channel": "email",
        "subject": "en_cl_fix at Enclustra",
        "message": "Hey Oliver,\n\nThe en_cl_fix library from Enclustra is interesting. Fixed-point VHDL libraries are one of those things everyone needs but nobody wants to maintain. With 6 contributors, is it mostly an internal Enclustra tool that you opened up, or do you get meaningful outside contributions? Curious how that dynamic works at a company that ships FPGA modules.\n\nSeverin"
    },
    "endofexclusive": {
        "channel": "email",
        "subject": "ghdl work from Sweden",
        "message": "Hey Martin,\n\nYou're contributing to ghdl, which has grown to 150 contributors now. What's your corner of the project? The synthesis backend, simulation, or something else entirely? Trying to understand how the work gets divided on a project that size with a distributed contributor base.\n\nSeverin"
    },
    "LarsAsplund": {
        "channel": "email",
        "subject": "VUnit at 820 stars",
        "message": "Hey Lars,\n\nVUnit hitting 820 stars with 120 contributors is serious traction for a VHDL verification framework. Most HDL open source projects plateau way earlier. What do you think got VUnit past the initial adoption hump? Was it the CI integration angle, or something else that clicked with teams? Genuinely curious because most VHDL tooling never reaches that scale.\n\nSeverin"
    },
}

# Step 1: Read first 1000 rows and filter
with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    all_rows = []
    for i, row in enumerate(reader):
        if i >= MAX_ROWS:
            break
        all_rows.append(row)

filtered = [r for r in all_rows if (r.get("email") or "").strip() or (r.get("linkedin") or "").strip()]
print(f"Step 1: Read {len(all_rows)} rows, kept {len(filtered)} with email or linkedin.\n")

# Step 2: Apply outreach to first 10, blanks for rest
new_fields = ["outreach_channel", "outreach_subject", "outreach_message"]
outreach_fields = ["number"] + fieldnames + new_fields

results = []
for i, row in enumerate(filtered):
    username = row.get("username", "")
    has_email = bool((row.get("email") or "").strip())
    has_linkedin = bool((row.get("linkedin") or "").strip())
    channel = "email" if has_email else "linkedin"

    row["number"] = i + 1

    if i < OUTREACH_COUNT and username in OUTREACH:
        o = OUTREACH[username]
        row["outreach_channel"] = o["channel"]
        row["outreach_subject"] = o["subject"]
        row["outreach_message"] = o["message"]
        results.append((row, o["channel"], o["subject"], o["message"]))
    else:
        row["outreach_channel"] = channel
        row["outreach_subject"] = ""
        row["outreach_message"] = ""

# Step 3: Save
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=outreach_fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(filtered)

# Report
email_count = sum(1 for r in filtered if bool((r.get("email") or "").strip()))
linkedin_count = sum(1 for r in filtered if bool((r.get("linkedin") or "").strip()))
both_count = sum(1 for r in filtered if bool((r.get("email") or "").strip()) and bool((r.get("linkedin") or "").strip()))

print(f"{'='*60}")
print(f"Total rows in output file: {len(filtered)}")
print(f"Rows with email: {email_count}")
print(f"Rows with linkedin: {linkedin_count}")
print(f"Rows with both: {both_count}")
print(f"{'='*60}\n")

for i, (row, channel, subject, message) in enumerate(results):
    print(f"--- Lead {i+1}: {row.get('username', '?')} ({channel}) ---")
    if subject:
        print(f"Subject: {subject}")
    print(f"Message:\n{message}")
    print()
