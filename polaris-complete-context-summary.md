# POLARIS — Complete Context Summary (March 12, 2026)

## What Polaris Is

Polaris is a real-time conflict detection tool for development teams. It's an IDE extension (VS Code/Cursor) that watches teammates' uncommitted code and flags breaking changes in seconds, before anyone pushes. The tagline: "We catch the conflicts git can't see."

**Slogan:** "See breaking changes before they break."

**Core differentiator:** Deterministic detection (no AI guesswork), pre-push (before commit/PR/CI), cross-file dependency tracing, and first-class support for firmware/FPGA/embedded languages that no other tool covers.

## Founders

- **Severin Spagnola** — CTO & Co-Founder. 19, sophomore Aerospace Engineering at SJSU. Built the entire technical stack solo. 4x hackathon winner (NVIDIA, Google DeepMind). Previous projects: CrowdQuant, HealthGrid AI, AgentRouter, Darwinian Optimization Lab.
- **Nayab Hossain** — CEO & Co-Founder. 19, sophomore Computer Engineering at SJSU. Handles business/GTM.

## Current Status

- **In Plug and Play accelerator** (Enterprise & AI, Spring 2026 batch)
- **Raising pre-seed:** $700K SAFE
- **VS Code marketplace:** Live as "Polaris-Dev"
- **Website:** polaris-dev.co (clean, demos, audit page, privacy policy)
- **Auth chain:** Working end-to-end (signup → API key → extension → human names in alerts)
- **Pre-revenue.** No paying customers yet. First pilots being onboarded.

## Technical Stack

- **Backend:** FastAPI/Python, ~16K lines in `main.py`, hosted on Render
- **Extension:** TypeScript, VS Code/Cursor extension
- **Database:** PostgreSQL
- **Detection:** Fully deterministic — regex-based symbol extraction, merge-tree analysis, dependency graph traversal

## What It Detects (All Working)

### Languages (9) + File Types (10):
- TypeScript/JavaScript — function signatures, exports, imports
- C/C++ — function signatures, #include chains, header changes
- Python — functions, classes, dataclasses, enums (recently added)
- VHDL — entity ports, generics, widths, directions
- Verilog — module ports, parameters, widths
- Rust — pub functions, structs, enums, traits
- Linker scripts (.ld) — memory regions, ORIGIN, LENGTH
- Device trees (.dts) — properties, compatible strings, status
- Kconfig — config symbols, defaults, types
- CMake — variables, targets
- Makefiles — variables, targets

### Detection Types:
1. **Semantic conflicts** — function signature mismatches, port width changes, struct field renames, enum variant changes, parameter default changes
2. **Cross-file dependency breaks** — traces import/include/instantiation chains. If Dev A changes `spi.h`, Dev B's `main.c` gets flagged even though Dev B never touched `spi.h`
3. **Divergence detection** — same file edited differently by two devs
4. **Firmware-specific enrichment** — linker memory region conflicts, device tree property changes, Kconfig option conflicts

### Signal Lifecycle:
- Signals create on detection, persist while conflict exists, auto-close on revert
- Signal supersession (new signals replace stale ones for same device pair)
- Whitespace/comment-only diffs filtered out (configurable)

### Other Features:
- AI-powered conflict resolution suggestions (working, uses LLM API)
- Notification toggle (suppress popups, keep underlines)
- Comment detection toggle
- Whitespace detection toggle
- .polignore file support
- Symbol-only mode (no source code transmitted, only signatures — for defense/ITAR teams)
- Privacy policy page on site
- Compact hover tooltips showing only what changed, not full signatures

## Architecture

### Detection Flow:
1. Extension watches working tree for file changes
2. On save, creates WIP git bundle and uploads to backend
3. Backend runs merge-tree analysis between teammates' working trees
4. Semantic detectors extract symbols and compare signatures
5. DependencyIndex traces cross-file relationships
6. Signals created and pushed to extension
7. Extension renders inline underlines with hover details

