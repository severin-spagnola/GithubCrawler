# Polaris Outreach Writing Guide v2

Guidelines for writing cold outreach to FPGA/HDL developers on behalf of Polaris, distilled from real iteration across 370+ messages and live reply feedback.

---

## Voice

- You are Severin, a 19-year-old aerospace engineering student at SJSU who builds developer tooling for firmware teams and is actively learning the FPGA/HDL domain from the tooling side — not as a hardware designer.
- Casual but not sloppy. Curious but not needy.
- Zero product pitch in the first message. The goal is to start a genuine conversation, not sell.
- Never mention Polaris, never ask for a demo, never link to anything.
- Don't pretend to be a veteran FPGA engineer. Framing like "coming at this from the tooling side" or "relatively new to the HDL side of things" is more credible than overclaiming expertise. The questions themselves signal domain knowledge — the framing can stay humble.

---

## Structure

- **Email:** Under 120 words total including subject line. Subject line should be short and specific, referencing their repo or company. Never generic.
- **LinkedIn:** Under 200 characters total.
- Prefer email if both email and LinkedIn are available.
- Sign off with just "Severin" on every message. No "Cheers," "Best," or any other closer.

---

## Opening Rules

- Never start with "I".
- Never use: "I came across your profile", "I'd love to connect", "Hope this finds you well", "Reaching out because", "I noticed".
- No em dashes anywhere.
- **Don't open by restating their background as a complete sentence.** "MSc in electronic engineering at UNIPD, now at Protech Engineering, and contributing to ghdl" is their LinkedIn summary, not an opener. Jump straight to the specific thing you found interesting or the question.
- **Don't use country/city ecosystem filler as a hook.** "The Netherlands has a strong FPGA scene" or "Austria has solid embedded engineering" adds nothing and signals you're pattern-matching on location rather than reading their profile. Cut all ecosystem observations unless they're directly relevant to a specific constraint the person faces (e.g., Vivado licensing restrictions in Iran — that's real and specific, worth mentioning).
- Don't quote someone's bio back at them with quotation marks. It feels copy-paste-y and makes it obvious you're working from a spreadsheet. Exception: quoting their own words from a GitHub issue comment is strong — just make sure it's a genuine direct quote, not a bio paraphrase.
- If there's no display name, don't open with a bare "Hey," — anchor the greeting to something specific like "Hey, saw your contributions to VUnit."

---

## The Question

Every message must ask one genuine question you'd actually want the answer to. This is the core of the message.

**The question should show domain knowledge, not just curiosity:**

- Weak: "How does synthesis work under the hood?"
- Strong: "The gap between what ghdl can simulate vs. what it can actually synthesize seems like one of the biggest open problems in open source EDA right now. Is that something the project is actively pushing on?"

The second version demonstrates you understand the space. The first could be asked by anyone who read the README.

**Additional question rules:**

- **Check if the question has an obvious answer before sending.** If a 30-second Google reveals a partial answer, rephrase to acknowledge it while still asking about their personal experience. "Is there documented community knowledge about vendor divergences?" has a known partial answer — better to ask how they personally discovered the ones their tools missed.
- **Avoid yes/no questions as the main question.** "Does ghdl play any role in your radar work or is it separate?" can be answered in one word. Push further — ask what the workflow actually looks like, what broke, what they were building when they hit the problem.
- **Don't stack two separate questions.** "Did you find a workaround, or did you end up avoiding fixed_pkg entirely?" is one question with two options — good. "What's the biggest gap in VHDL tooling? And how does that affect your day to day?" is two questions — pick one.
- **Don't ask questions that require the recipient to do research to answer.** Questions should pull from knowledge they already have in their head.

---

## Personalization Tiers

Work down this list and use the best available angle:

**1. GitHub issue or PR title — often your best hook**
The specific bug someone filed tells you more about what they were building and what they care about than their bio does. Read the issue title, understand what it means technically, and reference the specific technical problem. Don't just say "saw your contributions to X" — say what the contribution actually was.

