import os, json, collections, re
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix
import lightgbm as lgb
import pickle

examples_dir = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/')

examples = []
for f in examples_dir.glob('*.json'):
    try:
        examples.append(json.loads(f.read_text()))
    except: pass

print(f'Loaded {len(examples)} examples')
cats = collections.Counter(e.get('bug_category') for e in examples)
print('All categories:', dict(sorted(cats.items(), key=lambda x: -x[1])))

# Only train on categories with >= 50 examples, EXCLUDE 'other' (too ambiguous)
EXCLUDE_CATS = {'other', 'clock_domain'}
viable_cats = {cat for cat, cnt in cats.items() if cnt >= 50 and cat not in EXCLUDE_CATS}
print(f'Training categories: {viable_cats}')
print(f'Excluded: {EXCLUDE_CATS | {cat for cat, cnt in cats.items() if cnt < 50}}')

examples = [e for e in examples if e.get('bug_category') in viable_cats]
print(f'Training set size: {len(examples)}')
cats2 = collections.Counter(e.get('bug_category') for e in examples)
print('Training distribution:', dict(sorted(cats2.items(), key=lambda x: -x[1])))

def extract_hand_features(ex):
    patch = ex.get('patch', '') or ''
    before = ex.get('before_code', '') or ''
    after = ex.get('after_code', '') or ''
    lang = (ex.get('language', '') or '').lower()
    patch_l = patch.lower()
    before_l = before.lower()

    added_lines = [l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('++')]
    removed_lines = [l[1:] for l in patch.splitlines() if l.startswith('-') and not l.startswith('--')]
    added = len(added_lines)
    removed = len(removed_lines)
    added_text = ' '.join(added_lines).lower()
    removed_text = ' '.join(removed_lines).lower()

    # Port width patterns: [N:0], [7:0], [31:0] changes
    port_width_added = len(re.findall(r'\[\s*\d+\s*:\s*\d+\s*\]', ' '.join(added_lines)))
    port_width_removed = len(re.findall(r'\[\s*\d+\s*:\s*\d+\s*\]', ' '.join(removed_lines)))
    port_width_changed = int(port_width_added != port_width_removed)

    # Port direction keywords in added/removed
    input_output_added = len(re.findall(r'\b(input|output|inout)\b', added_text))
    input_output_removed = len(re.findall(r'\b(input|output|inout)\b', removed_text))

    # Sensitivity list patterns: always @(...)
    always_block_added = len(re.findall(r'always\s*@\s*\(', added_text))
    always_block_removed = len(re.findall(r'always\s*@\s*\(', removed_text))
    has_star_sensitivity = int('always @(*)' in patch_l or 'always @( *)' in patch_l or 'always_comb' in patch_l)
    has_edge_in_sensitivity = int(bool(re.search(r'always\s*@\s*\([^)]*(?:posedge|negedge)[^)]*\)', patch_l)))
    sensitivity_list_changed = int(always_block_added > 0 or always_block_removed > 0)

    # Module/port instantiation changes
    module_keyword = int('module ' in patch_l or '.clk(' in patch_l or '.rst(' in patch_l)
    port_map_changed = len(re.findall(r'\.(\w+)\s*\(', patch))

    # Synthesis tool keywords
    has_synthesis_tool = int(any(kw in patch_l for kw in ['vivado', 'quartus', 'xdc', 'sdc', 'ucf', 'timing', 'constraint', 'bitstream']))
    has_pragma = int('synthesis' in patch_l or '/* synthesis' in patch_l or '// synthesis' in patch_l)

    # Latch/combinational logic issues
    has_latch_pattern = int('latch' in patch_l or "if (" in patch_l)
    case_without_default = int('case (' in patch_l and 'default' not in patch_l)

    # API-breaking: function signatures, typedefs, structs
    has_typedef = int('typedef' in patch_l)
    has_struct = int('struct' in patch_l)
    has_enum = int('enum ' in patch_l)
    has_define = int('#define' in patch_l)
    func_sig_changed = int(bool(re.search(r'(void|int|uint\w*|bool|char)\s+\w+\s*\(', patch_l)))

    # Language
    is_sv = int(lang == 'systemverilog')
    is_vhdl = int(lang == 'vhdl')
    is_c = int(lang in ('c', 'cpp', 'c++'))
    is_verilog = int(lang == 'verilog')

    # Patch statistics
    patch_len = len(patch)
    before_len = len(before)
    ratio = added / (added + removed + 1)

    is_synthetic = int(bool(ex.get('synthetic', False)))

    return [
        added, removed, ratio,
        port_width_added, port_width_removed, port_width_changed,
        input_output_added, input_output_removed,
        always_block_added, always_block_removed,
        has_star_sensitivity, has_edge_in_sensitivity, sensitivity_list_changed,
        module_keyword, port_map_changed,
        has_synthesis_tool, has_pragma,
        has_latch_pattern, case_without_default,
        has_typedef, has_struct, has_enum, has_define, func_sig_changed,
        is_sv, is_vhdl, is_c, is_verilog,
        patch_len, before_len,
        is_synthetic,
    ]

