import json
import os

path_d1 = r"runs\gan_s0_date_stage_d1_det_events_full_validation_gpt4_1_mini_20260528T065611Z\predictions.json"
path_v1 = r"archive\runs\gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z\predictions.json"

with open(path_d1, "r", encoding="utf-8") as f:
    data_d1 = json.load(f)

with open(path_v1, "r", encoding="utf-8") as f:
    data_v1 = json.load(f)

# Load gold labels
gold_path = r"data\splits\gan_2026_splits.json"
gold_data = {}
if os.path.exists(gold_path):
    with open(gold_path, "r", encoding="utf-8") as f:
        gold_json = json.load(f)
        # Check structure
        # typically splits contain a list of records under split names
        # Let's inspect the keys of gold_json
        print("Gold JSON keys:", list(gold_json.keys()))
        if "records" in gold_json:
            for r in gold_json["records"]:
                gold_data[r["document_id"]] = r
        elif "gan_2026_fixed_v1" in gold_json:
            # Let's see what is inside the split dictionary
            split_obj = gold_json["gan_2026_fixed_v1"]
            print("gan_2026_fixed_v1 keys:", list(split_obj.keys()))

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
            
        discrepancies.append({
            "document_id": doc_id,
            "d1_pred": val_d1,
            "v1_pred": val_v1,
            "evidence": text,
            "d1_candidates": pred_d1.get("metadata", {}).get("temporal_candidate_labels", []),
            "v1_candidates": pred_v1.get("metadata", {}).get("temporal_candidate_labels", [])
        })

print(f"Total discrepancies: {len(discrepancies)}")
print("\nFirst 10 discrepancies:")
for disc in discrepancies[:10]:
    print(f"ID: {disc['document_id']}")
    print(f"  D1 Pred: {disc['d1_pred']} (Candidates: {disc['d1_candidates']})")
    print(f"  V1 Pred: {disc['v1_pred']} (Candidates: {disc['v1_candidates']})")
    print(f"  Evidence: {disc['evidence']}")
    print("-" * 40)