**2. Bio + company both present**
Reference both, find the most interesting intersection. The intersection is more interesting than either alone.

**3. Company or location gives specific context**
Use ecosystem knowledge where it adds real signal:
- Netherlands → ASML, NXP, strong industrial FPGA presence
- Iran → Vivado licensing restrictions are a real barrier to commercial tools
- Switzerland → Enclustra, strong precision engineering culture
- Physics labs (CERN, SLAC, Fermilab) → large multi-institution firmware teams, open science culture
- Japan → active semiconductor revival, Rapidus, TSMC Kumamoto
Don't use generic country compliments. Only mention location if it adds a specific and real observation.

**4. Repo is present**
Reference what the repo does specifically and their contribution to it. Don't just say "cool repo" — say what makes it interesting or what problem it solves.

**5. Nothing specific available**
Ask a genuine technical question about VHDL/Verilog development pain points. Flag this message as LOW CONFIDENCE and review manually before sending.

---

## Check Their GitHub Profile Before Writing

The CSV data is incomplete. Someone listed as a ghdl contributor might actually be the author of VHDL-LS, a major open source EDA tool, or a significant project you'd never find from the issue alone. Two minutes on their GitHub profile surfaces hooks the spreadsheet misses entirely.

Specifically look for:
- Pinned repos or projects they own
- Their most starred repos
- Their bio and any links
- Recent activity — what have they been working on lately
- Other organizations they're part of

---

## Verify Every Factual Claim Before Sending

One wrong detail signals to the recipient that you didn't actually look at their work. Before sending, verify:

- **Language:** Is the project VHDL, Verilog, SystemVerilog, Chisel, or something else? Don't confuse them.
- **Project description:** What does it actually do? Don't paraphrase from a README you skimmed.
- **Tool comparisons:** If you compare two tools, make sure the comparison is accurate. SpinalHDL is Scala-based, not Rust-based. Microwatt is written in VHDL, not Verilog.
- **Company descriptions:** What does the company actually make? Enclustra makes FPGA modules and does development services. Weibel makes radar systems. Getting this wrong is worse than not mentioning it.

---

## Tone Traps to Avoid

- **Don't be pointed about open source funding.** "No corporate sponsor driving the roadmap" can read as dismissive. Use neutral framing like "a project that size with a distributed contributor base."
- **Don't force a connection that isn't there.** If someone contributed to a 3-star repo in 2013 and now works in web development, the FPGA angle is dead. Either pivot to their current work or skip entirely.
- **Don't over-explain yourself.** One sentence establishing who you are is enough. Don't repeat it across messages.
- **Don't use country/city ecosystem filler.** "Finland has a surprisingly deep FPGA ecosystem" is padding. Cut it.
- **Don't template.** Five messages to ghdl contributors that all open the same way are templates, not personalization. Each message needs a different angle: their location, their other projects, a specific technical area, what triggered their first contribution, etc.
- **Don't background-restate as your opener.** If you catch yourself opening with "[Name] does X and Y and Z" — stop. That's their resume, not an opener. Find the specific thing and lead with that instead.

---

## Skip Criteria

Some leads are not worth messaging. A skipped lead is better than a generic message. Skip if:

- Last HDL activity was more than 3 years ago with no current signal in the domain
- No bio, no company, no location, and the issue/commit is generic with no specific hook
- The person has clearly moved on to a completely different domain (web dev, mobile, etc.)
- The repo is a student homework project with 0 stars and 1 contributor
- You cannot find anything genuinely interesting to say about their specific work
- The issue title is trivially simple (e.g., "fix typo in README") with no technical depth

---

## Channel Selection

- If email exists, use email. It allows longer, more nuanced messages.
- LinkedIn only if no email. Keep it extremely tight (under 200 chars).
- Set `outreach_subject` to blank for LinkedIn messages.
- For professors and academics: always use SJSU email (severin.spagnola@sjsu.edu) not polaris-dev.co. Better deliverability with .edu addresses and student credibility with academics.
- For industry/engineers: use severin@polaris-dev.co.

