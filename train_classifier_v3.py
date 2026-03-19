import os, json, collections
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
import lightgbm as lgb

examples_dir = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/')

# ── Load all examples, unpacking nested structures ───────────────────────────
# Flat files (synthetic) have patch/language at top level.
# Nested files have an 'examples' array with the actual patch/language data.
raw_examples = []
for f in examples_dir.glob('*.json'):
    try:
        d = json.loads(f.read_text())
        if 'patch' in d:
            # Flat file (synthetic) — use as-is
            raw_examples.append(d)
        elif 'examples' in d:
            # Nested file — unpack each sub-example, inherit top-level bug_category
            parent_cat = d.get('bug_category')
            for ex in d['examples']:
                # Sub-example has its own bug_category (may differ from parent)
                if 'bug_category' not in ex and parent_cat:
                    ex = dict(ex)
                    ex['bug_category'] = parent_cat
                raw_examples.append(ex)
    except:
        pass

print(f'Loaded {len(raw_examples)} examples (after unpacking nested)')

# Use 'bug_category' as the label field
for e in raw_examples:
    e['label'] = e.get('bug_category')

# Exclude 'other' and 'clock_domain'
examples = [e for e in raw_examples if e.get('label') not in ('other', 'clock_domain', None)]
print(f'After exclusions: {len(examples)} examples')
cats = collections.Counter(e.get('label') for e in examples)
print('Label distribution:', dict(sorted(cats.items(), key=lambda x: -x[1])))

# ── Feature extraction (EXACT copy from train_classifier.py) ─────────────────
def extract_features(ex):
    patch = ex.get('patch', '') or ''
    before = ex.get('before_code', '') or ''
    after = ex.get('after_code', '') or ''
    lang = ex.get('language', '') or ''
    patch_l = patch.lower()
    before_l = before.lower()

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

# ── Classify each example as C or HDL ────────────────────────────────────────
C_LANGS = {'c', 'cpp', 'c++', 'c/c++'}

for e in examples:
    lang = (e.get('language', '') or '').lower()
    e['_is_c'] = lang in C_LANGS

# ── Stage 1: Binary classifier — C vs HDL ────────────────────────────────────
print('\n' + '='*60)
print('STAGE 1: Binary classifier — C vs HDL')
print('='*60)

X_all = np.array([extract_features(e) for e in examples], dtype=np.float32)
y_stage1 = np.array([1 if e['_is_c'] else 0 for e in examples])

c_count = int(y_stage1.sum())
hdl_count = int((y_stage1 == 0).sum())
print(f'Stage 1 class distribution — C (1): {c_count}, HDL (0): {hdl_count}')

X1_train, X1_test, y1_train, y1_test, idx_train, idx_test = train_test_split(
    X_all, y_stage1, np.arange(len(examples)),
    test_size=0.2, random_state=42, stratify=y_stage1
)

stage1_model = lgb.LGBMClassifier(
    objective='binary',
    class_weight='balanced',
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=5,
    n_estimators=300,
    verbose=-1,
)
stage1_model.fit(X1_train, y1_train)

y1_pred = stage1_model.predict(X1_test)
print(f'Stage 1 Accuracy: {accuracy_score(y1_test, y1_pred):.4f}')
print('Stage 1 Classification Report:')
print(classification_report(y1_test, y1_pred, target_names=['HDL', 'C']))

# ── Stage 2: HDL-only multiclass ─────────────────────────────────────────────
print('\n' + '='*60)
print('STAGE 2: HDL-only multiclass classifier')
print('='*60)

# Filter training set to HDL-only examples (stage1 label == 0 in TRAIN split)
train_examples = [examples[i] for i in idx_train]
train_hdl_mask = y1_train == 0
hdl_train_examples = [e for e, is_hdl in zip(train_examples, train_hdl_mask) if is_hdl]
X_hdl_hand_train = X1_train[train_hdl_mask]

print(f'HDL training examples for Stage 2: {len(hdl_train_examples)}')
hdl_train_labels = [e.get('label') for e in hdl_train_examples]
print('Stage 2 train label distribution:', dict(collections.Counter(hdl_train_labels)))

# TF-IDF fitted ONLY on HDL training patches
hdl_train_patches = [e.get('patch', '') or '' for e in hdl_train_examples]
tfidf = TfidfVectorizer(max_features=500)
X_hdl_tfidf_train = tfidf.fit_transform(hdl_train_patches).toarray()

# Combined features: hand-crafted + TF-IDF
X_hdl_train = np.hstack([X_hdl_hand_train, X_hdl_tfidf_train])

