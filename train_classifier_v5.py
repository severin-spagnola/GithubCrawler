"""
train_classifier_v5.py — V5 LightGBM classifier with:
  - Repo-level holdout split (80/20 by file count, random_state=42) — same 220-repo holdout as V4
  - Stage 1: binary C vs HDL classifier (unchanged from V4)
  - Stage 2: 3-class HDL classifier: synthesis_error, port_mismatch, sensitivity_list
    (api_breaking examples DROPPED from Stage 2 training entirely)
  - TF-IDF fitted ONLY on Stage 2 HDL training patches
  - class_weight='balanced' on LightGBM (no manual sample_weight — avoids V2 double-weighting bug)
  - OOS classification report saved to v5_oos_report.json
  - Model saved to polaris_classifier_v5.pkl
"""

import os, json, collections, random
import numpy as np
import pickle
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
import lightgbm as lgb

examples_dir = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/')

# ---------------------------------------------------------------------------
# 1. Collect all JSON file paths and do a REPO-LEVEL 80/20 split
# ---------------------------------------------------------------------------
all_files = sorted(examples_dir.glob('*.json'))
n_files = len(all_files)
print(f'Total JSON files (repos): {n_files}')

n_train_files = int(n_files * 0.8)
n_test_files = n_files - n_train_files
print(f'Train files: {n_train_files}, Test files: {n_test_files}')

rng = random.Random(42)
shuffled_files = list(all_files)
rng.shuffle(shuffled_files)
train_files = set(str(f) for f in shuffled_files[:n_train_files])
test_files = set(str(f) for f in shuffled_files[n_train_files:])

# ---------------------------------------------------------------------------
# 2. Load examples, tracking which split each file belongs to
# ---------------------------------------------------------------------------
C_LANGS = {'c', 'cpp', 'c++', 'c/c++'}

STAGE2_CLASSES = {'synthesis_error', 'port_mismatch', 'sensitivity_list'}


def load_file(f: Path, split: str) -> list:
    """Load examples from a single JSON file, tagging them with their split."""
    results = []
    try:
        d = json.loads(f.read_text())
        if 'patch' in d:
            # Flat file (synthetic)
            d['_split'] = split
            d['_source_file'] = str(f)
            results.append(d)
        elif 'examples' in d:
            parent_cat = d.get('bug_category')
            for ex in d['examples']:
                if 'bug_category' not in ex and parent_cat:
                    ex = dict(ex)
                    ex['bug_category'] = parent_cat
                ex['_split'] = split
                ex['_source_file'] = str(f)
                results.append(ex)
    except Exception:
        pass
    return results


raw_examples = []
for f in all_files:
    split = 'train' if str(f) in train_files else 'test'
    raw_examples.extend(load_file(f, split))

print(f'Loaded {len(raw_examples)} total examples (after unpacking nested)')

# Assign label field
for e in raw_examples:
    e['label'] = e.get('bug_category')

# Exclude 'other' and 'clock_domain'
examples = [e for e in raw_examples if e.get('label') not in ('other', 'clock_domain', None)]
print(f'After exclusions: {len(examples)} examples')
cats = collections.Counter(e.get('label') for e in examples)
print('Label distribution:', dict(sorted(cats.items(), key=lambda x: -x[1])))

# Classify each example as C or HDL
for e in examples:
    lang = (e.get('language', '') or '').lower()
    e['_is_c'] = lang in C_LANGS

# Split into train/test sets
train_examples = [e for e in examples if e['_split'] == 'train']
test_examples = [e for e in examples if e['_split'] == 'test']
print(f'\nTrain examples: {len(train_examples)}, Test examples: {len(test_examples)}')

