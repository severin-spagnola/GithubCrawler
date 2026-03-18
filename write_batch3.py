#!/usr/bin/env python3
"""Write outreach for leads 165-200 to reach 150+ total with messages."""

import csv

OUTREACH_FILE = "fpga_outreach_leads.csv"

MESSAGES = {
    # ROW 165 - jeehoonkang: Furiosa AI CRO + KAIST + Corundum (2230 stars!)
    "jeehoonkang": {
        "subject": "Furiosa AI and Corundum FPGA NIC",
        "message": "Hey Jeehoon,\n\nCRO at Furiosa AI in Seoul building AI chip abstractions, and contributing to Corundum at 2230 stars. An open source FPGA NIC framework at that scale is rare. Curious whether there's overlap between the networking work and what Furiosa needs for AI inference, or if these are separate interests.\n\nSeverin"
    },
    # ROW 166 - rp-jt: Digital designer at JOTEGO + jtcores (287 stars)
    "rp-jt": {
        "subject": "jtcores at JOTEGO",
        "message": "Hey Rafa,\n\nDigital designer at JOTEGO working on jtcores at 287 stars with 24 contributors. That's one of the most active arcade FPGA core projects. Curious how the team divides work across different arcade platforms. Do you specialize in specific hardware architectures, or does everyone work across the full range?\n\nSeverin"
    },
    # ROW 167 - Smeds: Clinical Genomics Uppsala (skip - the Verilog repo is bioinformatics QC, not hardware)
    # ROW 168 - macpijan: 3mdeb + Dasharo LPC module
    "macpijan": {
        "subject": "Dasharo LPC module at 3mdeb",
        "message": "Hey Maciej,\n\n3mdeb and the Dasharo verilog-lpc-module from Gdansk. Open source firmware and now open hardware for the LPC bus. Curious whether this ties into Dasharo's coreboot work, like FPGA-based TPM or BMC implementations. The intersection of open firmware and open hardware is still underexplored.\n\nSeverin"
    },
    # ROW 169 - sethirus: Thiele Machine (skip - not hardware design, more theoretical)
    # ROW 170 - davidlattimore: Rust dev + CFU-Playground (skip - primarily a Rust/software person)
    # ROW 171 - zebreus: rhdl (291 stars, Rust HDL)
    "zebreus": {
        "subject": "RHDL at 291 stars",
        "message": "Hey Lennart,\n\nContributing to RHDL at 291 stars. Hardware design in Rust is one of those ideas that keeps gaining traction. Curious how RHDL compares to other Rust-based HDL approaches like SpinalHDL or Clash. Does the Rust type system actually translate well to hardware constraints?\n\nSeverin"
    },
    # ROW 172 - oharboe: Zylin AS + Norway + OpenROAD
    "oharboe": {
        "subject": "Zylin AS and open source EDA",
        "message": "Hey Oyvind,\n\nZylin AS in Norway contributing to OpenROAD. Open source place-and-route for ASICs is still early but moving fast. Curious whether Zylin uses OpenROAD for commercial work, or if the contribution is more about pushing the ecosystem forward for everyone.\n\nSeverin"
    },
    # ROW 173 - epsilon537: hacker/surfer/engineer + USB HID host (157 stars)
    "epsilon537": {
        "subject": "USB HID host in Verilog",
        "message": "Hey Ruben,\n\nContributing to usb_hid_host at 157 stars from Belgium. USB on FPGA is one of those problems that sounds straightforward until you hit the protocol complexity. Curious whether you use this for retro computing projects or something else. The hacker/surfer/engineer/retro combo suggests MiSTer or similar.\n\nSeverin"
    },
    # ROW 174 - jeffng-or: OpenROAD flow scripts (skip - no bio)
    # ROW 175 - shimoshida: Japan + OpenFPGA (1058 stars!)
    "shimoshida": {
        "subject": "OpenFPGA at 1058 stars",
        "message": "Hey,\n\nContributing to OpenFPGA at 1058 stars from Japan. An open source FPGA architecture exploration framework with 90 contributors is serious infrastructure. Curious what part of the project you work on. The architecture generation, the bitstream tooling, or something else?\n\nSeverin"
    },
    # ROW 176 - MarioPatetta: le Cnam Paris + Corundum (2230 stars)
    "MarioPatetta": {
        "subject": "Corundum FPGA NIC at le Cnam",
        "message": "Hey Mario,\n\nContributing to Corundum at 2230 stars from le Cnam in Paris. An open source 100G FPGA NIC with only 10 contributors means each person has significant impact. Curious what your focus area is. The datapath, the PCIe interface, or the network stack integration?\n\nSeverin"
    },
    # ROW 177 - paulusmack: Microwatt (712 stars, POWER ISA in VHDL!)
    "paulusmack": {
        "subject": "Microwatt POWER core at 712 stars",
        "message": "Hey Paul,\n\nMicrowatt at 712 stars is one of the most complete open source processor cores in Verilog. A POWER ISA implementation with 27 contributors. Curious how the project handles verification at the ISA compliance level. Do you run the official POWER test suites, or is it more ad-hoc testing?\n\nSeverin"
    },
    # ROW 178 - yanghuaxuan: skip (CEO of vaporware, OpenROAD, low signal)
    # ROW 179 - suttonr: skip (ws2812 driver, 0 stars, low signal)
    # ROW 180 - growly: Berkeley + Caravel user project (229 stars)
    "growly": {
        "subject": "Caravel user project at Berkeley",
        "message": "Hey Arya,\n\nCaravel user project at 229 stars from Berkeley. The Efabless shuttle program has made it possible for students and researchers to actually tape out chips. Curious what you designed for the caravel. Did you get silicon back, and how did it compare to simulation?\n\nSeverin"
    },
    # ROW 181 - GetPsyched: DE Shaw + LunaPnR
    "GetPsyched": {
        "subject": "LunaPnR and EDA at DE Shaw",
        "message": "Hey Priyanshu,\n\nDE Shaw and contributing to LunaPnR. A new place-and-route tool in the open source EDA space is ambitious. Curious what gap LunaPnR is targeting that OpenROAD doesn't cover. Is it a different algorithmic approach, or targeting a different part of the design flow?\n\nSeverin"
    },
    # ROW 182 - wsnyder: Veripool + Verilator (3419 stars!!!)
    "wsnyder": {
        "subject": "Verilator at 3419 stars",
        "message": "Hey Wilson,\n\nVerilator at 3419 stars with 330 contributors is arguably the most important open source EDA tool in existence. Curious what you think the next major frontier is for Verilator. Is it full SystemVerilog coverage, simulation performance, or something else? The project seems to keep expanding scope while maintaining quality.\n\nSeverin"
    },
    # ROW 183 - TJackhammer: Efficient Computer + Verilator fork
    "TJackhammer": {
        "subject": "Verilator at Efficient Computer",
        "message": "Hey Tom,\n\nEfficient Computer maintaining a Verilator fork with 300 contributors. Curious what modifications you need for your workflow that upstream Verilator doesn't provide. Custom simulator features for specific architecture exploration, or more about integration with your design flow?\n\nSeverin"
    },
    # ROW 184 - zarubaf: Axelera AI + Zurich + Core-V-MCU (195 stars)
    "zarubaf": {
        "subject": "Core-V-MCU at Axelera AI",
        "message": "Hey Florian,\n\nAxelera AI in Zurich contributing to Core-V-MCU at 195 stars. The OpenHW Group RISC-V ecosystem is growing fast. Curious how the Core-V work connects to what Axelera is building for AI edge inference. Is RISC-V the control plane for the AI accelerator, or something more integrated?\n\nSeverin"
    },
    # ROW 185 - PengchengYang-xdu: Xidian MSE + PULPissimo (463 stars)
    "PengchengYang-xdu": {
        "subject": "PULPissimo and RISC-V SoC research",
        "message": "Hey Pengcheng,\n\nMSE at Xidian working on PULPissimo at 463 stars. Interested in digital IC, RISC-V, SoC, and AI accelerators. Curious which part of PULPissimo you focus on. The processor core integration, the peripheral subsystem, or the AI accelerator interface?\n\nSeverin"
    },
    # ROW 186 - Charitha-Jeewanka: Synopsys + Sri Lanka + Verilator (skip - ML engineer bio, tangential)
    # ROW 187 - godblesszhouzhou: Verilator (skip - no bio/company)
    # ROW 188 - YilouWang: PlanV Munich + verification
    "YilouWang": {
        "subject": "Verification at PlanV",
        "message": "Hey Yilou,\n\nDigital verification engineer at PlanV in Munich working on Verilator feature tests. Verification-focused companies pushing open source simulator capabilities forward is exactly what the ecosystem needs. Curious what the biggest gap in Verilator's verification feature set is from PlanV's perspective.\n\nSeverin"
    },
    # ROW 189 - phsauter: ETH PhD + open source EDA focus + PULP common_cells (723 stars)
    "phsauter": {
        "subject": "Open source EDA at ETH Zurich",
        "message": "Hey Philippe,\n\nEE PhD at ETH focused on open source EDA tools, contributing to PULP common_cells at 723 stars. That's exactly where the leverage is. Curious what your thesis work focuses on specifically. Is it about improving existing tools like Yosys or Verilator, or building something new?\n\nSeverin"
    },
    # ROW 190 - luismarques: lowRISC + Lisbon + OpenTitan
    "luismarques": {
        "subject": "OpenTitan at lowRISC from Lisbon",
        "message": "Hey Luis,\n\nlowRISC contributing to OpenTitan from Lisbon. With 270 contributors on a silicon-proven security chip, the project management challenge alone is interesting. Curious what your area of focus is within OpenTitan. The crypto accelerators, the secure boot flow, or something else?\n\nSeverin"
    },
    # ROW 191 - yanjiuntw: NKUST Taiwan + PULP AXI (1516 stars!)
    "yanjiuntw": {
        "subject": "PULP AXI library at 1516 stars",
        "message": "Hey YanJiun,\n\nContributing to the PULP AXI library at 1516 stars from Taiwan. The AXI interconnect infrastructure is one of the most reused components in the entire PULP ecosystem. Curious what drew you to this specific part of the stack. Is it the protocol complexity, or the performance optimization challenge?\n\nSeverin"
    },
    # ROW 192 - machshev: lowRISC + Cambridge + software engineer on OpenTitan
    "machshev": {
        "subject": "Software engineering on OpenTitan",
        "message": "Hey James,\n\nPrincipal software engineer at lowRISC working on OpenTitan from Cambridgeshire. Software engineering on a hardware security project is an interesting role. Curious how the software side interacts with the RTL team. Do you work on the firmware, the testing infrastructure, or something else?\n\nSeverin"
    },
    # ROW 193 - ArturBieniek4: Antmicro intern + Wroclaw + Verilator
    "ArturBieniek4": {
        "subject": "Verilator contributions at Antmicro",
        "message": "Hey Artur,\n\nCS student at Wroclaw contributing to Verilator through Antmicro. Antmicro's intern program for open source EDA tools is one of the better on-ramps for getting into this space. Curious what part of Verilator you've been working on. Simulation performance, SystemVerilog features, or something else?\n\nSeverin"
    },
    # ROW 194 - msfschaffner: Google + OpenTitan
    "msfschaffner": {
        "subject": "OpenTitan at Google",
        "message": "Hey Michael,\n\nGoogle contributing to OpenTitan at 3226 stars. Having Google's backing on an open source silicon root of trust is significant for the ecosystem. Curious what your specific area is within the project. The security architecture, the verification infrastructure, or something else?\n\nSeverin"
    },
    # ROW 195 - nickelpro: submarines + Kitware + Purdue UART
    "nickelpro": {
        "subject": "From submarines to Kitware",
        "message": "Hey Vito,\n\nSubmarines, then NYU, Purdue, and now Kitware in Brooklyn. That's a trajectory. The Purdue SoCET UART project suggests some hardware background from the academic side. Curious whether the hardware work continues at Kitware, or if you've moved fully to the software visualization side.\n\nSeverin"
    },
    # ROW 196 - farzamgl: UW Seattle + Black Parrot subsystems
    "farzamgl": {
        "subject": "Black Parrot at UW",
        "message": "Hey Farzam,\n\nBlack Parrot subsystems at UW Seattle. The Black Parrot RISC-V core is one of the more serious academic processor projects. Curious what the subsystem work involves. Is it the cache hierarchy, the coherence protocol, or something more peripheral?\n\nSeverin"
    },
    # ROW 197 - mballance: AMD + Verilator (3419 stars)
    "mballance": {
        "subject": "Verilator contributions from AMD",
        "message": "Hey Matthew,\n\nAMD and Verilator contributions from Portland. Having AMD engineers contributing to open source simulation tools is a good signal for the ecosystem. Curious whether Verilator plays a role in AMD's internal flow, or if the contribution is more personal.\n\nSeverin"
    },
    # ROW 198 - ericvanwyk: UMN + Silver (extensible language framework) - skip (not hardware)
    # ROW 199 - niyas-sait: tiny-gpu (11919 stars!!!) + Cambridge UK
    "niyas-sait": {
        "subject": "tiny-gpu at 11919 stars",
        "message": "Hey Niyas,\n\ntiny-gpu at nearly 12K stars is viral-level traction for a hardware project. Empowering Arm platforms and building a GPU from scratch in SystemVerilog. Curious what motivated the project. Was it educational, or are you exploring a real micro-GPU architecture for edge inference on Arm?\n\nSeverin"
    },
    # ROW 200 - LapinFou: Caen + verilog-mode (282 stars)
    "LapinFou": {
        "subject": "Verilog-mode from Caen",
        "message": "Hey Sebastien,\n\nContributing to verilog-mode at 282 stars from Caen. Emacs verilog-mode is one of those tools that a lot of chip designers depend on daily but few people actively maintain. Curious what drives your contributions. Is it scratching your own itch for features you need, or more community maintenance?\n\nSeverin"
    },
}