le2 = LabelEncoder()
y_hdl_train = le2.fit_transform(hdl_train_labels)
print(f'Stage 2 classes: {list(le2.classes_)}')

# Stage 2 test set — HDL examples in the test split
test_examples_all = [examples[i] for i in idx_test]
test_hdl_mask = y1_test == 0
hdl_test_examples = [e for e, is_hdl in zip(test_examples_all, test_hdl_mask) if is_hdl]
X_hdl_hand_test = X1_test[test_hdl_mask]
hdl_test_labels = [e.get('label') for e in hdl_test_examples]

# Filter test labels to only classes seen in training
valid_test_mask = [lbl in set(le2.classes_) for lbl in hdl_test_labels]
hdl_test_examples_valid = [e for e, v in zip(hdl_test_examples, valid_test_mask) if v]
X_hdl_hand_test_valid = X_hdl_hand_test[valid_test_mask]
hdl_test_labels_valid = [lbl for lbl, v in zip(hdl_test_labels, valid_test_mask) if v]

hdl_test_patches = [e.get('patch', '') or '' for e in hdl_test_examples_valid]
X_hdl_tfidf_test = tfidf.transform(hdl_test_patches).toarray()
X_hdl_test = np.hstack([X_hdl_hand_test_valid, X_hdl_tfidf_test])
y_hdl_test = le2.transform(hdl_test_labels_valid)

# 80/20 split for stage2 reporting — do an internal split of the HDL training data
X2_tr, X2_te, y2_tr, y2_te = train_test_split(
    X_hdl_train, y_hdl_train, test_size=0.2, random_state=42, stratify=y_hdl_train
)

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
stage2_model.fit(X2_tr, y2_tr)

y2_pred = stage2_model.predict(X2_te)
print(f'Stage 2 Accuracy (internal split): {accuracy_score(y2_te, y2_pred):.4f}')
print('Stage 2 Classification Report (internal split):')
print(classification_report(y2_te, y2_pred, target_names=le2.classes_))

# Re-train stage2 on full HDL training data for final model
stage2_model.fit(X_hdl_train, y_hdl_train)

# Top 20 TF-IDF tokens by corpus frequency
vocab = tfidf.get_feature_names_out()
corpus_freq = np.asarray(X_hdl_tfidf_train.sum(axis=0)).flatten()
top20_idx = corpus_freq.argsort()[::-1][:20]
print('\nTop 20 TF-IDF tokens by corpus frequency:')
for i in top20_idx:
    print(f'  {vocab[i]}: {corpus_freq[i]:.2f}')

# ── Combined evaluation on full test set ─────────────────────────────────────
print('\n' + '='*60)
print('COMBINED EVALUATION (full test set)')
print('='*60)

stage1_test_pred = stage1_model.predict(X1_test)

combined_true = []
combined_pred = []

for i, (ex, s1_pred) in enumerate(zip(test_examples_all, stage1_test_pred)):
    true_label = ex.get('label')
    combined_true.append(true_label)

    if s1_pred == 1:
        # C example -> api_breaking
        combined_pred.append('api_breaking')
    else:
        # HDL example -> Stage 2
        hand_feat = X1_test[i].reshape(1, -1)
        patch_text = ex.get('patch', '') or ''
        tfidf_feat = tfidf.transform([patch_text]).toarray()
        combined_feat = np.hstack([hand_feat, tfidf_feat])
        s2_pred_enc = stage2_model.predict(combined_feat)[0]
        s2_pred_label = le2.inverse_transform([s2_pred_enc])[0]
        combined_pred.append(s2_pred_label)

correct = sum(t == p for t, p in zip(combined_true, combined_pred))
combined_acc = correct / len(combined_true)
print(f'Combined Accuracy: {combined_acc:.4f} ({combined_acc*100:.1f}%)')
print(f'V1 Baseline: 52.0%')
print(f'Delta vs V1: {(combined_acc - 0.52)*100:+.1f}%')

all_labels = sorted(set(combined_true) | set(combined_pred))
print('\nCombined Classification Report:')
print(classification_report(combined_true, combined_pred, labels=all_labels, zero_division=0))

# ── Save model ───────────────────────────────────────────────────────────────
model_path = Path('/Users/severinspagnola/Desktop/GithubCrawler/polaris_classifier_v3.pkl')
with open(model_path, 'wb') as f:
    pickle.dump({
        'stage1_model': stage1_model,
        'stage2_model': stage2_model,
        'stage2_tfidf': tfidf,
        'label_encoder': le2,
        'hand_feature_names': HAND_FEATURE_NAMES,
        'version': 3,
    }, f)
print(f'\nModel saved to {model_path}')
