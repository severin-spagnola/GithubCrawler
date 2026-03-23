#!/usr/bin/env python3
"""rewrite_outreach_v1.py — Rewrite outreach messages using Claude claude-sonnet-4-6 + the Outreach Writing Guide."""

import argparse
import json
import math
import re
import time

import anthropic
import pandas as pd

CSV_PATH = "fpga_outreach_leads.csv"
BATCH_SIZE = 25

INTER_BATCH_SLEEP = 1  # seconds

OUTREACH_RULES = r"""
# Polaris Outreach Writing Guide v3

Guidelines for writing cold outreach to FPGA/HDL developers on behalf of Polaris, distilled from real iteration across 497 messages, a full 8-rule audit, and live reply feedback.

---

## Voice

- You are Severin, a 19-year-old aerospace engineering student at SJSU who builds developer tooling for firmware teams and is actively learning the FPGA/HDL domain from the tooling side.
- Casual but not sloppy. Curious but not needy.
- Zero product pitch in the first message. The goal is to start a genuine conversation, not sell.
- Never mention Polaris, never ask for a demo, never link to anything.

---

## The 8 Rules (hard requirements)

Every outreach message must pass all 8 of these. No exceptions.

### Rule 1 — No geographic filler
Never reference where someone is from as a hook or observation. Do not say "The German FPGA scene is strong," "The Dutch ecosystem between ASML and the university groups," "The Australian embedded scene tends to go deep," or any variant. Location is not a hook. If the only interesting thing you found about someone is where they live, find something else.

**Exception:** Location is allowed only when it creates a specific, real constraint relevant to their work (e.g., Vivado licensing restrictions in Iran). Generic country observations are never allowed.

### Rule 2 — No restating their profile back at them
Do not open with a description of who they are that they already know. "[Title] at [Company] contributing to [repo] at N stars" is not a hook. The person knows where they work and what they contribute to.

Find something specific about their actual contribution — a bug they filed, a PR they opened, a specific technical detail from their work — and reference that instead.

### Rule 3 — No "what does the FPGA/EDA landscape look like in [place]" questions
This is a lazy question that signals you have nothing specific to say. Cut it entirely.

### Rule 4 — No cliche openers or filler praise
- Do not start with "I came across your work," "I noticed your contributions," "I saw your profile," or any variant.
- Do not start with "I" at all.
- Do not use "fascinating," "impressive," "interesting combination," "caught my eye," "caught my attention," or similar filler praise.
- Do not use mild flattery like "you probably spotted it faster than most" — it undercuts an otherwise clean message.

### Rule 5 — One genuine question only
Every message ends with exactly one question. The question must be specific to what the person actually worked on — not a generic "do you use this professionally or personally" question unless there is genuinely nothing more specific to ask.

Prefer questions about:
- Technical decisions they made in a specific PR or issue
- Specific bugs or diagnostic details ("did it manifest as corrupted data, or no output at all?")
- How a specific tool fits into a real workflow

### Rule 6 — No pitch, no product mention
Do not mention Polaris. Do not mention conflict detection. Do not mention any product. Zero selling in the first message.

### Rule 7 — Sign off with just "Severin"
No "Best," no "Thanks," no "Regards," no "Cheers." Just "Severin" on its own line.

### Rule 8 — Length
Maximum 4 sentences including the question. Shorter is better. If you cannot find enough specific information to write 2 genuine sentences, write a SKIP instead of a message — do not pad with filler to reach a minimum length.

---

## How to Find Hooks

The CSV contains a `commit_message` and `commit_url` for each lead. These are your primary hooks.

**Priority order:**

1. **The specific issue/PR title** — this is almost always your best hook. Read the title, understand what it means technically, and reference the specific problem. "The ISERDESE2 reset problem you reported on OpenHBMC" is 10x better than "Contributing to OpenHBMC."

2. **The technical implication** — don't just name the issue, show you understand why it matters. "Naming mismatches between synthesis and simulation silently break verification" shows you understood the fix. "Your PR on cell renaming" does not.

3. **A genuine diagnostic question** — the best questions are ones a fellow engineer would ask. "Did it manifest as corrupted data reads, or was the ISERDES not producing valid output at all?" is a real diagnostic question. "What got you involved?" is not.

4. **Bio/company intersection** — only if it adds signal beyond what the issue already provides. Never restate context the person already knows ("NVIDIA's networking division does serious FPGA and ASIC work for SmartNICs" — they know this, cut it).

**If no specific hook exists** (no issue title, no bio, no company, generic commit), write SKIP.

---

## Subject Line Rules

Subject lines must be specific to the person's actual work.

**Good:** `ISERDESE2 reset issue in OpenHBMC`, `VUnit circular dependency with shared entities`, `ghdl discriminant assertion failure`, `mc6809 AVMA signal behavior`

**Bad:** `FPGA tooling question`, `quick question`, `your open source work`, `VHDL developer outreach`, `FPGA work from Seattle`

If you cannot write a specific subject line, the message should probably be SKIP.

---

## What Makes a Strong Message (from user feedback)

These messages were called out as excellent:

**Ross Schlaikjer (SERV ret behavior):** Specific bug, clear technical understanding, genuine question.

**Viktor Schneider (GF180 cell renaming):** The observation about naming mismatches silently breaking verification shows you understood why the fix matters.

**Mohammad Hossein Ghasemi (ISERDESE2):** Good technical detail, the question about corrupted data vs no output at all is a real diagnostic question not a filler question.

**Chuck Benedict (mc6809 AVMA):** Specific, warm, the retrocomputing angle is genuine.

**Giuseppe Sarda (Vortex spawn_kernel):** Technically sharp, the hardware vs software runtime question is exactly the right thing to ask.

### Pattern: what these all share
- Lead with the specific technical artifact (bug, PR, issue)
- Show you understood the technical implication, not just the title
- Ask one question that a fellow engineer would genuinely want answered
- No geographic filler, no profile restating, no cliches

---

## What to Avoid (from user feedback)

- **Restating context they already know:** "NVIDIA's networking division (ex-Mellanox) does serious FPGA and ASIC work for SmartNICs" — they work there, they know this. Cut it. Go straight to the question.
- **Mild flattery:** "you probably spotted it faster than most" undercuts an otherwise clean message. Cut it.
- **Broad questions when specific ones exist:** "Have you ever considered applying CI/CD thinking to hardware verification?" is decent but broad. If there's something specific about their Jenkins work that connects to hardware verification, use that instead.
- **Country/ecosystem filler as padding:** This was the #1 violation in the audit (139 messages). It's never a hook.
- **Profile restating as opener:** This was the #2 violation (147 messages). Never open with who they are and where they work.

---

## Structure

- **Email:** Max 4 sentences including the question. Subject line should be specific to their contribution.
- **LinkedIn:** Under 200 characters total. No subject line.
- Sign off with just "Severin" on every message.

---

## Verify Every Factual Claim Before Sending

One wrong detail signals to the recipient that you didn't actually look at their work. Before sending, verify:

- **Language:** Is the project VHDL, Verilog, SystemVerilog, Chisel, or something else?
- **Project description:** What does it actually do?
- **Tool comparisons:** SpinalHDL is Scala-based, not Rust-based. Microwatt is VHDL, not Verilog.
- **Company descriptions:** What does the company actually make?

---

## Skip Criteria

Some leads are not worth messaging. A skipped lead is better than a generic message. Skip if:

- The commit_message is trivially simple ("fix typo", "update README") with no technical depth
- No bio, no company, and the issue has no specific technical hook
- The person has clearly moved on to a different domain
- The repo is a student homework project with 0 stars and 1 contributor
- You cannot write 2 genuine sentences without padding

---

## Channel Selection

- If email exists, use email.
- LinkedIn only if no email. Keep it under 200 chars.
- Set `outreach_subject` to blank for LinkedIn messages.
"""


