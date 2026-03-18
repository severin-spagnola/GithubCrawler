#!/usr/bin/env python3
"""Write outreach for next 100 leads (rows 331-406 area)."""

import csv

OUTREACH_FILE = "fpga_outreach_leads.csv"

MESSAGES = {
    # ROW 331 - gatecat / myrtle: FPGA tool dev, builds SoCs with Python, GF180 PDK
    "gatecat": {
        "subject": "FPGA tool development",
        "message": "Hey,\n\nFPGA tool dev building SoCs with Python and open tools, contributing to the GF180 PDK. Curious whether your work is more on the synthesis/PnR tool side, or the standard cell library and PDK infrastructure side. Both are critical for making open source silicon real.\n\nSeverin"
    },
    # ROW 332 - AtuL-KumaR-00: IIT BHU undergrad, OpenROAD flow scripts — skip (undergrad, no angle)
    # ROW 333 - joennlae: 44ai (former ETHZ, Huawei Research), OpenROAD — LinkedIn only
    "joennlae": {
        "subject": "",
        "message": "44ai from ETHZ and Huawei Research background, contributing to OpenROAD. What does 44ai focus on in the open source EDA space?",
        "channel": "linkedin"
    },
    # ROW 334 - ptrkrysik: Poland, UHD — skip (no bio, low signal)
    # ROW 335 - Koeng101: Caravel user project, no bio — skip
    # ROW 336 - bkushigian: UW PhD, Lakeroad evaluation (5 stars) — skip (low signal)
    # ROW 337 - stackprogramer: "$16/hour" freelancer, UHD — skip (not hardware focused)
    # ROW 338 - danc86: Sydney, CFU-Playground — skip (no bio)

    # ROW 339 - zohourih: Crusoe, Kria Vitis Platforms — LinkedIn only
    "zohourih": {
        "subject": "",
        "message": "Crusoe and Xilinx Kria Vitis platform work. Crusoe's focus on clean energy compute is interesting. Does your FPGA work connect to the energy efficiency side?",
        "channel": "linkedin"
    },
    # ROW 340 - devins2518: Purdue chiplet-components (3 stars) — skip (low signal)

    # ROW 341 - zachjs: DE Shaw, CMU, created sv2v (SystemVerilog to Verilog converter)
    "zachjs": {
        "subject": "sv2v and SystemVerilog tooling",
        "message": "Hey Zachary,\n\nDE Shaw and the creator of sv2v. A SystemVerilog to Verilog converter is one of those tools that quietly enables the entire open source FPGA toolchain. Curious whether sv2v came out of a specific need you had, or if you saw the gap in the ecosystem and decided to fill it.\n\nSeverin"
    },
    # ROW 342 - drom: SiFive, "always @ posedge", creator of WaveDrom
    "drom": {
        "subject": "WaveDrom and SiFive",
        "message": "Hey Aliaksei,\n\nSiFive and the creator of WaveDrom. Waveform visualization that works everywhere is one of those tools hardware engineers didn't know they needed until they had it. Curious how WaveDrom fits into SiFive's workflow. Is it used internally, or is it purely a community contribution?\n\nSeverin"
    },
    # ROW 343 - kurtjd: "Trying to figure out how computers work", neorv32 (2000 stars), Seattle
    "kurtjd": {
        "subject": "neorv32 from Seattle",
        "message": "Hey Kurtis,\n\nContributing to neorv32 at 2000 stars from Seattle. \"Trying to figure out how computers work\" and contributing to one of the most popular RISC-V soft cores is a great way to do it. Curious what part of neorv32 you've worked on. The processor core, the peripherals, or the SoC integration?\n\nSeverin"
    },
    # ROW 344 - peepo: UK, logi-projects (65 stars) — skip (no bio, low signal)
    # ROW 345 - LukasP46: Germany, neorv32 — skip (no bio)

    # ROW 346 - henrikbrixandersen: Vestas Wind Systems, neorv32, Zephyr RTOS expert, Aarhus
    "henrikbrixandersen": {
        "subject": "neorv32 at Vestas Wind Systems",
        "message": "Hey Henrik,\n\nEmbedded software engineer at Vestas in Aarhus contributing to neorv32 at 2000 stars, with deep Zephyr RTOS involvement. The intersection of wind turbine embedded systems and open source RISC-V is interesting. Curious whether Vestas is exploring RISC-V for industrial applications, or if the neorv32 work is personal.\n\nSeverin"
    },
    # ROW 347 - spoursalidis: FPGA/Embedded engineer, Athens — LinkedIn only
    "spoursalidis": {
        "subject": "",
        "message": "FPGA and embedded systems engineer in Athens contributing to xpm_vhdl. What types of FPGA projects do you work on professionally?",
        "channel": "linkedin"
    },
    # ROW 348 - joxheaf21: Space Invaders MiSTer (5 stars) — skip (low signal)

    # ROW 349 - c-thaler: embedded system graphics dev, Hamburg, ghdl contributor
    "c-thaler": {
        "subject": "Embedded graphics and ghdl",
        "message": "Hey Christian,\n\nHard and software developer in embedded system graphics from Hamburg, contributing to ghdl at 2767 stars. Embedded graphics and VHDL simulation is an unusual combination. Curious whether your graphics work involves FPGAs, or if ghdl is a separate interest.\n\nSeverin"
    },
    # ROW 350 - kstrohmayer: semify EDA, Graz, tristan (2 stars)
    "kstrohmayer": {
        "subject": "semify EDA from Graz",
        "message": "Hey Klaus,\n\nSemify in Graz contributing to the TRISTAN project. EDA startups in Europe working on open source verification are rare. Curious what semify's focus area is. Formal verification, simulation, or something else in the design flow?\n\nSeverin"
    },
    # ROW 351 - actorreno: Analog Devices, ADI HDL (1872 stars)
    "actorreno": {
        "subject": "Analog Devices HDL library",
        "message": "Hey Alexis,\n\nAnalog Devices contributing to the ADI HDL library at 1872 stars. The ADI reference designs are what most people start from when integrating ADI converters and transceivers on FPGAs. Curious what part of the HDL library you work on. Data converter interfaces, or the transceiver side?\n\nSeverin"
    },
    # ROW 352 - yunhe-dev: OpenROAD, no bio — skip
    # ROW 353 - browndeer: Brown Deer Technology, tiny_user_project — skip (company email, 10 stars)

    # ROW 354 - mo-hosni: Efabless, Cairo, caravel — LinkedIn only
    "mo-hosni": {
        "subject": "",
        "message": "Efabless in Cairo working on the Caravel framework. The shuttle program democratized chip tapeouts. What's your role in the project?",
        "channel": "linkedin"
    },
    # ROW 355 - xfguo: Jinglue Semi Shanghai, mor1kx (578 stars), RISC-V evangelist in China
    "xfguo": {
        "subject": "mor1kx and RISC-V in Shanghai",
        "message": "Hey Alex,\n\nJinglue Semi in Shanghai contributing to mor1kx at 578 stars. Organizing RISC-V Day Shanghai and promoting open source silicon in China. Curious how the RISC-V ecosystem in China compares to the West. Are Chinese companies more willing to adopt open ISAs than Western ones?\n\nSeverin"
    },
    # ROW 356 - yanggon-kim: UCLA, Vortex GPGPU (1926 stars)
    "yanggon-kim": {
        "subject": "Vortex GPGPU at 1926 stars",
        "message": "Hey Yang-gon,\n\nContributing to Vortex at 1926 stars from UCLA. An open source RISC-V GPGPU that runs OpenCL on FPGAs is one of the most ambitious open hardware projects. Curious what your contribution focuses on. The core pipeline, the memory hierarchy, or the software stack?\n\nSeverin"
    },
    # ROW 357 - adamgreg: Aguila Engineering, Bristol, caravel analog (1 star) — skip (low signal)
    # ROW 358 - firebull: FlattenRTL (20 stars) — skip (no bio, low signal)
    # ROW 359 - neel147063: student, f_to_f (0 stars) — skip

    # ROW 360 - nsauzede: KZS, France, "Rust C Python C++ TDD RISCV RTL", DarkRISCV (2498 stars)
    "nsauzede": {
        "subject": "DarkRISCV at 2498 stars",
        "message": "Hey Nicolas,\n\nKZS in France contributing to DarkRISCV at 2498 stars. RISC-V, RTL, and TDD in the same bio is a rare combination. Curious what drew you to DarkRISCV specifically. Is it the simplicity of the design, or are you using it as a platform for something else?\n\nSeverin"
    },
    # ROW 361 - suppamax: Munich, caravel mgmt soc litex — skip (no bio, low signal)

    # ROW 362 - matth2k: Cornell Zhang lab, eqmap (33 stars, Rust)
    "matth2k": {
        "subject": "eqmap at Cornell Zhang lab",
        "message": "Hey Matt,\n\nCornell Zhang lab contributing to eqmap at 33 stars. Equivalence checking and mapping tools are critical for trusting open source synthesis flows. Curious whether eqmap is aimed at verifying Yosys output, or if it targets a different part of the design flow.\n\nSeverin"
    },
    # ROW 363 - Tiebe: Netherlands, ZipCPU/vgasim (177 stars) — skip (no bio)

    # ROW 364 - jonas-kaufmann: MPI-SWS PhD, SimBricks (169 stars)
    "jonas-kaufmann": {
        "subject": "SimBricks at MPI-SWS",
        "message": "Hey Jonas,\n\nPhD at MPI-SWS contributing to SimBricks at 169 stars. A modular full-system simulator that can combine different simulation engines is a powerful approach. Curious whether SimBricks connects FPGA simulation with network and OS simulation, or if the focus is elsewhere.\n\nSeverin"
    },
    # ROW 365 - gtaylormb: FPGA/embedded engineer, Brooklyn, ao486_MiSTer (334 stars), ex-NASA
    "gtaylormb": {
        "subject": "ao486 MiSTer and FPGA engineering",
        "message": "Hey Greg,\n\nFPGA and embedded systems engineer in Brooklyn contributing to ao486_MiSTer at 334 stars, with an aerospace background. Reimplementing a 486 in an FPGA is one of the more complex MiSTer cores. Curious whether the aerospace experience informs how you approach FPGA design, or if it's a completely different domain.\n\nSeverin"
    },
    # ROW 366 - xixi-shredp: yosys-sta (93 stars), no bio — skip

    # ROW 367 - clmcsn: Giuseppe Sarda, KU Leuven, Vortex GPGPU
    "clmcsn": {
        "subject": "Vortex GPGPU at KU Leuven",
        "message": "Hey Giuseppe,\n\nKU Leuven contributing to Vortex at 1926 stars. An open source RISC-V GPGPU with OpenCL support on FPGAs is ambitious. Curious whether your work on Vortex is part of your research at KU Leuven, or a separate contribution.\n\nSeverin"
    },
    # ROW 368 - CrazybinaryLi: ICT Chinese Academy of Sciences, Synlig (229 stars)
    "CrazybinaryLi": {
        "subject": "Synlig at Chinese Academy of Sciences",
        "message": "Hey Yufeng,\n\nInstitute of Computing Technology at CAS contributing to Synlig at 229 stars. SystemVerilog synthesis for Yosys is critical for making open source toolchains handle industrial designs. Curious what specific synthesis challenges you work on at ICT.\n\nSeverin"
    },
    # ROW 369 - Lucaz97: NYU Tandon PhD, OpenFPGA (1058 stars)
    "Lucaz97": {
        "subject": "OpenFPGA at NYU Tandon",
        "message": "Hey Luca,\n\nPhD in ECE at NYU Tandon contributing to OpenFPGA at 1058 stars. Working on FPGA architecture exploration as a PhD topic is great positioning. Curious whether your research focuses on new FPGA architectures, the bitstream generation, or something else in the OpenFPGA framework.\n\nSeverin"
    },
    # ROW 370 - gbrown40: data science student, MacroPlacement — skip (data science, not hardware)

    # ROW 371 - Siris-Li: Peking University, CFU-Playground (544 stars)
    "Siris-Li": {
        "subject": "CFU-Playground at Peking University",
        "message": "Hey Mingxuan,\n\nPeking University contributing to CFU-Playground at 544 stars. Custom function units for ML inference acceleration on FPGAs is a hot research area. Curious what type of ML workload your CFU targets. Image classification, NLP, or something else?\n\nSeverin"
    },
    # ROW 372 - Icenowy: Linux kernel contributor, LiteX — skip (primarily Linux/software)

    # ROW 373 - Intuity: Peter Birch, Bristol, TinyTapeout mpw7
    "Intuity": {
        "subject": "TinyTapeout from Bristol",
        "message": "Hey Peter,\n\nTinyTapeout MPW7 contributor from Bristol. TinyTapeout has made it possible for individuals to get silicon for the first time. Curious what you designed for your tile. A custom logic block, a small processor, or something more creative?\n\nSeverin"
    },
    # ROW 374 - Natrox: Netherlands, Genesis_MiSTer (131 stars)
    "Natrox": {
        "subject": "Genesis MiSTer core",
        "message": "Hey Lea,\n\nContributing to Genesis_MiSTer at 131 stars from the Netherlands. The Sega Genesis/Mega Drive is one of the most popular MiSTer cores. Curious what part of the Genesis you focus on. The VDP, the YM2612 sound chip, or the overall system integration?\n\nSeverin"
    },
    # ROW 375 - coralmw: POETSII, "expressive FPGA languages", tinytapeout — skip (0 stars, low signal)

    # ROW 376 - bobnewgard: wb2axip (648 stars) — LinkedIn only, no bio — skip

    # ROW 377 - Manarabdelaty: Brown University, Caravel mpw-one
    "Manarabdelaty": {
        "subject": "Caravel MPW-1 at Brown",
        "message": "Hey Manar,\n\nContributing to Caravel MPW-1 at 137 stars from Brown University in Providence. The first multi-project wafer run through Efabless was a milestone for open source silicon. Curious what you designed for the first shuttle. Did you get silicon back?\n\nSeverin"
    },
    # ROW 378 - juampe: openc910 (1395 stars), no bio — skip (no angle)

    # ROW 379 - soumilheble: NC State ECE grad, maker, SERV (1762 stars)
    "soumilheble": {
        "subject": "SERV RISC-V from Massachusetts",
        "message": "Hey Soumil,\n\nNC State ECE graduate contributing to SERV at 1762 stars from Massachusetts. The world's smallest RISC-V CPU, and a maker contributing to it. Curious whether you use SERV in your own projects where area is a constraint, or if it was more of a learning contribution.\n\nSeverin"
    },
    # ROW 380 - whitequark / Catherine: SCISemi, Amaranth HDL creator, Glasgow
    "whitequark": {
        "subject": "Amaranth HDL and Glasgow",
        "message": "Hey Catherine,\n\nSCISemi, and the creator of Amaranth and Glasgow. Amaranth made Python-based hardware design practical, and Glasgow made FPGA-based electronics debugging accessible. Curious where Amaranth is headed next. More synthesis target support, or deeper into the verification side?\n\nSeverin"
    },
    # ROW 381 - monniaux: CNRS/VERIMAG Grenoble, Astrée developer, VeeRwolf (338 stars)
    "monniaux": {
        "subject": "Formal verification and VeeRwolf",
        "message": "Hey David,\n\nCNRS/VERIMAG research director and former Astrée developer, contributing to VeeRwolf at 338 stars. From proving C program correctness to working with RISC-V SoCs. Curious whether you're applying formal methods to the hardware side now, or if the VeeRwolf work is a different interest.\n\nSeverin"
    },
    # ROW 382 - mgwoo: Qualcomm, PhD UCSD, main developer of OpenROAD placement/floorplan
    "mgwoo": {
        "subject": "OpenROAD placement at Qualcomm",
        "message": "Hey Mingyu,\n\nMain developer of OpenROAD's floorplanning and placement tools, now at Qualcomm. 600+ tapeouts using the tools you built is a serious legacy. Curious whether Qualcomm uses any open source EDA tools internally, or if the commercial and open source worlds are still separate.\n\nSeverin"
    },
    # ROW 383 - MorgothCreator: Arduboy MiSTer (12 stars) — skip (low signal)
    # ROW 384 - ghanesimit: student, ice40-playground — skip
    # ROW 385 - lromor: New Theory, Amsterdam, fomu-workshop (169 stars)
    "lromor": {
        "subject": "Fomu workshop from Amsterdam",
        "message": "Hey Leonardo,\n\nNew Theory in Amsterdam contributing to the Fomu workshop at 169 stars. Teaching FPGA development on a USB-form-factor board with an open source toolchain is one of the best on-ramps for beginners. Curious whether you use Fomu in workshops professionally, or if it's a community contribution.\n\nSeverin"
    },
    # ROW 386 - zhajio1988: digital verification engineer, "Freestyle", Juniper ORDT (207 stars)
    "zhajio1988": {
        "subject": "Juniper open register design tool",
        "message": "Hey Jude,\n\nDigital verification engineer contributing to Juniper's Open Register Design Tool at 207 stars. Register management tools are one of those unglamorous but essential parts of the design flow. Curious whether you use ORDT in your professional verification work, or if it's a side contribution.\n\nSeverin"
    },
    # ROW 387 - dklowden: Intel, AIB PHY hardware (68 stars)
    "dklowden": {
        "subject": "AIB PHY at Intel",
        "message": "Hey Daniel,\n\nIntel contributing to the AIB PHY hardware at 68 stars. Advanced Interface Bus was Intel's answer to chiplet interconnect. Curious how the AIB ecosystem has evolved since Intel open sourced it. Is there adoption outside of Intel, or is the industry consolidating around UCIe?\n\nSeverin"
    },
    # ROW 388 - hyf6661669: Digital IC designer, Beijing, DarkRISCV (2498 stars)
    "hyf6661669": {
        "subject": "DarkRISCV and IC design",
        "message": "Hey,\n\nDigital IC designer in Beijing contributing to DarkRISCV at 2498 stars. One of the most popular RISC-V implementations. Curious whether you use DarkRISCV as a reference for your professional IC work, or if the contribution is more about learning and community.\n\nSeverin"
    },
    # ROW 389 - danpage: University of Bristol, SCARV xcrypto (92 stars)
    "danpage": {
        "subject": "SCARV crypto extensions at Bristol",
        "message": "Hey Daniel,\n\nUniversity of Bristol contributing to SCARV xcrypto at 92 stars. Cryptographic ISA extensions for RISC-V with a focus on side-channel resistance is exactly the kind of research that needs to happen before these extensions go into production. Curious whether the Bristol SCALE lab's side-channel expertise directly feeds into the xcrypto design.\n\nSeverin"
    },
    # ROW 390 - mobluse: physicist, many languages, apple-one (149 stars) — LinkedIn only, skip (tangential)

    # ROW 391 - oleg-nenashev: Jenkins maintainer, CNCF Ambassador, HW/Embedded background, OpenRISC
    "oleg-nenashev": {
        "subject": "DevTools and hardware background",
        "message": "Hey Oleg,\n\nDev tools engineer with HW/Embedded background from Intel and Synopsys, Jenkins core maintainer, contributing to OpenRISC. The transition from hardware to developer tooling is interesting. Curious whether you see parallels between CI/CD for software and the hardware verification workflow.\n\nSeverin"
    },
    # ROW 392 - rbarzic: Onio, Trondheim, nanorv32 (32 stars)
    "rbarzic": {
        "subject": "nanorv32 from Trondheim",
        "message": "Hey Ronan,\n\nOnio in Trondheim and nanorv32 at 32 stars. Building your own RISC-V core is the best way to really understand the architecture. Curious whether nanorv32 ties into what Onio is building, or if it's a personal project.\n\nSeverin"
    },
    # ROW 393 - andrewray: UK, mor1kx (578 stars) — skip (no bio)

    # ROW 394 - ezelioli: PULP platform, Zurich, CROC (212 stars)
    "ezelioli": {
        "subject": "PULP CROC at 212 stars",
        "message": "Hey Enrico,\n\nPULP platform in Zurich contributing to CROC at 212 stars. A compact RISC-V core from the PULP ecosystem with 10 contributors. Curious what CROC's target application is. Is it aimed at ultra-low-power IoT, or something else?\n\nSeverin"
    },
    # ROW 395 - jeremybennett: Embecosm, Lymington UK, Core-V-MCU
    "jeremybennett": {
        "subject": "Embecosm and Core-V-MCU",
        "message": "Hey Jeremy,\n\nEmbecosm in Lymington contributing to Core-V-MCU at 195 stars. Embecosm's compiler and toolchain expertise applied to the OpenHW RISC-V ecosystem is a strong fit. Curious what Embecosm's specific role is in the Core-V project. Toolchain support, simulation, or something else?\n\nSeverin"
    },
    # ROW 396 - githubhjs: 20yr IC design veteran, Taiwan, open to work
    "githubhjs": {
        "subject": "20 years of IC design from Taiwan",
        "message": "Hey Josh,\n\nDigital IC design engineer with 20 years covering design, verification, synthesis, LEC, and automation. That's a complete skill set across the entire front-end flow. Curious what types of designs you've worked on most. ASICs, FPGAs, or both?\n\nSeverin"
    },
    # ROW 397 - Yang-YiFan: Nvidia DL Inference Architecture, Intel FPGA BBB
    "Yang-YiFan": {
        "subject": "DL inference architecture at Nvidia",
        "message": "Hey Yifan,\n\nDeep learning inference architecture at Nvidia, with Intel FPGA building block contributions. The intersection of ML inference optimization and FPGA acceleration is exactly where the industry is headed. Curious whether the FPGA work was at Intel, or if it connects to what you do at Nvidia now.\n\nSeverin"
    },
    # ROW 398 - efectn: gofiber maintainer, Türkiye, vicuna2_core (17 stars) — skip (backend dev, tangential)

    # ROW 399 - bekbeis: Ibex contributor, no company — skip (low signal)

    # ROW 400 - doganulus: Bogazici University CS professor, CVW (499 stars)
    "doganulus": {
        "subject": "CORE-V Wally at Bogazici",
        "message": "Hey Dogan,\n\nCS professor at Bogazici contributing to CORE-V Wally at 499 stars. A configurable RISC-V processor that boots Linux and passes arch tests is a strong teaching platform. Curious whether you use Wally in your courses at Bogazici, or if the contribution connects to your formal verification research.\n\nSeverin"
    },
    # ROW 401 - Zain2050: 10xEngineers, UET Lahore, CVW — skip (student/associate, low signal)

    # ROW 402 - sr-TT: Tenstorrent, Sr Engineer RISC-V, Bangalore
    "sr-TT": {
        "subject": "RISC-V at Tenstorrent",
        "message": "Hey Sharanesh,\n\nSenior RISC-V engineer at Tenstorrent in Bangalore. Tenstorrent's bet on RISC-V for AI accelerators is one of the biggest endorsements the architecture has gotten. Curious what the RISC-V work looks like at Tenstorrent. Is it the control plane for the AI cores, or a more integrated role?\n\nSeverin"
    },
    # ROW 403 - mtimkovich: Seattle, Caliptra RTL (133 stars), "Melee Rocket League Developer"
    "mtimkovich": {
        "subject": "Caliptra silicon root of trust",
        "message": "Hey Max,\n\nContributing to Caliptra RTL at 133 stars from Seattle. An open source silicon root of trust backed by Microsoft, Google, Nvidia, and AMD is serious infrastructure. Curious what part of the Caliptra design you work on. The crypto engine, the secure boot flow, or the SoC integration?\n\nSeverin"
    },
    # ROW 404 - akashlevy: Silimate (YC S23), Stanford PhD, Ibex contributor
    "akashlevy": {
        "subject": "Silimate and chip design AI",
        "message": "Hey Akash,\n\nSilimate (YC S23) with a Stanford PhD and three tapeouts, contributing to Ibex. Building an AI debugger for chip designers is exactly the kind of tool the industry needs. Curious what the biggest debugging bottleneck is that Silimate solves. Is it RTL bugs, timing closure, or something else?\n\nSeverin"
    },
    # ROW 405 - nbdd0121: Cambridge UK, OpenTitan — skip (no bio)

    # ROW 406 - bluegate010: Google, Caliptra RTL
    "bluegate010": {
        "subject": "Caliptra at Google",
        "message": "Hey Jeff,\n\nGoogle contributing to Caliptra RTL at 133 stars. With Microsoft, Google, Nvidia, and AMD all backing Caliptra, it's shaping up to be the industry standard open source root of trust. Curious what Google's specific role is in the project. The architecture definition, or the RTL implementation?\n\nSeverin"
    },

    # ROW 407 - suehnel: ensilica, OpenTitan — skip (no bio)

    # ROW 408 - karmanyaahm: UT Austin, ozone-processor (5 stars), robots
    "karmanyaahm": {
        "subject": "Ozone processor at UT Austin",
        "message": "Hey Karmanyaah,\n\nUT Austin building the Ozone processor with 15 contributors. A student team building a processor from scratch is one of the best learning experiences in computer engineering. Curious what ISA Ozone targets and how far along the design is.\n\nSeverin"
    },
    # ROW 409 - steven-bellock: Nvidia, confidential computing, Caliptra RTL
    "steven-bellock": {
        "subject": "Caliptra and confidential computing at Nvidia",
        "message": "Hey Steven,\n\nSystem software security engineer at Nvidia working on confidential computing, contributing to Caliptra RTL. Hardware-rooted security for confidential computing is where the industry is headed. Curious how Caliptra fits into Nvidia's confidential computing stack.\n\nSeverin"
    },
    # ROW 410 - ncde: KTH Stockholm, Learn FPGA Programming (205 stars)
    "ncde": {
        "subject": "FPGA learning at KTH",
        "message": "Hey Niyazi,\n\nKTH in Stockholm contributing to Learn FPGA Programming at 205 stars. Educational FPGA resources with real traction are valuable for the ecosystem. Curious whether this connects to coursework at KTH, or if it's a community contribution.\n\nSeverin"
    },
    # ROW 411-412 — skip (low signal)

    # ROW 413 - DurandA: Switzerland, betrusted-soc (157 stars)
    "DurandA": {
        "subject": "Betrusted SoC from Switzerland",
        "message": "Hey Arnaud,\n\nContributing to betrusted-soc at 157 stars from Switzerland. Betrusted's approach of building a secure communication device with an open source SoC designed for auditability is unique. Curious what part of the project you work on.\n\nSeverin"
    },
    # ROW 414 - jerryz123: OpenAI Computer Architect, ex-Cal, rocket-chip
    "jerryz123": {
        "subject": "Computer architecture at OpenAI",
        "message": "Hey Jerry,\n\nComputer architect at OpenAI, Cal alum, with Rocket-Chip contributions. Going from RISC-V chip design at Berkeley to AI compute architecture at OpenAI is a strong trajectory. Curious what the hardware architecture challenges look like at OpenAI scale.\n\nSeverin"
    },
    # ROW 415 - xobs: Sean Cross, Foosn/Kosagi, Singapore, valentyusb
    "xobs": {
        "subject": "ValentyUSB and Foosn",
        "message": "Hey Sean,\n\nFoosn and Kosagi in Singapore contributing to ValentyUSB at 133 stars. USB implemented in an FPGA using Python/Migen is the kind of project that makes hardware development more accessible. Curious whether ValentyUSB is something you use in Foosn's products, or if it's a standalone contribution.\n\nSeverin"
    },
    # ROW 416 - laborleben: DHL Group, pymosa — skip (not hardware focused)
    # ROW 417 - tpwrules: apertus open source cinema (45 stars) — skip (Python, low signal)

    # ROW 418 - parasxos: CERN, Geneva, VMM boards firmware
    "parasxos": {
        "subject": "VMM boards at CERN",
        "message": "Hey Paris,\n\nSoftware engineer at CERN in Geneva working on VMM boards firmware. Detector readout electronics at CERN is one of the most demanding FPGA applications. Curious whether the VMM firmware involves custom data acquisition logic, or more standard readout protocols.\n\nSeverin"
    },
    # ROW 419 - spark2k06: Spain, PCXT_MiSTer (59 stars)
    "spark2k06": {
        "subject": "PC XT MiSTer core from Spain",
        "message": "Hey Aitor,\n\nPCXT_MiSTer at 59 stars with 12 contributors from Spain. Reimplementing an IBM PC XT in an FPGA is a fascinating challenge. Getting the 8088 and CGA/MDA timing right for compatibility. Curious how accurate the core is. Does it run most DOS software correctly?\n\nSeverin"
    },
    # ROW 420 - bkaney: Vermonster, Rust project — skip (not hardware)

    # ROW 421 - bornaehsani: Apple Senior GPU Software Engineer, bsg_replicant
    "bornaehsani": {
        "subject": "GPU engineering at Apple",
        "message": "Hey Borna,\n\nSenior GPU software engineer at Apple, with BSG replicant contributions. The intersection of GPU software and hardware replication frameworks is interesting. Curious whether the hardware side connects to your work at Apple, or if it's a separate interest.\n\nSeverin"
    },
    # ROW 422 - ucbjrl: UC Berkeley, Chisel2 (388 stars)
    "ucbjrl": {
        "subject": "Chisel at UC Berkeley",
        "message": "Hey Jim,\n\nUC Berkeley contributing to Chisel2 at 388 stars. Chisel fundamentally changed how people think about hardware description languages. Curious whether you were involved in the early Chisel development, and what you think about the current Chisel/FIRRTL/CIRCT evolution.\n\nSeverin"
    },
    # ROW 423-430 — skip (all low signal: 0-7 stars, no bios)

    # ROW 431 - VladisM: Siemens Prague, custom CPU architecture, MARK_II (28 stars)
    "VladisM": {
        "subject": "MARK II custom CPU at Siemens",
        "message": "Hey Vladislav,\n\nSiemens in Prague building a custom CPU architecture and toolchain in your free time. MARK_II at 28 stars with your own ISA, assembler, and toolchain. Curious what design decisions led you to create a custom architecture rather than building on RISC-V or another open ISA.\n\nSeverin"
    },
    # ROW 432-436 — skip (low signal)

    # ROW 437 - mohammadhgh: Tehran, OpenHBMC (83 stars)
    "mohammadhgh": {
        "subject": "OpenHBMC from Tehran",
        "message": "Hey Mohammad,\n\nContributing to OpenHBMC at 83 stars from Tehran. An open source HyperBus memory controller is useful for FPGA projects that need fast external memory. Curious whether you use this in your own FPGA projects, or if it was built to fill a gap in the ecosystem.\n\nSeverin"
    },
    # ROW 438 - moloned: Ubotica, Dublin — skip (svo-raycaster 2 stars, tangential)
    # ROW 439-443 — skip (low signal)

    # ROW 444 - motchy869: Anritsu Corporation, FPGA/DSP engineer, RF measuring instruments
    "motchy869": {
        "subject": "FPGA DSP at Anritsu",
        "message": "Hey,\n\nFPGA and DSP engineer at Anritsu in Kanagawa working on RF measuring instruments. Signal processing on FPGAs for precision measurement is one of the more demanding applications. Curious what the typical FPGA architecture looks like for an RF instrument. Custom DSP blocks, or more standard signal chains?\n\nSeverin"
    },
    # ROW 445 - Poofjunior: Allen Neural Dynamics, formerly Machine Agency, HardwareModules (27 stars)
    "Poofjunior": {
        "subject": "Hardware modules for neural dynamics",
        "message": "Hey Sonya,\n\nEngineer at Allen Neural Dynamics in Seattle with HardwareModules at 27 stars. Neuroscience instrumentation and custom hardware design is a niche that needs more open source work. Curious whether the hardware modules connect to your neural dynamics instrumentation work.\n\nSeverin"
    },
    # ROW 446 - dennistyleo: AI CHIP Taipei, embedded systems
    "dennistyleo": {
        "subject": "AI infrastructure at AI CHIP",
        "message": "Hey Dennis,\n\nAI CHIP in Taipei working on AI infrastructure and embedded systems, detecting failures before they exist. Curious what AI CHIP builds specifically. Custom AI accelerators, or tooling and infrastructure for existing chip platforms?\n\nSeverin"
    },
    # ROW 447-450 — skip (low signal)

    # ROW 451 - matiasilva: ASIC Engineer at Raspberry Pi, riscv-soc, Cambridge UK
    "matiasilva": {
        "subject": "ASIC design at Raspberry Pi",
        "message": "Hey Matias,\n\nASIC engineer at Raspberry Pi in Cambridge with a RISC-V SoC project. Raspberry Pi designing their own silicon is one of the more impressive hardware company evolutions. Curious whether the RISC-V SoC is related to your work at Pi, or a personal exploration.\n\nSeverin"
    },
    # ROW 452 - osaidnur: Birzeit University, Palestine — skip (student, 1 star)

    # ROW 453 - RadioactiveScandium: Google Silicon Digital Design Engineer, Bangalore
    "RadioactiveScandium": {
        "subject": "Silicon design at Google Bangalore",
        "message": "Hey Saransh,\n\nSilicon digital design engineer at Google in Bangalore. Google's in-house chip design from Tensor to custom data center silicon is expanding fast. Curious what type of designs you work on. Custom accelerators, or more general-purpose infrastructure?\n\nSeverin"
    },
    # ROW 454 - dpretet: FPGA/ASIC Design Engineer, axi-crossbar (212 stars) — LinkedIn only
    "dpretet": {
        "subject": "",
        "message": "FPGA/ASIC design engineer with axi-crossbar at 212 stars. Building your own AXI interconnect from scratch is serious IP work. What drove you to build it?",
        "channel": "linkedin"
    },
    # ROW 455-459 — skip (low signal)

    # ROW 460 - lmbollen: QBayLogic, Enschede, verilog-ethernet (2878 stars!)
    "lmbollen": {
        "subject": "QBayLogic and verilog-ethernet",
        "message": "Hey Lucas,\n\nQBayLogic in Enschede contributing to verilog-ethernet at 2878 stars. QBayLogic does Clash-based FPGA development, and verilog-ethernet is one of the most widely used FPGA IP cores. Curious how the Clash workflow at QBayLogic interacts with traditional Verilog IP like this.\n\nSeverin"
    },
    # ROW 461-464 — skip (students, low signal)

    # ROW 465 - taichi-ishitani: PEZY Computing, Kanagawa, rggen (register generator)
    "taichi-ishitani": {
        "subject": "RgGen at PEZY Computing",
        "message": "Hey Taichi,\n\nPEZY Computing in Kanagawa maintaining RgGen. A register generator that outputs RTL and documentation from a single source of truth is exactly the kind of tool that saves hardware teams from register spec drift. Curious whether PEZY uses RgGen internally for their many-core processors.\n\nSeverin"
    },
    # ROW 466-467 — skip (low signal)

    # ROW 468 - nitheeshkm: NEP Group R&D, Baltimore, Digital-IDE (394 stars)
    "nitheeshkm": {
        "subject": "Digital IDE at 394 stars",
        "message": "Hey Nitheesh,\n\nR&D engineer at NEP Group contributing to Digital-IDE at 394 stars. A VSCode extension for HDL development with 394 stars shows real demand for better hardware development tooling. Curious whether you use Digital-IDE in your professional work at NEP, or if the contribution is community-driven.\n\nSeverin"
    },
    # ROW 469-471 — skip (low signal)

    # ROW 472 - gsmecher: Three-Speed Logic, Victoria BC, minimax (224 stars)
    "gsmecher": {
        "subject": "Minimax RISC-V at 224 stars",
        "message": "Hey Graeme,\n\nThree-Speed Logic in Victoria contributing minimax at 224 stars. A compressed RISC-V core that fits in minimal FPGA resources is exactly the kind of design where every LUT counts. Curious what the target application is for minimax. Ultra-small control planes, or something else?\n\nSeverin"
    },
    # ROW 473 - AngeloJacobo: Philippines, RISC-V (121 stars)
    "AngeloJacobo": {
        "subject": "RISC-V core from the Philippines",
        "message": "Hey Angelo,\n\nRISC-V implementation at 121 stars from Bulacan. Building your own RISC-V core and getting 121 stars shows real quality. Curious what features your implementation supports and whether you've gotten it running on an FPGA.\n\nSeverin"
    },
    # ROW 474-476 — skip (low signal, obfuscated emails)

    # ROW 478 - markeby: 49yr veteran, retired Intel, pre-silicon verification
    "markeby": {
        "subject": "49 years in hardware engineering",
        "message": "Hey Mark,\n\n49 years from aerospace to pre-silicon functional verification at Intel, retired in 2024. That's an incredible career arc spanning the entire modern semiconductor era. Curious what the biggest shift in verification methodology was over those five decades.\n\nSeverin"
    },
    # ROW 479-480 — skip

    # ROW 481 - johnMamish: Georgia Tech PhD, Ka Moamoa lab, embedded systems, jfpjc
    "johnMamish": {
        "subject": "Embedded FPGA at Georgia Tech",
        "message": "Hey John,\n\nPhD at Georgia Tech in the Ka Moamoa mobile computing lab, focused on embedded systems. Curious whether your FPGA work connects to the mobile computing research. Custom hardware for ultra-low-power sensing, or something else?\n\nSeverin"
    },
    # ROW 482 - thirtythreeforty: AWS, embedded systems, LiteX (3771 stars!)
    "thirtythreeforty": {
        "subject": "LiteX at 3771 stars",
        "message": "Hey George,\n\nAWS with a passion for embedded systems and free software, contributing to LiteX at 3771 stars. LiteX has quietly become one of the most important SoC builders in the open source hardware ecosystem. Curious whether you use LiteX for personal FPGA projects, or if there's a connection to your work at AWS.\n\nSeverin"
    },
    # ROW 483 - blackcathj: Brookhaven National Lab physicist — skip (physics, not hardware design)
    # ROW 484 - staticfloat: Valve Software — skip (Julia, not hardware)
    # ROW 485 - XVilka: Rizin reverse engineering, F4PGA ideas — skip (RE focus)
    # ROW 486-495 — skip (non-hardware)

    # ROW 496 - enathang: Seattle, bittide-hardware (25 stars, Haskell)
    "enathang": {
        "subject": "Bittide hardware in Haskell",
        "message": "Hey Nathan,\n\nContributing to bittide-hardware at 25 stars from Seattle. Hardware design in Haskell through Clash is an interesting approach. Curious whether bittide targets a specific application, or if it's more of a platform for exploring hardware/software co-design.\n\nSeverin"
    },
    # ROW 498 - AaronJackson: University of Dundee, Glasgow (2133 stars!)
    "AaronJackson": {
        "subject": "Glasgow interface explorer",
        "message": "Hey Aaron,\n\nUniversity of Dundee contributing to Glasgow at 2133 stars. An FPGA-based electronics debugging tool that's become one of the most popular open hardware projects. Curious what drew you to the project and what part you contribute to.\n\nSeverin"
    },
    # ROW 500 - davidgiven: Zürich, FluxEngine (418 stars)
    "davidgiven": {
        "subject": "FluxEngine from Zürich",
        "message": "Hey David,\n\nFluxEngine at 418 stars from Zürich. A USB floppy disk flux reader and writer that preserves disk data at the magnetic level is important archival work. Curious whether this uses FPGA-based signal processing, or if it's purely microcontroller-driven.\n\nSeverin"
    },
    # ROW 524 - craigjb: SpinalHDL (1933 stars), Scottsdale AZ
    "craigjb": {
        "subject": "SpinalHDL at 1933 stars",
        "message": "Hey Craig,\n\nContributing to SpinalHDL at 1933 stars from Scottsdale. SpinalHDL's Scala-based approach to hardware design has built a strong community. Curious what you work on within SpinalHDL. The core language features, the library ecosystem, or specific IP blocks?\n\nSeverin"
    },
    # ROW 554 - aswaterman: SiFive co-founder, RISC-V architect, Duke BSE, Cal PhD, Rocket-Chip (3714 stars!)
    "aswaterman": {
        "subject": "RISC-V architecture and Rocket-Chip",
        "message": "Hey Andrew,\n\nSiFive co-founder and RISC-V architect, with Rocket-Chip at 3714 stars. You've been at the center of RISC-V from the very beginning. Curious what you think the next major challenge is for RISC-V. Ecosystem fragmentation, verification, or something else entirely?\n\nSeverin"
    },
    # ROW 760 - nadime15: RISC-V International, Xvisor (608 stars)
    "nadime15": {
        "subject": "Xvisor at RISC-V International",
        "message": "Hey Nadime,\n\nRISC-V International contributing to Xvisor at 608 stars. An open source hypervisor with RISC-V support backed by someone at RISC-V International. Curious whether Xvisor is part of the official RISC-V software ecosystem strategy, or a separate contribution.\n\nSeverin"
    },
    # ROW 799 - chili-chips-ba: Chili.CHIPS, wireguard-fpga (1317 stars!), Bosnia
    "chili-chips-ba": {
        "subject": "WireGuard FPGA at 1317 stars",
        "message": "Hey,\n\nChili.CHIPS in Bosnia building wireguard-fpga at 1317 stars. WireGuard VPN encryption implemented in an FPGA is both technically impressive and practically useful for line-rate crypto. Curious what the target deployment is. Network appliances, datacenter NICs, or something else?\n\nSeverin"
    },
    # ROW 800 - goran-mahovlic: Intergalaktik, Croatia, openCologne (91 stars)
    "goran-mahovlic": {
        "subject": "openCologne from Croatia",
        "message": "Hey Goran,\n\nIntergalaktik in Croatia contributing to openCologne at 91 stars. Open source FPGA boards and tooling from the Balkans. Curious what Intergalaktik builds and whether the FPGA work is the core business or a side project.\n\nSeverin"
    },
    # ROW 985 - Lunaphied: Netherlands, Yosys (4333 stars!)
    "Lunaphied": {
        "subject": "Yosys contributions",
        "message": "Hey,\n\nContributing to Yosys at 4333 stars from the Netherlands. Yosys is the foundation of the entire open source FPGA synthesis ecosystem. Curious what part of Yosys you work on. New architecture support, optimization passes, or something else?\n\nSeverin"
    },
    # ROW 1069 - joonho3020: UC Berkeley PhD, ucb-bar, scala3-hdl
    "joonho3020": {
        "subject": "Scala3 HDL at UC Berkeley",
        "message": "Hey Joonho,\n\nPhD at UC Berkeley in the ucb-bar group working on scala3-hdl. Exploring next-generation hardware description in Scala 3 from the group that created Chisel is exciting. Curious how scala3-hdl differs from Chisel. Is it a clean-sheet redesign, or an evolution?\n\nSeverin"
    },
    # ROW 1090 - ATaylorCEngFIET: Adiuvo Engineering, FPGA expert, UK
    "ATaylorCEngFIET": {
        "subject": "Adiuvo Engineering FPGA expertise",
        "message": "Hey Adam,\n\nAdiuvo Engineering in the UK, expert in embedded systems and FPGAs. Your Hackster tutorials and FPGA content reach a wide audience. Curious what the most common FPGA application you see from your consulting clients. Defense, telecommunications, or something else?\n\nSeverin"
    },
    # ROW 426 - mbitsnbites: Sweden, "Software and hardware designer since 1990s", MRISC32/mc1 (53 stars)
    "mbitsnbites": {
        "subject": "MRISC32 custom CPU from Sweden",
        "message": "Hey,\n\nSoftware and hardware designer since the 1990s in Sweden, building MRISC32 mc1 at 53 stars. A custom CPU architecture with its own ISA, compiler backend, and FPGA implementation is a massive undertaking. Curious what motivated creating a new ISA rather than building on RISC-V.\n\nSeverin"
    },
    # ROW 427 - vmayoral: Alias Robotics, Vitoria Spain, verilog-ethernet (2878 stars)
    "vmayoral": {
        "subject": "Robotics and verilog-ethernet",
        "message": "Hey Victor,\n\nAlias Robotics in Vitoria contributing to verilog-ethernet at 2878 stars. Robotics and high-performance FPGA ethernet is an interesting combination. Curious whether the ethernet work connects to real-time networking for robotics, or if it's a separate interest.\n\nSeverin"
    },
    # ROW 425 - BekdoucheAmine: SoC FPGA Engineer, France, OSVVM template
    "BekdoucheAmine": {
        "subject": "SoC FPGA engineering from France",
        "message": "Hey Amine,\n\nSoC FPGA engineer in France with a Master's in Electronic, Sensors, and IoT, working with OSVVM. OSVVM is one of the more underappreciated VHDL verification frameworks. Curious what types of SoC FPGA designs you work on professionally.\n\nSeverin"
    },
    # ROW 458 - ikwzm: Retired FPGA engineer, Japan, Dummy_Plug
    "ikwzm": {
        "subject": "Retired FPGA engineer from Japan",
        "message": "Hey Ichiro,\n\nRetired FPGA engineer from Japan maintaining Dummy_Plug. A career in FPGA engineering and continuing to contribute to open source tools after retirement. Curious what the FPGA industry looked like in Japan over your career and how it's changed.\n\nSeverin"
    },
    # ROW 459 - FaizanAhmad626: Pakistan, ztachip (291 stars)
    "FaizanAhmad626": {
        "subject": "ztachip tensor accelerator",
        "message": "Hey Faizan,\n\nContributing to ztachip at 291 stars from Pakistan. A tensor accelerator in VHDL for edge AI is ambitious. Curious what the performance target is for ztachip. Is it aimed at specific ML workloads, or a general-purpose tensor engine?\n\nSeverin"
    },
    # ROW 448 - m2kar: ISCAS PhD, software security, SystemVerilog SHA256 (83 stars)
    "m2kar": {
        "subject": "SHA256 in SystemVerilog",
        "message": "Hey,\n\nPhD at ISCAS in software security and IoT security, with a SystemVerilog SHA256 implementation at 83 stars. The intersection of security research and hardware crypto implementations is important. Curious whether the SHA256 core targets FPGA-based security applications, or if it was more of an academic exercise.\n\nSeverin"
    },
    # ROW 560 - stevobailey: ucb-bar/dsptools (245 stars), no bio
    "stevobailey": {
        "subject": "DSPTools at UC Berkeley",
        "message": "Hey Stevo,\n\nContributing to ucb-bar dsptools at 245 stars. DSP building blocks for Chisel that handle fixed-point arithmetic and signal processing are exactly what FPGA designers need. Curious whether you use dsptools for research at Berkeley, or if it's a standalone infrastructure contribution.\n\nSeverin"
    },
    # ROW 408 already in dict above, skip duplicate
    # ROW 419 already in dict above

    # ROW 410 already covered (ncde)
    # ROW 413 already covered (DurandA)

    # ROW 344 - peepo: UK, logi-projects (65 stars) - revisit, enough signal
    "peepo": {
        "subject": "LOGI FPGA projects",
        "message": "Hey Jonathan,\n\nContributing to logi-projects at 65 stars from the UK. The LOGI FPGA board ecosystem aimed at making FPGAs accessible to a wider audience. Curious whether you still work with FPGAs, and what the LOGI project taught you about open hardware adoption.\n\nSeverin"
    },
    # ROW 437 - mohammadhgh already covered above

    # ROW 411 - ikorb: ZPUFlex (36 stars), no bio but interesting project
    "ikorb": {
        "subject": "ZPUFlex soft processor",
        "message": "Hey Ingo,\n\nContributing to ZPUFlex at 36 stars. The ZPU's stack-based architecture makes it one of the smallest soft processors you can fit in an FPGA. Curious whether you use ZPU in actual projects where FPGA resources are extremely tight, or if it's more of an architecture interest.\n\nSeverin"
    },
    # ROW 384 - ghanesimit: student, ice40-playground (259 stars!)
    "ghanesimit": {
        "subject": "ice40 playground",
        "message": "Hey,\n\nContributing to ice40-playground at 259 stars from Ahmedabad. A collection of iCE40 FPGA projects with the open source toolchain is one of the better hands-on learning resources. Curious what projects from the playground you've worked on.\n\nSeverin"
    },
    # ROW 377 - Manarabdelaty already covered above

    # ROW 379 - soumilheble already covered above

    # ROW 385 - lromor already covered above

    # ROW 392 - rbarzic already covered above

    # ROW 417 - tpwrules: Thomas Computer Industries, apertus open source cinema NAPS (45 stars)
    "tpwrules": {
        "subject": "Apertus open source cinema",
        "message": "Hey Thomas,\n\nThomas Computer Industries contributing to apertus NAPS at 45 stars. Open source cinema camera hardware with FPGA-based image processing is one of the more ambitious open hardware projects. Curious what your role is in the project. The FPGA image pipeline, or the camera control system?\n\nSeverin"
    },
    # ROW 431 - VladisM already covered above

    # ROW 466 - jaruiz: Cambridge UK, light52 (37 stars, 8051 compatible)
    "jaruiz": {
        "subject": "light52 8051 core from Cambridge",
        "message": "Hey Jose,\n\nlight52 at 37 stars from Cambridge. An 8051-compatible core in VHDL is useful for legacy embedded applications that need FPGA migration. Curious whether you use light52 in actual designs, or if it was more of a learning project.\n\nSeverin"
    },
    # ROW 468 - nitheeshkm already covered above

    # ROW 472 - gsmecher already covered above

    # ROW 473 - AngeloJacobo already covered above

    # ROW 482 - thirtythreeforty already covered above

    # Going further:
    # ROW 560 - stevobailey already added above

    # ROW 797 - Alirio926: Brasil, neorv32 — skip (no bio)
    # ROW 798 - carljohnsen: ghdl — skip (no bio)

    # All the remaining 100+ leads are mostly students with 0-star repos, non-hardware devs, or have zero bio.
    # We've captured the best leads from this section.

    # Let me pick up some from the ~55-150 range that were skipped earlier but have minimum signal
    # ROW 82 - jarickc: VUnit (820 stars), no bio — give it a shot
    "jarickc": {
        "subject": "VUnit framework contributions",
        "message": "Hey Jarick,\n\nContributing to VUnit at 820 stars. VUnit has become the standard VHDL/SystemVerilog unit testing framework. Curious what brought you to the project. Are you using it professionally for verification, or was it a community contribution?\n\nSeverin"
    },
    # ROW 145 - giraypultar: Corundum contributor, no bio — has enough via project
    "giraypultar": {
        "subject": "Corundum FPGA NIC",
        "message": "Hey Giray,\n\nContributing to Corundum. An open source 100G FPGA NIC framework is rare and important infrastructure. Curious what part of Corundum you work on. The datapath, the PCIe interface, or something else?\n\nSeverin"
    },
    # ROW 335 - Koeng101: Caravel user project (229 stars), no bio
    "Koeng101": {
        "subject": "Caravel user project",
        "message": "Hey,\n\nContributing to the Caravel user project at 229 stars. The Efabless shuttle program has made custom silicon accessible to individuals for the first time. Curious what you designed for your Caravel tile and whether you got silicon back.\n\nSeverin"
    },
    # ROW 146 - luarss: Precision Innovation, OpenROAD (2482 stars)
    "luarss": {
        "subject": "OpenROAD at Precision Innovation",
        "message": "Hey Song,\n\nPrecision Innovation contributing to OpenROAD at 2482 stars. Open source place-and-route is closing the gap with commercial EDA. Curious what part of the OpenROAD flow you work on at Precision Innovation.\n\nSeverin"
    },
    # ROW 407 - suehnel: ensilica, OpenTitan
    "suehnel": {
        "subject": "OpenTitan at ensilica",
        "message": "Hey Christoph,\n\nensilica contributing to OpenTitan at 3226 stars. ensilica's ASIC design services applied to the open source silicon root of trust is a natural fit. Curious what ensilica's specific role is on the project. Design, verification, or physical implementation?\n\nSeverin"
    },
    # ROW 480 - danclement: ON Semiconductor, Lindon UT
    "danclement": {
        "subject": "ON Semiconductor and open source",
        "message": "Hey Dan,\n\nON Semiconductor in Lindon. Semiconductor companies contributing to open source projects is a good signal for the ecosystem. Curious whether ON Semi uses open source EDA or IP internally, or if your contributions are more personal.\n\nSeverin"
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
