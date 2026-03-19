"""Generate additional synthetic api_breaking examples to reach 100+ total."""
import os, json, hashlib, difflib, time
from pathlib import Path

examples_dir = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/')

# Count existing api_breaking
existing = []
for f in examples_dir.glob('*.json'):
    try:
        d = json.loads(f.read_text())
        if d.get('bug_category') == 'api_breaking':
            existing.append((f.name, d))
    except:
        pass

print(f'Existing api_breaking: {len(existing)}')
existing_synth = [f for f, d in existing if d.get('synthetic')]
print(f'  synthetic: {len(existing_synth)}')

# Find highest existing synthetic index
max_idx = 0
for fname, _ in existing:
    if fname.startswith('synthetic_api_breaking_'):
        try:
            idx = int(fname.replace('synthetic_api_breaking_', '').replace('.json', ''))
            max_idx = max(max_idx, idx)
        except:
            pass
print(f'Highest existing synthetic index: {max_idx}')

# Collect existing patch_hashes
existing_hashes = set()
for _, d in existing:
    ph = d.get('patch_hash', '')
    if ph:
        existing_hashes.add(ph)
print(f'Existing hashes: {len(existing_hashes)}')

# Read API key
env_path = Path('/Users/severinspagnola/Desktop/CIRCA/.env')
api_key = None
for line in env_path.read_text().splitlines():
    if line.startswith('ANTHROPIC_API_KEY='):
        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
        break

if not api_key:
    print('ERROR: No ANTHROPIC_API_KEY found')
    exit(1)

import anthropic
client = anthropic.Anthropic(api_key=api_key)

system_prompt = '''You are an expert firmware/embedded systems engineer generating training data for a bug classifier. Generate realistic C/C++ firmware code examples of api_breaking bugs — changes that break the API contract for callers. These should look like real commits from real embedded/firmware projects.'''

user_prompt = '''Generate a JSON array of exactly 10 unique api_breaking examples. Each object must have:
- "before_code": the C/C++ firmware code before the breaking change (10-40 lines, realistic)
- "after_code": the same file after the breaking change
- "language": always "c"
- "description": one sentence describing the breaking change

Variety is important. Mix these types: function signature changes (added/removed/renamed params), struct layout changes, removed exported functions, macro redefinitions, enum value shifts, typedef changes, removed header exports, callback signature changes, return type changes, error code value changes.

Return ONLY the raw JSON array, no markdown, no explanation.'''

synthetics = []
target_new = 50  # generate 50 more to be safe (57 + 50 = 107 total)
batches_needed = (target_new + 9) // 10  # ceiling div

for batch in range(batches_needed):
    print(f'  Generating batch {batch+1}/{batches_needed}...')
    for attempt in range(3):
        try:
            msg = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=8192,
                messages=[{'role': 'user', 'content': user_prompt}],
                system=system_prompt
            )
            text = msg.content[0].text.strip()
            # Strip markdown code blocks if present
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
            batch_examples = json.loads(text)
            if isinstance(batch_examples, list):
                synthetics.extend(batch_examples)
                print(f'    Got {len(batch_examples)} examples (total so far: {len(synthetics)})')
                break
        except Exception as e:
            print(f'    Attempt {attempt+1} failed: {e}')
            if attempt < 2:
                time.sleep(2)
    time.sleep(0.5)

print(f'\nGenerated {len(synthetics)} raw synthetic examples')

# Write unique ones
added = 0
hashes_seen = set(existing_hashes)
next_idx = max_idx + 1

for i, s in enumerate(synthetics):
    if added >= target_new:
        break
    before = s.get('before_code', '')
    after = s.get('after_code', '')
    lang = s.get('language', 'c')
    desc = s.get('description', '')

    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    patch_lines = list(difflib.unified_diff(before_lines, after_lines, fromfile='a/firmware.c', tofile='b/firmware.c'))
    patch = ''.join(patch_lines)

    ph = hashlib.sha256(patch.encode()).hexdigest() if patch else hashlib.sha256(f'synth_extra_{i}'.encode()).hexdigest()
    if ph in hashes_seen:
        print(f'  Skipping duplicate synthetic {i}')
        continue
    hashes_seen.add(ph)

    fname = f'synthetic_api_breaking_{next_idx:03d}.json'
    obj = {
        'before_code': before,
        'after_code': after,
        'patch': patch,
        'bug_category': 'api_breaking',
        'language': lang,
        'before_ref': 'synthetic',
        'synthetic': True,
        'description': desc,
        'patch_hash': ph
    }
    (examples_dir / fname).write_text(json.dumps(obj, indent=2))
    added += 1
    next_idx += 1

print(f'Added {added} new synthetic api_breaking examples')
print(f'New total api_breaking: {len(existing) + added}')

# Update summary.json
import collections
all_cats = collections.Counter()
for f in examples_dir.glob('*.json'):
    try:
        d = json.loads(f.read_text())
        all_cats[d.get('bug_category', '?')] += 1
    except:
        pass

summary_path = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/summary.json')
summary = json.loads(summary_path.read_text())
summary['category_counts'] = dict(all_cats)
summary['total_examples'] = sum(all_cats.values())
summary['consolidation_applied'] = True
summary_path.write_text(json.dumps(summary, indent=2))

print('\nFinal category distribution:')
for cat, cnt in sorted(all_cats.items(), key=lambda x: -x[1]):
    flag = ' <-- BELOW 50' if cnt < 50 else (' <-- BELOW 100' if cnt < 100 else '')
    print(f'  {cnt:5d}  {cat}{flag}')
print(f'  TOTAL: {sum(all_cats.values())}')
print('Updated summary.json')