def build_prompt(row: pd.Series) -> str:
    """Build the per-row prompt for Claude."""
    commit_message = str(row.get("commit_message", "") or "")
    bio = str(row.get("bio", "") or "")
    company = str(row.get("company", "") or "")
    display_name = str(row.get("display_name", "") or "")
    commit_url = str(row.get("commit_url", "") or "")
    repo = str(row.get("repo", "") or "")
    username = str(row.get("username", "") or "")
    outreach_channel = str(row.get("outreach_channel", "") or "")

    return f"""You are writing a cold outreach message for Severin to send to an FPGA/HDL developer.

LEAD INFO:
- Display name: {display_name}
- Username: {username}
- Company: {company}
- Bio: {bio}
- Repo: {repo}
- Commit/issue title: {commit_message}
- Commit URL: {commit_url}
- Outreach channel: {outreach_channel}

{OUTREACH_RULES}

INSTRUCTIONS:
Write one outreach message for this lead following ALL rules above.

Return your response as JSON with exactly these keys:
- "subject": The email subject line (leave empty string if channel is LinkedIn)
- "message": The full outreach message text
- "status": Either "DONE" if you wrote a real message, or "SKIP" if the hook data is insufficient per the skip criteria above

If status is "SKIP", set subject and message to empty strings."""