### Key Architecture Decision:
- **DependencyIndex** handles cross-file detection (import/include chains)
- **PathIndex** handles same-file divergence (both devs editing same file)
- Both are complementary, not exclusive

### Known Bugs/Limitations:
- VHDL cross-file signals don't always close properly on revert (revalidation logic was modified then reverted — needs proper fix)
- Whitespace-only diffs in cross-file path should be filtered (check added but verify)
- Two VS Code instances with same API key = same user_id = self-conflicts filtered out. Workaround: use different API keys per instance. Long-term: workspace-level keys where device_id differentiates users.

## Pricing Model

- **Free ($0/mo):** Up to 5 teammates, 1 workspace, all features
- **Pro ($25/workspace/mo):** 6-10 teammates, multiple workspaces, conflict history, priority support
- **Team ($50/workspace/mo):** 10-15 teammates, symbol-only mode, admin dashboard
- **Enterprise ($25/seat/mo, contact us):** 16+ unlimited, on-prem deployment, custom detectors, SLA, dedicated onboarding

28-day free trial for all plans. No Stripe integration yet — manual tier upgrades via admin dashboard.

## Workspace/Auth Model

- 1 API key per account, required to use extension
- Workspaces have unique auto-generated IDs (ws_xxxx) and display names
- One person creates workspace, shares ID with team
- Seat enforcement at backend level — workspace rejects new members when full
- Admin can manually upgrade tiers via admin endpoints (X-Admin-Secret: GOON)

## Outreach & GTM Status

### University Outreach:
- **Professor Choo (EE 178, FPGA/VHDL/Verilog):** Met in person. Feedback: product is "too basic/amateur" — needs behavioral verification, spec compliance checking, not just port mismatches. Suggested studying real use cases. Referred to study architecture docs. Valuable feedback but harsh. Follow-up email sent asking for architecture spec reference material.
- **Professor Ghofraniha (CMPE 125, Verilog):** Office hours Tuesdays 10AM-12PM at E273. Has not been visited yet.
- **Professor Wu (CMPE 195, Senior Design):** Thursday office hours 9-11AM by appointment.
- **Professor Fox:** Engaged via email. Objection: "disciplined teams shouldn't need this." Replied with "reinforces discipline + catches cross-file issues process can't" framing. He suggested reaching out to SAE (Spartan Racing).
- **Professor Rojas (CMPE 131):** Replied saying students need to learn from breakages themselves. Suggested SAE club.
- **Professor Luca (remote):** Impressed, didn't realize it was a VS Code extension. Asked for referrals to colleagues with team-heavy project courses.
- **Morris Jones (EE 272, SystemVerilog):** Referred by Thuy Le (EE dept chair). Email sent. morris.jones@sjsu.edu, office ENG 295.
- **97 university professor leads** in CSV with personalized emails (no em dashes, IDE not VSCode, location-based CTAs — in-person for local, Google Meet for remote)

### Pilot Status:
- **SCU Robotics:** Confirmed pilot. C++, Python, ROS. Club still forming engineering teams. Logo swap agreed.
- **No other active pilots yet.**

### Enterprise/Industry Outreach:
- **Tony Long (Northrop Grumman, Innovation Manager):** HIGHEST PRIORITY LEAD. His literal job is scouting early-stage tech for Northrop. 23 years at NG. Runs Technology Accelerator Program with FedTech. Message sent with full pitch + symbol-only mode mention + PnP connection.
- **Krunal Patil (NVIDIA, Firmware Engineering Manager):** Responded! NVIDIA uses AI agents aware of specs/arch docs/firmware code/RTL to catch issues. Key intel: confirms spec-aware detection is the direction. Conversation ongoing — asked about real-time vs review-step approach.
- **Thomas Yeh (Synopsys, SJSU alum):** Staff engineer doing FPGA workflow automation. His FPGA optical flow project is still on SJSU ENG building wall. Personalized message sent referencing poster.
- **Ivan Kravets (PlatformIO CEO):** Connected. Potential integration partner — PlatformIO has zero conflict detection features. Message sent proposing partnership/integration conversation.
- **Martin Vo (VC, SJSU CE alum):** Met at event, follow-up sent asking for call.
- **Wasif Iqbal:** Asked detailed technical questions (monorepo, security, Go/PHP). Replied with full technical answers. His team may use Go/PHP which we don't support yet.
- **40+ SMB firmware companies** in lead CSV with personalized outreach. Need to find actual engineering contacts (not CEOs) for companies 30+.
- **90+ SJSU ENG building poster alumni leads** photographed and added to CSV with two-step outreach (connect request, then pitch after accept).

