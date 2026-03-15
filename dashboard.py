from __future__ import annotations

import csv
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request, send_file


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RAW_RESULTS_PATH = BASE_DIR / "results_local.csv"
LIVE_RESULTS_PATH = Path("/tmp/results_local_run.csv")
LEGACY_RESULTS_PATH = RESULTS_DIR / "results_local.csv"
FINAL_RESULTS_PATH = BASE_DIR / "final_leads.csv"
CONTACTED_PATH = BASE_DIR / "contacted.json"
QUERIES_PATH = BASE_DIR / "queries.txt"

app = Flask(__name__)


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GitHub Crawler Dashboard</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #121a2b;
      --panel-2: #172036;
      --line: rgba(148, 163, 184, 0.18);
      --text: #e5edf8;
      --muted: #8ea0bc;
      --accent: #4f8cff;
      --green: #34d399;
      --yellow: #fbbf24;
      --grey: #94a3b8;
      --red: #f87171;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px),
        radial-gradient(circle at top, rgba(79, 140, 255, 0.16), transparent 30%),
        var(--bg);
      background-size: 32px 32px, 32px 32px, auto, auto;
      color: var(--text);
    }
    .shell {
      width: min(1440px, calc(100% - 32px));
      margin: 24px auto 40px;
    }
    .header, .panel, .stat-card {
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
      border-radius: 14px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
      backdrop-filter: blur(10px);
    }
    .header {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: center;
      padding: 22px 24px;
      margin-bottom: 18px;
    }
    h1, h2, h3, p { margin: 0; }
    .title {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .title p { color: var(--muted); }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.03);
      font-size: 14px;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--grey);
      box-shadow: 0 0 0 0 rgba(148, 163, 184, 0.4);
      animation: pulse 1.8s infinite;
    }
    .status-dot.live { background: var(--green); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.45); }
    .status-dot.dead { background: var(--red); box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.45); }
    @keyframes pulse {
      0% { transform: scale(1); }
      70% { box-shadow: 0 0 0 12px rgba(79, 140, 255, 0); }
      100% { transform: scale(1); }
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .stat-card {
      padding: 18px;
      min-height: 112px;
    }
    .label {
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .value {
      margin-top: 10px;
      font-size: 34px;
      font-weight: 700;
    }
    .meta {
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }
    .panel {
      padding: 18px;
      margin-bottom: 18px;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 14px;
    }
    .chips, .filters, .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .chip, button, select {
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.04);
      color: var(--text);
      border-radius: 10px;
      padding: 10px 12px;
      cursor: pointer;
    }
    .chip.active {
      background: rgba(79, 140, 255, 0.22);
      border-color: rgba(79, 140, 255, 0.7);
    }
    select { cursor: pointer; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 14px;
    }
    th, td {
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }
    th {
      position: sticky;
      top: 0;
      background: #11192a;
      z-index: 1;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }
    tbody tr:hover { background: rgba(255,255,255,0.03); }
    tbody tr.p1 { background: rgba(52, 211, 153, 0.08); }
    tbody tr.p2 { background: rgba(251, 191, 36, 0.09); }
    tbody tr.p3 { background: rgba(148, 163, 184, 0.06); }
    tbody tr.contacted td {
      text-decoration: line-through;
      color: #8fa1bb;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 6px 10px;
      font-weight: 700;
      font-size: 12px;
    }
    .badge.p1 { background: rgba(52, 211, 153, 0.18); color: #8ef0c9; }
    .badge.p2 { background: rgba(251, 191, 36, 0.16); color: #ffd978; }
    .badge.p3 { background: rgba(148, 163, 184, 0.14); color: #d6deea; }
    .table-wrap {
      overflow: auto;
      max-height: 72vh;
      border-radius: 12px;
      border: 1px solid var(--line);
      margin-top: 14px;
    }
    a { color: #8db4ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .muted { color: var(--muted); }
    .toolbar { justify-content: space-between; align-items: center; }
    .actions button { padding: 8px 10px; font-size: 12px; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    @media (max-width: 1100px) {
      .grid, .summary-grid { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 760px) {
      .header { flex-direction: column; align-items: flex-start; }
      .grid, .summary-grid { grid-template-columns: 1fr; }
      .shell { width: min(100% - 20px, 1440px); }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="header">
      <div class="title">
        <h1>GitHub Crawler Dashboard</h1>
        <p>Local crawl monitor for live results, final leads, and outreach state.</p>
      </div>
      <div class="status-pill">
        <span id="status-dot" class="status-dot"></span>
        <span id="status-text">Loading status…</span>
      </div>
    </section>

    <section class="grid">
      <div class="stat-card">
        <div class="label">Current Cycle Progress</div>
        <div class="value" id="queries-processed">0 / 0</div>
        <div class="meta" id="current-updated">Cycle update time: N/A</div>
      </div>
      <div class="stat-card">
        <div class="label">New This Cycle</div>
        <div class="value" id="new-cycle-leads">0</div>
        <div class="meta" id="current-source-meta">Current file: results_local_run.csv</div>
      </div>
      <div class="stat-card">
        <div class="label">Accumulated Backlog</div>
        <div class="value" id="stored-leads">0</div>
        <div class="meta" id="stored-updated">Backlog update time: N/A</div>
      </div>
      <div class="stat-card">
        <div class="label">Grand Total Known</div>
        <div class="value" id="grand-total-leads">0</div>
        <div class="meta">Backlog plus net-new leads from the active cycle.</div>
      </div>
    </section>

    <section class="grid">
      <div class="stat-card">
        <div class="label">Already Seen This Cycle</div>
        <div class="value" id="known-cycle-leads">0</div>
        <div class="meta" id="stored-source-meta">Backlog file: final_leads.csv</div>
      </div>
      <div class="stat-card">
        <div class="label">Current Cycle Total</div>
        <div class="value" id="cycle-total-leads">0</div>
        <div class="meta">All leads observed in the current run, including repeats.</div>
      </div>
      <div class="stat-card">
        <div class="label">Current View Size</div>
        <div class="value" id="current-view-size">0</div>
        <div class="meta">Rows currently shown in the selected scope.</div>
      </div>
      <div class="stat-card">
        <div class="label">What To Work</div>
        <div class="value" id="work-now-count">0</div>
        <div class="meta">Default outreach queue: new unique leads in this cycle.</div>
      </div>
    </section>

    <section class="panel">
      <div class="summary-grid">
        <div>
          <h2>Summary Stats</h2>
          <div class="meta" style="margin-top: 8px;">Default view is new leads from the current cycle so you know who needs outreach now.</div>
          <div class="chips" style="margin-top: 14px;">
            <div class="chip">Current View: <strong id="total-leads">0</strong></div>
            <div class="chip">P1: <strong id="p1-count">0</strong></div>
            <div class="chip">P2: <strong id="p2-count">0</strong></div>
            <div class="chip">P3: <strong id="p3-count">0</strong></div>
            <div class="chip">Public Email: <strong id="email-count">0</strong></div>
            <div class="chip">LinkedIn: <strong id="linkedin-count">0</strong></div>
          </div>
        </div>
        <div>
          <h3>Top Languages</h3>
          <div id="language-breakdown" class="chips" style="margin-top: 14px;"></div>
        </div>
        <div>
          <h3>Queue Scope</h3>
          <div class="filters" style="margin-top: 14px;">
            <button class="chip active" data-scope="current_new">New This Cycle</button>
            <button class="chip" data-scope="stored">Accumulated Backlog</button>
            <button class="chip" data-scope="all">Everything</button>
          </div>
          <h3 style="margin-top: 16px;">Filters</h3>
          <div class="filters" style="margin-top: 14px;">
            <button class="chip active" data-priority="all">All</button>
            <button class="chip" data-priority="P1">P1</button>
            <button class="chip" data-priority="P2">P2</button>
            <button class="chip" data-priority="P3">P3</button>
            <select id="language-filter">
              <option value="all">All languages</option>
            </select>
            <select id="email-filter">
              <option value="all">Email: all</option>
              <option value="yes">Email: yes</option>
              <option value="no">Email: no</option>
            </select>
            <select id="linkedin-filter">
              <option value="all">LinkedIn: all</option>
              <option value="yes">LinkedIn: yes</option>
              <option value="no">LinkedIn: no</option>
            </select>
          </div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="toolbar">
        <div>
          <h2>Export</h2>
          <div class="meta">Download the current active CSV file directly from the Pi.</div>
        </div>
        <div class="chips">
          <a class="chip" href="/export.csv">Download Current CSV</a>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="toolbar">
        <div>
          <h2>Leads</h2>
          <div class="meta">Sorted by <span class="mono">priority_score</span> descending.</div>
        </div>
        <div class="muted">Auto-refresh every 30 seconds</div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Cohort</th>
              <th>Priority</th>
              <th>Name</th>
              <th>Username</th>
              <th>Company</th>
              <th>Language</th>
              <th>Contributors</th>
              <th>Email</th>
              <th>LinkedIn</th>
              <th>Commit Message</th>
              <th>Commit URL</th>
              <th>Commit Date</th>
              <th>Contacted</th>
            </tr>
          </thead>
          <tbody id="leads-body"></tbody>
        </table>
      </div>
    </section>
  </div>

  <script>
const state = {
      rows: { current_new: [], current_known: [], stored: [], all: [] },
      contacted: [],
      scope: 'current_new',
      priority: 'all',
      language: 'all',
      hasEmail: 'all',
      hasLinkedIn: 'all',
    };

    async function fetchState() {
      const resp = await fetch('/api/data', { cache: 'no-store' });
      if (!resp.ok) throw new Error('Failed to load dashboard data');
      return resp.json();
    }

    function setStatus(alive, label) {
      const dot = document.getElementById('status-dot');
      const text = document.getElementById('status-text');
      dot.className = `status-dot ${alive ? 'live' : 'dead'}`;
      text.textContent = label;
    }

    function updateSummary(data) {
      const scopeSummary = data.summary[state.scope] || data.summary.current_new;
      document.getElementById('queries-processed').textContent = `${data.status.queries_processed_current} / ${data.status.queries_total}`;
      document.getElementById('new-cycle-leads').textContent = data.status.new_this_cycle;
      document.getElementById('stored-leads').textContent = data.status.accumulated_total_leads;
      document.getElementById('grand-total-leads').textContent = data.status.accumulated_total_leads + data.status.new_this_cycle;
      document.getElementById('known-cycle-leads').textContent = data.status.already_known_this_cycle;
      document.getElementById('cycle-total-leads').textContent = data.status.current_cycle_raw_leads;
      document.getElementById('current-view-size').textContent = scopeSummary.total;
      document.getElementById('work-now-count').textContent = data.status.new_this_cycle;
      document.getElementById('current-updated').textContent = `Cycle update time: ${data.status.current_cycle_last_updated || 'N/A'}`;
      document.getElementById('stored-updated').textContent = `Backlog update time: ${data.status.accumulated_last_updated || 'N/A'}`;
      document.getElementById('current-source-meta').textContent = `Current file: ${data.status.current_cycle_source_file || 'N/A'}`;
      document.getElementById('stored-source-meta').textContent = `Backlog file: ${data.status.accumulated_source_file || 'N/A'}`;
      document.getElementById('total-leads').textContent = scopeSummary.total;
      document.getElementById('p1-count').textContent = scopeSummary.p1;
      document.getElementById('p2-count').textContent = scopeSummary.p2;
      document.getElementById('p3-count').textContent = scopeSummary.p3;
      document.getElementById('email-count').textContent = scopeSummary.with_email;
      document.getElementById('linkedin-count').textContent = scopeSummary.with_linkedin;

      const box = document.getElementById('language-breakdown');
      box.innerHTML = '';
      const items = scopeSummary.top_languages.length ? scopeSummary.top_languages : [['None', 0]];
      for (const [language, count] of items) {
        const pill = document.createElement('div');
        pill.className = 'chip';
        pill.textContent = `${language}: ${count}`;
        box.appendChild(pill);
      }

      const statusLabel = data.status.running
        ? `Cycle live • ${data.status.new_this_cycle} new / ${data.status.accumulated_total_leads} accumulated`
        : 'Crawler idle';
      setStatus(data.status.running, statusLabel);
    }

    function updateLanguageOptions(rows) {
      const select = document.getElementById('language-filter');
      const current = state.language;
      const langs = Array.from(new Set(rows.map(r => (r.language || '').trim()).filter(Boolean))).sort((a, b) => a.localeCompare(b));
      select.innerHTML = '<option value="all">All languages</option>';
      for (const lang of langs) {
        const opt = document.createElement('option');
        opt.value = lang;
        opt.textContent = lang;
        if (lang === current) opt.selected = true;
        select.appendChild(opt);
      }
    }

    function truncate(text, max = 120) {
      if (!text) return '';
      return text.length > max ? `${text.slice(0, max - 1)}…` : text;
    }

    function scopeRows() {
      return state.rows[state.scope] || [];
    }

    function filteredRows() {
      return scopeRows().filter((row) => {
        if (state.priority !== 'all' && row.priority !== state.priority) return false;
        if (state.language !== 'all' && (row.language || '') !== state.language) return false;
        if (state.hasEmail === 'yes' && !row.email) return false;
        if (state.hasEmail === 'no' && row.email) return false;
        if (state.hasLinkedIn === 'yes' && !row.linkedin) return false;
        if (state.hasLinkedIn === 'no' && row.linkedin) return false;
        return true;
      });
    }

    function renderTable() {
      const tbody = document.getElementById('leads-body');
      tbody.innerHTML = '';
      for (const row of filteredRows()) {
        const tr = document.createElement('tr');
        tr.className = `${(row.priority || 'P3').toLowerCase()} ${row.contacted ? 'contacted' : ''}`;
        const cohortLabel = row.cohort === 'current_new'
          ? 'New This Cycle'
          : row.cohort === 'current_known'
            ? 'Seen Again'
            : 'Backlog';
        tr.innerHTML = `
          <td><span class="badge ${row.cohort === 'current_new' ? 'p1' : row.cohort === 'current_known' ? 'p2' : 'p3'}">${cohortLabel}</span></td>
          <td><span class="badge ${(row.priority || 'P3').toLowerCase()}">${row.priority || 'P3'} (${row.priority_score || 0})</span></td>
          <td>${row.display_name || '<span class="muted">Unknown</span>'}</td>
          <td class="mono">${row.username || ''}</td>
          <td>${row.company || '<span class="muted">-</span>'}</td>
          <td>${row.language || '<span class="muted">-</span>'}</td>
          <td>${row.contributor_count || '<span class="muted">-</span>'}</td>
          <td>${row.email ? `<a href="mailto:${row.email}">${row.email}</a>` : '<span class="muted">-</span>'}</td>
          <td>${row.linkedin ? `<a href="${row.linkedin}" target="_blank" rel="noreferrer">Open</a>` : '<span class="muted">-</span>'}</td>
          <td title="${(row.commit_message || '').replace(/"/g, '&quot;')}">${truncate(row.commit_message || '', 90) || '<span class="muted">-</span>'}</td>
          <td>${row.commit_url ? `<a href="${row.commit_url}" target="_blank" rel="noreferrer">View commit</a>` : '<span class="muted">-</span>'}</td>
          <td class="mono">${row.commit_date || '<span class="muted">-</span>'}</td>
          <td class="actions"><button data-username="${row.username}" ${!row.username ? 'disabled' : ''}>${row.contacted ? 'Contacted' : 'Mark Contacted'}</button></td>
        `;
        tbody.appendChild(tr);
      }
    }

    async function markContacted(username) {
      const resp = await fetch('/api/contacted', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username }),
      });
      if (!resp.ok) throw new Error('Failed to update contacted state');
      const data = await resp.json();
      state.contacted = data.contacted;
      for (const key of Object.keys(state.rows)) {
        state.rows[key] = state.rows[key].map((row) => ({
          ...row,
          contacted: state.contacted.includes(row.username),
        }));
      }
      renderTable();
    }

    async function refresh() {
      const data = await fetchState();
      state.rows = data.rows;
      state.contacted = data.contacted;
      updateSummary(data);
      updateLanguageOptions(scopeRows());
      renderTable();
    }

    document.addEventListener('click', async (event) => {
      const scope = event.target.getAttribute('data-scope');
      if (scope) {
        state.scope = scope;
        document.querySelectorAll('[data-scope]').forEach((btn) => btn.classList.toggle('active', btn.getAttribute('data-scope') === scope));
        updateLanguageOptions(scopeRows());
        const data = await fetchState();
        state.rows = data.rows;
        updateSummary(data);
        renderTable();
      }
      const priority = event.target.getAttribute('data-priority');
      if (priority) {
        state.priority = priority;
        document.querySelectorAll('[data-priority]').forEach((btn) => btn.classList.toggle('active', btn.getAttribute('data-priority') === priority));
        renderTable();
      }
      const username = event.target.getAttribute('data-username');
      if (username) {
        event.target.disabled = true;
        try {
          await markContacted(username);
        } catch (err) {
          event.target.disabled = false;
          alert(err.message);
        }
      }
    });

    document.getElementById('language-filter').addEventListener('change', (event) => {
      state.language = event.target.value;
      renderTable();
    });
    document.getElementById('email-filter').addEventListener('change', (event) => {
      state.hasEmail = event.target.value;
      renderTable();
    });
    document.getElementById('linkedin-filter').addEventListener('change', (event) => {
      state.hasLinkedIn = event.target.value;
      renderTable();
    });

    refresh();
    setInterval(refresh, 30000);
  </script>
</body>
</html>
"""


def count_queries_total() -> int:
    if not QUERIES_PATH.exists():
        return 0
    total = 0
    with QUERIES_PATH.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line and not line.startswith("#"):
                total += 1
    return total


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def load_contacted() -> list[str]:
    if not CONTACTED_PATH.exists():
        return []
    try:
        data = json.loads(CONTACTED_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return sorted({str(item).strip() for item in data if str(item).strip()})


def save_contacted(usernames: list[str]) -> None:
    CONTACTED_PATH.write_text(json.dumps(sorted(set(usernames)), indent=2), encoding="utf-8")


def has_data_rows(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            next(reader)
            return True
    except (OSError, StopIteration):
        return False


def file_timestamp(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def current_cycle_path() -> Path:
    candidates = [LIVE_RESULTS_PATH]
    available = [path for path in candidates if has_data_rows(path)]
    if available:
        return max(available, key=lambda path: path.stat().st_mtime)
    return LIVE_RESULTS_PATH


def persistent_path() -> Path:
    candidates = [RAW_RESULTS_PATH, FINAL_RESULTS_PATH, LEGACY_RESULTS_PATH]
    available = [path for path in candidates if has_data_rows(path)]
    if available:
        return max(available, key=lambda path: path.stat().st_mtime)
    return RAW_RESULTS_PATH


def source_path() -> Path:
    current = current_cycle_path()
    if has_data_rows(current):
        return current
    return persistent_path()


def row_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        (row.get("username") or "").strip(),
        (row.get("repo") or "").strip(),
        (row.get("commit_url") or "").strip(),
    )


def dedupe_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        key = row_key(row)
        if not any(key) or key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def normalize_row(row: dict[str, str], contacted: set[str], cohort: str) -> dict[str, Any]:
    score_raw = row.get("priority_score") or "0"
    try:
      score = int(score_raw)
    except ValueError:
      score = 0
    priority = row.get("priority") or "P3"
    username = (row.get("username") or "").strip()
    return {
        "priority": priority,
        "priority_score": score,
        "display_name": (row.get("display_name") or "").strip(),
        "username": username,
        "company": (row.get("company") or "").strip(),
        "language": (row.get("language") or "").strip(),
        "contributor_count": (row.get("contributor_count") or "").strip(),
        "email": (row.get("email") or "").strip(),
        "linkedin": (row.get("linkedin") or "").strip(),
        "commit_message": (row.get("commit_message") or "").strip(),
        "commit_url": (row.get("commit_url") or "").strip(),
        "commit_date": (row.get("commit_date") or "").strip(),
        "contacted": username in contacted,
        "cohort": cohort,
    }


def compute_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    languages = Counter(row["language"] for row in rows if row["language"])
    return {
        "total": len(rows),
        "p1": sum(1 for row in rows if row["priority"] == "P1"),
        "p2": sum(1 for row in rows if row["priority"] == "P2"),
        "p3": sum(1 for row in rows if row["priority"] == "P3"),
        "with_email": sum(1 for row in rows if row["email"]),
        "with_linkedin": sum(1 for row in rows if row["linkedin"]),
        "top_languages": languages.most_common(5),
    }


def compute_status(current_rows: list[dict[str, str]], stored_rows: list[dict[str, str]]) -> dict[str, Any]:
    current_path = current_cycle_path()
    stored_path = persistent_path()
    current_keys = {row_key(row) for row in current_rows if any(row_key(row))}
    stored_keys = {row_key(row) for row in stored_rows if any(row_key(row))}
    processed = len({(row.get("query") or "").strip() for row in current_rows if (row.get("query") or "").strip()})
    return {
        "queries_processed_current": processed,
        "queries_total": count_queries_total(),
        "current_cycle_raw_leads": len(current_rows),
        "accumulated_total_leads": len(stored_rows),
        "new_this_cycle": len(current_keys - stored_keys),
        "already_known_this_cycle": len(current_keys & stored_keys),
        "current_cycle_last_updated": file_timestamp(current_path),
        "accumulated_last_updated": file_timestamp(stored_path),
        "current_cycle_source_file": current_path.name,
        "accumulated_source_file": stored_path.name,
        "running": current_path.exists(),
    }


@app.get("/")
def index() -> str:
    return render_template_string(HTML)


@app.get("/export.csv")
def export_csv() -> Any:
    active = source_path()
    download_name = active.name if active.exists() else "results.csv"
    return send_file(active, as_attachment=True, download_name=download_name, mimetype="text/csv")


@app.get("/api/data")
def api_data() -> Any:
    current_rows = dedupe_rows(read_csv_rows(current_cycle_path()))
    stored_rows = dedupe_rows(read_csv_rows(persistent_path()))
    contacted = set(load_contacted())
    stored_keys = {row_key(row) for row in stored_rows if any(row_key(row))}
    current_new_rows = [row for row in current_rows if row_key(row) not in stored_keys]
    current_known_rows = [row for row in current_rows if row_key(row) in stored_keys]

    rows_current_new = [normalize_row(row, contacted, "current_new") for row in current_new_rows]
    rows_current_known = [normalize_row(row, contacted, "current_known") for row in current_known_rows]
    rows_stored = [normalize_row(row, contacted, "stored") for row in stored_rows]
    rows_all = rows_current_new + rows_current_known + rows_stored

    for collection in (rows_current_new, rows_current_known, rows_stored, rows_all):
        collection.sort(key=lambda row: row["priority_score"], reverse=True)
    return jsonify(
        {
            "status": compute_status(current_rows, stored_rows),
            "summary": {
                "current_new": compute_summary(rows_current_new),
                "current_cycle": compute_summary(rows_current_new + rows_current_known),
                "stored": compute_summary(rows_stored),
                "all": compute_summary(rows_all),
            },
            "rows": {
                "current_new": rows_current_new,
                "current_known": rows_current_known,
                "stored": rows_stored,
                "all": rows_all,
            },
            "contacted": sorted(contacted),
        }
    )


@app.post("/api/contacted")
def api_contacted() -> Any:
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400
    contacted = load_contacted()
    if username not in contacted:
        contacted.append(username)
        save_contacted(contacted)
    return jsonify({"contacted": sorted(contacted)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
