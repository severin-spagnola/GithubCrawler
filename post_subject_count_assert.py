#!/usr/bin/env python3
"""Read post-run outreach_subject count from fpga_outreach_leads.csv and assert it is strictly greater than the pre-run count saved in /tmp/pre_subject_count.txt."""

import sys
import pandas as pd

CSV_PATH = "fpga_outreach_leads.csv"
PRE_COUNT_PATH = "/tmp/pre_subject_count.txt"


def main() -> None:
    with open(PRE_COUNT_PATH, "r") as f:
        pre_count = int(f.read().strip())

    df = pd.read_csv(CSV_PATH)
    post_count = int(
        (df["outreach_subject"].fillna("").astype(str).str.strip() != "").sum()
    )

    print(f"Pre-run outreach_subject count:  {pre_count}")
    print(f"Post-run outreach_subject count: {post_count}")

    assert post_count > pre_count, (
        f"FAIL: post-run count ({post_count}) is not strictly greater than "
        f"pre-run count ({pre_count})"
    )
    print(f"PASS: outreach_subject count increased by {post_count - pre_count}")


if __name__ == "__main__":
    main()
