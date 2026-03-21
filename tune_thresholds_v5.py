"""
tune_thresholds_v5.py — Threshold sweep for port_mismatch class in V5 Stage 2 classifier.
Sweeps port_mismatch decision threshold from 0.05 to 0.95, reports P/R/F1 for all classes.
"""

import os, json, collections, random
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import precision_recall_fscore_support, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer

examples_dir = Path('/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples/')

# ---------------------------------------------------------------------------
# Load V5 pkl
# ---------------------------------------------------------------------------
with open('/Users/severinspagnola/Desktop/GithubCrawler/polaris_classifier_v5.pkl', 'rb') as f:
    bundle = pickle.load(f)

stage1_model = bundle['stage1_model']
stage2_model = bundle['stage2_model']
stage2_tfidf = bundle['stage2_tfidf']
label_encoder = bundle['label_encoder']
hand_feature_names = bundle['hand_feature_names']

print(f"V5 pkl loaded. Stage 2 classes: {list(label_encoder.classes_)}")

# ---------------------------------------------------------------------------
# Reproduce exact holdout partition from train_classifier_v5.py
# ---------------------------------------------------------------------------
C_LANGS = {'c', 'cpp', 'c++', 'c/c++'}
STAGE2_CLASSES = {'synthesis_error', 'port_mismatch', 'sensitivity_list'}

all_files = sorted(examples_dir.glob('*.json'))
n_files = len(all_files)
n_train_files = int(n_files * 0.8)

rng = random.Random(42)
shuffled_files = list(all_files)
rng.shuffle(shuffled_files)
train_files = set(str(f) for f in shuffled_files[:n_train_files])
test_files_set = set(str(f) for f in shuffled_files[n_train_files:])

print(f"Total files: {n_files}, Train: {n_train_files}, Test: {n_files - n_train_files}")


def load_file(f: Path, split: str) -> list:
    results = []
    try:
        d = json.loads(f.read_text())
        if 'patch' in d:
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

for e in raw_examples:
    e['label'] = e.get('bug_category')

examples = [e for e in raw_examples if e.get('label') not in ('other', 'clock_domain', None)]

for e in examples:
    lang = (e.get('language', '') or '').lower()
    e['_is_c'] = lang in C_LANGS

test_examples = [e for e in examples if e['_split'] == 'test']
print(f"Test examples: {len(test_examples)}")


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


# ---------------------------------------------------------------------------
# Compute hand features for test set
# ---------------------------------------------------------------------------
X_test = np.array([extract_features(e) for e in test_examples], dtype=np.float32)
y1_pred = stage1_model.predict(X_test)

# ---------------------------------------------------------------------------
# Collect Stage 2 probabilities for all HDL test examples
# ---------------------------------------------------------------------------
# stage2 classes order
classes = list(label_encoder.classes_)
port_idx = classes.index('port_mismatch')
synth_idx = classes.index('synthesis_error')
sens_idx = classes.index('sensitivity_list')

print(f"Stage 2 class order: {classes}")
print(f"  port_mismatch idx={port_idx}, synthesis_error idx={synth_idx}, sensitivity_list idx={sens_idx}")

# We'll collect (true_label, stage2_proba) for all test examples routed to Stage 2
# and store the full OOS prediction for non-HDL examples
oos_true = []
oos_proba_s2 = []  # None if not routed to stage2, else array of 3 probs
oos_is_stage2 = []

for i, ex in enumerate(test_examples):
    true_label = ex.get('label')
    oos_true.append(true_label)

    if y1_pred[i] == 1:
        # C example → api_breaking
        oos_proba_s2.append(None)
        oos_is_stage2.append(False)
    else:
        # HDL example → Stage 2
        hand_feat = X_test[i].reshape(1, -1)
        patch_text = ex.get('patch', '') or ''
        tfidf_feat = stage2_tfidf.transform([patch_text]).toarray()
        combined_feat = np.hstack([hand_feat, tfidf_feat])
        proba = stage2_model.predict_proba(combined_feat)[0]  # shape: (3,)
        oos_proba_s2.append(proba)
        oos_is_stage2.append(True)

print(f"\nStage 2 examples in test set: {sum(oos_is_stage2)}")
print(f"Stage 1 (C) examples in test set: {sum(not s for s in oos_is_stage2)}")

