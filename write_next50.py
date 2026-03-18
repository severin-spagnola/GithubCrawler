#!/usr/bin/env python3
"""Write outreach for leads 11-60, handling dupes (one message per unique person)."""

import csv

OUTREACH_FILE = "fpga_outreach_leads.csv"

# Messages keyed by (username) for leads 11-60
# For duplicate usernames, we write the message on the first occurrence and leave subsequent ones blank
MESSAGES = {
    # Lead 11 - Xiretza already got outreach in lead 4, this is a different repo entry
    # but same person. Skip.

    # Lead 12
    "Ravenwater": {
        "subject": "Stillwater and custom compute for robotics",
        "message": "Hey Theodore,\n\nBuilding custom compute engines for robotics and HPC at Stillwater is a pretty specific niche. Curious how much of that work lives in VHDL vs. higher-level synthesis tools. When you're designing something that has to hit real-time constraints for computer vision, does the verification bottleneck ever become the dominant time sink over actual design work?\n\nSeverin"
    },

    # Lead 13
    "borjarevuelta-tec": {
        "subject": "Open-Logic at The Exploration Company",
        "message": "Hey Borja,\n\nDigital electronics for a space company in Munich contributing to open-logic is a great combination. With 899 stars that project has real traction. How much of your day-to-day FPGA work at The Exploration Company relies on open source libraries like that vs. vendor IP? Space-grade designs seem like they'd have very different constraints on what you can pull in.\n\nSeverin"
    },

    # Lead 14
    "Martoni": {
        "subject": "Armadeus and ghdl",
        "message": "Hey Fabien,\n\nArmadeus Systems does some interesting work bridging embedded Linux and FPGAs. You're contributing to ghdl too, which feels like a natural fit given the embedded angle. Do you use ghdl for simulation on actual Armadeus product designs, or is the contribution more of a personal interest thing?\n\nSeverin"
    },

    # Lead 15 - obruendl already has outreach from lead 8, skip

    # Lead 16
    "rodrigomelo9": {
        "subject": "VUnit and FPGA work at indie Semi",
        "message": "Hey Rodrigo,\n\nFPGA engineer at indie Semiconductor contributing to VUnit from Argentina. Curious how VUnit fits into the verification flow at a company like indie. Do your colleagues use it too, or is it more of a personal workflow choice that you bring into projects? Trying to understand how open source verification tools actually get adopted inside semiconductor companies.\n\nSeverin"
    },

    # Lead 17
    "rhinton": {
        "subject": "ghdl contributions from SLC",
        "message": "Hey Ryan,\n\nYou're contributing to ghdl with 150 other people. What area of the project do you focus on? Trying to map out who works on what in ghdl since it's one of the biggest community-driven VHDL projects and the contributor dynamics are interesting.\n\nSeverin"
    },

    # Lead 18
    "jhegeman": {
        "subject": "ipbus-firmware at 43 stars",
        "message": "Hey Jeroen,\n\nThe ipbus-firmware project is interesting. Control of hardware over IP in VHDL with 20 contributors feels like it came out of a physics lab environment. Is this used primarily in detector readout or something similar? Curious what the typical deployment looks like.\n\nSeverin"
    },

    # Lead 19
    "gardners": {
        "subject": "MEGA65 and resilient systems",
        "message": "Hey Paul,\n\nThe MEGA65 project is fascinating. Building a retro computer in VHDL with 60 contributors is serious community traction. Your bio mentions resilient and self-sovereign systems, and the Serval disaster comms project. How does thinking about resilience in communications systems influence how you approach the hardware design side of MEGA65?\n\nSeverin"
    },

    # Lead 20
    "antonblanchard": {
        "subject": "Tenstorrent and ghdl",
        "message": "Hey Anton,\n\nTenstorrent and ghdl contributions is an interesting combo. Working on RISC-V AI accelerators and also contributing to open source VHDL tooling covers a lot of ground. Does ghdl play any role in the Tenstorrent workflow, or is the contribution more from personal interest in open EDA?\n\nSeverin"
    },

    # Lead 21
    "GyrosGeier": {
        "subject": "ghdl from Tokyo",
        "message": "Hey Simon,\n\nContributing to ghdl from Tokyo puts you in an interesting spot given the Japanese semiconductor push happening right now with TSMC and Rapidus. Curious whether you're seeing increased interest in open source EDA tools in that ecosystem, or if it's still mostly dominated by the big commercial vendors.\n\nSeverin"
    },

    # Lead 22
    "tasgomes": {
        "channel": "linkedin",
        "subject": "",
        "message": "Hey Tiago, saw your contributions to open-logic and VUnit. Curious what your main VHDL workflow looks like day to day and what tools you wish existed."
    },

    # Lead 23
    "MrKelpy": {
        "subject": "VHDL roulette project at ISEL",
        "message": "Hey Alexandre,\n\nSaw the roulette project in VHDL from your ISEL coursework. Building a full game in hardware is a solid way to learn digital design. What was the hardest part, the state machine logic or getting the I/O timing right? Curious because university VHDL projects always seem to hit unexpected walls.\n\nSeverin"
    },

    # Lead 24 - fernandoka, no bio/company/display name, ghdl contributor
    "fernandoka": {
        "subject": "ghdl contributions",
        "message": "Hey Fernando,\n\nSaw your work on ghdl. What part of the project do you mainly touch? The codebase is big enough that most contributors seem to specialize. Curious what drew you to working on it.\n\nSeverin"
    },

    # Lead 25
    "dansanderson": {
        "subject": "MEGA65 core and PICO-8",
        "message": "Hey Dan,\n\nSoftware engineer working on the MEGA65 VHDL core and also into PICO-8 is a fun range. With 60 contributors on mega65-core, how does the team coordinate changes to the hardware design? Curious whether you've hit cases where two people's changes to the VHDL conflict in ways that are hard to catch before synthesis.\n\nSeverin"
    },

    # Lead 26 - twilco, no bio/company, ghdl contributor
    "twilco": {
        "subject": "ghdl contributions",
        "message": "Hey Tyler,\n\nSaw your contributions to ghdl. With 150 contributors it's one of the biggest open source VHDL projects out there. What area do you focus on, and what's the thing about the development workflow that you'd most want to improve?\n\nSeverin"
    },

    # Lead 27
    "MoriARosland": {
        "subject": "RSA hardware accelerator at NTNU",
        "message": "Hey Mori,\n\nAn RSA hardware accelerator in VHDL for your NTNU masters is a solid project. Crypto in hardware always runs into fun problems around timing attacks and constant-time execution. Did you have to deal with any of that, or was the focus more on raw throughput?\n\nSeverin"
    },

    # Lead 28 - josyb, Citium CommV, ghdl contributor
    "josyb": {
        "subject": "Citium and ghdl contributions",
        "message": "Hey Josy,\n\nContributing to ghdl from Belgium while running Citium. Curious if ghdl is something you use in your commercial work or if the contribution is more of a community interest thing. The line between \"using open source EDA\" and \"contributing to it\" seems blurry for a lot of people in this space.\n\nSeverin"
    },

    # Lead 29
    "Rutherther": {
        "subject": "vhdl-ts-mode and digital verification",
        "message": "Hey,\n\nSaw your contributions to vhdl-ts-mode. Building better editor support for VHDL is something most people just complain about rather than actually fixing. Your bio mentions digital design and verification as your focus. What's the most painful part of the VHDL editing experience that tree-sitter can realistically solve?\n\nSeverin"
    },

    # Lead 30
    "Araneidae": {
        "subject": "ghdl at Diamond Light Source",
        "message": "Hey Michael,\n\nDiamond Light Source and ghdl contributions is an interesting combination. Synchrotron control systems have some wild timing requirements. Do you use VHDL for the beamline control hardware, and does ghdl fit into that workflow at all, or is the contribution more separate from the day job?\n\nSeverin"
    },

    # Lead 31
    "JennySmith888": {
        "subject": "SURF tutorial at SLAC",
        "message": "Hey Jenny,\n\nStaff electronics engineer at SLAC working on surf-tutorial. The SURF framework seems pretty central to how SLAC does FPGA firmware. Curious what the biggest friction points are when onboarding new engineers onto that kind of framework. Does the tutorial repo come from direct pain you saw with people ramping up?\n\nSeverin"
    },

    # Lead 32 - tasgomes duplicate, skip
    # Lead 33
    "jefflieu": {
        "subject": "ghdl and making something",
        "message": "Hey Jeff,\n\nYour bio says \"let's make something\" and you're contributing to ghdl from Australia. Curious what you're building with it. Simulation, synthesis, or something else entirely? Always interested in what motivates people to contribute to open source EDA tools.\n\nSeverin"
    },

    # Lead 34
    "Remillard": {
        "subject": "UVVM and FPGA board design",
        "message": "Hey Mark,\n\nEE doing both digital board design and HDL, contributing to UVVM. That's a useful perspective since you see both the hardware and the firmware sides. How does UVVM compare to VUnit in your experience? People seem to pick camps and I'm curious what drives the choice for someone who's actually used them.\n\nSeverin"
    },

    # Lead 35
    "MJoergen": {
        "subject": "Weibel Scientific and ghdl",
        "message": "Hey Michael,\n\nFirmware at Weibel Scientific in Denmark and contributing to ghdl. Weibel does radar systems, which means some serious signal processing in hardware. Does ghdl play any role in your radar firmware development, or is the open source contribution separate from the Weibel work?\n\nSeverin"
    },

    # Lead 36
    "tmeissner": {
        "subject": "FPGA verification with SVA and PSL",
        "message": "Hey T.,\n\nYour bio mentions design and verification using VHDL, SystemVerilog, SVA, and PSL. That's a broader formal verification toolkit than most FPGA engineers touch. Curious what made you adopt PSL specifically. It seems underused relative to SVA despite being the VHDL-native option. Is tooling support the bottleneck?\n\nSeverin"
    },

    # Lead 37
    "ribru17": {
        "subject": "tree-sitter-vhdl at Google",
        "message": "Hey Riley,\n\nContributing to tree-sitter-vhdl while at Google is an interesting side project. Better parsing for VHDL in editors could actually move the needle for the whole ecosystem. What drove you to work on this? Do you write VHDL at work, or is it a personal interest that led you to fix the tooling?\n\nSeverin"
    },

    # Lead 38
    "rapgenic": {
        "subject": "ghdl and Protech Engineering",
        "message": "Hey Giulio,\n\nMSc in electronic engineering at UNIPD, now at Protech Engineering, and contributing to ghdl. Curious whether ghdl is something you use at Protech or if the contribution comes from your academic work. The Italian embedded engineering scene is strong but I rarely hear about open source EDA adoption there.\n\nSeverin"
    },

    # Lead 39
    "JonasDann": {
        "subject": "vhsnunzip at ETH Zurich",
        "message": "Hey Jonas,\n\nThe vhsnunzip project from TU Delft is interesting, and now you're doing postdoc research at ETH. Hardware decompression in VHDL seems like it has applications in high-throughput data pipelines. What's the target use case? Is this for accelerating data ingestion on FPGAs in a datacenter context?\n\nSeverin"
    },

    # Lead 40 - EmilioPeJu, no bio/company, ghdl contributor
    "EmilioPeJu": {
        "subject": "ghdl contributions",
        "message": "Hey Emilio,\n\nSaw your work on ghdl. Curious what area of the project you focus on. With 150 contributors, people tend to specialize. What's the thing about VHDL development tooling that you'd most want to see improved?\n\nSeverin"
    },

    # Lead 41
    "arbrauns": {
        "subject": "SILA Embedded Solutions and ghdl",
        "message": "Hey Armin,\n\nSILA Embedded Solutions in Austria and ghdl contributions. Curious whether ghdl fits into any of your embedded work at SILA, or if the contribution is more of a community involvement thing. Austrian engineering companies seem to have a solid FPGA presence but I don't hear much about open source EDA tool adoption there.\n\nSeverin"
    },

    # Lead 42 - obruendl duplicate, skip
    # Lead 43
    "JC-LL": {
        "subject": "neorv32 at 2000 stars",
        "message": "Hey Jean-Christophe,\n\nSaw your contributions to neorv32, which hit 2000 stars. A RISC-V core in VHDL with that kind of traction is impressive. Most RISC-V implementations go with Verilog or Chisel. Do you think VHDL's stronger typing actually helps catch bugs earlier in a processor design, or is it mostly a preference thing?\n\nSeverin"
    },

    # Lead 44
    "am9417": {
        "subject": "UVVM at University of Vaasa",
        "message": "Hey Konsta,\n\nSW developer and FPGA engineer contributing to UVVM from Vaasa. Finland has a surprisingly deep FPGA ecosystem for its size. Curious how you split your time between software and hardware. Do you find the verification methodology transfers between the two, or are they fundamentally different workflows?\n\nSeverin"
    },

    # Lead 45
    "igmar": {
        "subject": "ghdl from ING Bank",
        "message": "Hey Igmar,\n\nING Bank and ghdl contributions is an unexpected combo. Most people don't associate banking with VHDL. Is the ghdl work a personal interest, or does ING have hardware acceleration use cases that most people don't know about? Curious because FPGA adoption in fintech keeps growing quietly.\n\nSeverin"
    },

    # Lead 46
    "JimLewis": {
        "subject": "OSVVM and IEEE VHDL WG",
        "message": "Hey Jim,\n\nOSVVM author, IEEE VHDL working group chair, and yoga teacher is quite the combination. OSVVM has become foundational for a lot of VHDL verification workflows. Curious what you think is the biggest gap remaining in VHDL verification methodology that the language or tooling hasn't solved yet.\n\nSeverin"
    },

    # Lead 47
    "nickg": {
        "subject": "VHDL Compliance Tests",
        "message": "Hey Nick,\n\nMaintaining the VHDL Compliance Tests repo with 9 contributors is important work that most people never think about. Curious how comprehensive the coverage actually is right now. Are there areas of the VHDL spec that are still basically untested across simulators?\n\nSeverin"
    },

    # Lead 48 - Martoni duplicate, skip
    # Lead 49
    "bpadalino": {
        "subject": "UVVM contributions from Rochester",
        "message": "Hey Brian,\n\nSaw your contributions to UVVM and the VHDL Compliance Tests. Working on both verification frameworks and spec compliance is a pretty deep commitment to the VHDL ecosystem. What's the thing about VHDL tooling that frustrates you most day to day?\n\nSeverin"
    },

    # Lead 50
    "kraigher": {
        "subject": "ghdl contributions",
        "message": "Hey Olof,\n\nSaw your work on ghdl. With 150 contributors it's one of the most active open source VHDL projects. What area do you mainly work in? Curious what keeps you contributing and what you think the project's biggest unsolved challenge is.\n\nSeverin"
    },

    # Lead 51 - tasgomes duplicate, skip
    # Lead 52
    "react66": {
        "subject": "Tensor Logic and 30 years in semiconductors",
        "message": "Hey Robert,\n\nThirty years across semiconductors, ASICs, and sensor tech at Tensor Logic is a deep run. Curious how much the FPGA design workflow has actually improved over that time vs. how much of it still feels like the same problems with shinier tools. You've probably seen more tooling generations than most.\n\nSeverin"
    },

    # Lead 53 - bpadalino duplicate, skip
    # Lead 54 - bjourne, no bio/company
    "bjourne": {
        "subject": "ghdl contributions",
        "message": "Hey Bjorn,\n\nSaw your work on ghdl. Curious what area of the project you focus on and what originally pulled you into contributing. The project has grown to 150 contributors now and I'm trying to understand what motivates people to work on open source VHDL tooling.\n\nSeverin"
    },

    # Lead 55
    "augustofg": {
        "subject": "ghdl and CNPEM-LNLS",
        "message": "Hey Augusto,\n\nElectrical engineer at CNPEM-LNLS in Sao Paulo contributing to ghdl. Working at a synchrotron light source means some serious control system hardware. Does VHDL play a role in the beamline instrumentation at LNLS, and does ghdl fit into that workflow at all?\n\nSeverin"
    },

    # Lead 56
    "mikey": {
        "subject": "A2I core and Tenstorrent",
        "message": "Hey Michael,\n\nThe A2I OpenPOWER core at 247 stars is serious work. A full processor core in VHDL with 8 contributors. Curious how the development coordination works on something that complex. Do you hit cases where changes in one pipeline stage silently break assumptions in another? That kind of cross-module dependency seems like it'd be brutal to catch.\n\nSeverin"
    },

    # Lead 57 - mikey duplicate, skip
    # Lead 58
    "jotego": {
        "subject": "MiSTer FPGA cores from Valencia",
        "message": "Hey Jose,\n\nCreating arcade FPGA cores for MiSTer and Pocket is some of the most visible FPGA work happening right now. The SMS MiSTer core has 22 contributors. Curious what the development workflow looks like when multiple people are working on a core simultaneously. Do you have a way to catch when someone's changes break compatibility before synthesis?\n\nSeverin"
    },

    # Lead 59 - jamochl, bio is Linux/DevOps, ghdl contributor
    "jamochl": {
        "subject": "DevOps meets ghdl",
        "message": "Hey James,\n\nDevOps engineer contributing to ghdl is an interesting crossover. Curious what drew you to VHDL tooling from the Linux and containers world. Are you working on the CI/build infrastructure side of ghdl, or something closer to the simulator itself?\n\nSeverin"
    },

    # Lead 60 - bpadalino duplicate, skip
}