### GitHub Crawler Project:
- Multi-machine crawler system designed to run across SJSU iHouse lab computers
- Coordinated via Raspberry Pi over SSH
- Searches GitHub for commits/PRs/issues mentioning merge conflicts, breaking changes, port mismatches etc.
- Extracts contributor profiles, emails, LinkedIn URLs
- Priority scoring system: VHDL/Verilog repos with 5-50 contributors score highest
- Full project spec with code written and ready to deploy

### Outreach Messaging Principles (learned through iteration):
- Say "IDE extension" not "VSCode extension"
- Say "catches the conflicts git can't see" not "Grammarly for merge conflicts" or "real-time merge conflict detection"
- No em dashes in any messaging
- For professors: offer demo first, don't ask to drop things in course channels
- For engineers: be direct, reference specific repos/commits/hiring
- For VCs: don't pitch hard, plant seeds, follow up with traction
- For defense: always mention symbol-only mode
- LinkedIn connection requests: short, no pitch, reference something specific. Pitch comes AFTER they accept.
- Email from SJSU address to professors (better deliverability + student credibility)
- Email from polaris-dev.co to companies
- Slow email sending: 5-10/day max to avoid domain reputation damage (currently 8.9/10 on mail-tester, DKIM setup done on GoDaddy/Outlook)

## Professor Choo's Feedback (Critical — Shapes Future Direction)

Choo said the product was "too basic/amateur" for serious FPGA teams. His key points:
1. **Port mismatches are surface-level.** Real hardware teams need behavioral verification — ensuring acquired IP or new changes match architecture specifications.
2. **Spec-driven validation:** Given an architecture doc that specifies power requirements, response times, interface contracts, the tool should be able to verify that code/IP matches those specs.
3. **His suggestion:** Study 1-3 real use cases (e.g., aerospace navigation systems) and build detection around those specific scenarios.

**How this connects to NVIDIA's approach (from Krunal):** NVIDIA uses AI agents that are "aware of specification, arch/uarch docs, C firmware code and verilog rtl design" to answer these kinds of questions. This validates Choo's direction.

**The long-term roadmap this implies:**
1. **Now:** Deterministic structural detection (what we have — ports, signatures, configs)
2. **Next:** Spec-aware detection (parse architecture docs, verify IP behavioral contracts)
3. **Long-term:** Pattern-learned detection (trained on aggregate conflict data across customers)

**For demos going forward:** Show 3+ different conflict types, not just one. The Choo meeting failed partly because only the port width demo was shown, making him think that's all we do.

## Plug and Play Program

- **Program Manager:** Brenda Flores-Reyes (Enterprise & AI, Silicon Valley)
- **Happy Hour:** April 2, 2026, Southern Pacific Brewing, SF — register and attend
- **Silicon Valley Summit:** May 19-20, 2026. Enterprise & AI pitch slot May 19th 3:15-4:45 PM. Audience of 3,000 including VCs and corporate partners. THIS IS THE BIG EVENT.
- **Workshops:** Weekly on Thursdays, already added to calendar
- **Mentor sessions:** 1-on-1, 30 minutes, first come first serve. Sign up for mentors with enterprise software, dev tools, or hardware/semiconductor backgrounds.
- **Perks:** Email perks@pnptc.com for full catalog. Look for LinkedIn Sales Navigator, Microsoft for Startups (Azure credits), HubSpot CRM.
- **Key events to attend:** IP protection presentation, government collaboration workshop, LinkedIn service partner overview
- **Press release:** March 26, 2026 (batch announcement — confidential until then)
- **Need to do:** Complete intake form, share availability for 1-on-1 with program manager, watch orientation recording

