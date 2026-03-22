#!/usr/bin/env python3
"""Record the pre-run count of rows with a non-empty outreach_subject to /tmp/pre_subject_count.txt."""

import pandas as pd

CSV_PATH = "fpga_outreach_leads.csv"
OUTPUT_PATH = "/tmp/pre_subject_count.txt"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    count = int(
        (df["outreach_subject"].fillna("").astype(str).str.strip() != "").sum()
    )
    with open(OUTPUT_PATH, "w") as f:
        f.write(str(count))
    print(f"Pre-run outreach_subject count: {count} (saved to {OUTPUT_PATH})")


if __name__ == "__main__":
    main()
