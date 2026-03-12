# GitHub Crawler

Searches GitHub commits and issues for developers experiencing merge conflict pain, enriches each lead with GitHub profile and repo metadata, and outputs a prioritised CSV ranked by signal strength. Designed to run distributed across multiple lab PCs coordinated from a Raspberry Pi.

---

## Requirements

- Python 3.8+ on the Raspberry Pi and each lab PC
- SSH access from the Pi to each lab PC (passwordless after setup)
- One GitHub personal access token per lab PC (classic tokens with `read:user` and `public_repo` scopes)

---

## Setup

### 1. Clone the repo onto the Raspberry Pi

```bash
git clone <repo-url> github-crawler
cd github-crawler
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|---|---|
| `PC_IPS` | Comma-separated IP addresses of lab PCs |
| `PC_USER` | SSH username on each lab PC |
| `GITHUB_TOKENS` | One token per PC, in the same order as `PC_IPS` |
| `QUERIES_FILE` | Path to `queries.txt` (default: `./queries.txt`) |
| `RESULTS_DIR` | Directory where per-PC CSVs are collected (default: `./results`) |
| `OUTPUT_FILE` | Final merged output path (default: `./final_leads.csv`) |

### 4. Push SSH keys and deploy crawler to each PC

```bash
./setup_coordinator.sh
```

This generates `~/.ssh/id_rsa` if needed, runs `ssh-copy-id` to each PC (prompts for password once per PC), and SCPs `crawler.py` to `/tmp/crawler.py` on each machine.

---

## Running

```bash
./run_crawl.sh
```

Or directly:

```bash
python3 coordinator.py
```

The coordinator:
1. Splits `queries.txt` evenly across all PCs
2. SSHs into each PC in parallel and runs the crawler
3. Polls every 60 seconds until all crawlers finish (timeout: 4 hours)
4. SCPs result CSVs back to `RESULTS_DIR`
5. Runs `merge_results.py` to deduplicate, score, and produce the final output

---

## Output

**`final_leads.csv`** contains one row per unique `(username, repo)` lead with the following fields:

| Field | Description |
|---|---|
| `query` | The search query that surfaced this lead |
| `source_type` | `commit`, `issue`, or `pr` |
| `repo` / `repo_name` | Full repo path and short name |
| `org` / `org_type` | Owner login and whether it's a `User` or `Organization` |
| `contributor_count` | Number of contributors to the repo |
| `language` | Primary repo language |
| `stars` | Repo star count |
| `username` | GitHub username |
| `display_name`, `email`, `company`, `bio`, `location` | GitHub profile fields |
| `github_profile`, `linkedin`, `twitter`, `blog` | Contact/social links |
| `commit_message` / `commit_url` / `commit_date` | Source commit or issue details |
| `priority_score` | Integer score (see below) |
| `priority` | `P1`, `P2`, or `P3` |

### Priority tiers

| Label | Score | Meaning |
|---|---|---|
| **P1** | ≥ 8 | High-signal lead — strong repo fit, contact info present, relevant query |
| **P2** | 5–7 | Good lead — worth reaching out |
| **P3** | < 5 | Weak signal — low-fit repo or sparse profile |

Scoring bonuses include: contributor count in the 5–50 sweet spot (+3), email/LinkedIn present (+2 each), org account (+2), hardware language like VHDL/Verilog (+3), systems language like C/C++/Rust (+2), and high-pain queries like "merge conflict" or "synthesis error" (+2).

Leads are filtered before output: bots and CI accounts are removed, and repos with fewer than 3 or more than 500 contributors are excluded.

---

## Rate Limits

GitHub enforces **30 search requests/minute** and **5,000 API calls/hour** per token. With 4 PCs each using a separate token:

- **120 search requests/minute** combined
- **20,000 API calls/hour** combined

The crawler enforces a 2.1-second delay between every API call per token to stay safely within limits. If a 403 rate-limit response is received, the crawler reads the `X-RateLimit-Reset` header and sleeps until the window resets.

---

## A Note on Language Filtering

GitHub's `language:` filter **only works with code search** (`/search/code`), not with commit or issue search. Applying it to commit or issue queries silently returns zero results.

This crawler intentionally omits `language:` from all queries and instead filters by language **after enrichment**, using the primary language field from each repo's metadata. This means you get full result coverage and can filter to any language in post-processing.