HAND_FEATURE_NAMES = [
    'patch_lines_added', 'patch_lines_removed', 'patch_ratio',
    'port_width_tokens_added', 'port_width_tokens_removed', 'port_width_changed',
    'input_output_tokens_added', 'input_output_tokens_removed',
    'always_block_added', 'always_block_removed',
    'has_star_sensitivity', 'has_edge_in_sensitivity', 'sensitivity_list_changed',
    'module_keyword', 'port_map_changed',
    'has_synthesis_tool', 'has_pragma',
    'has_latch_pattern', 'case_without_default',
    'has_typedef', 'has_struct', 'has_enum', 'has_define', 'func_sig_changed',
    'is_systemverilog', 'is_vhdl', 'is_c', 'is_verilog',
    'patch_length', 'before_code_length',
    'is_synthetic',
]

# Build hand features
X_hand = np.array([extract_hand_features(e) for e in examples], dtype=np.float32)

# Build TF-IDF features on patch text
print('Fitting TF-IDF...')
patch_texts = [e.get('patch', '') or '' for e in examples]
tfidf = TfidfVectorizer(
    max_features=150,
    ngram_range=(1, 2),
    min_df=3,
    sublinear_tf=True,
    token_pattern=r'[a-zA-Z_][a-zA-Z0-9_]{2,}',  # identifiers only, min 3 chars
)
X_tfidf = tfidf.fit_transform(patch_texts)
print(f'TF-IDF shape: {X_tfidf.shape}')

# Combine
X_combined = hstack([csr_matrix(X_hand), X_tfidf]).toarray().astype(np.float32)
print(f'Combined feature matrix: {X_combined.shape}')

y_raw = [e.get('bug_category') for e in examples]
le = LabelEncoder()
y = le.fit_transform(y_raw)
print(f'Classes: {list(le.classes_)}')

# Class weights to handle imbalance
class_counts = collections.Counter(y_raw)
max_count = max(class_counts.values())
class_weight = {le.transform([cat])[0]: max_count / cnt for cat, cnt in class_counts.items()}
print(f'Class weights: {class_weight}')

X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y, test_size=0.2, random_state=42, stratify=y
)
print(f'Train: {len(X_train)}, Test: {len(X_test)}')

# Sample weights for training
sample_weights = np.array([class_weight[yi] for yi in y_train])

params = {
    'objective': 'multiclass',
    'num_class': len(le.classes_),
    'metric': 'multi_logloss',
    'learning_rate': 0.05,
    'num_leaves': 63,
    'min_child_samples': 5,
    'n_estimators': 500,
    'verbose': -1,
    'random_state': 42,
    'class_weight': 'balanced',
}

model = lgb.LGBMClassifier(**params)
model.fit(
    X_train, y_train,
    sample_weight=sample_weights,
    eval_set=[(X_test, y_test)],
    callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(100)]
)

y_pred = model.predict(X_test)
print('\nClassification Report:')
print(classification_report(y_test, y_pred, target_names=le.classes_))

model_path = Path('/Users/severinspagnola/Desktop/GithubCrawler/polaris_classifier_v2.pkl')
with open(model_path, 'wb') as f:
    pickle.dump({
        'model': model,
        'label_encoder': le,
        'feature_names': HAND_FEATURE_NAMES + [f'tfidf_{t}' for t in tfidf.get_feature_names_out()],
        'tfidf': tfidf,
        'hand_feature_names': HAND_FEATURE_NAMES,
        'excluded_categories': list(EXCLUDE_CATS),
        'version': 2,
    }, f)
print(f'Model saved to {model_path}')

# Top features
print('\nTop 20 feature importances:')
all_names = HAND_FEATURE_NAMES + [f'tfidf_{t}' for t in tfidf.get_feature_names_out()]
importances = model.feature_importances_
for name, imp in sorted(zip(all_names, importances), key=lambda x: -x[1])[:20]:
    print(f'  {imp:6.1f}  {name}')

# Top TF-IDF tokens
print('\nTop TF-IDF tokens by importance:')
tfidf_names = tfidf.get_feature_names_out()
tfidf_imps = importances[len(HAND_FEATURE_NAMES):]
for name, imp in sorted(zip(tfidf_names, tfidf_imps), key=lambda x: -x[1])[:15]:
    print(f'  {imp:6.1f}  {name}')
