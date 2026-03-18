#!/usr/bin/env python3
"""Write outreach for the next 150 leads without messages."""

import csv

OUTREACH_FILE = "fpga_outreach_leads.csv"

MESSAGES = {
    # ROW 51 - sjaeckel: SUSE + libtom + cryptography + ghdl
    "sjaeckel": {
        "subject": "SUSE, libtom, and VHDL",
        "message": "Hey Steffen,\n\nSoftware, hardware, and cryptography at SUSE while maintaining libtom is a wide stack. Curious how the hardware side fits in. Do you use VHDL for crypto implementations, or is the ghdl contribution coming from a different angle entirely?\n\nSeverin"
    },
    # ROW 52 - DanielG: Debian developer + ghdl
    "DanielG": {
        "subject": "Debian packaging and ghdl",
        "message": "Hey Daniel,\n\nA Debian maintainer contributing to ghdl makes sense since packaging EDA tools for Linux is its own kind of challenge. Curious whether the contribution started from trying to get ghdl to build cleanly in Debian, or if the interest in VHDL came first.\n\nSeverin"
    },
    # ROW 53 - mkj: CodeConstruct + Perth + ghdl
    "mkj": {
        "subject": "CodeConstruct and ghdl",
        "message": "Hey Matt,\n\nCodeConstruct in Perth and ghdl contributions. The Australian embedded scene is smaller but tends to go deep. Is ghdl something you use at CodeConstruct, or more of a personal project? Curious how the commercial and open source sides overlap for you.\n\nSeverin"
    },
    # ROW 54 - talonmyburgh: MydonSolutions + ghdl
    "talonmyburgh": {
        "subject": "MydonSolutions and ghdl",
        "message": "Hey Talon,\n\nMydonSolutions and ghdl contributions. Curious what pulled you into the project. Did it start from needing open source VHDL simulation for work, or was it more of a tooling interest that grew into active contribution?\n\nSeverin"
    },
    # ROW 55 - suzizecat: no bio/company, ghdl - skip (too generic, low signal)
    # ROW 56 - turbinenreiter: Motius + neorv32
    "turbinenreiter": {
        "subject": "Motius and neorv32",
        "message": "Hey Sebastian,\n\nMotius does technology consulting in Munich, and you're contributing to neorv32, which is one of the most popular RISC-V cores in VHDL. Does neorv32 come up in client projects at Motius, or is this more personal interest in processor design?\n\nSeverin"
    },
    # ROW 57 - j-zeppenfeld: rust_hdl/VHDL-LS contributor!
    "j-zeppenfeld": {
        "subject": "VHDL-LS and rust_hdl",
        "message": "Hey Johannes,\n\nYou're one of 60 contributors to rust_hdl, which powers the VHDL language server that a lot of us rely on daily. Curious what part of the project you work on. The parsing layer, the LSP features, or something else? Building a real language server for VHDL feels like it requires dealing with some truly cursed corners of the spec.\n\nSeverin"
    },
    # ROW 58 - hrvach: Facebook/Meta production engineer + FPGA maker
    "hrvach": {
        "subject": "Production engineering at Meta and FPGAs",
        "message": "Hey Hrvoje,\n\nProduction engineer at Meta by day, FPGA and retro computing by night. That's a fun split. Curious whether any of the infrastructure thinking from Meta scale influences how you approach hardware projects, or if they're completely separate headspaces.\n\nSeverin"
    },
    # ROW 59 - JulianKemmerer: Philly + ghdl
    "JulianKemmerer": {
        "subject": "VHDL tooling from Philly",
        "message": "Hey Julian,\n\nPhilly doesn't have the biggest FPGA scene compared to the defense corridor or Silicon Valley. Curious what your day-to-day looks like with VHDL. Is it mostly professional work, or did open source EDA pull you in from a different direction?\n\nSeverin"
    },
    # ROW 60 - FFY00: Python core dev + nuclear physics enthusiast + ghdl
    "FFY00": {
        "subject": "Python core dev and semiconductor manufacturing",
        "message": "Hey Filipe,\n\nPython core dev, Arch Linux packager, and semiconductor manufacturing enthusiast from Portugal. That's a rare combination. Curious what the semiconductor interest looks like in practice. Is it more on the fabrication/process side, or do you actually write HDL?\n\nSeverin"
    },
    # ROW 61 - suoto: LinkedIn only, ghdl
    "suoto": {
        "channel": "linkedin",
        "subject": "",
        "message": "Hey Andre, saw your ghdl contributions from the UK. Curious what area of the project you focus on and whether you use it professionally or as a personal tool."
    },
    # ROW 62 - targeted: no bio/company/location - skip (too low signal)
    # ROW 63 - benreynwar: Independent + Tucson + ghdl
    "benreynwar": {
        "subject": "Independent FPGA work from Tucson",
        "message": "Hey Ben,\n\nIndependent and contributing to ghdl from Tucson. Curious whether the ghdl work ties into consulting or contract FPGA projects, or if it's more of a personal contribution to the ecosystem. Independent FPGA engineers seem to have interesting perspectives on tooling since they see more varied workflows.\n\nSeverin"
    },
    # ROW 64 - forrestv: no bio/company - skip (too low signal)
    # ROW 65 - thatweaver: SLAC + lcls-timing-core
    "thatweaver": {
        "subject": "LCLS timing core at SLAC",
        "message": "Hey Matt,\n\nThe LCLS timing core at SLAC with 16 contributors is specialized work. Timing distribution for a free-electron laser has some of the tightest requirements out there. Curious how the team handles changes to the VHDL when the timing margins are that critical. Is there a formal verification step, or is it more simulation-heavy?\n\nSeverin"
    },
    # ROW 66 - bellaz89: RF controllers + ghdl
    "bellaz89": {
        "subject": "RF controllers and ghdl",
        "message": "Hey,\n\nWorking on RF controllers and contributing to ghdl is a natural combination. RF control loops in FPGA have some tight latency constraints. Curious whether ghdl is part of your RF development workflow or if the contribution is more separate from the day-to-day work.\n\nSeverin"
    },
    # ROW 67 - dstadelm: Supercomputing Systems AG + VUnit
    "dstadelm": {
        "subject": "VUnit at Supercomputing Systems",
        "message": "Hey David,\n\nSupercomputing Systems AG and VUnit contributions. Curious whether VUnit is part of the verification flow at SCS, or more of a personal workflow. Companies doing high-performance computing hardware seem like a natural fit for structured VHDL verification but I rarely hear about how it actually gets adopted internally.\n\nSeverin"
    },
    # ROW 68 - Fatsie: Chips4Makers + retro computing journey
    "Fatsie": {
        "subject": "Chips4Makers and the open silicon path",
        "message": "Hey Staf,\n\nYour progression from retro computing through OrConf and 34C3 to Chips4Makers tells a story. Open silicon and ghdl contributions are a natural fit. Curious where Chips4Makers is headed. Are you targeting actual tape-outs, or more focused on the tooling and design side?\n\nSeverin"
    },
    # ROW 69 - anquegi: Telefonica/ElevenPaths + Valencia + ghdl
    "anquegi": {
        "subject": "Telefonica and ghdl",
        "message": "Hey Antonio,\n\nElevenPaths at Telefonica and ghdl contributions from Valencia is unexpected. Telecom security and VHDL don't obviously overlap. Curious whether there's a hardware security angle at Telefonica that connects these, or if the ghdl work is a separate interest.\n\nSeverin"
    },
    # ROW 70 - gojimmypi: wolfSSL + CalPoly EE + hdl4fpga
    "gojimmypi": {
        "subject": "hdl4fpga and wolfSSL embedded work",
        "message": "Hey,\n\nCalPoly EE background, wolfSSL embedded security work, and contributing to hdl4fpga at 185 stars. That's a strong embedded-to-FPGA pipeline. Curious what hdl4fpga's main use case is for you. Does it tie into the security work, or is it a separate hardware project?\n\nSeverin"
    },
    # ROW 71 - pepijndevos: obfuscated email, Netherlands + ghdl
    "pepijndevos": {
        "subject": "ghdl from Gelderland",
        "message": "Hey Pepijn,\n\nContributing to ghdl from the Netherlands. With the Dutch FPGA ecosystem being as strong as it is between ASML and the university groups, curious whether you're in that world professionally or if the VHDL work comes from a different direction.\n\nSeverin"
    },
    # ROW 72 - hdl4fpga: author of hdl4fpga, Buenos Aires
    "hdl4fpga": {
        "subject": "hdl4fpga at 185 stars",
        "message": "Hey Miguel,\n\nhdl4fpga at 185 stars with 6 contributors from Buenos Aires. Building a VHDL library that gets that kind of traction takes real commitment. What's the primary use case people are using it for? Curious whether it's mostly for prototyping or if people are pulling it into production designs.\n\nSeverin"
    },
    # ROW 73 - egk696: Java dev -> PhD -> ASIC -> FPGA at Silicom Denmark + Patmos
    "egk696": {
        "subject": "Patmos and the path from Java to FPGA",
        "message": "Hey Eleftherios,\n\nJava developer to real-time systems PhD to ASIC to FPGA at Silicom Denmark is one of the more interesting career arcs I've seen. Contributing to Patmos at 153 stars too. Curious how the real-time systems research influences your FPGA work at Silicom. Does the time-predictable architecture from Patmos show up in commercial designs?\n\nSeverin"
    },
    # ROW 74 - Nnadozie: LinkedIn only, Fronte.io, cloud
    "Nnadozie": {
        "channel": "linkedin",
        "subject": "",
        "message": "Hey Nnadozie, saw your DSD-E VHDL work. Curious how the hardware design experience at Fronte.io connects to your cloud deployment work."
    },
    # ROW 75 - dave2pi: UK + VUnit
    "dave2pi": {
        "subject": "VUnit contributions from the UK",
        "message": "Hey Dave,\n\nSaw your VUnit contributions. The UK FPGA scene spans defense, telecom, and academic groups. Curious what your main verification workflow looks like. Do you use VUnit as your primary framework, or does it supplement something else?\n\nSeverin"
    },
    # ROW 76 - jbnote: Criteo + Paris + ghdl
    "jbnote": {
        "subject": "Criteo and ghdl",
        "message": "Hey Jean-Baptiste,\n\nCriteo and ghdl contributions from Paris. Criteo does serious data processing at scale. Curious whether there's an FPGA acceleration angle at Criteo that connects to the ghdl work, or if the hardware side is a separate interest.\n\nSeverin"
    },
    # ROW 77 - DerekYu177: Shopify + Montreal + university VHDL project (1 star, skip - low value lead)
    # ROW 78 - Obijuan: URJC professor + open source advocate + ghdl-yosys-plugin
    "Obijuan": {
        "subject": "Open source FPGA at URJC",
        "message": "Hey Juan,\n\nAn assistant professor at URJC who genuinely believes in open source, contributing to the ghdl-yosys-plugin. Curious how you use open source FPGA tooling in your teaching. Do students actually use ghdl and yosys in coursework, or is it still mostly Vivado and Quartus in the classroom?\n\nSeverin"
    },
    # ROW 79 - rafaelgmota: NoCThor (1 star, skip - low signal)
    # ROW 80 - jmferreiratech: TrincaTech + NoCThor (1 star, skip)
    # ROW 81 - clynamen: Turin + ghdl
    "clynamen": {
        "subject": "ghdl contributions from Turin",
        "message": "Hey Vincenzo,\n\nContributing to ghdl from Turin. Northern Italy has a solid embedded engineering presence but open source EDA adoption seems less visible compared to Germany or the Netherlands. Is that changing, or is open source VHDL tooling still niche there?\n\nSeverin"
    },
    # ROW 82 - jarickc: VUnit, no bio/company (skip - too low signal)
    # ROW 83 - m42uko: electronics geek + Germany + ghdl
    "m42uko": {
        "subject": "Electronics and ghdl from Germany",
        "message": "Hey Markus,\n\nElectronics enthusiast contributing to ghdl from Germany. Curious whether the ghdl contribution comes from a professional FPGA workflow or more from personal hardware projects. Germany has a strong FPGA industry but the open source EDA adoption varies a lot by company.\n\nSeverin"
    },
    # ROW 84 - WayneBooth: MasterCard + Scotland + ghdl (unexpected combo!)
    "WayneBooth": {
        "subject": "MasterCard and ghdl",
        "message": "Hey Wayne,\n\nMasterCard Payment Gateway Services and ghdl contributions from Scotland. That's an unusual combination. Is there a hardware acceleration angle in payment processing, or is the VHDL work a completely separate interest? FPGA in fintech keeps growing but it's still surprising to see.\n\nSeverin"
    },
    # ROW 85 - vermaete: Belgium + VUnit
    "vermaete": {
        "subject": "VUnit from Belgium",
        "message": "Hey Jan,\n\nSaw your VUnit contributions from Belgium. Curious what your verification workflow looks like. Do you use VUnit as your main framework for VHDL testbenches, or does it complement a larger verification setup?\n\nSeverin"
    },
    # ROW 86 - hiyuh: Kyoto + nvc (Nick Gasson's VHDL simulator)
    "hiyuh": {
        "subject": "NVC contributions from Kyoto",
        "message": "Hey Masaru,\n\nContributing to nvc, which at 782 stars is becoming a serious alternative VHDL simulator. Curious what drew you to nvc over ghdl. Is it the performance angle, the codebase architecture, or something else? The fact that two competitive open source VHDL simulators exist now is pretty unusual for this space.\n\nSeverin"
    },
    # ROW 87 - lerwys: LBNL + BPM VHDL
    "lerwys": {
        "subject": "BPM firmware at LBNL",
        "message": "Hey Lucas,\n\nBeam position monitor firmware at Lawrence Berkeley National Lab. Particle accelerator instrumentation has some of the most demanding FPGA timing requirements. Curious how the firmware development workflow looks at a national lab. Do you have formal verification in the loop, or is it mostly simulation-driven?\n\nSeverin"
    },
    # ROW 88 - anton-malakhov: basics-graphics-music (Verilog educational)
    "anton-malakhov": {
        "subject": "basics-graphics-music Verilog project",
        "message": "Hey Anton,\n\nThe basics-graphics-music repo at 158 stars with 60 contributors is a big educational Verilog project. Curious what the teaching approach looks like. Is this used in a formal course, or more of a community-driven learning resource? Making FPGA accessible to beginners is hard to do well.\n\nSeverin"
    },
    # ROW 89 - kleinreact: QBayLogic + bittide-hardware (Haskell!)
    "kleinreact": {
        "subject": "Bittide hardware at QBayLogic",
        "message": "Hey Felix,\n\nQBayLogic and bittide-hardware in Haskell is a unique approach. Using Clash to generate hardware from Haskell is one of those ideas that seems either brilliant or insane depending on who you ask. Curious what the practical experience has been. Does the type system actually catch hardware bugs that VHDL or Verilog would miss?\n\nSeverin"
    },
    # ROW 90 - trabucayre: Apicula (Gowin FPGA reverse engineering)
    "trabucayre": {
        "subject": "Apicula and open source Gowin support",
        "message": "Hey Gwenhael,\n\nApicula at 647 stars is doing important work reverse-engineering Gowin FPGA bitstreams. Open source toolchains for non-Xilinx/Intel FPGAs are still rare. Curious what the biggest remaining challenge is. Is it the bitstream format complexity, or more about getting the timing models accurate enough for real designs?\n\nSeverin"
    },
    # ROW 91 - loglow: Tall Dog Electronics + MiSTer NES core
    "loglow": {
        "subject": "NES MiSTer core and Tall Dog Electronics",
        "message": "Hey Daniel,\n\nTall Dog Electronics and contributing to the NES MiSTer core at 194 stars. Running a hardware company while contributing to FPGA retro cores means you probably have opinions about development workflows. Curious how you handle testing changes to the NES core. Is it mostly manual testing on hardware, or do you have simulation in the loop?\n\nSeverin"
    },
    # ROW 92 - zero9178: ETH Zurich + MLIR/LLVM + Snitch cluster
    "zero9178": {
        "subject": "MLIR, LLVM, and Snitch cluster at ETH",
        "message": "Hey Markus,\n\nMLIR and LLVM fun while contributing to the Snitch cluster at ETH Zurich. The compiler-to-hardware pipeline is where a lot of interesting problems live. Curious how the MLIR work connects to the Snitch hardware. Are you working on lowering from MLIR to something the cluster can execute, or is it more on the hardware side?\n\nSeverin"
    },
    # ROW 93 - andreondra: Tropic Square + Prague + RISC-V
    "andreondra": {
        "subject": "Tropic Square and vesp-alpha",
        "message": "Hey Ondrej,\n\nTropic Square in Prague does secure hardware, and you're working on vesp-alpha in SystemVerilog. Hardware security chips are a niche where the verification requirements are extreme. Curious how Tropic Square handles the gap between simulation and actual silicon validation.\n\nSeverin"
    },
    # ROW 94 - rosethompson: PhD student OSU + CVW (RISC-V core, 499 stars)
    "rosethompson": {
        "subject": "CVW RISC-V core at Oklahoma State",
        "message": "Hey Rose,\n\nThe CVW RISC-V core at 499 stars with 120 contributors is impressive for a university-led project. Doing your PhD while contributing to something at that scale means you probably have strong opinions about verification. Curious what the biggest open problem is in teaching hardware design at the grad level.\n\nSeverin"
    },
    # ROW 95 - matutem: Synopsys fellow + Berkeley + OpenTitan (3226 stars!)
    "matutem": {
        "subject": "OpenTitan and processor architecture",
        "message": "Hey Matute,\n\nSynopsys fellow, processor architect at Sun Micro, and now contributing to OpenTitan at 3226 stars from Berkeley. That's a career arc that spans most of modern chip design. Curious what you think has changed most about verification methodology from the Sun days to now. The problems seem similar but the scale is completely different.\n\nSeverin"
    },
    # ROW 96 - rswarbrick: lowRISC + Cambridge + OpenTitan
    "rswarbrick": {
        "subject": "OpenTitan at lowRISC",
        "message": "Hey Rupert,\n\nlowRISC and OpenTitan from Cambridge. With 270 contributors on a security chip, the coordination challenge alone is fascinating. Curious how lowRISC manages cross-team changes that could affect security properties. Is there a formal process for reviewing hardware changes that touch the trust boundary?\n\nSeverin"
    },
    # ROW 97 - svenka3: VerifWorks + OpenTitan
    "svenka3": {
        "subject": "VerifWorks and OpenTitan verification",
        "message": "Hey Srinivasan,\n\nVerifWorks and OpenTitan contributions. A verification-focused company contributing to one of the most verification-heavy open source silicon projects makes perfect sense. Curious what the biggest gap is in open source verification IP right now. Is it coverage tools, formal methods support, or something else?\n\nSeverin"
    },
    # ROW 98 - bvaughn: React core dev at Citadel - NOT a hardware person, skip
    # ROW 99 - oswald3141: FPGA dev (VHDL, Verilog, C++) + Finland + vhdl-extras
    "oswald3141": {
        "subject": "vhdl-extras and FPGA development",
        "message": "Hey Andrei,\n\nFPGA developer doing VHDL, Verilog, and C++ from Finland, contributing to vhdl-extras. Utility libraries like that are the kind of unglamorous infrastructure that makes everyone's life easier. Curious what gap vhdl-extras fills for you that the standard libraries don't cover.\n\nSeverin"
    },
    # ROW 100 - Emoun: Patmos contributor (skip - no bio/company/location, low signal)
    # ROW 101 - mahdifani14: Co-founder + Amsterdam + Orio (autotuning)
    "mahdifani14": {
        "subject": "Orio autotuning and FPGA optimization",
        "message": "Hey Mahdi,\n\nCo-founder in Amsterdam contributing to Orio, which does autotuning for performance optimization. The intersection of automated optimization and FPGA design is interesting. Curious whether Orio touches hardware generation at all, or if it's more on the software side of the HPC stack.\n\nSeverin"
    },
    # ROW 102 - MohamedAbdelaiem: Cairo U student + RISCify
    "MohamedAbdelaiem": {
        "subject": "RISCify at Cairo University",
        "message": "Hey Mohamed,\n\nBuilding RISCify in VHDL at Cairo University. Implementing a RISC processor as a student project is a great way to learn computer architecture from the ground up. Curious what the hardest part has been. The pipeline hazard logic, or something less obvious?\n\nSeverin"
    },
    # ROW 103 - enjoy-digital: EnjoyDigital + LimeSDR
    "enjoy-digital": {
        "subject": "EnjoyDigital and LimeSDR",
        "message": "Hey Florent,\n\nEnjoyDigital contributing to LimeSDR gateware. LiteX and the broader EnjoyDigital ecosystem has become foundational for a lot of open source FPGA projects. Curious what the next frontier looks like for you. Is it broader SoC support, better tooling, or something else?\n\nSeverin"
    },
    # ROW 104 - shu-soleil: Synchrotron SOLEIL + PandABlocks-FPGA
    "shu-soleil": {
        "subject": "PandABlocks at Synchrotron SOLEIL",
        "message": "Hey Shu,\n\nPandABlocks-FPGA at Synchrotron SOLEIL. Programmable control blocks for beamline instrumentation is specialized FPGA work. With 60 contributors, it's bigger than most institutional FPGA projects. Curious how the team coordinates hardware changes when the instruments are in active use.\n\nSeverin"
    },
    # ROW 105 - CharlesAverill: UTD CS PhD + neorv32
    "CharlesAverill": {
        "subject": "neorv32 and the UTD PhD grind",
        "message": "Hey Charles,\n\nCS PhD at UTD in security while contributing to neorv32. Losing your mind grading is very relatable. Curious whether the neorv32 work ties into your security research at all. RISC-V security extensions seem like a natural intersection.\n\nSeverin"
    },
    # ROW 106 - AyaElAkhras: EPFL PhD + Dynamatic (170 stars, HLS)
    "AyaElAkhras": {
        "subject": "Dynamatic at EPFL",
        "message": "Hey Aya,\n\nDynamatic at EPFL with 170 stars is doing interesting work in dynamic high-level synthesis. The gap between HLS promise and HLS reality has been a recurring theme in the industry. Curious what Dynamatic's approach gets right that other HLS tools miss.\n\nSeverin"
    },
    # ROW 107 - dpetrisko: elephant project (skip - low signal, no bio)
    # ROW 108 - watsonjj: DESY astrophysicist + hdl-modules (198 stars)
    "watsonjj": {
        "subject": "hdl-modules and CTA at DESY",
        "message": "Hey Jason,\n\nAstrophysicist building the Cherenkov Telescope Array camera firmware at DESY, contributing to hdl-modules at 198 stars. Detector readout for gamma-ray telescopes has some wild data rate requirements. Curious whether hdl-modules came out of reusable patterns you developed for CTA, or if it predates that work.\n\nSeverin"
    },
    # ROW 109 - gfcwfzkm: microcontrollers + PCBs + TerosHDL
    "gfcwfzkm": {
        "subject": "TerosHDL and embedded hardware",
        "message": "Hey Pazzy,\n\nMostly microcontrollers and PCBs, but contributing to TerosHDL. Curious what drew you to the HDL editor tooling side. Did you start writing VHDL and find the editing experience painful enough to fix, or did the software engineering side pull you in differently?\n\nSeverin"
    },
    # ROW 110 - ohenley: Ubisoft/Autodesk/AdaCore + neorv32
    "ohenley": {
        "subject": "From Ubisoft to neorv32",
        "message": "Hey Olivier,\n\nUbisoft (with a motion patent), Autodesk, then AdaCore, and now contributing to neorv32. That trajectory from game engines to Ada to RISC-V hardware is unusual. Curious whether the Ada experience at AdaCore influenced your interest in VHDL, given the shared emphasis on strong typing and correctness.\n\nSeverin"
    },
    # ROW 111 - guilhermerc: CNPEM/LNLS + FOFB gateware
    "guilhermerc": {
        "subject": "FOFB gateware at LNLS",
        "message": "Hey Guilherme,\n\nFast orbit feedback gateware at LNLS is serious real-time FPGA work. Sub-microsecond control loops for beam stability require some tight timing. Curious how the verification workflow looks for something where latency constraints are that critical. Is it mostly simulation, or do you have hardware-in-the-loop testing?\n\nSeverin"
    },
    # ROW 112 - ivanholmes: UK + neorv32-setups
    "ivanholmes": {
        "subject": "neorv32-setups at 89 stars",
        "message": "Hey Ivan,\n\nneorv32-setups at 89 stars with 21 contributors is solid traction for a board support package collection. Curious what the most requested target board or platform is. Making a RISC-V core easy to deploy across different FPGA boards seems like it solves a real onboarding problem.\n\nSeverin"
    },
    # ROW 113 - MP2E: SNES MiSTer core + Las Vegas
    "MP2E": {
        "subject": "SNES MiSTer core",
        "message": "Hey Cray,\n\nThe SNES MiSTer core at 235 stars with 25 contributors. SNES emulation in FPGA is notoriously tricky because of the custom chips (SPC700, Mode 7, DSP). Curious which part of the SNES architecture was the hardest to get right in hardware.\n\nSeverin"
    },
    # ROW 114 - jonahshader: vampire_survivors_vhdl (fun project!)
    "jonahshader": {
        "subject": "Vampire Survivors in VHDL",
        "message": "Hey Jonah,\n\nVampire Survivors in VHDL is the kind of project that makes people double-take. Implementing a real game entirely in hardware is a genuinely hard problem. Curious how you handled the game loop. Did you use a state machine approach, or something more creative for the entity management?\n\nSeverin"
    },
    # ROW 115 - jgoeders: BYU Associate Professor + bfasst
    "jgoeders": {
        "subject": "bfasst and FPGA research at BYU",
        "message": "Hey Jeff,\n\nAssociate professor at BYU working on bfasst with 16 contributors. BYU has a strong FPGA research reputation. Curious what bfasst's main research question is. Is it about comparing different FPGA toolchain outputs, or something broader about synthesis verification?\n\nSeverin"
    },
    # ROW 116 - pintert3: Auri Studio + Kampala Uganda + TerosHDL
    "pintert3": {
        "subject": "TerosHDL contributions from Kampala",
        "message": "Hey Phillip,\n\nEmbedded engineer at Auri Studio in Kampala contributing to TerosHDL. FPGA development from Uganda is rare to see in the open source community. Curious what the HDL scene looks like there. Are there local companies doing FPGA work, or is it mostly remote/international projects?\n\nSeverin"
    },
    # ROW 117 - LorgeN: CS student Norway + vgacentrifuge VHDL project
    "LorgeN": {
        "subject": "VGA centrifuge FPGA project",
        "message": "Hey Eirik,\n\nA VGA centrifuge in VHDL with 7 contributors from Norway. That sounds like a university project with some creative scope. Curious what the centrifuge actually does. Is it a visual demo, a game, or something else entirely? FPGA projects with display output are always fun to debug.\n\nSeverin"
    },
    # ROW 118 - birdybro: MiSTer FPGA community + learning HDL
    "birdybro": {
        "subject": "Learning HDL through MiSTer",
        "message": "Hey Kevin,\n\nIT generalist learning HDL through the MiSTer community from Longmont. The MiSTer ecosystem is probably one of the best on-ramps for learning FPGA development because you get tangible results fast. Curious what's been the steepest part of the learning curve so far. The HDL syntax, or understanding the hardware concepts?\n\nSeverin"
    },
    # ROW 119 - haggaie: NVIDIA networking + Israel + VUnit
    "haggaie": {
        "subject": "VUnit and NVIDIA networking",
        "message": "Hey Haggai,\n\nNetworked systems research at NVIDIA Networking in Yokneam, contributing to VUnit. NVIDIA's networking division (ex-Mellanox) does serious FPGA and ASIC work for SmartNICs. Curious whether VUnit is part of the verification flow at NVIDIA Networking, or more of a personal tool.\n\nSeverin"
    },
    # ROW 120 - lucask07: covg_fpga (skip - low signal, no bio/company)
    # ROW 121 - 71GA: Slovenia + ghdl-yosys-plugin
    "71GA": {
        "subject": "ghdl-yosys-plugin from Slovenia",
        "message": "Hey Ziga,\n\nContributing to the ghdl-yosys-plugin from Ljubljana. The bridge between ghdl and yosys is one of the key pieces for an open source VHDL synthesis flow. Curious what your experience has been with it for actual designs. Is it production-ready, or still more of an experimental path?\n\nSeverin"
    },
    # ROW 122 - Godhart: ghdl, no bio/company (skip - low signal)
    # ROW 123 - Kitrinx: Unity Technologies + X68000 MiSTer core
    "Kitrinx": {
        "subject": "X68000 MiSTer core from Unity",
        "message": "Hey Jamie,\n\nUnity Technologies by day, X68000 MiSTer core by night. The Sharp X68000 is one of the more obscure machines to recreate in FPGA. Curious what drew you to that specific platform. The custom sprite hardware? And does working at Unity give you a different perspective on how to approach the graphics pipeline in HDL?\n\nSeverin"
    },
    # ROW 124 - torerams: Firmware Design AS + Stavanger + neorv32
    "torerams": {
        "subject": "Firmware Design AS and neorv32",
        "message": "Hey Tore,\n\nFirmware Design AS in Stavanger contributing to neorv32. Running a firmware company in Norway's oil and gas tech hub while contributing to open source RISC-V. Curious whether neorv32 is something you deploy in client projects, or if the contribution is separate from the commercial work.\n\nSeverin"
    },
    # ROW 125 - AriesKo: Satrec Initiative (satellite company!) + TerosHDL
    "AriesKo": {
        "subject": "TerosHDL at Satrec Initiative",
        "message": "Hey,\n\nSatrec Initiative does satellite imaging systems, and you're contributing to TerosHDL. Space-grade FPGA firmware for Earth observation satellites has extreme reliability requirements. Curious whether open source HDL tooling like TerosHDL is making its way into the workflow at a satellite company, or if it's still all vendor tools.\n\nSeverin"
    },
    # ROW 126 - evgeniyBolnov: Yadro MP + St Petersburg + TerosHDL
    "evgeniyBolnov": {
        "subject": "TerosHDL at Yadro",
        "message": "Hey Evgeniy,\n\nYadro MP in St. Petersburg and TerosHDL contributions. Yadro does server and networking hardware, which means serious FPGA and ASIC work. Curious how the HDL development workflow looks at Yadro. Is there appetite for open source tooling, or is it mostly commercial EDA internally?\n\nSeverin"
    },
    # ROW 127 - molnara: Solutions Architect + SNES MiSTer
    "molnara": {
        "subject": "SNES MiSTer core from Hamilton",
        "message": "Hey Adam,\n\nSolutions architect contributing to the SNES MiSTer core from Hamilton. The SNES core has 25 contributors now, which is a lot for a retro FPGA project. Curious what part of the SNES you work on. The PPU rendering, the audio DSP, or something else?\n\nSeverin"
    },
    # ROW 128 - dominiksalvet: ghdl, no bio (skip - low signal)
    # ROW 129 - henrikh: Denmark + Patmos
    "henrikh": {
        "subject": "Patmos time-predictable processor",
        "message": "Hey Henrik,\n\nContributing to Patmos from Denmark. A time-predictable processor architecture with 90 contributors is unique. Most processor designs optimize for average-case throughput, but real-time systems need worst-case guarantees. Curious what the main application domain is. Is it avionics, automotive, or something else?\n\nSeverin"
    },
    # ROW 130 - rattboi: BlueOwlDev + Portland + SMS MiSTer
    "rattboi": {
        "subject": "SMS MiSTer core from Portland",
        "message": "Hey Bradon,\n\nBlueOwlDev in Portland and contributing to the SMS MiSTer core. The Sega Master System seems simpler than SNES or Genesis, but getting the VDP timing right in FPGA is still tricky. Curious whether the SMS core is complete at this point, or if there are still edge cases in specific games.\n\nSeverin"
    },
    # ROW 131 - bjbford: Iowa State + CASPER/mlib_devel (radio astronomy!)
    "bjbford": {
        "subject": "CASPER FPGA at Iowa State",
        "message": "Hey Brian,\n\nCASPER mlib_devel at Iowa State with 150 contributors. Radio astronomy signal processing on FPGAs is some of the most demanding DSP work in the field. Curious how the CASPER framework handles the diversity of telescope backends. Is it flexible enough for different instruments, or do you end up customizing heavily per deployment?\n\nSeverin"
    },
    # ROW 132 - slacrherbst: SLAC + SURF (450 stars!)
    "slacrherbst": {
        "subject": "SURF framework at SLAC",
        "message": "Hey Ryan,\n\nSURF at 450 stars with 60 contributors is one of the most widely used FPGA firmware frameworks in physics. Curious how you manage backward compatibility as the framework evolves. With so many instruments depending on it, changes to core modules must require careful coordination.\n\nSeverin"
    },
    # ROW 133 - cdsteinkuehler: NewTek + mksocfpga (Machinekit SoC FPGA)
    "cdsteinkuehler": {
        "subject": "mksocfpga and Machinekit",
        "message": "Hey Charles,\n\nNewTek and the Machinekit SoC FPGA project. Bridging Linux-based CNC control with FPGA acceleration is a niche that needs more attention. Curious how the FPGA side handles real-time motion control. Is it mostly custom IP, or do you use SoC FPGA fabric for the timing-critical parts?\n\nSeverin"
    },
    # ROW 134 - cfelton: HDMI2USB firmware + Rochester MN
    "cfelton": {
        "subject": "HDMI2USB firmware",
        "message": "Hey Christopher,\n\nThe HDMI2USB firmware at 108 stars. Video capture and streaming on FPGA is one of those problems that sounds simple until you hit the HDMI spec and timing requirements. Curious whether the project is still actively developed or if it's more in maintenance mode now.\n\nSeverin"
    },
    # ROW 135 - olajep: LinkedIn only, Parallella hardware (422 stars!)
    "olajep": {
        "channel": "linkedin",
        "subject": "",
        "message": "Hey Ola, the Parallella hardware project at 422 stars is fascinating. Curious whether the Epiphany multicore approach still has applications you're exploring, or if you've moved on to different architectures."
    },
    # ROW 136 - Damin3927: Tokyo + many companies + CFU Proving Ground (Verilog)
    "Damin3927": {
        "subject": "CFU Proving Ground and Verilog",
        "message": "Hey Hiroaki,\n\nCFU Proving Ground in Tokyo with contributions across multiple research orgs including the Matsuo Lab. Custom function units for ML acceleration on FPGAs is a hot area. Curious what the main bottleneck is. Is it the hardware design itself, or the compiler integration to actually use the custom instructions?\n\nSeverin"
    },
    # ROW 137 - luizademelo: UFMG undergrad + Chimera (112 stars, Verilog)
    "luizademelo": {
        "subject": "Chimera at UFMG",
        "message": "Hey Luiza,\n\nChimera at 112 stars from UFMG in Belo Horizonte. A Verilog project with that kind of traction from an undergrad program is impressive. Curious what Chimera does specifically and what your contribution to it has been.\n\nSeverin"
    },
    # ROW 138 - marwaneltoukhy: LinkedIn only, Efabless + Cairo
    "marwaneltoukhy": {
        "channel": "linkedin",
        "subject": "",
        "message": "Hey Marwan, Efabless in Cairo doing open source silicon is fascinating. Curious how the SHA256 hardware implementation workflow looks and whether you use open source EDA tools for the design."
    },
    # ROW 139 - leoo-c1: Sydney + UART Verilog (skip - low signal, no bio)
    # ROW 140 - proppy: Google + GlobalFoundries PDK
    "proppy": {
        "subject": "Google and the GF180 PDK",
        "message": "Hey Johan,\n\nGoogle contributing to the GlobalFoundries 180nm PDK in Tokyo. The open source PDK movement is one of the most impactful things happening in chip design accessibility right now. Curious what the adoption looks like internally. Is Google using this for actual tape-outs, or is it more about enabling the external ecosystem?\n\nSeverin"
    },
    # ROW 141 - mithro: Tim Ansell, Wafer Space + TimVideos + F4PGA examples
    "mithro": {
        "subject": "Wafer Space and F4PGA",
        "message": "Hey Tim,\n\nWafer Space, TimVideos, and F4PGA examples from Adelaide. You've been pushing open source FPGA tooling forward for years. Curious what you think the biggest remaining blocker is for mainstream open source FPGA adoption. Is it tool maturity, vendor cooperation, or just awareness?\n\nSeverin"
    },
    # ROW 142 - alokkumardalei-wq: student + OpenROAD (skip - very junior, low signal)
    # ROW 143 - hzeller: Code Poet + Munich + yosys-f4pga-plugins
    "hzeller": {
        "subject": "Yosys F4PGA plugins from Munich",
        "message": "Hey Henner,\n\nCode poet, photographer, and maker contributing to yosys-f4pga-plugins from Munich. The F4PGA ecosystem is filling in a lot of gaps in open source FPGA synthesis. Curious what drew you to the plugin side specifically. Is there a particular FPGA target or feature you're working to support?\n\nSeverin"
    },
    # ROW 144 - MiaoHao-oops: ICT CAS + UCAS + OpenC910 (1395 stars!)
    "MiaoHao-oops": {
        "subject": "OpenC910 and heterogeneous systems",
        "message": "Hey Hao,\n\nContributing to the OpenC910 RISC-V core at 1395 stars while researching heterogeneous systems at ICT CAS. A high-performance out-of-order RISC-V core with only 5 contributors means each person touches a lot of the design. Curious what your specific area is. The memory subsystem, the execution pipeline, or the heterogeneous integration?\n\nSeverin"
    },
    # ROW 145 - giraypultar: Corundum (FPGA NIC, 67 stars) (skip - no bio)
    # ROW 146 - luarss: PrecisionInnovation + OpenROAD (skip - no bio, generic)
    # ROW 147 - Shahzaib2028: RISC-V + CHISEL + F4PGA
    "Shahzaib2028": {
        "subject": "RISC-V and Chisel development",
        "message": "Hey Muhammad,\n\nWorking on RISC-V ISA with Chisel and contributing to F4PGA examples. The Chisel-to-Verilog flow for RISC-V is an interesting design choice. Curious whether you've found Chisel's abstractions actually help catch bugs that raw Verilog would miss, or if the generated code adds its own debugging challenges.\n\nSeverin"
    },
    # ROW 148 - VJSchneid: Hannover + GF PDK (skip - no bio, low signal)
    # ROW 149 - Peter-van-Tol: LiteX-CNC (78 stars!) + Rotterdam
    "Peter-van-Tol": {
        "subject": "LiteX-CNC from Rotterdam",
        "message": "Hey,\n\nLiteX-CNC at 78 stars from Rotterdam. Bridging LiteX FPGA SoC with LinuxCNC for machine control is a practical project that fills a real gap. Curious what made you choose LiteX over a traditional FPGA approach. Was it the Python-based design flow, or the SoC integration that sold you?\n\nSeverin"
    },
    # ROW 150 - jhkim-pii: PrecisionInnovation + OpenROAD (skip - no bio)
    # ROW 151 - smosanu: UVA PhD HPLP + MEMulator
    "smosanu": {
        "subject": "MEMulator at UVA HPLP",
        "message": "Hey Sergiu,\n\nPhD at UVA's High Performance Low Power lab working on MEMulator. Memory emulation in hardware is a niche but important research area. Curious what MEMulator's target is. Emulating emerging memory technologies, or more about characterizing existing memory behavior under different workloads?\n\nSeverin"
    },
    # ROW 152 - kamilrakoczy: Antmicro + yosys-f4pga-plugins
    "kamilrakoczy": {
        "subject": "F4PGA plugins at Antmicro",
        "message": "Hey Kamil,\n\nAntmicro and yosys-f4pga-plugins. Antmicro has been one of the biggest drivers of the open source FPGA ecosystem. Curious what the internal perspective is on where F4PGA is relative to production readiness. Is it getting pulled into real customer projects, or still mostly R&D?\n\nSeverin"
    },
    # ROW 153 - hongted: OpenROAD (skip - no bio, generic)
    # ROW 154 - uglyoldbob: NESTang (436 stars, NES on Tang FPGA)
    "uglyoldbob": {
        "subject": "NESTang NES on Tang FPGA",
        "message": "Hey Thomas,\n\nContributing to NESTang at 436 stars. An NES implementation targeting Tang Nano FPGAs is a smart choice since those boards are cheap and accessible. Curious what the development workflow looks like. Do you simulate in Verilator first, or is it mostly test-on-hardware for the retro cores?\n\nSeverin"
    },
    # ROW 155 - ysba: Companytec + Brazil + DRUM (approximate multiplier)
    "ysba": {
        "subject": "DRUM approximate multiplier at Companytec",
        "message": "Hey Yuri,\n\nElectronics engineering at Companytec in Brazil, contributing to DRUM approximate multipliers. Approximate computing in hardware is one of those areas where the power savings can be massive if you can tolerate the error. Curious what the target application is. ML inference, image processing, or something else?\n\nSeverin"
    },
    # ROW 156 - newhouseb: FPGA-peripherals (185 stars) (skip - no bio)
    # ROW 157 - ggangliu: Chengdu + CFU-Playground (544 stars!)
    "ggangliu": {
        "subject": "CFU-Playground and ML acceleration",
        "message": "Hey Yonggang,\n\nCFU-Playground at 544 stars from Chengdu. Custom function units for ML acceleration on FPGAs is where a lot of edge AI is heading. Curious what models or operations you've found benefit most from custom hardware acceleration. Is it mostly convolutions, or are there other bottlenecks worth targeting?\n\nSeverin"
    },
    # ROW 158 - frno7: Sweden + jt49 (Jotego's YM2149 core)
    "frno7": {
        "subject": "JT49 YM2149 sound core",
        "message": "Hey Fredrik,\n\nContributing to jt49, the YM2149 sound chip implementation, from Sweden. Recreating vintage sound chips in FPGA requires getting the analog behavior right in digital. Curious whether you've worked with the actual hardware to validate the implementation, or if it's more documentation-driven.\n\nSeverin"
    },
    # ROW 159 - zzattack: Netherlands + SPI slave (229 stars)
    "zzattack": {
        "subject": "SPI slave at 229 stars",
        "message": "Hey Frank,\n\nThe nandland SPI slave at 229 stars from the Netherlands. A clean SPI implementation is one of those building blocks everyone needs but few people get right. Curious whether you wrote this for a specific project or more as a reusable peripheral for the community.\n\nSeverin"
    },
    # ROW 160 - intv0id: LinkedIn only, Google + TinyKalman
    "intv0id": {
        "channel": "linkedin",
        "subject": "",
        "message": "Hey Clement, TinyKalman on IHP silicon is a cool project. Curious whether the Kalman filter design was driven by a specific application or more as a proof of concept for the IHP shuttle."
    },
    # ROW 161 - mp-17: Zurich + OpenC906 (391 stars)
    "mp-17": {
        "subject": "OpenC906 RISC-V core",
        "message": "Hey Matteo,\n\nContributing to the OpenC906 from Zurich. An in-order RISC-V core at 391 stars from XuanTie with only 4 contributors means deep involvement. Curious what your focus area is. The microarchitecture, the verification, or the integration with the broader XuanTie ecosystem?\n\nSeverin"
    },
    # ROW 162 - tmichalak: Antmicro + Caravel management SoC
    "tmichalak": {
        "subject": "Caravel SoC at Antmicro",
        "message": "Hey Tomasz,\n\nAntmicro and the Caravel management SoC for Efabless shuttle runs. The open source silicon pipeline from design to tape-out is still new territory. Curious what the biggest friction point is in the flow right now. Is it the tooling, the PDK maturity, or the turnaround time?\n\nSeverin"
    },
    # ROW 163 - s-holst: Synlig (SystemVerilog to Yosys, 229 stars)
    "s-holst": {
        "subject": "Synlig SystemVerilog frontend",
        "message": "Hey Stefan,\n\nSynlig at 229 stars is doing important work bridging SystemVerilog into the Yosys ecosystem. SystemVerilog support has been the biggest gap in open source synthesis for years. Curious how complete the language coverage is now. Are most real-world designs synthesizable through Synlig, or are there still major gaps?\n\nSeverin"
    },
    # ROW 164 - WalkerLau: SoftMC (146 stars, DRAM controller)
    "WalkerLau": {
        "subject": "SoftMC DRAM controller",
        "message": "Hey,\n\nSoftMC at 146 stars from CMU-SAFARI. A software-defined DRAM controller on FPGA for memory research is a clever approach. Curious what kind of experiments it enables. Is it mainly for testing new memory scheduling policies, or does it go deeper into DRAM timing characterization?\n\nSeverin"
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
print(f"New outreach messages written: {new_count}")
print(f"Total rows with outreach: {total_with_outreach}")
print(f"Total rows in file: {len(rows)}")