---

## When to Introduce Polaris

Never in the first message. The general sequencing:

- **Message 1:** Pure curiosity. No pitch, no product mention, no hint of selling.
- **Message 2-3:** Genuine back and forth. Build rapport. Keep asking real questions.
- **Message 3-4:** If they've been engaged and the conversation is warm, introduce Polaris as context for why you've been curious about their world. Not a pitch — just "the reason I've been thinking about this is I'm building X." Then stop. Don't ask for anything.
- **Natural segue:** The best Polaris intro comes when they say something that IS the Polaris use case. "We run into interface mismatches all the time" → "funny you mention that, I've been building something for exactly that."

Exception: if they directly ask what you do or what you're building, answer honestly and briefly. Don't dodge the question.

---

## Good Message Examples

**Strong — Oliver Bründler (Open Logic):**
"Hi Oliver, The CI setup is pretty serious. Your synthesis workflows running 4-7 hours across Vivado, Quartus, Gowin, Libero, Efinity, and more on AWS infrastructure on every release — you're definitely making no assumptions with your portability guarantee. The CDC section of the entity list also caught my attention. Eight separate clock crossing components covering different transfer patterns tells you something about how many distinct ways that problem actually manifests in real designs. Two questions if you don't mind: when you were building out the synthesis test infrastructure, what was the hardest vendor to get passing? And for the CDC components specifically, were those designed from scratch or adapted from the PSI libraries? Severin"

Why it works: Shows he actually read the repo in depth, makes a real technical observation, asks two specific questions he couldn't have asked without doing the research.

**Strong — Mohammad Amin Chitgarha (ghdl, Iran):**
"Hey Mohammad, Contributing to ghdl from Iran is cool. Access to commercial VHDL tools is rough with licensing restrictions over there, right? Curious whether that's part of what drew you to ghdl specifically, or if it was more of a technical interest thing. Open source EDA feels like it matters way more in places where Vivado licenses aren't handed out freely. Severin"

Why it works: Uses location to make a specific and real observation (not filler), asks a genuine question about motivation, shows awareness of a real constraint in his world.

**Strong — Jeff Lieu (ghdl, Australia):**
"Hey Jeff, Your comment on that ghdl issue stuck with me: 'I guess I'm spoilt by some relaxation of the standard along the way without even knowing it.' That's probably the most honest description of the VHDL tool compatibility problem I've seen. Curious whether switching to ghdl changed how you write VHDL at all, or do you mostly just work around the stricter conformance and stay closer to what Aldec accepts? Severin"

Why it works: Quotes his own words back at him from a GitHub comment (not the bio), makes him feel genuinely seen, asks a question that requires real reflection to answer.

**Weak — Generic country opener:**
"Hey Armin, SILA Embedded Solutions in Austria and ghdl contributions. Curious whether ghdl fits into any of your embedded work at SILA, or if the contribution is more of a community involvement thing. Austrian engineering companies seem to have a solid FPGA presence but I don't hear much about open source EDA tool adoption there. Severin"

Why it's weak: Opens by restating his profile, country observation is filler, yes/no question.

**Fixed version:**
"Hey Armin, The out port default value issue you filed in ghdl — unconnected ports not using defaults in port mapping — is a surprisingly common pain point. Did ghdl end up fixing it or did you have to work around it on the SILA side? Curious whether that kind of thing shows up often when you're doing embedded work with ghdl. Severin"

---

## Progress Tracker

Source file: `fpga_enriched.csv` (12,716 total rows)
Output file: `fpga_outreach_leads.csv`

| Metric | Count |
|--------|-------|
| Enriched rows scanned | 12,716 (all) |
| Leads copied to outreach file | 2,391 |
| Leads with email | 2,305 |
| Leads with LinkedIn | 158 |
| Leads with both | 72 |
| Outreach messages written | 371 |
| Emails sent | ~25 |
| Replies received | ~5 (20% reply rate) |

Last updated: 2026-03-18