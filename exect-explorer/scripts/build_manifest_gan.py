#!/usr/bin/env python3
"""
Build a unified manifest for all Gan (2026) synthetic letters by parsing
synthetic_data_subset_1500.json and computing quote offsets.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAN_FILE = ROOT / "data" / "Gan (2026)" / "synthetic_data_subset_1500.json"
OUT_DIR = ROOT / "exect-explorer" / "public" / "data"

ENTITY_COLOURS = {
    "SeizureFrequency": "#b85cb8",
}

ORACLE_RATES = {
    "SeizureFrequency": 0.292,
}

def find_offsets(text: str, quote: str) -> tuple[int, int]:
    if not quote or not text:
        return 0, 0
    # Try exact match first
    idx = text.find(quote)
    if idx != -1:
        return idx, idx + len(quote)
    
    # Try case-insensitive or stripping extra whitespace/quotes match
    normalized_quote = " ".join(quote.split())
    for q in [quote, quote.strip('"\' \t\n\r'), normalized_quote]:
        idx = text.find(q)
        if idx != -1:
            return idx, idx + len(q)
        idx = text.lower().find(q.lower())
        if idx != -1:
            return idx, idx + len(q)
            
    # Try first 20 characters of the quote
    first_part = quote[:20]
    idx = text.find(first_part)
    if idx != -1:
        return idx, min(idx + len(quote), len(text))
        
    return 0, 0

def build_manifest():
    if not GAN_FILE.exists():
        print(f"Error: Gan file not found at {GAN_FILE}")
        return

    with open(GAN_FILE, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    print(f"Loaded {len(raw_records)} raw Gan records")
    manifest = []

    for raw in raw_records:
        source_row_index = int(raw["source_row_index"])
        letter_id = f"gan_{source_row_index}"
        text = raw["clinic_date"] # The note text is in clinic_date
        
        frequency = raw["check__Seizure Frequency Number"]
        gold = frequency["seizure_frequency_number"]
        reference = frequency.get("reference") or [None, None]
        
        gold_label = gold[0] if gold[0] else "unknown"
        gold_evidence = gold[1] if len(gold) > 1 and gold[1] else None
        
        reference_label = reference[0] if reference[0] else None
        reference_evidence = reference[1] if len(reference) > 1 and reference[1] else None
        
        entities = []
        
        # Gold entity
        if gold_evidence:
            start_g, end_g = find_offsets(text, gold_evidence)
            if end_g > start_g:
                entities.append({
                    "id": "T_gold",
                    "type": "SeizureFrequency",
                    "start": start_g,
                    "end": end_g,
                    "text": gold_evidence,
                    "attributes": {
                        "Label": gold_label,
                        "Type": "gold"
                    }
                })
                
        # Reference entity
        if reference_evidence:
            start_r, end_r = find_offsets(text, reference_evidence)
            if end_r > start_r:
                entities.append({
                    "id": "T_ref",
                    "type": "SeizureFrequency",
                    "start": start_r,
                    "end": end_r,
                    "text": reference_evidence,
                    "attributes": {
                        "Label": reference_label or "None",
                        "Type": "reference"
                    }
                })

        # Add flaws based on flags
        flaws = []
        gold_norm = gold_label.strip().lower()
        ref_norm = reference_label.strip().lower() if reference_label else None
        
        if ref_norm is not None and gold_norm != ref_norm:
            flaws.append({
                "category": "label_reference_disagreement",
                "description": f"Gold ({gold_label}) disagrees with Reference ({reference_label})",
                "oracle_impact": "scoring_ambiguity"
            })
        if gold_norm == "unknown":
            flaws.append({
                "category": "unknown",
                "description": "Gold label is unknown",
                "oracle_impact": None
            })
        if gold_norm == "no seizure frequency reference":
            flaws.append({
                "category": "no_seizure_frequency_reference",
                "description": "No seizure frequency referenced in gold",
                "oracle_impact": None
            })
        if not raw.get("row_ok", True):
            flaws.append({
                "category": "row_not_ok",
                "description": "Row marked as not OK in raw dataset",
                "oracle_impact": "scoring_ambiguity"
            })
        quote_issues = raw.get("quote_issue_categories", "")
        if quote_issues and "Seizure Frequency Number" in str(quote_issues):
            flaws.append({
                "category": "frequency_quote_issue",
                "description": "Quote issue flagged for seizure frequency",
                "oracle_impact": "scoring_ambiguity"
            })

        # Count types
        type_counts = {"SeizureFrequency": len(entities)}

        manifest.append({
            "id": letter_id,
            "text": text,
            "entities": entities,
            "json_export": raw,
            "overlaps": [],
            "temporal_sparse": [],
            "incomplete_meds": [],
            "timeline_events": [],
            "type_counts": type_counts,
            "flaws": flaws,
            "negated_entities": [],
            "low_certainty": [],
            "has_unknown_seizure": False,
        })

    # Write individual letter manifest files
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for m in manifest:
        out_path = OUT_DIR / f"{m['id']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)

    # Write index
    index = {
        "letters": [{"id": m["id"], "type_counts": m["type_counts"], "flaw_count": len(m["flaws"])} for m in manifest],
        "entity_colours": ENTITY_COLOURS,
        "oracle_rates": ORACLE_RATES,
        "total_letters": len(manifest),
    }
    with open(OUT_DIR / "index_gan.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(manifest)} Gan letter manifests and index_gan.json to {OUT_DIR}")

if __name__ == "__main__":
    build_manifest()