def rewrite_outreach(csv_path: str, start_row: int = 0, end_row: int = None, force: bool = False) -> None:
    """Main rewrite loop."""
    client = anthropic.Anthropic()

    df = pd.read_csv(csv_path)

    # Record pre-run count of rows with non-empty outreach_subject
    pre_subject_count = int(
        (df["outreach_subject"].fillna("").astype(str).str.strip() != "").sum()
    )
    with open("/tmp/pre_subject_count.txt", "w") as f:
        f.write(str(pre_subject_count))
    print(f"Pre-run outreach_subject count: {pre_subject_count} (saved to /tmp/pre_subject_count.txt)")

    # Determine which rows need processing
    if force:
        mask = pd.Series([True] * len(df))
    else:
        done_col = df["done"].fillna("").astype(str).str.strip().str.upper()
        mask = ~done_col.isin(["YES", "SKIP"])

    indices = df.index[mask].tolist()
    indices = indices[start_row:(end_row if end_row is not None else None)]
    total_rows = len(indices)
    total_batches = math.ceil(total_rows / BATCH_SIZE) if total_rows > 0 else 0

    if total_rows == 0:
        print("WARNING: 0 rows selected — nothing to do. Check --start-row/--end-row or use --force to override.")
        return

    print(f"Total rows to process: {total_rows} in {total_batches} batches")

    for batch_num in range(total_batches):
        batch_start = batch_num * BATCH_SIZE
        batch_end = min(batch_start + BATCH_SIZE, total_rows)
        batch_indices = indices[batch_start:batch_end]

        rewritten = 0
        skipped = 0

        for idx in batch_indices:
            row = df.loc[idx]
            prompt = build_prompt(row)

            try:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )

                text = response.content[0].text
                clean = re.sub(r'^```[a-z]*\n?|```$', '', text.strip(), flags=re.MULTILINE).strip()
                result = json.loads(clean)

                status = result.get("status", "SKIP").upper()
                print(f"  [{idx}] {status} — {df.at[idx, 'username']}")
                if status == "SKIP":
                    df.at[idx, "done"] = "SKIP"
                    df.at[idx, "outreach_subject"] = ""
                    df.at[idx, "outreach_message"] = ""
                    skipped += 1
                else:
                    df.at[idx, "outreach_subject"] = result.get("subject", "")
                    df.at[idx, "outreach_message"] = result.get("message", "")
                    df.at[idx, "done"] = "YES"
                    rewritten += 1

            except Exception as e:
                print(f"  Error on row {idx} ({df.at[idx, 'username']}): {e}")
                skipped += 1

        # Checkpoint: write updated DataFrame back to CSV after each batch
        df.to_csv(csv_path, index=False)

        print(
            f"Batch {batch_num + 1}/{total_batches} done — "
            f"{rewritten} rewritten, {skipped} skipped"
        )

        # Sleep between batches (not after the last one)
        if batch_num < total_batches - 1:
            time.sleep(INTER_BATCH_SLEEP)

    print("All batches complete.")

    # --- Post-run verification ---
    df_final = pd.read_csv(csv_path)
    total_skip = (df_final["done"].astype(str).str.strip().str.upper() == "SKIP").sum()
    print(f"\nTotal SKIP count: {total_skip}")

    # Check every non-SKIP row has a non-empty outreach_subject
    non_skip = df_final[df_final["done"].astype(str).str.strip().str.upper() != "SKIP"]
    empty_subjects = non_skip[non_skip["outreach_subject"].fillna("").astype(str).str.strip() == ""]
    if len(empty_subjects) > 0:
        print(f"WARNING: {len(empty_subjects)} non-SKIP rows have empty outreach_subject")
        print(empty_subjects[["username"]].to_string())
    else:
        print("OK: All non-SKIP rows have a non-empty outreach_subject.")

    # Validate CSV is readable
    try:
        pd.read_csv(csv_path)
        print(f"OK: {csv_path} is valid CSV ({len(df_final)} rows).")
    except Exception as e:
        print(f"ERROR: CSV validation failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rewrite outreach messages via Claude claude-sonnet-4-6")
    parser.add_argument("--csv", default=CSV_PATH, help=f"Path to CSV (default: {CSV_PATH})")
    parser.add_argument("--start-row", type=int, default=0)
    parser.add_argument("--end-row", type=int, default=None, help="Exclusive end index for row processing")
    parser.add_argument("--force", action="store_true", help="Force-overwrite all rows, ignoring done status")
    args = parser.parse_args()

    rewrite_outreach(args.csv, start_row=args.start_row, end_row=args.end_row, force=args.force)
