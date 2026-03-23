"""Flip done='YES' for iloc rows 25–29 after asserting outreach fields are populated."""

import pandas as pd

CSV = "fpga_outreach_leads.csv"

df = pd.read_csv(CSV)

for i in range(25, 30):
    row = df.iloc[i]
    username = row["username"]
    old_done = row["done"]
    subject = row["outreach_subject"]
    message = row["outreach_message"]

    assert isinstance(subject, str) and subject.strip(), (
        f"Row {i} ({username}): outreach_subject is empty or missing"
    )
    assert isinstance(message, str) and message.strip(), (
        f"Row {i} ({username}): outreach_message is empty or missing"
    )

    print(f"[BEFORE] iloc {i} | username={username} | done={old_done} | outreach_subject={subject[:80]}")

    df.at[df.index[i], "done"] = "YES"

    print(f"[AFTER]  iloc {i} | username={username} | done=YES | outreach_subject={subject[:80]}")
    print()

df.to_csv(CSV, index=False)
print("CSV written.")