## Social Media / Content

### LinkedIn Posts (planned):
1. ✅ Company intro post (written, ready to publish with demo video)
2. Product capabilities post (multiple demo videos showing TS, C, config conflicts)
3. "Polaris or Git? Polaris AND git"
4. "AI code review tools fix one bug and introduce another" — contrarian take
5. Marketplace announcement
6. "We tried to replace project managers" — why passive detection beats active PM
7. Professor Choo meeting post: "An FPGA professor told us our product was too basic. He's right. Back to the drawing board on firmware detection."
8. "We sent 40 cold LinkedIn messages to defense contractors. Zero responses. Then we walked into a building on campus."
9. "Two 19-year-olds trying to sell dev tools to Lockheed Martin"

### Posting Rules:
- Native video > links > images on LinkedIn
- 1080x1080 square for mobile feed real estate
- Post demo videos directly, don't link to site
- Drop site URL in comments, not in post body
- Don't name-drop competitor products (Claude, Copilot) until established
- Don't use CTAs — let the demo speak

## Key Files Created This Session

- `/polaris-dashboard-overhaul.md` — Dashboard alignment with actual product
- `/polaris-audit-auth-apikeys-onboarding.md` — Auth chain audit prompt
- `/polaris-debug-vhdl-crossfile.md` — VHDL detection debug prompt
- `/polaris-test-real-extension-crossfile.md` — Real extension test protocol
- `/polaris-codex-add-consumer-scan-vhdl-verilog-rust.md` — Consumer scan for 3 languages
- `/polaris-implement-python-support.md` — Python language support prompt
- `/polaris-implement-workspace-tiers.md` — Workspace tier enforcement + admin controls
- `/polaris-symbol-only-privacy-stripe.md` — Symbol-only mode + privacy policy + Stripe guide
- `/polaris-marketplace-readme-metadata.md` — VS Code marketplace listing content
- `/polaris-smb-outreach-rewrite-prompt.md` — SMB firmware company outreach rewrite
- `/polaris-github-crawler-project.md` — Full GitHub crawler lead gen system
- `/polaris-github-search-phrases.md` — Search query list for crawler
- `/polaris-update-pricing-page.md` — Pricing page feature lists
- `/Polaris-Overview.docx` — One-page company overview document
- `/PolarisLeads_University_Rewritten.csv` — 97 professor emails rewritten
- `/PolarisLeads_SJSU_ENG_Updated.csv` — 105 SJSU alumni leads with two-step outreach
- `/GIF-SCENARIOS.md` — 10 demo scenarios for landing page GIFs

## Immediate Priorities

1. **Visit Professor Ghofraniha** — Tuesday office hours 10AM E273. Bring VHDL AND Verilog demos. Show 3+ conflict types.
2. **Book Professor Wu** — Thursday 9-11AM appointment.
3. **Reply to Krunal** — Async, keep learning, don't push for call yet.
4. **Monitor Tony Long response** — Northrop Grumman. If he replies, drop everything and respond immediately.
5. **Deploy GitHub crawlers** on iHouse lab computers.
6. **Complete PnP intake form** and share availability with program manager.
7. **Register for April 2 happy hour.**
8. **Start prepping May 19 Summit pitch.**
9. **Fix the two-API-key demo setup** so it works reliably for professor visits.
10. **Study 1-3 real VHDL/Verilog architecture examples** per Choo's advice.

## Things NOT to Do Right Now

- Don't build Stripe integration (manual upgrades until first paying customer)
- Don't build JetBrains support (only when a customer asks)
- Don't build SystemVerilog (only basic Verilog for now)
- Don't build behavioral/spec verification (learn first, build later)
- Don't spend money on Apollo/Sales Nav (use PnP LinkedIn perk instead)
- Don't restructure auth model (two API keys workaround is fine for demos)
- Don't send more than 5-10 cold emails per day from polaris-dev.co domain