# Read existing outreach file
with open(OUTREACH_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# Track who already has outreach
written_usernames = set()
for r in rows:
    if (r.get("outreach_message") or "").strip():
        written_usernames.add(r.get("username", ""))

# Apply messages
new_count = 0
for r in rows:
    username = r.get("username", "")
    if username in MESSAGES and username not in written_usernames:
        msg = MESSAGES[username]
        channel = msg.get("channel", r.get("outreach_channel", "email"))
        r["outreach_channel"] = channel
        r["outreach_subject"] = msg["subject"]
        r["outreach_message"] = msg["message"]
        written_usernames.add(username)
        new_count += 1

# Write back
with open(OUTREACH_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

total_with_outreach = sum(1 for r in rows if (r.get("outreach_message") or "").strip())
email_count = sum(1 for r in rows if bool((r.get("email") or "").strip()))
linkedin_count = sum(1 for r in rows if bool((r.get("linkedin") or "").strip()))
both_count = sum(1 for r in rows if bool((r.get("email") or "").strip()) and bool((r.get("linkedin") or "").strip()))

print(f"New outreach messages written: {new_count}")
print(f"Total rows with outreach: {total_with_outreach}")
print(f"Total rows in file: {len(rows)}")
print(f"Email: {email_count}, LinkedIn: {linkedin_count}, Both: {both_count}")