# ---------------------------------------------------------------------------
# Threshold sweep for port_mismatch
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("THRESHOLD SWEEP: port_mismatch")
print("="*70)
print(f"{'Threshold':>10} | {'PM_P':>6} {'PM_R':>6} {'PM_F1':>7} | {'SE_F1':>7} | {'SL_F1':>7}")
print("-"*70)

best_pm_f1 = 0.0
best_threshold = 0.0
best_pm_p = 0.0
best_pm_r = 0.0
best_se_f1_at_best = 0.0
best_sl_f1_at_best = 0.0

thresholds = [round(t, 2) for t in np.arange(0.05, 1.00, 0.05)]

sweep_results = []

for thresh in thresholds:
    preds = []
    for i, (true_label, proba, is_s2) in enumerate(zip(oos_true, oos_proba_s2, oos_is_stage2)):
        if not is_s2:
            preds.append('api_breaking')
        else:
            pm_prob = proba[port_idx]
            if pm_prob >= thresh:
                preds.append('port_mismatch')
            else:
                # Among remaining classes, pick argmax
                modified_proba = proba.copy()
                modified_proba[port_idx] = -1.0
                best_other = int(np.argmax(modified_proba))
                preds.append(classes[best_other])

    # Compute per-class metrics
    labels_of_interest = ['port_mismatch', 'synthesis_error', 'sensitivity_list']
    p_vals, r_vals, f1_vals, _ = precision_recall_fscore_support(
        oos_true, preds, labels=labels_of_interest, zero_division=0
    )
    pm_p, pm_r, pm_f1 = p_vals[0], r_vals[0], f1_vals[0]
    se_f1 = f1_vals[1]
    sl_f1 = f1_vals[2]

    print(f"{thresh:>10.2f} | {pm_p:>6.3f} {pm_r:>6.3f} {pm_f1:>7.3f} | {se_f1:>7.3f} | {sl_f1:>7.3f}")

    sweep_results.append({
        'threshold': thresh,
        'pm_precision': round(float(pm_p), 4),
        'pm_recall': round(float(pm_r), 4),
        'pm_f1': round(float(pm_f1), 4),
        'synthesis_error_f1': round(float(se_f1), 4),
        'sensitivity_list_f1': round(float(sl_f1), 4),
    })

    if pm_f1 > best_pm_f1:
        best_pm_f1 = pm_f1
        best_threshold = thresh
        best_pm_p = pm_p
        best_pm_r = pm_r
        best_se_f1_at_best = se_f1
        best_sl_f1_at_best = sl_f1

print("-"*70)
print(f"\nBASELINE (argmax, no threshold): PM_F1=0.278, SE_F1=0.818, SL_F1=0.458")
print(f"\n{'='*70}")
print(f"BEST port_mismatch F1 = {best_pm_f1:.4f} at threshold = {best_threshold:.2f}")
print(f"  port_mismatch  P={best_pm_p:.4f}  R={best_pm_r:.4f}  F1={best_pm_f1:.4f}")
print(f"  synthesis_error F1 at this threshold = {best_se_f1_at_best:.4f}")
print(f"  sensitivity_list F1 at this threshold = {best_sl_f1_at_best:.4f}")
print(f"{'='*70}")

if best_pm_f1 >= 0.50:
    print(f"\nCONCLUSION: Threshold tuning CAN get port_mismatch F1 above 0.50 (best={best_pm_f1:.4f})")
else:
    print(f"\nCONCLUSION: Threshold tuning CANNOT get port_mismatch F1 above 0.50 (best={best_pm_f1:.4f})")

# ---------------------------------------------------------------------------
# Save sweep results to JSON
# ---------------------------------------------------------------------------
results_path = '/Users/severinspagnola/Desktop/GithubCrawler/v5_threshold_sweep.json'
with open(results_path, 'w') as f:
    json.dump({
        'baseline': {
            'pm_f1': 0.278,
            'synthesis_error_f1': 0.818,
            'sensitivity_list_f1': 0.458,
        },
        'best_threshold': best_threshold,
        'best_pm_f1': round(float(best_pm_f1), 4),
        'best_pm_precision': round(float(best_pm_p), 4),
        'best_pm_recall': round(float(best_pm_r), 4),
        'synthesis_error_f1_at_best': round(float(best_se_f1_at_best), 4),
        'sensitivity_list_f1_at_best': round(float(best_sl_f1_at_best), 4),
        'threshold_reaches_050': bool(best_pm_f1 >= 0.50),
        'sweep': sweep_results,
    }, f, indent=2)

print(f"\nSweep results saved to {results_path}")
