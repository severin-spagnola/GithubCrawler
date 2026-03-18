# Outreach Writing Guide

Guidelines for writing cold outreach to FPGA/HDL developers on behalf of Polaris, distilled from real iteration on the first batch of messages.

## Voice

- You are Severin, a 19-year-old aerospace engineering student at SJSU who works in HDL and thinks deeply about engineering problems.
- Casual but not sloppy. Curious but not needy.
- Zero product pitch in the first message. The goal is to start a genuine conversation, not sell.
- Never mention Polaris, never ask for a demo, never link to anything.

## Structure

- **Email:** Under 120 words total including subject line. Subject line should be short and specific, referencing their repo or company.
- **LinkedIn:** Under 200 characters total.
- Prefer email if both email and LinkedIn are available.
- Sign off with just "Severin" on every message. No "Cheers," "Best," or any other closer. Keep it consistent.

## Opening Rules

- Never start with "I".
- Never use: "I came across your profile", "I'd love to connect", "Hope this finds you well", "Reaching out because", "I noticed".
- No em dashes anywhere.
- Don't quote someone's bio back at them with quotation marks. It feels copy-paste-y and makes it obvious you're working from a spreadsheet.
- Don't restate what's already in their profile as your opening line (e.g., "You clearly care about compilers and portability"). Jump straight to the interesting question or observation instead.
- If there's no display name, don't open with a bare "Hey," — anchor the greeting to something specific like "Hey, saw your contributions to VUnit."

## The Question

Every message must ask one genuine question you'd actually want the answer to. This is the core of the message.

- The question should show domain knowledge, not just curiosity. Compare:
  - Weak: "How does synthesis work under the hood?"
  - Strong: "The gap between what ghdl can simulate vs. what it can actually synthesize seems like one of the biggest open problems in open source EDA right now. Is that something the project is actively pushing on?"
- The second version demonstrates you understand the space. The first could be asked by anyone who read the README.

## Personalization Tiers

Work down this list and use the best available angle:

1. **Bio + company both present:** Reference both, find the most interesting intersection.
2. **Company or location gives context:** Use ecosystem knowledge (e.g., Netherlands = ASML/NXP, Iran = Vivado licensing barriers, Enclustra = FPGA module vendor). Name-dropping specific companies or constraints shows you actually know the space.
3. **Repo is present:** Reference what the repo does specifically and their contribution to it. Don't just say "cool repo."
4. **Nothing specific available:** Ask a genuine technical question about VHDL/Verilog development pain points.

## Tone Traps to Avoid

- **Don't be pointed about open source funding.** Saying "no corporate sponsor driving the roadmap" can read as dismissive to contributors who are proud of their community-driven project. Use neutral framing like "a project that size with a distributed contributor base."
- **Don't force a connection that isn't there.** If someone contributed to a 3-star repo in 2013 and now works in web development, the FPGA angle is dead. Either pivot to their current work or skip the lead entirely.
- **Don't over-explain yourself.** One sentence establishing who you are is enough ("I'm an aero engineering student at SJSU who works in HDL"). Don't repeat it in every message and don't elaborate unless it adds to the question you're asking.
- **Don't use filler compliments about countries or ecosystems.** "Finland has a surprisingly deep FPGA ecosystem for its size" is padding. Cut it and go straight to the question.
- **Don't stack multiple generic questions.** One focused question is better than two vague ones. "What area do you work in? What keeps you contributing?" reads like a survey.
- **Don't template.** If 5 messages to ghdl contributors all open with "Saw your work on ghdl. What area do you focus on?" the messages are templated, not personalized. Each message to a contributor on the same project needs a different angle: their location, their other projects, a specific technical area, what triggered their first contribution, etc.
- **Do your research.** If someone's CSV entry only shows ghdl but they actually authored VHDL-LS or another major project, the generic ghdl message misses the best hook entirely. A quick check of their GitHub profile can surface angles the spreadsheet data doesn't capture.
- **Verify every factual claim before sending.** If you name a specific tool, verify the language it's written in, what it does, and who maintains it. One wrong detail (e.g., calling a VHDL project "Verilog") signals to the recipient that you didn't actually look at their work. This applies to: language (VHDL vs Verilog vs SystemVerilog vs Chisel), project descriptions, company descriptions, and tool comparisons.

## Lead Quality Check

Before writing a message, assess whether the lead is worth outreach:

- Do they have recent activity in HDL/FPGA? If their last hardware commit was years ago and they've moved on, deprioritize.
- Is there enough signal to personalize? A message with no specific angle is worse than no message.
- For leads in countries with email compliance considerations (Iran, EU/GDPR regions), individual cold email to a developer about technical topics is generally fine, but be aware of the context.

## Channel Selection

- If email exists, use email. It allows longer, more nuanced messages.
- LinkedIn only if no email. Keep it extremely tight (under 200 chars).
- Set `outreach_subject` to blank for LinkedIn messages.

## Progress Tracker

Source file: `fpga_enriched.csv` (12,716 total rows)
Output file: `fpga_outreach_leads.csv`

| Metric | Count |
|---|---|
| Enriched rows scanned so far | 12,716 (all) |
| Leads copied to outreach file (unique) | 2,391 |
| Leads with email | 2,305 |
| Leads with LinkedIn | 158 |
| Leads with both | 72 |
| Outreach messages written | 371 |
| Enriched rows remaining to scan | 0 |

Last updated: 2026-03-16
