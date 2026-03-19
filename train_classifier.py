import os, json, collections
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import lightgbm as lgb

examples_dir = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/')

# Load all examples
examples = []
for f in examples_dir.glob('*.json'):
    try:
        d = json.loads(f.read_text())
        examples.append(d)
    except: pass

print(f'Loaded {len(examples)} examples')
cats = collections.Counter(e.get('bug_category') for e in examples)
print('Categories:', dict(cats))

# Only train on categories with >= 50 examples
viable_cats = {cat for cat, cnt in cats.items() if cnt >= 50}
print(f'Viable categories (>=50): {viable_cats}')
excluded = {cat: cnt for cat, cnt in cats.items() if cnt < 50}
if excluded:
    print(f'Excluded categories (<50): {excluded}')
examples = [e for e in examples if e.get('bug_category') in viable_cats]
print(f'Training set size: {len(examples)}')

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

FEATURE_NAMES = [
    'patch_lines_added', 'patch_lines_removed', 'patch_ratio',
    'has_sensitivity_list_keyword', 'has_clock_keyword', 'has_reset_keyword',
    'has_port_keyword', 'has_synthesis_keyword', 'has_api_keyword',
    'is_systemverilog', 'is_vhdl', 'is_c',
    'patch_length', 'before_code_length',
    'has_latch_keyword', 'is_synthetic'
]

X = np.array([extract_features(e) for e in examples], dtype=np.float32)
y_raw = [e.get('bug_category') for e in examples]

le = LabelEncoder()
y = le.fit_transform(y_raw)
print(f'Classes: {list(le.classes_)}')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f'Train: {len(X_train)}, Test: {len(X_test)}')

# Train LightGBM
params = {
    'objective': 'multiclass',
    'num_class': len(le.classes_),
    'metric': 'multi_logloss',
    'learning_rate': 0.05,
    'num_leaves': 31,
    'min_child_samples': 5,
    'n_estimators': 300,
    'verbose': -1,
}

model = lgb.LGBMClassifier(**params)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)],
          callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(50)])

y_pred = model.predict(X_test)
print('\nClassification Report:')
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Save model
import pickle
model_path = Path('/Users/severinspagnola/Desktop/GithubCrawler/polaris_classifier.pkl')
with open(model_path, 'wb') as f:
    pickle.dump({'model': model, 'label_encoder': le, 'feature_names': FEATURE_NAMES}, f)
print(f'Model saved to {model_path}')

# Feature importance
print('\nFeature importances:')
importances = model.feature_importances_
for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: -x[1]):
    print(f'  {imp:6.1f}  {name}')