# ---------------------------------------------------------------------------
# 3. Feature extraction
# ---------------------------------------------------------------------------
def extract_features(ex):
    patch = ex.get('patch', '') or ''
    before = ex.get('before_code', '') or ''
    lang = ex.get('language', '') or ''
    patch_l = patch.lower()

    added = sum(1 for line in patch.splitlines() if line.startswith('+') and not line.startswith('++'))
    removed = sum(1 for line in patch.splitlines() if line.startswith('-') and not line.startswith('--'))

    return [
        added,
        removed,
        added / (added + removed + 1),
        int('always @' in patch_l or 'process (' in patch_l),
        int('clk' in patch_l or 'clock' in patch_l or 'posedge' in patch_l or 'negedge' in patch_l),
        int('rst' in patch_l or 'reset' in patch_l or 'areset' in patch_l),
        int('input' in patch_l or 'output' in patch_l or 'inout' in patch_l or 'port' in patch_l),
        int('synthesis' in patch_l or 'constraint' in patch_l or 'timing' in patch_l or 'vivado' in patch_l or 'quartus' in patch_l),
        int('void ' in patch_l or 'typedef' in patch_l or 'struct' in patch_l or 'enum' in patch_l or '#define' in patch_l),
        int(lang == 'systemverilog'),
        int(lang == 'vhdl'),
        int(lang in ('c', 'cpp', 'c++')),
        len(patch),
        len(before),
        int('latch' in patch_l or 'if (' in patch_l or 'case (' in patch_l),
        int(ex.get('synthetic', False) == True),
    ]


HAND_FEATURE_NAMES = [
    'patch_lines_added', 'patch_lines_removed', 'patch_ratio',
    'has_sensitivity_list_keyword', 'has_clock_keyword', 'has_reset_keyword',
    'has_port_keyword', 'has_synthesis_keyword', 'has_api_keyword',
    'is_systemverilog', 'is_vhdl', 'is_c',
    'patch_length', 'before_code_length',
    'has_latch_keyword', 'is_synthetic'
]

# ---------------------------------------------------------------------------
# 4. Stage 1: Binary C vs HDL — trained on train set only
# ---------------------------------------------------------------------------
print('\n' + '='*60)
print('STAGE 1: Binary classifier — C vs HDL  (train set only)')
print('='*60)

X_train = np.array([extract_features(e) for e in train_examples], dtype=np.float32)
y1_train = np.array([1 if e['_is_c'] else 0 for e in train_examples])

X_test = np.array([extract_features(e) for e in test_examples], dtype=np.float32)
y1_test = np.array([1 if e['_is_c'] else 0 for e in test_examples])

c_count = int(y1_train.sum())
hdl_count = int((y1_train == 0).sum())
print(f'Train Stage 1 class dist — C (1): {c_count}, HDL (0): {hdl_count}')

stage1_model = lgb.LGBMClassifier(
    objective='binary',
    class_weight='balanced',
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=5,
    n_estimators=300,
    verbose=-1,
)
stage1_model.fit(X_train, y1_train)

# Stage 1 quick eval on test set
y1_pred = stage1_model.predict(X_test)
print(f'Stage 1 OOS Accuracy: {accuracy_score(y1_test, y1_pred):.4f}')
print('Stage 1 OOS Classification Report:')
print(classification_report(y1_test, y1_pred, target_names=['HDL', 'C']))

# ---------------------------------------------------------------------------
# 5. Stage 2: HDL-only 3-class classifier (synthesis_error, port_mismatch, sensitivity_list)
#    - api_breaking examples DROPPED entirely from Stage 2 training
#    - TF-IDF fitted ONLY on Stage 2 HDL training patches
#    - class_weight='balanced' (no manual sample_weight)
# ---------------------------------------------------------------------------
print('\n' + '='*60)
print('STAGE 2: HDL-only 3-class classifier (synthesis_error, port_mismatch, sensitivity_list)')
print('='*60)

# Filter train examples: HDL only, labels in STAGE2_CLASSES (drop api_breaking)
hdl_train_all = [(e, X_train[i]) for i, e in enumerate(train_examples) if not e['_is_c']]
hdl_train_s2 = [(e, x) for e, x in hdl_train_all if e.get('label') in STAGE2_CLASSES]
dropped_api_breaking = sum(1 for e, _ in hdl_train_all if e.get('label') == 'api_breaking')
print(f'HDL train examples available: {len(hdl_train_all)}')
print(f'  Dropped api_breaking (HDL): {dropped_api_breaking}')
print(f'  Stage 2 training examples: {len(hdl_train_s2)}')

train_s2_examples = [e for e, _ in hdl_train_s2]
X_hdl_hand_train = np.array([x for _, x in hdl_train_s2], dtype=np.float32)

s2_label_dist = collections.Counter(e.get('label') for e in train_s2_examples)
print('Stage 2 train label distribution:', dict(s2_label_dist))

