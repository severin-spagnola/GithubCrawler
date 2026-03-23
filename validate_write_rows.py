"""
Validate quality of WRITE rows in fpga_outreach_leads.csv.

Checks for each row where status=WRITE:
  (a) outreach_message has <= 4 sentences
  (b) first word is not 'I'
  (c) message does not contain banned phrases:
      'fascinating', 'impressive', 'unique approach', 'FPGA scene', 'open source FPGA'

Prints any violations found.
"""

import csv
import re
import sys

CSV_PATH = "fpga_outreach_leads.csv"

BANNED_PHRASES = [
    "fascinating",
    "impressive",
    "unique approach",
    "fpga scene",
    "open source fpga",
]


def count_sentences(text: str) -> int:
    """Count sentences by splitting on sentence-ending punctuation followed by space or end."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty strings
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)


def validate():
    violations = []

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_num = row.get("number", "?")
            status = (row.get("status") or "").strip()

            if status != "WRITE":
                continue

            msg = (row.get("outreach_message") or "").strip()
            if not msg:
                violations.append(f"Row {row_num}: outreach_message is empty")
                continue

            # (a) <= 4 sentences
            n_sentences = count_sentences(msg)
            if n_sentences > 4:
                violations.append(
                    f"Row {row_num}: {n_sentences} sentences (max 4). Message: {msg[:80]}..."
                )

            # (b) first word is not 'I'
            first_word = msg.split()[0] if msg.split() else ""
            if first_word == "I":
                violations.append(
                    f"Row {row_num}: first word is 'I'. Message: {msg[:80]}..."
                )

            # (c) no banned phrases (case-insensitive)
            msg_lower = msg.lower()
            for phrase in BANNED_PHRASES:
                if phrase in msg_lower:
                    violations.append(
                        f"Row {row_num}: contains banned phrase '{phrase}'. Message: {msg[:80]}..."
                    )

    # Report
    if violations:
        print(f"VIOLATIONS FOUND: {len(violations)}\n")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("ALL WRITE ROWS PASS VALIDATION. No violations found.")
        sys.exit(0)


if __name__ == "__main__":
    validate()
