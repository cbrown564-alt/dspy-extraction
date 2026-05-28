import sys
from pathlib import Path

# Add src/ to python path so we can import clinical_extraction
sys.path.insert(0, str(Path("src").resolve()))

import json
from clinical_extraction.datasets.gan import load_gan_records

path_d1 = r"runs\gan_s0_date_stage_d1_det_events_full_validation_gpt4_1_mini_20260528T065611Z\predictions.json"
path_v1 = r"archive\runs\gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z\predictions.json"

with open(path_d1, "r", encoding="utf-8") as f:
    data_d1 = json.load(f)

with open(path_v1, "r", encoding="utf-8") as f:
    data_v1 = json.load(f)

# Load gold records
records = load_gan_records()
gold_records = {r.record_id: r for r in records}

# Let's map predictions by document_id
preds_d1 = {p["document_id"]: p for p in data_d1["predictions"]}
preds_v1 = {p["document_id"]: p for p in data_v1["predictions"]}

discrepancies = []
for doc_id, pred_d1 in preds_d1.items():
    pred_v1 = preds_v1.get(doc_id)
    if not pred_v1:
        continue
    
    val_d1 = pred_d1["values"][0]["normalized_value"] if pred_d1["values"] else "missing"
    val_v1 = pred_v1["values"][0]["normalized_value"] if pred_v1["values"] else "missing"
    
    if val_d1 != val_v1:
        # Get text evidence
        text = ""
        if pred_d1["values"] and pred_d1["values"][0]["evidence"]:
            text = pred_d1["values"][0]["evidence"][0]["text"]
        elif pred_v1["values"] and pred_v1["values"][0]["evidence"]:
            text = pred_v1["values"][0]["evidence"][0]["text"]
            
        record = gold_records.get(doc_id)
        discrepancies.append({
            "document_id": doc_id,
            "d1_pred": val_d1,
            "v1_pred": val_v1,
            "gold": record.gold_label if record else "unknown",
            "gold_evidence": record.gold_evidence if record else "unknown",
            "evidence": text,
            "flags": record.flags if record else []
        })

print(f"Total discrepancies: {len(discrepancies)}")
print("\nDiscrepancy Details:")
# Print ones where D1 matches gold but V1 does not, and vice versa
d1_correct_v1_wrong = [d for d in discrepancies if d["d1_pred"] == d["gold"]]
v1_correct_d1_wrong = [d for d in discrepancies if d["v1_pred"] == d["gold"]]
both_wrong = [d for d in discrepancies if d["d1_pred"] != d["gold"] and d["v1_pred"] != d["gold"]]

print(f"\nD1 Correct, V1 Wrong: {len(d1_correct_v1_wrong)}")
for d in d1_correct_v1_wrong[:10]:
    print(f"ID: {d['document_id']} (Flags: {d['flags']})")
    print(f"  Gold:    {d['gold']}")
    print(f"  D1 Pred: {d['d1_pred']} (CORRECT)")
    print(f"  V1 Pred: {d['v1_pred']} (WRONG)")
    print(f"  Evidence: {d['evidence']}")
    print("-" * 40)

print(f"\nV1 Correct, D1 Wrong: {len(v1_correct_d1_wrong)}")
for d in v1_correct_d1_wrong[:10]:
    print(f"ID: {d['document_id']} (Flags: {d['flags']})")
    print(f"  Gold:    {d['gold']}")
    print(f"  D1 Pred: {d['d1_pred']} (WRONG)")
    print(f"  V1 Pred: {d['v1_pred']} (CORRECT)")
    print(f"  Evidence: {d['evidence']}")
    print("-" * 40)

print(f"\nBoth Wrong (Different predictions): {len(both_wrong)}")
for d in both_wrong[:10]:
    print(f"ID: {d['document_id']} (Flags: {d['flags']})")
    print(f"  Gold:    {d['gold']}")
    print(f"  D1 Pred: {d['d1_pred']} (WRONG)")
    print(f"  V1 Pred: {d['v1_pred']} (WRONG)")
    print(f"  Evidence: {d['evidence']}")
    print("-" * 40)