# TF-IDF fitted ONLY on Stage 2 HDL training patches
hdl_train_patches = [e.get('patch', '') or '' for e in train_s2_examples]
tfidf = TfidfVectorizer(max_features=500)
X_hdl_tfidf_train = tfidf.fit_transform(hdl_train_patches).toarray()

X_hdl_train = np.hstack([X_hdl_hand_train, X_hdl_tfidf_train])

le2 = LabelEncoder()
y_hdl_train = le2.fit_transform([e.get('label') for e in train_s2_examples])
print(f'Stage 2 classes: {list(le2.classes_)}')

stage2_model = lgb.LGBMClassifier(
    objective='multiclass',
    num_class=len(le2.classes_),
    class_weight='balanced',
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=5,
    n_estimators=300,
    verbose=-1,
)
stage2_model.fit(X_hdl_train, y_hdl_train)

# ---------------------------------------------------------------------------
# 6. Save model
# ---------------------------------------------------------------------------
model_path = Path('/Users/severinspagnola/Desktop/GithubCrawler/polaris_classifier_v5.pkl')
with open(model_path, 'wb') as f:
    pickle.dump({
        'stage1_model': stage1_model,
        'stage2_model': stage2_model,
        'stage2_tfidf': tfidf,
        'label_encoder': le2,
        'hand_feature_names': HAND_FEATURE_NAMES,
        'version': 5,
    }, f)
print(f'\nModel saved to {model_path}')

# ---------------------------------------------------------------------------
# 7. OOS evaluation on held-out test set
# ---------------------------------------------------------------------------
print('\n' + '='*60)
print('OOS EVALUATION (held-out test set)')
print('='*60)

combined_true = []
combined_pred = []

for i, (ex, s1_pred_val) in enumerate(zip(test_examples, y1_pred)):
    true_label = ex.get('label')
    combined_true.append(true_label)

    if s1_pred_val == 1:
        # C example → api_breaking
        combined_pred.append('api_breaking')
    else:
        # HDL example → Stage 2
        hand_feat = X_test[i].reshape(1, -1)
        patch_text = ex.get('patch', '') or ''
        tfidf_feat = tfidf.transform([patch_text]).toarray()
        combined_feat = np.hstack([hand_feat, tfidf_feat])
        s2_pred_enc = stage2_model.predict(combined_feat)[0]
        s2_pred_label = le2.inverse_transform([s2_pred_enc])[0]
        combined_pred.append(s2_pred_label)

# HDL examples truly labeled api_breaking in the test set cannot be predicted correctly by Stage 2
hdl_api_breaking_in_test = sum(
    1 for e in test_examples
    if not e['_is_c'] and e.get('label') == 'api_breaking'
)
print(f'Note: {hdl_api_breaking_in_test} HDL api_breaking examples in test set — '
      f'Stage 2 cannot predict this class, they will be misclassified')

correct = sum(t == p for t, p in zip(combined_true, combined_pred))
combined_acc = correct / len(combined_true)
print(f'\nOOS Combined Accuracy: {combined_acc:.4f} ({combined_acc*100:.1f}%)')

all_labels = sorted(set(combined_true) | set(combined_pred))
report_str = classification_report(combined_true, combined_pred, labels=all_labels, zero_division=0)
print('\nOOS Combined Classification Report:')
print(report_str)

from sklearn.metrics import classification_report as cr
report_dict = cr(combined_true, combined_pred, labels=all_labels, zero_division=0, output_dict=True)

# ---------------------------------------------------------------------------
# 8. Save OOS report JSON
# ---------------------------------------------------------------------------
oos_report = {
    'version': 5,
    'n_train_files': n_train_files,
    'n_test_files': n_test_files,
    'n_train_examples': len(train_examples),
    'n_test_examples': len(test_examples),
    'stage2_classes': list(le2.classes_),
    'hdl_api_breaking_in_test': hdl_api_breaking_in_test,
    'oos_accuracy': round(combined_acc, 4),
    'classification_report': report_dict,
}

oos_path = Path('/Users/severinspagnola/Desktop/GithubCrawler/v5_oos_report.json')
with open(oos_path, 'w') as f:
    json.dump(oos_report, f, indent=2)
print(f'\nOOS report saved to {oos_path}')
