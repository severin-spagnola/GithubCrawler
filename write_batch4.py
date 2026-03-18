#!/usr/bin/env python3
"""Write outreach for next 100 leads (rows 201-290 area)."""

import csv

OUTREACH_FILE = "fpga_outreach_leads.csv"

MESSAGES = {
    # ROW 55 - suzizecat: ghdl contributor, no bio/company — skip (no personalization angle, already have many ghdl contributors)
    # ROW 62 - targeted: Dmitry Dvoinikov, ghdl contributor, no bio — skip (no angle)
    # ROW 64 - forrestv: ghdl contributor, USA, no bio — skip (no angle)
    # ROW 77 - DerekYu177: Shopify + ressystlab, Montreal, 425G14 repo (1 star VHDL)
    # skip — Shopify engineer, the VHDL repo is a university project from years ago
    # ROW 79 - rafaelgmota: NoCThor (1 star), no bio — skip (low signal)
    # ROW 80 - jmferreiratech: TrincaTech, Brazil, NoCThor — skip (software engineer, NoCThor is 1 star)
    # ROW 82 - jarickc: VUnit contributor, no bio/company — skip (no angle beyond VUnit, already have VUnit messages)
    # ROW 98 - bvaughn: Citadel, ex-React core at Facebook — skip (not hardware, JavaScript repo)
    # ROW 100 - Emoun: Patmos contributor, no bio — skip (low signal, already have Patmos messages)
    # ROW 107 - dpetrisko: pllab/elephant (4 stars), no bio
    # skip — too low signal
    # ROW 120 - lucask07: covg_fpga (7 stars), no bio
    # skip — low signal
    # ROW 122 - Godhart: ghdl contributor, no bio — skip
    # ROW 128 - dominiksalvet: ghdl contributor, no bio — skip
    # ROW 139 - leoo-c1: Leo Chinchilla, Sydney, ben-marshall/uart (177 stars)
    "leoo-c1": {
        "subject": "UART core at 177 stars",
        "message": "Hey Leo,\n\nContributing to ben-marshall's UART core at 177 stars from Sydney. A clean, minimal UART implementation that lots of people depend on. Curious what drew you to this specific project. Are you using it in your own FPGA work, or was it more of a contribution opportunity?\n\nSeverin"
    },
    # ROW 142 - alokkumardalei-wq: student at Vedam School of Technology, OpenROAD contributor
    # skip — CP enthusiast, student, low hardware signal
    # ROW 145 - giraypultar: Corundum contributor (67 stars fork?), no bio
    # skip — no personalization angle
    # ROW 146 - luarss: Precision Innovation, OpenROAD contributor, no bio
    # skip — no angle
    # ROW 148 - VJSchneid: Viktor Schneider, Hannover, GF180 PDK contributor
    "VJSchneid": {
        "subject": "GF180 PDK work from Hannover",
        "message": "Hey Viktor,\n\nContributing to the GlobalFoundries 180nm PDK from Hannover. Open source PDKs are what made the Efabless shuttle program possible. Curious whether you're using GF180 for tapeouts, or if the contribution is more about improving the ecosystem for others.\n\nSeverin"
    },
    # ROW 150 - jhkim-pii: Precision Innovation, OpenROAD — skip (no bio, same company as luarss)
    # ROW 153 - hongted: Ted Hong, OpenROAD — skip (no bio)
    # ROW 156 - newhouseb: Ben Newhouse, East Coast, FPGA-peripherals (185 stars)
    "newhouseb": {
        "subject": "FPGA-peripherals at 185 stars",
        "message": "Hey Ben,\n\nContributing to FPGAwars FPGA-peripherals at 185 stars. The FPGAwars ecosystem around the iCE40 and open toolchains has quietly become one of the best on-ramps for learning FPGA development. Curious what peripherals you've worked on. SPI, I2C, or something more specialized?\n\nSeverin"
    },
    # ROW 167 - Smeds: Clinical Genomics Uppsala — skip (bioinformatics QC, not hardware)
    # ROW 169 - sethirus: Thiele Machine — skip (theoretical computation model, not hardware)
    # ROW 170 - davidlattimore: Rust dev, CFU-Playground — skip (primarily Rust/software person)
    # ROW 174 - jeffng-or: Precision Innovation, OpenROAD flow scripts — skip (no bio)
    # ROW 178 - yanghuaxuan: "CEO of vaporware", OpenROAD — skip
    # ROW 179 - suttonr: ws2812 driver (0 stars) — skip
    # ROW 186 - Charitha-Jeewanka: Synopsys, ML Engineer, Verilator — skip (ML focus, tangential)
    # ROW 187 - godblesszhouzhou: Verilator, no bio — skip

    # ROW 201 - ZhongYic00: Ibex contributor, joke bio, active bug reporter
    "ZhongYic00": {
        "subject": "Ibex RISC-V verification work",
        "message": "Hey,\n\nSaw your issue reports on lowRISC Ibex. Detailed cosim and verification bug reports on a core that complex are genuinely valuable. Curious whether you're running Ibex in a specific project, or if the verification work is more research-driven.\n\nSeverin"
    },
    # ROW 202 - Mo0nbase: Julian Carrier, Michigan CE, Monero/Rust/Nix, Verilator contributor
    "Mo0nbase": {
        "subject": "CE and Verilator at Michigan",
        "message": "Hey Julian,\n\nComputer engineering at Michigan with Monero, Rust, and Verilator contributions. That's an interesting mix of crypto and hardware simulation. Curious what brought you to Verilator specifically. Is it tied to your CE coursework, or a personal project?\n\nSeverin"
    },
    # ROW 203 - rickliu2000: Ibex contributor, Nanjing — skip (no bio, low signal)

    # ROW 204 - abarajithan11: University of Moratuwa, Sri Lanka, "Mostly Harmless", Verilator
    "abarajithan11": {
        "subject": "Verilator at University of Moratuwa",
        "message": "Hey Abarajithan,\n\nContributing to Verilator from the University of Moratuwa. Getting undergrad or early-career contributions into a tool with 330 contributors is no small thing. Curious what part of Verilator you've worked on. Simulation performance, language features, or something else?\n\nSeverin"
    },
    # ROW 205 - GregAC: Greg Chadwick, Digital Design Lead at lowRISC, ex-Arm/Broadcom, Bristol
    "GregAC": {
        "subject": "Ibex and OpenTitan at lowRISC",
        "message": "Hey Greg,\n\nDigital design lead at lowRISC with Arm CPU memory systems and Broadcom GPU in the background. That's a strong path into open source silicon. Curious how the experience at Arm and Broadcom shaped your approach to OpenTitan. Do open source silicon projects fundamentally require different design practices?\n\nSeverin"
    },
    # ROW 206 - MatiasYezzi: Orlando, IEEE-UCF Gaming CPU Project (10 stars)
    "MatiasYezzi": {
        "subject": "Gaming CPU project at UCF",
        "message": "Hey Matias,\n\nIEEE-UCF Gaming CPU Project at 10 stars with 12 contributors from Orlando. Building a CPU as a student team project is ambitious. Curious how far along the design is. Have you gotten it running on an FPGA, or is it still in simulation?\n\nSeverin"
    },
    # ROW 207 - RKNAGA18: VIT Chennai, Black Parrot contributor
    "RKNAGA18": {
        "subject": "Black Parrot at VIT Chennai",
        "message": "Hey Naga Arjun,\n\nContributing to Black Parrot at 780 stars from VIT Chennai. Black Parrot is one of the more serious open source RISC-V multicore projects. Curious what part of the design you work on. The core pipeline, the cache coherence, or the uncore infrastructure?\n\nSeverin"
    },
    # ROW 208 - Weissnix4711: Thomas Aldrian, Imperial College, Verilator contributor
    "Weissnix4711": {
        "subject": "Verilator contributions from Imperial",
        "message": "Hey Thomas,\n\nContributing to Verilator from Imperial College. Getting into open source EDA as an undergrad puts you ahead of most people in the space. Curious what part of Verilator you've worked on and whether it connects to your coursework or is a separate interest.\n\nSeverin"
    },
    # ROW 209 - cst-ayushm: CircuitSutra, Core-V-MCU contributor
    "cst-ayushm": {
        "subject": "Core-V-MCU at CircuitSutra",
        "message": "Hey Ayush,\n\nMember of consulting staff at CircuitSutra working on Core-V-MCU. CircuitSutra's SystemC and verification expertise applied to the OpenHW ecosystem is a natural fit. Curious what CircuitSutra's focus area is on Core-V. Verification, integration, or something else?\n\nSeverin"
    },
    # ROW 210 - davideschiavone: Davide Schiavone, EPFL PostDoc + OpenHW Director of Eng, CVE2
    "davideschiavone": {
        "subject": "CVE2 and OpenHW engineering",
        "message": "Hey Davide,\n\nPostDoc at EPFL and Director of Engineering at OpenHW Group, leading CVE2 industrial verification. Bridging academic RISC-V research and production-grade verification is exactly what the ecosystem needs. Curious what the biggest challenge is in getting academic cores to industrial quality. Is it the verification methodology, the documentation, or something else?\n\nSeverin"
    },
    # ROW 211 - krame505: Lucas Kramer, MatX Inc, Silver language framework
    # skip — Silver is a compiler/language framework, not hardware-related. MatX is interesting but the repo connection is wrong.
    # ROW 212 - RRozak: Antmicro, Verilator contributor, Wroclaw
    "RRozak": {
        "subject": "Verilator at Antmicro Wroclaw",
        "message": "Hey Ryszard,\n\nAntmicro in Wroclaw contributing to Verilator. Antmicro has become one of the biggest commercial drivers of open source EDA. Curious what your specific focus area is on Verilator. SystemVerilog feature coverage, performance, or integration with Antmicro's other tools?\n\nSeverin"
    },
    # ROW 213 - gdessouky: Google OpenTitan team, Munich
    "gdessouky": {
        "subject": "OpenTitan at Google Munich",
        "message": "Hey Ghada,\n\nGoogle OpenTitan team from Munich. Having a dedicated security team contributing to an open source root of trust is significant. Curious what your focus area is within OpenTitan. The crypto subsystem, the security lifecycle, or something else?\n\nSeverin"
    },
    # ROW 214 - lucat1: Luca Tagliavini, Zurich, Coyote contributor, into distributed systems
    "lucat1": {
        "subject": "Coyote FPGA shell from Zurich",
        "message": "Hey Luca,\n\nContributing to Coyote at 329 stars from Zurich. An FPGA shell with RDMA and dynamic partial reconfiguration for datacenter platforms is serious infrastructure. With your distributed systems and compilers background, curious whether you're working on the networking stack or the reconfiguration framework.\n\nSeverin"
    },
    # ROW 215 - HarshitSharm-a: Lund University, PULPissimo contributor
    # skip — no bio, student, low signal
    # ROW 216 - hcallahan-lowrisc: lowRISC, OpenTitan contributor
    "hcallahan-lowrisc": {
        "subject": "OpenTitan at lowRISC",
        "message": "Hey Harry,\n\nlowRISC contributing to OpenTitan at 3226 stars. With 270 contributors on a silicon root of trust, the coordination challenge is as hard as the engineering. Curious what your area of focus is. The RTL design, the verification infrastructure, or the software stack?\n\nSeverin"
    },
    # ROW 217 - certainly-param: UNC Chapel Hill, Verilator contributor
    "certainly-param": {
        "subject": "Verilator at UNC Chapel Hill",
        "message": "Hey Param,\n\nContributing to Verilator from UNC Chapel Hill. Open source EDA contributions from the academic side are what keep tools like Verilator moving forward. Curious what drew you to Verilator specifically and what part of the codebase you've worked on.\n\nSeverin"
    },
    # ROW 218 - vignajeth: PULPissimo, Denmark — LinkedIn only, no bio — skip (too little signal for 200 chars)

    # ROW 219 - StMiky: Michele Caon, EPFL Postdoc, cv32e40x contributor
    "StMiky": {
        "subject": "CV32E40X verification at EPFL",
        "message": "Hey Michele,\n\nPostdoc at ESL-EPFL contributing to CV32E40X at 261 stars. The CV32E40X is one of the more verification-intensive OpenHW cores. Curious whether your work connects to the X-HEEP platform or if it's focused purely on the core verification side.\n\nSeverin"
    },
    # ROW 220 - l-krrish: Waterloo, Rogers, ML Engineer, FPGA hackathon (0 stars)
    # skip — ML engineer, hackathon project, low hardware signal

    # ROW 221 - alphan: OpenTitan, Framingham MA
    "alphan": {
        "subject": "OpenTitan engineering",
        "message": "Hey Alphan,\n\nOpenTitan at 3226 stars from Framingham. Working directly under the OpenTitan org rather than through lowRISC or Google is interesting. Curious what your specific area is within the project. The design, the verification, or the program management side?\n\nSeverin"
    },
    # ROW 222 - sterin: Baruch Sterin, Verilator contributor — skip (no bio/company, low signal)

    # ROW 223 - yarons: Israel, "Open Source", aws/aws-fpga contributor
    "yarons": {
        "subject": "AWS FPGA from Israel",
        "message": "Hey Yaron,\n\nContributing to aws-fpga at 1645 stars from Israel. The AWS F1 FPGA instances opened up cloud-based hardware acceleration to a much wider audience. Curious whether you use F1 instances for your own work, or if the contribution is more about the open source shell and tooling.\n\nSeverin"
    },
    # ROW 224 - fischeti: Tim Fischer, ETH Zurich, PULP serial_link
    "fischeti": {
        "subject": "PULP serial link at ETH",
        "message": "Hey Tim,\n\nPULP serial_link at 36 stars from ETH Zurich. Chip-to-chip serial links are one of those critical building blocks that every SoC needs but few projects open source well. Curious whether this is tied to your research at IIS or if it's a standalone infrastructure piece for the PULP ecosystem.\n\nSeverin"
    },
    # ROW 225 - cameronwaite-mq: Macquarie University, Sydney, Verilator
    "cameronwaite-mq": {
        "subject": "Verilator at Macquarie University",
        "message": "Hey Cameron,\n\nContributing to Verilator from Macquarie University in Sydney. Academic contributions to open source simulation tools are what keep the ecosystem healthy. Curious what aspect of Verilator you've worked on and whether it ties into research at Macquarie.\n\nSeverin"
    },
    # ROW 226 - caryr: Cary R., sv-tests contributor (367 stars)
    "caryr": {
        "subject": "SystemVerilog test suites",
        "message": "Hey Cary,\n\nContributing to CHIPS Alliance sv-tests at 367 stars. A standardized SystemVerilog compliance test suite is exactly what open source EDA tools need to close the gap with commercial simulators. Curious what drives your contributions. Tool development, or finding spec compliance gaps?\n\nSeverin"
    },
    # ROW 227 - johnjohnlin: Taiwan, GPU/VLSI research, Verilator
    "johnjohnlin": {
        "subject": "GPU and VLSI research in Taiwan",
        "message": "Hey Yu-Sheng,\n\nGPU and VLSI design research at NTU, contributing to Verilator. The intersection of GPU architecture research and open source simulation tools is interesting. Curious whether you use Verilator for GPU RTL simulation in your research, or if the contribution is separate from the VLSI work.\n\nSeverin"
    },
    # ROW 228 - raiyyanfaisal09: LinkedIn only, MS EE from Cal State — skip (low signal for LinkedIn)

    # ROW 229 - jxc98728: Chris John, Zhejiang University, Coyote contributor
    "jxc98728": {
        "subject": "Coyote FPGA framework at Zhejiang",
        "message": "Hey Chris,\n\nContributing to Coyote at 329 stars from Zhejiang University. An FPGA datacenter shell with RDMA and dynamic reconfiguration is cutting edge. Curious whether your work on Coyote is part of your research at Zhejiang or a separate contribution.\n\nSeverin"
    },
    # ROW 230 - bo3z: Benjamin Ramhorst, ETH Zurich, Coyote — LinkedIn only
    # skip — LinkedIn, no bio, would need <200 chars

    # ROW 231 - ayj: Jason Young, Google, OpenTitan, Kirkland WA
    "ayj": {
        "subject": "OpenTitan at Google Kirkland",
        "message": "Hey Jason,\n\nGoogle contributing to OpenTitan at 3226 stars from Kirkland. With Google backing an open source silicon root of trust, the project has resources most open hardware projects never get. Curious what your specific role is. RTL design, verification, or the software integration side?\n\nSeverin"
    },
    # ROW 232 - hankhsu1996: Shou-Li Hsu, AheadComputing, Verilator, Portland
    "hankhsu1996": {
        "subject": "Verilator at AheadComputing",
        "message": "Hey Shou-Li,\n\nAheadComputing in Portland contributing to Verilator. Curious what AheadComputing's focus is and how Verilator fits into your workflow. Are you building on top of Verilator for your own simulation needs, or contributing upstream features?\n\nSeverin"
    },
    # ROW 233 - MikeOpenHWGroup: Mike Thompson, OpenHW Foundation Director of Engineering, Verification
    "MikeOpenHWGroup": {
        "subject": "OpenHW verification methodology",
        "message": "Hey Mike,\n\nDirector of Engineering for verification at OpenHW Foundation, running Covrado on the side. Defining the verification methodology for an entire family of open source RISC-V cores is a unique challenge. Curious what the biggest gap is in open source verification tooling right now from your perspective.\n\nSeverin"
    },
    # ROW 234 - mkannwischer: Quantum-Safe Migration Center, Chelpis Quantum Tech, Taipei
    "mkannwischer": {
        "subject": "Post-quantum crypto and hardware",
        "message": "Hey Matthias,\n\nResearch Director at Quantum-Safe Migration Center in Taipei, contributing to the OpenTitan ecosystem. Post-quantum cryptography is going to need hardware acceleration at some point. Curious whether your work involves PQC hardware implementations, or if it's more on the migration strategy side.\n\nSeverin"
    },
    # ROW 235 - ramonwirsch: Daisytuner, Darmstadt, CVA5 contributor
    "ramonwirsch": {
        "subject": "CVA5 RISC-V core from Darmstadt",
        "message": "Hey Ramon,\n\nDaisytuner in Darmstadt contributing to CVA5 at 128 stars. CVA5 is one of the more performant open source RISC-V cores with its superscalar pipeline. Curious what Daisytuner's angle is on this. Performance tuning for the core itself, or using CVA5 as a platform for something else?\n\nSeverin"
    },
    # ROW 236 - mgottscho: Mark Gottscho, OpenAI MTS, xlsynth/bedrock-rtl, ex-Google TPU/SambaNova
    "mgottscho": {
        "subject": "bedrock-rtl at OpenAI",
        "message": "Hey Mark,\n\nMTS at OpenAI building bedrock-rtl, with Google TPU and SambaNova in the background. Composable SystemVerilog RTL libraries with clean ready/valid interfaces is the kind of infrastructure that compounds. Curious what drove the decision to open source bedrock-rtl. Is it about building an ecosystem, or enabling external contributions?\n\nSeverin"
    },
    # ROW 237 - MaistoV: Vincenzo Maisto, Simply-V (16 stars)
    "MaistoV": {
        "subject": "Simply-V vector extension",
        "message": "Hey Vincenzo,\n\nContributing to Simply-V at 16 stars. A RISC-V vector extension implementation is ambitious, especially with the V spec's complexity. Curious whether Simply-V targets a specific application domain like DSP or ML inference, or if it's a general-purpose V implementation.\n\nSeverin"
    },
    # ROW 238 - sasdf: no display name, no bio, OpenTitan — skip (no angle)
    # ROW 239 - sameo: Samuel Ortiz, Meta, OpenTitan contributor
    "sameo": {
        "subject": "OpenTitan at Meta",
        "message": "Hey Samuel,\n\nMeta contributing to OpenTitan at 3226 stars. Having another hyperscaler beyond Google investing in an open source root of trust is a strong signal for the project. Curious what Meta's interest in OpenTitan looks like. Is it about deploying it in server infrastructure, or more about the security architecture?\n\nSeverin"
    },
    # ROW 240 - InfiniBuilds: "Data & Tech Enthusiast", TreeMultiplier (1 star) — skip (ML/web dev, not hardware)

    # ROW 241 - philipaxer: Verilator contributor, no bio — skip (no angle)

    # ROW 242 - dosadi: Jon Taylor, hydra repo (0 stars, C++) — skip (no hardware signal)

    # ROW 243 - Scheremo: Moritz Scherer, Mosaic SoC CTO, PhD Computer Architecture, PULP common_cells
    "Scheremo": {
        "subject": "Mosaic SoC and PULP ecosystem",
        "message": "Hey Moritz,\n\nCTO at Mosaic SoC with a PhD in computer architecture, contributing to PULP common_cells at 723 stars. Taking PULP ecosystem components and building a commercial product around them is exactly the kind of path open source silicon needs. Curious what Mosaic's target application is. AI edge inference, or something else?\n\nSeverin"
    },
    # ROW 244 - celuk: TOBB ETU, Ankara, cv-hpdcache (101 stars)
    "celuk": {
        "subject": "CV-HPDCache from Ankara",
        "message": "Hey Seyyid,\n\nContributing to cv-hpdcache at 101 stars from TOBB ETU in Ankara. A high-performance data cache for the CVA6 pipeline is critical infrastructure for the OpenHW ecosystem. Curious whether this is part of your research, and what the performance targets are for the cache.\n\nSeverin"
    },
    # ROW 245 - IveanEx: Yunhao Deng, ESAT-MICAS KU Leuven, SNAX cluster
    "IveanEx": {
        "subject": "SNAX accelerator cluster at KU Leuven",
        "message": "Hey Yunhao,\n\nESAT-MICAS at KU Leuven contributing to SNAX cluster at 35 stars. A heterogeneous accelerator framework with MLIR-based toolchain is exactly the right approach for custom accelerator design. Curious whether your work focuses on a specific accelerator type, or the framework infrastructure itself.\n\nSeverin"
    },
    # ROW 246 - Kuba-J: Saturn_MiSTer (89 stars), Poland
    "Kuba-J": {
        "subject": "Saturn MiSTer core from Poland",
        "message": "Hey Kuba,\n\nContributing to Saturn_MiSTer at 89 stars from Poland. A Sega Saturn FPGA core is one of the harder retro consoles to implement because of the dual SH2 and VDP2. Curious what part of the Saturn you work on. The CPU cores, the video pipeline, or the CD subsystem?\n\nSeverin"
    },
    # ROW 247 - korran: Google, OpenTitan, SF Bay Area
    "korran": {
        "subject": "OpenTitan at Google",
        "message": "Hey Kor,\n\nGoogle contributing to OpenTitan from the Bay Area. Curious what your specific area is within the project. With 270 contributors, OpenTitan has enough surface area that people can go deep on crypto, boot, or verification without overlapping much.\n\nSeverin"
    },
    # ROW 248 - SEBv15: Sebastian, Chicago, ANL-ASIC/matvec (0 stars)
    "SEBv15": {
        "subject": "Matrix-vector accelerator at Argonne",
        "message": "Hey Sebastian,\n\nContributing to ANL-ASIC matvec from Chicago. A matrix-vector accelerator ASIC at Argonne National Lab is interesting. Curious whether this targets scientific computing workloads specific to the lab, or if it's a more general-purpose ML accelerator.\n\nSeverin"
    },
    # ROW 249 - marcelocarvalhoLowRisc: lowRISC, Sr Design HW Verification Engineer, Cambridge
    "marcelocarvalhoLowRisc": {
        "subject": "OpenTitan verification at lowRISC",
        "message": "Hey Marcelo,\n\nSenior design hardware verification engineer at lowRISC in Cambridge working on OpenTitan. Verification on a security-critical open source chip is high stakes. Curious what verification methodology lowRISC uses. UVM, formal, or a custom approach built around the open source toolchain?\n\nSeverin"
    },
    # ROW 250 - Granp4sso: Stefano Mercogliano, University of Naples + Qualcomm, CPU designer, Simply-V
    "Granp4sso": {
        "subject": "CPU design at Naples and Qualcomm",
        "message": "Hey Stefano,\n\nComputer engineer and CPU designer at University of Naples and Qualcomm, contributing to Simply-V. Research at a university and industry experience at Qualcomm is a strong combination. Curious how the academic RISC-V vector work relates to what you see at Qualcomm. Different constraints entirely, or some overlap?\n\nSeverin"
    },
    # ROW 251 - stefanpie: Stefan Abi-Karam, Georgia Tech, AI for Chip Design, NVlabs/verilog-eval
    "stefanpie": {
        "subject": "AI for chip design at Georgia Tech",
        "message": "Hey Stefan,\n\nPhD at Georgia Tech working on AI for chip design, contributing to NVlabs verilog-eval at 386 stars. The IEEE LAD fellowship for agentic HLS is cutting edge. Curious how well current LLMs actually handle RTL generation compared to HLS. Is verilog-eval showing that the gap is closing, or still significant?\n\nSeverin"
    },
    # ROW 252 - Aquaticfuller: Zexin Fu, ETH IIS, PULP AXI
    "Aquaticfuller": {
        "subject": "PULP AXI at ETH Zurich",
        "message": "Hey Zexin,\n\nContributing to the PULP AXI library at 1516 stars from ETH IIS. The AXI interconnect is one of the most reused pieces of the PULP ecosystem. Curious what your specific work focuses on. Protocol compliance, performance optimization, or adding new features?\n\nSeverin"
    },
    # ROW 253 - asturur: Andrea Bogazzi, Rome, S32X_MiSTer (63 stars)
    "asturur": {
        "subject": "Sega 32X MiSTer core from Rome",
        "message": "Hey Andrea,\n\nContributing to S32X_MiSTer at 63 stars from Rome. The 32X is an interesting target because the dual SH2 processors add real complexity on top of the Genesis. Curious what part of the 32X implementation you focus on.\n\nSeverin"
    },
    # ROW 254 - cyyself: Yangyu Chen, Chongqing University, PhD, Computer Architecture, Verilator
    "cyyself": {
        "subject": "Computer architecture research and Verilator",
        "message": "Hey Yangyu,\n\nPhD at Chongqing University in computer architecture and software co-design, contributing to Verilator. Open source enthusiast doing architecture research is the right combination. Curious whether you use Verilator for your own architecture research, or if the contributions are focused on the tool itself.\n\nSeverin"
    },
    # ROW 255 - hasseily: Tiny_But_Mighty_I2C_Master (37 stars) — skip (no bio, 0xArt repo, low signal)

    # ROW 256 - jorendumoulin: MICAS KU Leuven, SNAX cluster
    "jorendumoulin": {
        "subject": "SNAX cluster at MICAS",
        "message": "Hey Joren,\n\nMICAS at KU Leuven contributing to SNAX cluster. With both you and the MICAS group contributing, the cluster is getting serious institutional backing. Curious whether your focus is on the hardware accelerator integration or the MLIR compiler toolchain side.\n\nSeverin"
    },
    # ROW 257 - Abraxas3d: "Optimized Tomfoolery", pluto_msk, San Diego, amateur radio
    "Abraxas3d": {
        "subject": "MSK modulation on Pluto SDR",
        "message": "Hey,\n\nPluto MSK at Open Research Institute from San Diego. Implementing minimum shift keying on the ADALM-Pluto for amateur radio broadband digital comms is a niche that few people work in. Curious whether this is for AMSAT or terrestrial amateur microwave work.\n\nSeverin"
    },
    # ROW 258 - kitakaaki: vending-machine (1 star) — skip (student project, no signal)
    # ROW 259 - yyan7223: VectorCGRA (44 stars), no bio, no display name — skip

    # ROW 260 - mkurc-ant: Maciej Kurc, Antmicro, yosys-f4pga-plugins
    "mkurc-ant": {
        "subject": "Yosys F4PGA plugins at Antmicro",
        "message": "Hey Maciej,\n\nAntmicro contributing to yosys-f4pga-plugins at 83 stars. The plugins that bridge Yosys and the F4PGA flow are critical for making open source FPGA toolchains work with real devices. Curious what specific FPGA families your work targets. Xilinx 7-series, QuickLogic, or others?\n\nSeverin"
    },
    # ROW 261 - Songchun-Li: UW Seattle, BaseJump STL (650 stars)
    "Songchun-Li": {
        "subject": "BaseJump STL at UW",
        "message": "Hey Songchun,\n\nMaster's in ECE at UW contributing to BaseJump STL at 650 stars. A SystemVerilog standard template library that's been used in production tapeouts including the Celerity RISC-V chip is serious infrastructure. Curious what components you've worked on. The memory interfaces, the async modules, or something else?\n\nSeverin"
    },
    # ROW 262 - xusine: "Explorer, Pioneer, and Caretaker", BaseJump STL — skip (no company/location, low signal)

    # ROW 263 - stdavids: Scott Davidson, UW Seattle, BaseJump STL
    "stdavids": {
        "subject": "BaseJump STL at UW Seattle",
        "message": "Hey Scott,\n\nUW contributing to BaseJump STL at 650 stars from Seattle. BaseJump is one of the few SystemVerilog IP libraries that has actually been proven in silicon. Curious whether your work on it connects to the Bespoke Silicon Group's research, or if it's a standalone contribution.\n\nSeverin"
    },
    # ROW 264 - tbunker-openai: Trevor Bunker, OpenAI, bedrock-rtl, ex-Google Tensor SoC
    "tbunker-openai": {
        "subject": "bedrock-rtl at OpenAI",
        "message": "Hey Trevor,\n\nOpenAI building bedrock-rtl, with Google Tensor G-series SoC design in the background. Going from production mobile SoCs to composable RTL libraries for AI infrastructure is a big shift. Curious what the biggest design challenge is at OpenAI scale that bedrock-rtl is trying to solve.\n\nSeverin"
    },
    # ROW 265 - wallento: Stefan Wallentowitz, Professor HM Munich, FOSSi Foundation, RISC-V board, VeeR-EL2
    "wallento": {
        "subject": "VeeR-EL2 and FOSSi Foundation",
        "message": "Hey Stefan,\n\nProfessor at Munich UAS, FOSSi Foundation and RISC-V board member, maintaining VeeR-EL2 at 321 stars. You're one of the people holding the open source silicon ecosystem together. Curious what you see as the next big bottleneck for open hardware adoption. Is it tools, IP quality, or something else?\n\nSeverin"
    },
    # ROW 266 - iamkarthikbk: InCore Semi, IIT Madras, OpenTitan contributor
    "iamkarthikbk": {
        "subject": "CPU microarchitecture at InCore Semi",
        "message": "Hey Karthik,\n\nCPU core microarchitecture at InCore Semi with MS research from IIT Madras, contributing to OpenTitan. InCore's RISC-V work out of IIT Madras is one of the most active silicon design efforts in India. Curious how the OpenTitan contribution connects to InCore's own core development.\n\nSeverin"
    },
    # ROW 267 - nij-intel: Intel, aib-protocols (29 stars) — skip (no bio, low signal)

    # ROW 268 - strichmo: Steve Richmond, Silicon Labs, Design Verification Manager, cv32e40x
    "strichmo": {
        "subject": "CV32E40X verification at Silicon Labs",
        "message": "Hey Steve,\n\nDesign verification manager at Silicon Labs in Austin, co-chairing verification for the OpenHW Group. 20+ years in verification and now defining methodology for open source RISC-V cores. Curious what the biggest difference is between verifying proprietary Silicon Labs cores and open source OpenHW cores.\n\nSeverin"
    },
    # ROW 269 - suehtamacv: Matheus Cavalcante, Arago Computing, PULP AXI — LinkedIn only
    # LinkedIn: under 200 chars
    "suehtamacv": {
        "subject": "",
        "message": "Arago Computing and PULP AXI at 1516 stars. Taking PULP IP into a startup is the right path for open source silicon. What's Arago's target market?",
        "channel": "linkedin"
    },
    # ROW 270 - happycube: Chad Page, Goleta CA, Atari800_MiSTer (42 stars)
    "happycube": {
        "subject": "Atari 800 MiSTer core",
        "message": "Hey Chad,\n\nContributing to Atari800_MiSTer at 42 stars from Goleta. The Atari 800 is a classic target for FPGA reimplementation. Curious whether you focus on the ANTIC/GTIA video system, the POKEY audio, or the overall system integration.\n\nSeverin"
    },
    # ROW 271 - jsvogt: IBM Germany R&D, Böblingen, CAPI2 BSP (VHDL)
    "jsvogt": {
        "subject": "CAPI2 BSP at IBM Böblingen",
        "message": "Hey Joerg-Stephan,\n\nIBM Germany R&D in Böblingen contributing to the CAPI2 BSP. CAPI and OpenCAPI were ahead of their time for coherent accelerator attach. Curious whether this work continues under IBM's current POWER strategy, or if the focus has shifted to CXL.\n\nSeverin"
    },
    # ROW 272 - fransschreuder: Schreuder Electronics, Netherlands, ghdl contributor
    "fransschreuder": {
        "subject": "ghdl and Schreuder Electronics",
        "message": "Hey Frans,\n\nSchreuder Electronics in the Netherlands contributing to ghdl at 2767 stars. Running your own electronics company and contributing to the main open source VHDL simulator is a strong combination. Curious whether you use ghdl in your commercial work, or if the contribution is more about giving back to the ecosystem.\n\nSeverin"
    },
    # ROW 273 - Divinesoumyadip: competitive programmer, B.Tech, OpenROAD — skip (CP focus, not hardware design)

    # ROW 274 - AnttiLukats: micro-FPGA, "Electronics since 1979", c65gs, Bünde Germany
    "AnttiLukats": {
        "subject": "micro-FPGA and 45 years of electronics",
        "message": "Hey Antti,\n\nElectronics since 1979 and micro-FPGA from Bünde. Contributing to c65gs at 86 stars. That's nearly half a century in electronics, and now building open FPGA tools. Curious what micro-FPGA is working on currently. FPGA development boards, tooling, or something else?\n\nSeverin"
    },
    # ROW 275 - ahmed532: OpenROAD, no bio — skip
    # ROW 276 - kconger: Black Box Embedded, Jaguar_MiSTer (21 stars)
    "kconger": {
        "subject": "Jaguar MiSTer core",
        "message": "Hey Keith,\n\nBlack Box Embedded contributing to Jaguar_MiSTer at 21 stars. The Atari Jaguar is one of the hardest retro consoles to emulate, let alone reimplement in an FPGA. Curious how far along the core is. Does it handle the Tom and Jerry custom chips accurately?\n\nSeverin"
    },
    # ROW 277 - donn: Mohamed Gaber, FOSSi Foundation, LibreLane maintainer, Cairo
    "donn": {
        "subject": "LibreLane at FOSSi Foundation",
        "message": "Hey Mohamed,\n\nLibreLane maintainer at the FOSSi Foundation from Cairo. Taking over the OpenLane flow after Efabless and keeping it alive under FOSSi is critical work for the open source silicon community. Curious what the roadmap looks like. Is it about maintaining compatibility, or pushing the flow in new directions?\n\nSeverin"
    },
    # ROW 278 - zephray: Wenting Zhang, Modos Tech co-founder, UMI contributor, Boston, retro computing
    "zephray": {
        "subject": "Modos Tech and open hardware",
        "message": "Hey Wenting,\n\nCo-founder of Modos Tech in Boston, contributing to ZeroASIC UMI at 157 stars. Open source hardware enthusiast building a startup and contributing to chip-to-chip interfaces. Curious how UMI fits into what Modos Tech is building. Is it about integrating chiplets, or more general infrastructure work?\n\nSeverin"
    },
    # ROW 279 - macd: Don MacMillen, OpenROAD, obfuscated email — skip (can't send email with that format)

    # ROW 280 - tornupnegatives: Joseph Bellahcen, NHanced Semiconductors, OpenFPGA
    "tornupnegatives": {
        "subject": "OpenFPGA at NHanced Semiconductors",
        "message": "Hey Joseph,\n\nFPGA architect at NHanced Semiconductors contributing to OpenFPGA at 1058 stars. Working at the world's first pure-play advanced packaging foundry and contributing to FPGA architecture exploration is a unique combination. Curious how the packaging work connects to the FPGA side.\n\nSeverin"
    },
    # ROW 281 - Chandler-Kluser: YosysHQ/apicula (647 stars), no bio
    "Chandler-Kluser": {
        "subject": "Project Apicula for Gowin FPGAs",
        "message": "Hey Chandler,\n\nContributing to Project Apicula at 647 stars. Reverse engineering Gowin FPGA bitstreams to enable open source toolchains is painstaking but important work. Curious what part of the bitstream format you've worked on. Routing, logic configuration, or IO?\n\nSeverin"
    },
    # ROW 282 - kiniry: Joseph Kiniry, Free & Fair, Sigil Logic, Galois, Portland
    "kiniry": {
        "subject": "Formal methods and BESSPIN at Galois",
        "message": "Hey Joseph,\n\nCEO at Free & Fair and Sigil Logic, Principal Scientist at Galois, contributing to BESSPIN-CloudGFE. 30+ years in formal methods applied to hardware security is rare expertise. Curious whether Sigil Logic is bringing formal verification to commercial FPGA or ASIC design, or if it's focused on the security side.\n\nSeverin"
    },
    # ROW 283 - craysiii: Charles, Bay Area, sd2snes (80 stars)
    "craysiii": {
        "subject": "sd2snes flash cart",
        "message": "Hey Charles,\n\nContributing to sd2snes at 80 stars from the Bay Area. The sd2snes FPGA flash cartridge is one of the most impressive pieces of retro gaming hardware. Curious what part of the project you work on. The SNES enhancement chip emulation, or the base cartridge functionality?\n\nSeverin"
    },
    # ROW 284 - podhrmic: Michal Podhradsky, Galois, BESSPIN-CloudGFE, Portland
    "podhrmic": {
        "subject": "BESSPIN at Galois Portland",
        "message": "Hey Michal,\n\nGalois in Portland contributing to BESSPIN-CloudGFE. DARPA's BESSPIN program for hardware security protections is one of the more ambitious government-funded hardware security efforts. Curious what your role in the project focuses on. The FPGA cloud infrastructure, or the security evaluation side?\n\nSeverin"
    },
    # ROW 285 - TheNageek: Keegan Walsh, Salt Lake City, EttusResearch/uhd (1212 stars)
    "TheNageek": {
        "subject": "USRP hardware driver at Ettus",
        "message": "Hey Keegan,\n\nContributing to Ettus UHD at 1212 stars from Salt Lake City. The USRP platform is the backbone of most serious SDR work. Curious whether you work on the FPGA RFNoC blocks, the host driver, or the overall framework integration.\n\nSeverin"
    },
    # ROW 286 - sommerlukas: AMD, TaPaSCo (118 stars), Germany
    "sommerlukas": {
        "subject": "TaPaSCo FPGA framework at AMD",
        "message": "Hey Lukas,\n\nAMD contributing to TaPaSCo at 118 stars from TU Darmstadt. An automated toolflow for building many-core FPGA architectures is exactly the kind of abstraction that makes FPGAs more accessible. Curious whether AMD uses TaPaSCo internally, or if this is continuation of your Darmstadt research.\n\nSeverin"
    },
    # ROW 287 - xlar54: Scott Hutter, Tennessee, 1541ultimate (248 stars)
    "xlar54": {
        "subject": "1541 Ultimate from Tennessee",
        "message": "Hey Scott,\n\nContributing to 1541 Ultimate at 248 stars from Tennessee. An FPGA-based Commodore 1541 disk drive replacement that also handles cartridge emulation is impressive engineering. Curious what part of the project you focus on. The drive emulation accuracy, or the cartridge and expansion functionality?\n\nSeverin"
    },
    # ROW 288 - tomtor: Tom Vijlbrief, Netherlands, FPGAs + Yosys + Vivado, ZipCPU/openarty
    "tomtor": {
        "subject": "OpenArty and open FPGA toolchains",
        "message": "Hey Tom,\n\nContributing to ZipCPU's OpenArty at 131 stars from the Netherlands. Interested in FPGAs with both Yosys and Vivado. Curious whether you've found open toolchains like Yosys competitive with Vivado for real projects yet, or if there's still a significant gap for Xilinx targets.\n\nSeverin"
    },
    # ROW 289 - ejk43: EJ Kreinar, EttusResearch/uhd — skip (no bio, no company, low signal)

    # ROW 290 - kunalg123: Kunal Ghosh, VSD Corp founder, ex-Qualcomm, OpenROAD RePlAce, Bangalore
    "kunalg123": {
        "subject": "VLSI System Design and OpenROAD",
        "message": "Hey Kunal,\n\nVLSI System Design Corp with Qualcomm physical design background, contributing to OpenROAD RePlAce at 247 stars. 50+ courses and 90K students learning open source EDA is massive for the ecosystem. Curious what you see as the tipping point for open source tools replacing commercial EDA in production. Are we close, or still years away?\n\nSeverin"
    },

    # ROW 198 - ericvanwyk: UMN, Silver (extensible language framework) — skip (not hardware)

    # ROW 291 - jefchaves: Jeferson Chaves, PhD in CS, NES_MiSTer (194 stars)
    "jefchaves": {
        "subject": "Energy efficient computing and NES MiSTer",
        "message": "Hey Jeferson,\n\nPhD in CS focused on energy efficient computers, contributing to NES_MiSTer at 194 stars. That's an interesting intersection. FPGA reimplementations of retro hardware are inherently more power-efficient than software emulation. Curious whether the energy efficiency research connects to the FPGA work, or if MiSTer is purely a hobby.\n\nSeverin"
    },
    # ROW 292 - rgantonio: Ryan Antonio, UPD + KU Leuven, SNAX cluster
    "rgantonio": {
        "subject": "SNAX cluster at KU Leuven",
        "message": "Hey Ryan,\n\nUP Diliman and KU Leuven contributing to SNAX cluster at 35 stars. Going from the Philippines to MICAS in Leuven for accelerator research is a strong path. Curious what type of accelerator you're integrating into the SNAX framework.\n\nSeverin"
    },
    # ROW 293 - grayresearch: Jan Gray, Gray Research LLC, CX (70 stars), fpga.org email
    "grayresearch": {
        "subject": "Composable extensions for RISC-V",
        "message": "Hey Jan,\n\nGray Research working on CX at 70 stars. Composable custom extensions for RISC-V is one of those ideas that could unlock a lot of value if the ecosystem adopts it. Curious where the standardization effort stands. Is the RISC-V Foundation engaging with this, or is it still in the proposal phase?\n\nSeverin"
    },
    # ROW 294 - robhancocksed: Robert Hancock, Calian Advanced Technologies, neorv32 (2000 stars)
    "robhancocksed": {
        "subject": "neorv32 at Calian Advanced Technologies",
        "message": "Hey Robert,\n\nSenior hardware architect at Calian in Saskatoon contributing to neorv32 at 2000 stars. Calian does a lot of defense and space work. Curious whether neorv32 is something Calian deploys in production systems, or if it's a personal contribution to the ecosystem.\n\nSeverin"
    },
    # ROW 295 - stamenkovicsasa: OneSpin, SatCat5 (492 stars) — LinkedIn only
    "stamenkovicsasa": {
        "subject": "",
        "message": "OneSpin and SatCat5 at 492 stars from Aerospace Corp. Formal verification on satellite networking hardware is a great niche. What's your focus area?",
        "channel": "linkedin"
    },
    # ROW 296 - davidbiancolin: SiFive, Berkeley/UofT alum, FireSim aws-fpga
    "davidbiancolin": {
        "subject": "FireSim at SiFive",
        "message": "Hey David,\n\nEngineer at SiFive, Cal and U of T alum, contributing to FireSim's AWS FPGA integration. FPGA-accelerated simulation for RISC-V chip development is exactly the kind of infrastructure SiFive needs. Curious whether FireSim is part of SiFive's internal chip development flow, or if you maintain the connection separately.\n\nSeverin"
    },
    # ROW 297 - jhu960213: AMD, ML Frameworks, F4PGA examples — skip (ML focus, F4PGA examples is low signal)

    # ROW 298 - gussmith23: PL/EDA/AI researcher, UW, VossII (56 stars)
    "gussmith23": {
        "subject": "VossII and PL/EDA research at UW",
        "message": "Hey Gus,\n\nPL/EDA/AI researcher at UW contributing to VossII at 56 stars. The intersection of programming languages and EDA is underexplored. Curious whether your research focuses on using PL techniques to improve hardware design tools, or on applying AI to the EDA flow.\n\nSeverin"
    },
    # ROW 299 - JacyCui: Nanjing University, basic_verilog (1937 stars!)
    "JacyCui": {
        "subject": "basic_verilog at 1937 stars",
        "message": "Hey Jacy,\n\nContributing to basic_verilog at 1937 stars from Nanjing University. A collection of fundamental Verilog modules with nearly 2000 stars shows how much demand there is for clean, reusable hardware building blocks. Curious whether you use these in your own coursework or research.\n\nSeverin"
    },
    # ROW 300 - fjpolo: Fran Co, Berlin, embedded audio, FPGAs in Verilog, ZipCPU/dspfilters
    "fjpolo": {
        "subject": "DSP filters and embedded audio",
        "message": "Hey Fran,\n\nEmbedded audio developer working with QCC/HiFi platforms, playing with FPGAs in Verilog, and contributing to ZipCPU dspfilters at 167 stars from Berlin. The audio DSP to FPGA pipeline is a natural fit. Curious whether you implement audio processing on FPGAs professionally, or if the Verilog side is more experimental.\n\nSeverin"
    },
    # ROW 301 - secworks: Joachim Strömbergson, Assured AB, Tillitis Key1 (433 stars), crypto hardware
    "secworks": {
        "subject": "Tillitis Key1 hardware security",
        "message": "Hey Joachim,\n\nAssured AB in Gothenburg contributing to Tillitis Key1 at 433 stars. Hardware crypto implementations and a physical security key with open source firmware and hardware. Curious whether the Key1 uses your own crypto cores, or if the hardware primitives come from somewhere else.\n\nSeverin"
    },
    # ROW 302 - rschlaikjer: Tokyo, SERV (1762 stars)
    "rschlaikjer": {
        "subject": "SERV RISC-V core at 1762 stars",
        "message": "Hey Ross,\n\nContributing to SERV at 1762 stars from Tokyo. The world's smallest RISC-V CPU is a beautifully minimal design. Curious what drew you to SERV specifically. Are you using it in a project where area matters, or is it more about the elegance of the bit-serial approach?\n\nSeverin"
    },
    # ROW 303 - Jbalkind: Jonathan Balkind, UCSB, Microwatt contributor
    "Jbalkind": {
        "subject": "Microwatt at UCSB",
        "message": "Hey Jonathan,\n\nUCSB contributing to Microwatt at 712 stars. An academic contributing to an open source POWER core is interesting. Curious whether you use Microwatt in your research at UCSB, or if the contribution is more about supporting the open ISA ecosystem.\n\nSeverin"
    },
    # ROW 304 - xqbumu: wujian100_open (1986 stars!), no bio — skip (no angle beyond star count)

    # ROW 305 - mkatsimpris: Zurich, test_jpeg (18 stars) — skip (low signal)

    # ROW 306 - skristiansson: Espoo Finland, OpenRISC orpsoc-cores (125 stars)
    "skristiansson": {
        "subject": "OpenRISC SoC cores from Finland",
        "message": "Hey Stefan,\n\nContributing to OpenRISC orpsoc-cores at 125 stars from Espoo. OpenRISC was one of the original open source processor projects before RISC-V took over. Curious whether you still actively work with OpenRISC, or if the ecosystem has mostly moved to RISC-V at this point.\n\nSeverin"
    },
    # ROW 307 - kaanari: TUM Munich, PULP APB — skip (low star count, no bio beyond TUM)

    # ROW 308 - vsukhoml: Google, Santa Clara, OpenTitan
    "vsukhoml": {
        "subject": "OpenTitan at Google Santa Clara",
        "message": "Hey Vadim,\n\nGoogle contributing to OpenTitan at 3226 stars from Santa Clara. Curious what your specific focus area is within the project. With the scope OpenTitan has grown to, each contributor tends to own a deep vertical.\n\nSeverin"
    },
    # ROW 309 - petermurphyiv: Intel, OFS examples-afu (4 stars) — skip (low signal)

    # ROW 310 - paulsc96: ETH IIS, Snitch cluster (124 stars)
    "paulsc96": {
        "subject": "Snitch cluster at ETH Zurich",
        "message": "Hey Paul,\n\nContributing to Snitch cluster at 124 stars from ETH IIS. Snitch's approach of using a tiny core with large floating-point units for HPC workloads is a clever architectural trade-off. Curious whether your work focuses on the core microarchitecture, the cluster interconnect, or the software stack.\n\nSeverin"
    },
    # ROW 311 - cfuguet: Inria/TIMA Grenoble, CVA6 contributor, processor architect — LinkedIn only
    "cfuguet": {
        "subject": "",
        "message": "Processor architect at TIMA/Inria contributing to CVA6 at 2843 stars. Research on computer architecture applied directly to an open source core. What area of CVA6 do you focus on?",
        "channel": "linkedin"
    },
    # ROW 312 - niwis: Nils Wistoff, ETH Zurich, CVA6
    "niwis": {
        "subject": "CVA6 at ETH Zurich",
        "message": "Hey Nils,\n\nETH Zurich contributing to CVA6 at 2843 stars. CVA6 is one of the most mature open source application-class RISC-V cores with 240 contributors. Curious what your focus area is. The pipeline, the memory subsystem, or the verification side?\n\nSeverin"
    },
    # ROW 313 - whutddk: Wuhan University of Technology, CVA6 — skip (joke location "Antarctica", low signal)

    # ROW 314 - vinamarora8: UPenn CS PhD, ex-Georgia Tech, IIT Roorkee, verilog-mode (282 stars)
    "vinamarora8": {
        "subject": "Verilog-mode at UPenn",
        "message": "Hey Vinam,\n\nCS PhD at UPenn contributing to verilog-mode at 282 stars. From IIT Roorkee to Georgia Tech to Penn. Curious whether you use verilog-mode in your research, or if the contribution is about improving the tooling for the broader community.\n\nSeverin"
    },
    # ROW 315 - dalance: Naoya Hatta, PEZY Computing, sv-tests (367 stars), Kanagawa Japan
    "dalance": {
        "subject": "sv-tests at PEZY Computing",
        "message": "Hey Naoya,\n\nPEZY Computing in Kanagawa contributing to CHIPS Alliance sv-tests at 367 stars. PEZY's many-core processor architecture is unique in the industry. Curious whether the sv-tests work connects to PEZY's internal verification needs, or if it's a separate ecosystem contribution.\n\nSeverin"
    },
    # ROW 316 - sripathi-muralitharan: UW Seattle, Black Parrot, MS in Computer Architecture
    "sripathi-muralitharan": {
        "subject": "Black Parrot at UW Seattle",
        "message": "Hey Sripathi,\n\nMaster's at UW specializing in computer architecture and VLSI, contributing to Black Parrot at 780 stars. Black Parrot is one of the more serious academic multicore RISC-V projects. Curious what part of the design you work on for your thesis.\n\nSeverin"
    },
    # ROW 317 - dmnewbold: STFC, ipbus-firmware (43 stars) — skip (no bio, low signal)

    # ROW 318 - jeandet: LPP Palaiseau, FSF member, ghdl contributor
    "jeandet": {
        "subject": "ghdl at Laboratoire de Physique des Plasmas",
        "message": "Hey Alexis,\n\nLaboratoire de Physique des Plasmas in Palaiseau contributing to ghdl at 2767 stars. Physics research labs using and contributing to open source VHDL tools is a good sign for the ecosystem. Curious whether ghdl is part of the instrumentation toolchain at LPP.\n\nSeverin"
    },
    # ROW 319 - fadyelgawly: AUC Cairo, Zybo HDMI — skip (12 stars, Digilent example project)
    # ROW 320 - taraxacum45e9a: NUS Singapore, Zybo base linux — skip (Digilent example, low signal)
    # ROW 321 - eugmes: Orca, Debian, Oslo, ghdl — skip (no specific angle beyond ghdl)
    # ROW 322 - rapperskull: Italy, gcvideo (745 stars!), no display name
    "rapperskull": {
        "subject": "GCVideo at 745 stars",
        "message": "Hey,\n\nContributing to GCVideo at 745 stars from Italy. An FPGA-based digital video output for GameCube and Wii is one of the most popular retro gaming hardware mods. Curious what part of the project you work on. The video encoding pipeline, the HDMI output, or board-level integration?\n\nSeverin"
    },
    # ROW 323 - koog1000: ghdl, no bio — skip
    # ROW 324 - wjl: Albuquerque, ghdl — skip (no bio, low signal)
    # ROW 325 - m-torhan: Antmicro, Gdansk, OpenROAD
    "m-torhan": {
        "subject": "OpenROAD at Antmicro Gdansk",
        "message": "Hey Maciej,\n\nAntmicro in Gdansk contributing to OpenROAD at 2482 stars. Antmicro's investment in open source EDA across simulation, synthesis, and now place-and-route is comprehensive. Curious what specific part of the OpenROAD flow you work on.\n\nSeverin"
    },
    # ROW 326 - wponghiran: TILOS MacroPlacement (309 stars) — LinkedIn only, no bio — skip

    # ROW 327 - seldridge: Schuyler Eldridge, SiFive, hardware compiler hacker, PhD BU, Arcade-Cave MiSTer
    "seldridge": {
        "subject": "Hardware compilers at SiFive",
        "message": "Hey Schuyler,\n\nHardware compiler hacker at SiFive with a PhD from BU, and contributing to Arcade-Cave MiSTer at 88 stars. The combination of production RISC-V work and retro arcade FPGA cores is great. Curious whether the hardware compiler work at SiFive involves CIRCT/FIRRTL, or something else.\n\nSeverin"
    },
    # ROW 328 - tgorochowik: Antmicro, Synlig (229 stars)
    "tgorochowik": {
        "subject": "Synlig at Antmicro",
        "message": "Hey Tomasz,\n\nAntmicro contributing to Synlig at 229 stars. A SystemVerilog synthesis plugin for Yosys is critical infrastructure for making open source FPGA toolchains handle real-world designs. Curious what the biggest SystemVerilog synthesis challenge is that Synlig is tackling right now.\n\nSeverin"
    },
    # ROW 329 - Emreyldz06: junior EE, Ankara, UHD — LinkedIn only
    "Emreyldz06": {
        "subject": "",
        "message": "Junior EE in Ankara contributing to Ettus UHD at 1212 stars. Digital design and signal processing on SDR hardware is a great combination. What area of UHD do you focus on?",
        "channel": "linkedin"
    },
    # ROW 329.5 - Emoun: Patmos contributor, no bio but active
    "Emoun": {
        "subject": "Patmos processor project",
        "message": "Hey Emad,\n\nContributing to Patmos at 153 stars. A time-predictable multicore processor for real-time systems is a specialized but important niche. Curious what draws you to the project. Is it the real-time guarantees, or the multicore architecture?\n\nSeverin"
    },
    # ROW 330 - Ttl: Henrik Forstén, Finland, ZipCPU/sdspi (359 stars)
    "Ttl": {
        "subject": "ZipCPU SD/SPI from Finland",
        "message": "Hey Henrik,\n\nContributing to ZipCPU's sdspi at 359 stars from Finland. A clean SD card SPI interface in Verilog is one of those building blocks that lots of FPGA projects need. Curious whether you use this in your own FPGA projects, or if it was more of a targeted contribution.\n\nSeverin"
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