# Read existing outreach file
with open(OUTREACH_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# Track which usernames already have outreach written (to handle dupes)
written_usernames = set()

# First pass: collect usernames that already have outreach
for r in rows:
    if (r.get("outreach_message") or "").strip():
        written_usernames.add(r.get("username", ""))

# Apply messages to leads 11-60 (indices 10-59)
outreach_written = 0
for i in range(10, min(60, len(rows))):
    row = rows[i]
    username = row.get("username", "")

    # Skip if this person already has outreach
    if username in written_usernames:
        continue

    if username in MESSAGES:
        msg = MESSAGES[username]
        channel = msg.get("channel", row.get("outreach_channel", "email"))
        row["outreach_channel"] = channel
        row["outreach_subject"] = msg["subject"]
        row["outreach_message"] = msg["message"]
        written_usernames.add(username)
        outreach_written += 1

# Write back
with open(OUTREACH_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

# Count stats
total_with_outreach = sum(1 for r in rows if (r.get("outreach_message") or "").strip())
print(f"New outreach messages written this run: {outreach_written}")
print(f"Total rows with outreach: {total_with_outreach}")
print(f"Total rows in file: {len(rows)}")

# Print all new messages for review
print(f"\n{'='*60}")
for i in range(10, min(60, len(rows))):
    row = rows[i]
    if (row.get("outreach_message") or "").strip():
        username = row.get("username", "")
        channel = row.get("outreach_channel", "")
        subject = row.get("outreach_subject", "")
        message = row.get("outreach_message", "")
        print(f"\n--- Lead {i+1}: {username} ({channel}) ---")
        if subject:
            print(f"Subject: {subject}")
        print(f"Message:\n{message}")
