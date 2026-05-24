import json
from pathlib import Path
from clinical_extraction.exect.primitives import (
    infer_exect_medication_temporality,
    build_exect_medication_candidate_payloads,
    canonical_medication_name,
    _BRAND_SURFACES,
)

# Load the predictions file
run_dir = Path("runs/exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_cap25_gpt4_1_mini_20260524T201708Z")
predictions_path = run_dir / "predictions.json"

with open(predictions_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find records with benchmark_bridge:medication_temporality_pruned
for pred in data["predictions"]:
    doc_id = pred["document_id"]
    note_text = ""
    # We need the note text. We can find it from the dataset or load it.
    # Let's import the loader.
    from clinical_extraction.datasets.exect import load_exect_gold_documents
    dataset = load_exect_gold_documents()
    # Find the document
    doc = next(d for d in dataset if d.document_id == doc_id)
    note_text = doc.text

    for val in pred["values"]:
        if val["field_name"] == "annotated_medication" and "benchmark_bridge:medication_temporality_pruned" in val.get("quality_flags", []):
            raw = val["raw_value"]
            evidence = val["evidence"][0]["text"] if val["evidence"] else ""
            print(f"--- Doc {doc_id} ---")
            print(f"Raw prediction: {raw}")
            print(f"Evidence: {evidence}")
            
            cleaned_raw = raw.strip().lower()
            if cleaned_raw in {"eplim", "eplim chrono"}:
                cleaned_raw = "epilim chrono"
            raw_canonical = canonical_medication_name(cleaned_raw)
            canonical = _BRAND_SURFACES.get(raw_canonical, raw_canonical)
            
            context = evidence or note_text
            inferred = infer_exect_medication_temporality(context)
            print(f"Canonical medication: {canonical}")
            print(f"Inferred temporality of evidence: {inferred.canonical_value}")
            
            candidates = build_exect_medication_candidate_payloads(note_text)
            print("Note candidates:")
            found_same = False
            for c in candidates:
                if c.normalized_value == canonical:
                    found_same = True
                    print(f"  - {c.normalized_value} ({c.raw_text}): temporality={c.metadata.get('temporality')}")
            if not found_same:
                print("  (None found for this canonical medication)")
