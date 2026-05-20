"""ExECT S0/S1 field-family DSPy program."""
from __future__ import annotations

import re
from collections.abc import Callable
from typing import Optional

import dspy

from clinical_extraction.datasets.exect import (
    canonical_clinical_phrase,
    canonical_medication_name,
    collapse_diagnoses_to_most_specific,
)
from clinical_extraction.pipeline.sectioning import select_context
from clinical_extraction.runs import RunMetadata
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

EXECT_DATASET = "exect_v2"
EXECT_S0_S1_SCHEMA_LEVEL = "exect_s0_s1_field_family"
EXECT_S0_S1_VARIANT = "exect_s0_s1_field_family_single_pass"
EXECT_S0_S1_SECTION_AWARE_VARIANT = "exect_s0_s1_field_family_section_aware"
EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT = "exect_s0_s1_field_family_diagnosis_recall"
EXECT_S0_S1_VERIFY_REPAIR_VARIANT = "exect_s0_s1_field_family_verify_repair"
EXECT_S0_S1_SCORER = "exect_field_family_deterministic_v1"
EXECT_S0_S1_PROMPT_VERSION = "exect_s0_s1_field_family_v4_10_label_policy"
EXECT_S0_S1_V4_9_PROMPT_VERSION = "exect_s0_s1_field_family_v4_9_label_policy"
EXECT_S0_S1_V4_8_PROMPT_VERSION = "exect_s0_s1_field_family_v4_8_label_policy"
EXECT_S0_S1_V4_7_PROMPT_VERSION = "exect_s0_s1_field_family_v4_7_label_policy"
EXECT_S0_S1_V4_6_PROMPT_VERSION = "exect_s0_s1_field_family_v4_6_label_policy"
EXECT_S0_S1_V4_5_PROMPT_VERSION = "exect_s0_s1_field_family_v4_5_label_policy"
EXECT_S0_S1_V4_4_PROMPT_VERSION = "exect_s0_s1_field_family_v4_4_label_policy"
EXECT_S0_S1_V4_3_PROMPT_VERSION = "exect_s0_s1_field_family_v4_3_label_policy"
EXECT_S0_S1_V4_2_PROMPT_VERSION = "exect_s0_s1_field_family_v4_2_label_policy"
EXECT_S0_S1_DIAGNOSIS_RECALL_PROMPT_VERSION = "exect_s0_s1_diagnosis_recall_v1"
EXECT_S0_S1_VERIFY_REPAIR_PROMPT_VERSION = "exect_s0_s1_field_family_verify_repair_v1"
EXECT_S0_S1_V3_PROMPT_VERSION = "exect_s0_s1_field_family_v3_seizure_evidence_policy"
EXECT_S0_S1_V4_PROMPT_VERSION = "exect_s0_s1_field_family_v4_label_policy"
EXECT_S0_S1_V4_1_PROMPT_VERSION = "exect_s0_s1_field_family_v4_1_label_policy"
EXECT_S0_S1_FIELD_FAMILIES = (
    "diagnosis",
    "seizure_type",
    "annotated_medication",
)
EXECT_S0_S1_LABEL_POLICY_GUIDANCE = (
    "Return benchmark-facing annotation labels only; do not expand into clinically richer labels.",
    "Diagnosis labels should preserve the explicit audited diagnosis surface after deterministic "
    "canonicalization; do not force all focal, temporal-lobe, symptomatic, refractory, or syndrome "
    "phrases into a five-label diagnosis set unless the scorer has an explicit mapping.",
    "Do not output a diagnosis for a single seizure event unless the note separately states an "
    "established epilepsy diagnosis.",
    "Use the audited seizure-type surface supported by the note. Preserve plural and modifier "
    "surfaces such as focal seizures with altered awareness or occipital lobe seizures when those "
    "are the benchmark-facing labels.",
    "Split fused seizure-type surfaces into audited benchmark labels when the note combines a "
    "lobe-specific type with a broader focal seizure type; for example temporal lobe onset focal "
    "seizures should produce temporal lobe seizure and focal seizures.",
    "When a note names focal seizures with secondary generalisation as one phrase, split it into "
    "focal seizures, secondary generalisation, and generalized tonic clonic seizure as separate "
    "benchmark-facing seizure-type labels.",
    "Preserve convulsive modifiers on focal to bilateral seizure labels when the audited scorer "
    "expects focal to bilateral convulsive seizure or seizures.",
    "Strip probable, possible, or similar uncertainty qualifiers from diagnosis labels when the "
    "benchmark-facing gold uses the definite audited diagnosis surface.",
    "Preserve modifier-rich audited diagnosis surfaces such as symptomatic structural focal "
    "epilepsy; do not drop focal or other audited modifiers unless specificity collapse applies.",
    "Keep seizure-type labels out of the diagnosis field and epilepsy diagnoses out of the "
    "seizure-type field; do not emit non-epilepsy conditions such as hydrocephalus as diagnosis.",
    "Only emit diagnosis labels from the audited epilepsy diagnosis vocabulary; never place "
    "seizure-type phrases, fused secondary-generalisation wording, or seizure-event descriptors "
    "in the diagnosis field.",
    "When splitting temporal-lobe-onset focal seizures, emit temporal lobe seizure and focal "
    "seizures as separate labels; do not replace them with temporal lobe seizures alone.",
    "When the note lists both focal seizures and a temporal-lobe seizure type, include both in "
    "seizure_type rather than moving focal seizures into diagnosis.",
    "For symptomatic structural focal epilepsy, keep the focal modifier; do not shorten to "
    "symptomatic structural epilepsy.",
    "When a note separately names parietal lobe epilepsy alongside focal epilepsy, include both "
    "diagnosis labels.",
    "When the note separately names generic epilepsy outside a compound diagnosis phrase "
    "(for example concerns with his epilepsy), include epilepsy alongside focal onset epilepsy, "
    "primary generalized epilepsy, symptomatic structural focal epilepsy, or other specific "
    "epilepsy diagnoses.",
    "When the diagnosis header states epilepsy unclassified or unclassified epilepsy, emit "
    "epilepsy as the benchmark-facing diagnosis label.",
    "Do not treat possible TLE or temporal lobe epilepsy in the diagnosis header as "
    "seizure-descriptor-only wording; preserve temporal lobe epilepsy when the header or "
    "impression names it.",
    "When the note names both focal epilepsy and focal onset epilepsy, include both audited "
    "diagnosis surfaces rather than keeping only one.",
    "Use epilepsy with generalized tonic clonic seizures on awakening when the note uses on "
    "awakening wording or when the diagnosis header uses from sleep phrasing for this syndrome.",
    "Prefer audited coarse seizure-type labels such as generalized seizures or generalized tonic "
    "clonic seizures over granular event descriptors such as jerks, absences, or absence events "
    "unless the note explicitly uses the audited benchmark surface.",
    "When the benchmark-facing seizure label is focal to bilateral convulsive seizure, use that "
    "surface even if the note says focal onset convulsive seizure.",
    "Do not infer seizure type from diagnosis alone, and do not add secondary generalisation as a "
    "separate current seizure type unless the note independently names it as current.",
    "Annotated medication means anti-seizure medications in the audited prescription annotation "
    "view only; do not include psychotropic or non-ASM drugs, planned starts, previous trials, "
    "taper/stop instructions, or medication-history mentions.",
    "When the note has no prescription-style current medication list, return an empty "
    "annotated_medication list rather than inferring ASM from seizure history or past trials.",
    "Do not emit ASM from prescription requests, planned switches, taper/stop instructions, "
    "or advice to restart after self-discontinuation.",
    "Preserve audited brand medication surfaces from the note (for example lamictal, "
    "epilim chrono) rather than substituting generic chemical names when the letter uses "
    "the brand form in the prescription list.",
    "Only emit a medication when its name appears in the note; do not infer ASM from "
    "discussion of past trials or hypothetical changes.",
    "Medication evidence must be the shortest exact contiguous quote from the note without "
    "invented section headers; omit header labels such as Medication: when they are not "
    "part of the source text.",
    "Do not emit jerks, absences, or absence events as separate seizure-type labels when the "
    "benchmark-facing surface is a coarse generalized or generalized tonic clonic label.",
    "For juvenile myoclonic epilepsy or JME notes, prefer the audited coarse seizure-type "
    "surface named in the letter (tonic clonic seizures, generalized tonic clonic seizures, or "
    "generalized tonic seizures) and do not add myoclonic seizures when that coarse label is "
    "already the benchmark-facing seizure type.",
    "When the note uses tonic clonic seizures without a generalized tonic clonic prefix, use "
    "tonic clonic seizures rather than generalized tonic clonic seizures.",
    "When the note uses generalized tonic seizures without a clonic modifier, use generalized "
    "tonic seizures rather than generalized tonic clonic seizures.",
    "Do not output an epilepsy diagnosis when the diagnosis header only lists seizure-type "
    "descriptors or possible JME without an established epilepsy diagnosis surface.",
    "When the note contrasts epileptic versus dissociative seizures and concludes the events "
    "are epileptic seizures, emit epileptic seizures in seizure_type; do not infer focal "
    "seizures from focal onset epilepsy diagnosis alone.",
    "When the note describes drug-refractory focal or occipital-lobe epilepsy with "
    "specificity-collapse gold, co-list the collapsed diagnosis tokens focal, drug, and "
    "occipital alongside focal epilepsy and occipital lobe epilepsy when supported.",
    "Keep current anti-epileptic medication entries when the prescription line includes "
    "a taper or stop plan in parentheses; exclude only separate planned-start lines.",
    "When specificity-collapse diagnosis context applies and the note names secondary "
    "generalised seizure(s), emit only secondary in seizure_type; do not add focal seizure "
    "descriptors or the full secondary generalised phrase.",
    "When the note names secondary generalised seizures as a current seizure type without "
    "specificity-collapse context, co-list secondary alongside the full audited label.",
    "Use exact contiguous evidence quotes; omit a value rather than supplying non-contiguous or "
    "unsupported evidence.",
)
EXECT_S0_S1_POLICY_EXAMPLES = (
    {
        "case": "planned_medication_exclusion",
        "note_fragment": "Current anti-epileptic medication: lamotrigine 75mg bd. To start levetiracetam.",
        "benchmark_output": {"annotated_medication": ["lamotrigine"]},
        "policy": "Exclude planned medication starts from the benchmark-facing medication list.",
    },
    {
        "case": "previous_medication_exclusion",
        "note_fragment": "Previously tried carbamazepine. Current treatment is sodium valproate.",
        "benchmark_output": {"annotated_medication": ["sodium valproate"]},
        "policy": "Exclude historical medication mentions from the benchmark-facing medication list.",
    },
    {
        "case": "canonical_seizure_type_granularity",
        "note_fragment": "The events are temporal-lobe-onset focal seizures.",
        "benchmark_output": {"seizure_type": ["temporal lobe seizure", "focal seizures"]},
        "policy": "Split the fused rich phrase into the audited benchmark seizure-type labels.",
    },
    {
        "case": "diagnosis_label_preservation",
        "note_fragment": "Diagnosis: symptomatic structural focal epilepsy.",
        "benchmark_output": {"diagnosis": ["symptomatic structural focal epilepsy"]},
        "policy": "Preserve the audited diagnosis surface rather than forcing a five-label collapse.",
    },
    {
        "case": "plural_seizure_type_preservation",
        "note_fragment": "Seizure type and frequency: focal seizures with altered awareness every 3 weeks.",
        "benchmark_output": {"seizure_type": ["focal seizures with altered awareness"]},
        "policy": "Preserve audited plural seizure-type surfaces when that is the scorer label.",
    },
    {
        "case": "evidence_quote_contiguity",
        "note_fragment": "Seizure type: occipital lobe seizures. Previous medication: lamotrigine.",
        "benchmark_output": {
            "seizure_type": ["occipital lobe seizures"],
            "seizure_type_evidence": ["occipital lobe seizures"],
        },
        "policy": "Evidence must be an exact contiguous quote, not a stitched or ellipsis quote.",
    },
    {
        "case": "single_event_diagnosis_null",
        "note_fragment": "This was a single focal seizure. There is no established epilepsy diagnosis.",
        "benchmark_output": {"diagnosis": []},
        "policy": "Do not convert a single seizure event into an established epilepsy diagnosis.",
    },
    {
        "case": "secondary_generalisation_split",
        "note_fragment": "Seizure type: focal seizures with secondary generalisation.",
        "benchmark_output": {
            "seizure_type": [
                "focal seizures",
                "secondary generalisation",
                "generalized tonic clonic seizure",
            ]
        },
        "policy": "Split fused secondary-generalisation phrases into separate benchmark seizure types.",
    },
    {
        "case": "focal_to_bilateral_convulsive_modifier",
        "note_fragment": "She has focal to bilateral seizures.",
        "benchmark_output": {"seizure_type": ["focal to bilateral convulsive seizures"]},
        "policy": "Preserve the convulsive modifier when that is the audited benchmark surface.",
    },
    {
        "case": "diagnosis_uncertainty_stripping",
        "note_fragment": "Diagnosis: probable juvenile myoclonic epilepsy.",
        "benchmark_output": {"diagnosis": ["juvenile myoclonic epilepsy"]},
        "policy": "Strip uncertainty qualifiers when the benchmark-facing label is definite.",
    },
    {
        "case": "cross_family_diagnosis_exclusion",
        "note_fragment": "Diagnosis: hydrocephalus. Seizure type: focal seizures.",
        "benchmark_output": {"diagnosis": [], "seizure_type": ["focal seizures"]},
        "policy": "Do not place non-epilepsy conditions or seizure types in the diagnosis field.",
    },
    {
        "case": "symptomatic_structural_focal_preservation",
        "note_fragment": "Diagnosis: symptomatic structural focal epilepsy.",
        "benchmark_output": {"diagnosis": ["symptomatic structural focal epilepsy"]},
        "policy": "Preserve the full audited focal diagnosis modifier rather than dropping focal.",
    },
    {
        "case": "temporal_lobe_seizures_split_pair",
        "note_fragment": "Seizure type: temporal lobe seizures with occipital lobe seizures.",
        "benchmark_output": {
            "seizure_type": [
                "temporal lobe seizure",
                "focal seizures",
                "occipital lobe seizures",
            ]
        },
        "policy": "Do not stop at temporal lobe seizures alone when focal seizures is also required.",
    },
    {
        "case": "focal_to_bilateral_annotation_surface",
        "note_fragment": "Seizure type and frequency: focal onset convulsive seizure.",
        "benchmark_output": {"seizure_type": ["focal to bilateral convulsive seizure"]},
        "policy": "Use the audited bilateral convulsive benchmark surface when that is the scorer label.",
    },
    {
        "case": "coarse_generalized_seizure_surface",
        "note_fragment": "She has absences and myoclonic jerks.",
        "benchmark_output": {"seizure_type": ["generalized seizures"]},
        "policy": "Prefer audited coarse generalized seizure labels over granular jerk/absence descriptors.",
    },
    {
        "case": "absence_events_to_gtcs_surface",
        "note_fragment": "He reports absence events.",
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": "Map absence-event wording to the audited generalized tonic clonic seizure surface when required.",
    },
    {
        "case": "on_awakening_diagnosis_phrasing",
        "note_fragment": "Diagnosis: epilepsy with generalized tonic clonic seizures on awakening.",
        "benchmark_output": {
            "diagnosis": ["epilepsy with generalized tonic clonic seizures on awakening"]
        },
        "policy": "Preserve on awakening wording in the audited diagnosis label.",
    },
    {
        "case": "from_sleep_header_to_on_awakening_diagnosis",
        "note_fragment": (
            "Diagnosis: New diagnosis of epilepsy with generalised tonic clonic seizures "
            "from sleep."
        ),
        "benchmark_output": {
            "diagnosis": ["epilepsy with generalized tonic clonic seizures on awakening"]
        },
        "policy": "Map from-sleep header phrasing to the on awakening benchmark diagnosis label.",
    },
    {
        "case": "co_listed_lobe_epilepsy_diagnoses",
        "note_fragment": "Diagnosis: focal epilepsy, probable parietal onset.",
        "benchmark_output": {"diagnosis": ["focal epilepsy", "parietal lobe epilepsy"]},
        "policy": "Emit separate lobe-specific epilepsy diagnoses when the note supports both.",
    },
    {
        "case": "generic_epilepsy_co_list_with_focal_onset",
        "note_fragment": (
            "Diagnosis: focal onset epilepsy. He should contact us with any concerns with his "
            "epilepsy."
        ),
        "benchmark_output": {"diagnosis": ["focal onset epilepsy", "epilepsy"]},
        "policy": (
            "Include generic epilepsy when the note separately names epilepsy outside compound "
            "diagnosis phrases."
        ),
    },
    {
        "case": "focal_onset_and_focal_epilepsy_co_list",
        "note_fragment": "Diagnosis: focal epilepsy. I think that this is focal onset epilepsy.",
        "benchmark_output": {"diagnosis": ["focal epilepsy", "focal onset epilepsy"]},
        "policy": "Keep both focal epilepsy and focal onset epilepsy when the note supports each.",
    },
    {
        "case": "generic_epilepsy_co_list_with_primary_generalized",
        "note_fragment": (
            "She has primary generalised epilepsy. Her epilepsy was not well controlled "
            "on carbamazepine monotherapy."
        ),
        "benchmark_output": {
            "diagnosis": ["primary generalized epilepsy", "epilepsy"],
        },
        "policy": (
            "Co-list generic epilepsy when the note separately names epilepsy outside the "
            "primary generalized epilepsy phrase."
        ),
    },
    {
        "case": "unclassified_epilepsy_header",
        "note_fragment": "Diagnosis: epilepsy unclassified",
        "benchmark_output": {"diagnosis": ["epilepsy"]},
        "policy": "Map unclassified epilepsy header wording to the generic epilepsy label.",
    },
    {
        "case": "possible_tle_header_preserves_temporal_lobe_epilepsy",
        "note_fragment": "Diagnosis: Focal seizures, possible TLE",
        "benchmark_output": {
            "diagnosis": ["temporal lobe epilepsy"],
            "seizure_type": ["focal seizures"],
        },
        "policy": (
            "TLE in the diagnosis header is an epilepsy diagnosis surface, not a "
            "seizure-descriptor-only header."
        ),
    },
    {
        "case": "reject_granular_jme_seizure_descriptors",
        "note_fragment": "She reports absences and myoclonic jerks. Seizure type: generalized tonic clonic seizures.",
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": "Do not add jerks or absences when the audited label is already coarse.",
    },
    {
        "case": "jme_coarse_gtcs_suppresses_myoclonic",
        "note_fragment": (
            "Diagnosis: juvenile myoclonic epilepsy. She also gets tonic clonic seizures "
            "and myoclonic jerks."
        ),
        "benchmark_output": {"seizure_type": ["tonic clonic seizures"]},
        "policy": "Prefer the coarse tonic clonic label; do not add myoclonic seizures.",
    },
    {
        "case": "jme_tonic_clonic_surface_without_generalized_prefix",
        "note_fragment": "Diagnosis: JME. Seizure type: tonic clonic seizures.",
        "benchmark_output": {"seizure_type": ["tonic clonic seizures"]},
        "policy": "Use tonic clonic seizures when the note does not use a generalized tonic clonic prefix.",
    },
    {
        "case": "jme_generalized_tonic_seizures_without_clonic",
        "note_fragment": (
            "Diagnosis: probably JME presenting with generalised tonic seizures, "
            "absences and myoclonic jerks."
        ),
        "benchmark_output": {"seizure_type": ["generalized tonic seizures"]},
        "policy": "Use generalized tonic seizures when the note names that surface without clonic.",
    },
    {
        "case": "specificity_collapse_diagnosis_co_list",
        "note_fragment": (
            "Diagnosis: Focal epilepsy, probable occipital lobe onset. Impression: drug "
            "refractory focal (occipital lobe) epilepsy."
        ),
        "benchmark_output": {
            "diagnosis": [
                "focal",
                "drug",
                "occipital",
                "focal epilepsy",
                "occipital lobe epilepsy",
            ]
        },
        "policy": (
            "Co-list collapsed focal, drug, and occipital diagnosis tokens with the "
            "lobe-specific epilepsy labels when the note supports specificity collapse."
        ),
    },
    {
        "case": "specificity_collapse_secondary_seizure_surface",
        "note_fragment": (
            "Diagnosis: Focal epilepsy, probable occipital lobe onset. Impression: drug "
            "refractory focal (occipital lobe) epilepsy. About once a month she will have a "
            "secondary generalised seizure."
        ),
        "benchmark_output": {"seizure_type": ["secondary"]},
        "policy": (
            "Emit only secondary when specificity-collapse diagnosis context applies; "
            "do not add focal seizure descriptors or the full secondary generalised phrase."
        ),
    },
    {
        "case": "secondary_token_co_list_with_full_phrase",
        "note_fragment": (
            "She has complex partial seizures and secondary generalised seizures per year."
        ),
        "benchmark_output": {
            "seizure_type": [
                "complex partial seizures",
                "secondary generalized seizures",
                "secondary",
            ]
        },
        "policy": (
            "Co-list secondary alongside the full secondary generalised seizures label "
            "when collapsed benchmark tokens are expected."
        ),
    },
    {
        "case": "current_prescription_with_taper_parenthetical",
        "note_fragment": (
            "Current anti-epileptic medication: lamotrigine 75mg bd "
            "(to reduce and stop as detailed below). To start levetiracetam as detailed below."
        ),
        "benchmark_output": {"annotated_medication": ["lamotrigine"]},
        "policy": (
            "Keep lamotrigine from the current prescription line; exclude the separate "
            "planned levetiracetam start."
        ),
    },
    {
        "case": "dissociative_epileptic_seizure_routing",
        "note_fragment": (
            "Diagnosis: Dissociative seizures, Focal onset epilepsy. Sometimes it is "
            "difficult to tell whether he is having epileptic or dissociative "
            "(non-epileptic) seizures but I think on balance these do sound like "
            "epileptic seizures."
        ),
        "benchmark_output": {
            "diagnosis": ["focal onset epilepsy"],
            "seizure_type": ["epileptic seizures"],
        },
        "policy": (
            "Route the epileptic-versus-dissociative conclusion to epileptic seizures; "
            "do not emit focal seizures from the epilepsy diagnosis alone."
        ),
    },
    {
        "case": "myoclonic_jerks_to_myoclonic_seizures",
        "note_fragment": "Seizure type: myoclonic jerks.",
        "benchmark_output": {"seizure_type": ["myoclonic seizures"]},
        "policy": "Map jerk wording to myoclonic seizures when that is the audited surface.",
    },
    {
        "case": "non_asm_medication_exclusion",
        "note_fragment": "Current medication: lamotrigine 100mg bd, citalopram 20mg od.",
        "benchmark_output": {"annotated_medication": ["lamotrigine"]},
        "policy": "Exclude non-anti-seizure medications from annotated_medication.",
    },
    {
        "case": "empty_medication_without_prescription_list",
        "note_fragment": "Seizure type: focal seizures. No current anti-epileptic medication documented.",
        "benchmark_output": {"annotated_medication": []},
        "policy": "Return empty medication when no prescription-style ASM list is present.",
    },
    {
        "case": "prescription_request_exclusion",
        "note_fragment": "I would be grateful if you could prescribe lamotrigine.",
        "benchmark_output": {"annotated_medication": []},
        "policy": "Exclude ASM mentioned only as a prescription request, not a current list.",
    },
    {
        "case": "planned_switch_exclusion",
        "note_fragment": "Carbamazepine 400mg bd (to change to eslicarbazepine as below). Zonisamide 100mg bd.",
        "benchmark_output": {"annotated_medication": ["carbamazepine", "zonisamide"]},
        "policy": "Exclude planned switches; keep current prescription entries only.",
    },
    {
        "case": "taper_stop_exclusion",
        "note_fragment": "Reduce the levetiracetam by 250mg every week until stopped. Increase carbamazepine.",
        "benchmark_output": {"annotated_medication": []},
        "policy": "Exclude taper/stop instructions; do not treat dose-change plans as current ASM.",
    },
    {
        "case": "restart_advice_after_self_stop",
        "note_fragment": "She decided to stop her medication herself. We advised that she continues with lamotrigine.",
        "benchmark_output": {"annotated_medication": []},
        "policy": "Exclude ASM mentioned only as advice after self-discontinuation.",
    },
    {
        "case": "brand_lamictal_preservation",
        "note_fragment": "Current medication: Lamictal 100mg BD.",
        "benchmark_output": {"annotated_medication": ["Lamictal"]},
        "policy": "Preserve the brand prescription surface when the note uses Lamictal.",
    },
    {
        "case": "brand_epilim_chrono_preservation",
        "note_fragment": "Current medication: Epilim Chrono 500mg nocte.",
        "benchmark_output": {"annotated_medication": ["Epilim Chrono"]},
        "policy": "Preserve multi-word brand surfaces such as Epilim Chrono.",
    },
)

_REJECTED_GRANULAR_SEIZURE_TYPES = frozenset(
    {
        "absences",
        "jerks",
        "occasional absences",
    }
)

_GRANULAR_SEIZURE_TYPE_COARSENING = {
    "myoclonic jerks": "myoclonic seizures",
    "absence events": "generalized tonic clonic seizures",
}

_JME_COARSE_SEIZURE_LABELS = frozenset(
    {
        "generalized tonic clonic seizures",
        "generalized tonic clonic seizure",
        "tonic clonic seizures",
        "tonic clonic seizure",
        "generalized tonic seizures",
        "generalized tonic seizure",
    }
)

_JME_MYCLONIC_SEIZURE_LABELS = frozenset(
    {
        "myoclonic seizures",
        "myoclonic seizure",
    }
)

_REJECTED_ANNOTATED_MEDICATIONS = frozenset(
    {
        "citalopram",
        "fluoxetine",
        "sertraline",
        "amitriptyline",
        "diazepam",
    }
)

_MEDICATION_SURFACE_REPAIRS = {
    "eslicarbazine": "eslicarbazepine",
    "brivitiracetam": "brivaracetam",
    "zonismaide": "zonisamide",
}

_MEDICATION_PLANNED_OR_HISTORICAL_EVIDENCE_PHRASES = (
    "to start",
    "please start",
    "plan to start",
    "will start",
    "recommend starting",
    "grateful if you could prescribe",
    "could prescribe",
    "previously",
    "prior ",
)

_MEDICATION_EVIDENCE_EXCLUSION_PHRASES = (
    "previously",
    "prior ",
    "to start",
    "to change to",
    "plan to start",
    "we plan",
    "tried ",
    "recommend starting",
    "will start",
    "please start",
    "would recommend",
    "grateful if you could prescribe",
    "could prescribe",
    "as detailed below",
    "reduce the",
    "stopped completely",
    "decided to stop",
    "stopping the medication",
    "stop her medication",
    "advised that",
    "continues with the",
    "every week until",
    "information leaflet on",
)

_MEDICATION_BRAND_NOTE_SURFACES = (
    ("lamotrigine", "lamictal", "lamictal"),
    ("sodium valproate", "epilim chrono", "epilim chrono"),
)

_MEDICATION_EVIDENCE_PREFIXES = (
    "medication:",
    "medications:",
    "current medication:",
    "current medications:",
    "current anti epileptic medication:",
    "current anti-epileptic medication:",
    "anti epileptic medication:",
    "anti-epileptic medication:",
)

_CURRENT_PRESCRIPTION_LINE_RE = re.compile(
    r"(?im)^(?:current\s+(?:anti[- ]?epileptic\s+)?medication|medications)\s*[:\s–\-]+(.+)$"
)

_KNOWN_PRESCRIPTION_MEDICATIONS = tuple(
    sorted(
        {
            "brivaracetam",
            "carbamazepine",
            "clobazam",
            "eslicarbazepine",
            "gabapentin",
            "lamotrigine",
            "lacosamide",
            "levetiracetam",
            "oxcarbazepine",
            "phenobarbital",
            "phenytoin",
            "pregabalin",
            "sodium valproate",
            "topiramate",
            "vigabatrin",
            "zonisamide",
            *_MEDICATION_SURFACE_REPAIRS,
            *_MEDICATION_SURFACE_REPAIRS.values(),
        },
        key=len,
        reverse=True,
    )
)

_SPECIFICITY_COLLAPSE_DIAGNOSIS_TOKENS = ("focal", "drug", "occipital")
_SPECIFICITY_COLLAPSE_TRIGGER_DIAGNOSES = frozenset(
    {
        "drug refractory epilepsy",
        "focal epilepsy",
        "occipital lobe epilepsy",
    }
)
_SECONDARY_COLLAPSED_SEIZURE_TOKEN = "secondary"
_SECONDARY_GENERALISED_SEIZURE_LABELS = frozenset(
    {
        "secondary generalised seizure",
        "secondary generalised seizures",
        "secondary generalized seizure",
        "secondary generalized seizures",
    }
)
_SECONDARY_GENERALISED_SEIZURE_NOTE_RE = re.compile(
    r"\bsecondary generali[sz]ed seiz"
)

_DIAGNOSIS_HEADER_RE = re.compile(r"(?im)^\s*diagnosis\s*[:\s–\-]+\s*([^\n]+)")

_ON_AWAKENING_SYNDROME_DIAGNOSIS = "epilepsy with generalized tonic clonic seizures on awakening"
_ON_AWAKENING_SYNDROME_NOTE_RE = re.compile(
    r"epilepsy with generali[sz]ed tonic clonic seiz(?:ure|ures)\s+(?:from sleep|on awakening)\b"
)

_EPILEPTIC_SEIZURES_LABEL = "epileptic seizures"
_DISSOCIATIVE_EPILEPTIC_FOCAL_SEIZURE_LABELS = frozenset(
    {"focal seizures", "focal seizure"}
)

_GENERIC_EPILEPSY_CO_LIST_TRIGGERS = (
    "focal onset epilepsy",
    "primary generalized epilepsy",
    "symptomatic structural focal epilepsy",
    "focal epilepsy",
    "generalized epilepsy",
    "genetic generalized epilepsy",
)

ALLOWED_DIAGNOSIS_LABELS = frozenset(
    {
        "drug",
        "drug refractory epilepsies",
        "drug refractory epilepsy",
        "drug resistant epilepsy",
        "epilepsy",
        "epilepsy due to stroke",
        "epilepsy with generalized tonic clonic seizure alone",
        "epilepsy with generalized tonic clonic seizures alone",
        "epilepsy with generalized tonic clonic seizures on awakening",
        "epilepsy, generalized",
        "focal",
        "focal epilepsy",
        "focal onset epilepsy",
        "focal symptomatic epilepsy",
        "frontal",
        "frontal lobe epilepsy",
        "generalized epilepsy",
        "genetic generalized epilepsy",
        "intractable epilepsy",
        "jme",
        "juvenile absence epilepsy",
        "juvenile myoclonic epilepsy",
        "localisation related epilepsy",
        "occipital",
        "occipital lobe epilepsy",
        "parietal lobe epilepsy",
        "primary generalized epilepsy",
        "refractory epilepsies",
        "status epilepticus",
        "symptomatic",
        "symptomatic epilepsy",
        "symptomatic focal epilepsy",
        "symptomatic structural focal epilepsy",
        "temporal lobe epilepsy",
    }
)


class ExectS0S1FieldFamilySignature(dspy.Signature):
    """Extract audited ExECT S0/S1 benchmark-facing field families.

    Return only labels directly supported by the note. This is an annotation-policy
    aligned task, not a clinically rich free extraction task.

    Policy:
    - diagnosis: established epilepsy diagnoses only. Preserve the explicit audited
      diagnosis surface after deterministic canonicalization; do not force every focal,
      temporal-lobe, symptomatic, refractory, or syndrome phrase into a five-label set
      unless the scorer has an explicit mapping. Do not infer epilepsy from a single
      seizure event, and do not infer subtype from seizure-type evidence alone.
    - seizure_type: seizure-type labels independently named in the note. Use the
      audited benchmark-facing surface supported by the note, preserving plural and
      modifier forms such as focal seizures with altered awareness, focal to bilateral
      convulsive seizures, or occipital lobe seizures when those are the scorer labels.
      Split fused phrases such as temporal lobe onset focal seizures or focal seizures
      with secondary generalisation into separate audited labels. Do not infer seizure
      type from diagnosis alone.
    - annotated_medication: audited prescription-style medication mentions only. Do
      not include planned starts, previous trials, taper/stop instructions, or medication
      history mentions in the benchmark-facing medication list.
    - evidence lists should align by index with the corresponding value lists and
      contain exact contiguous source quotes where possible.

    Boundary examples:
    - "Current anti-epileptic medication: lamotrigine 75mg bd. To start levetiracetam."
      -> annotated_medication = ["lamotrigine"]; exclude the planned levetiracetam start.
    - "Previously tried carbamazepine. Current treatment is sodium valproate."
      -> annotated_medication = ["sodium valproate"]; exclude previous carbamazepine.
    - "The events are temporal-lobe-onset focal seizures."
      -> seizure_type = ["temporal lobe seizure", "focal seizures"]; split the fused
      rich phrase into audited benchmark labels.
    - "Seizure type: focal seizures with secondary generalisation."
      -> seizure_type = ["focal seizures", "secondary generalisation",
      "generalized tonic clonic seizure"]; split fused secondary-generalisation phrases.
    - "She has focal to bilateral seizures."
      -> seizure_type = ["focal to bilateral convulsive seizures"]; preserve convulsive
      modifiers when required by the audited surface.
    - "Diagnosis: probable juvenile myoclonic epilepsy."
      -> diagnosis = ["juvenile myoclonic epilepsy"]; strip uncertainty qualifiers for
      benchmark-facing labels.
    - "Diagnosis: hydrocephalus. Seizure type: focal seizures."
      -> diagnosis = []; seizure_type = ["focal seizures"]; keep seizure types out of
      diagnosis and omit non-epilepsy diagnoses.
    - "Seizure type: temporal lobe seizures with occipital lobe seizures."
      -> seizure_type = ["temporal lobe seizure", "focal seizures", "occipital lobe
      seizures"]; do not stop at temporal lobe seizures alone.
    - "Seizure type and frequency: focal onset convulsive seizure."
      -> seizure_type = ["focal to bilateral convulsive seizure"]; use the audited
      bilateral convulsive benchmark surface when required.
    - "Diagnosis: epilepsy with generalized tonic clonic seizures on awakening."
      -> diagnosis = ["epilepsy with generalized tonic clonic seizures on awakening"];
      preserve on awakening wording.
    - "Diagnosis: symptomatic structural focal epilepsy."
      -> diagnosis = ["symptomatic structural focal epilepsy"]; preserve the audited label.
    - "Seizure type and frequency: focal seizures with altered awareness every 3 weeks."
      -> seizure_type = ["focal seizures with altered awareness"]; preserve plural wording.
    - "Seizure type: occipital lobe seizures. Previous medication: lamotrigine."
      -> seizure_type_evidence = ["occipital lobe seizures"]; use exact contiguous quotes.
    - "This was a single focal seizure. There is no established epilepsy diagnosis."
      -> diagnosis = []; do not convert a single event into established epilepsy.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    diagnosis: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing epilepsy diagnosis labels only. Preserve the explicit audited "
            "diagnosis surface after deterministic canonicalization; use [] for single "
            "seizure events without established epilepsy."
        )
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each diagnosis label, aligned by index."
    )
    seizure_type: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing seizure-type labels explicitly named in the note. "
            "Preserve audited plural and modifier surfaces when supported; do not infer "
            "these from diagnosis alone."
        )
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-type label, aligned by index."
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc=(
            "Audited prescription-style anti-seizure medication names. Exclude planned, "
            "previous, taper/stop, and medication-history-only mentions."
        )
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication label, aligned by index."
    )


class ExectS0S1FieldFamilyModule(dspy.Module):
    """Single-pass ExECT S0/S1 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class ExectS0S1DiagnosisSignature(dspy.Signature):
    """Extract benchmark-facing ExECT diagnosis labels only."""

    note_text: str = dspy.InputField(desc="Section-aware ExECT note context for diagnosis")
    diagnosis: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing epilepsy diagnosis labels only. Preserve the explicit audited "
            "diagnosis surface after deterministic canonicalization; use [] for single "
            "seizure events without established epilepsy."
        )
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each diagnosis label, aligned by index."
    )


class ExectS0S1SeizureTypeSignature(dspy.Signature):
    """Extract benchmark-facing ExECT seizure-type labels only."""

    note_text: str = dspy.InputField(desc="Section-aware ExECT note context for seizure type")
    seizure_type: list[str] = dspy.OutputField(
        desc=(
            "Benchmark-facing seizure-type labels explicitly named in the note. "
            "Preserve audited plural and modifier surfaces when supported; do not infer "
            "these from diagnosis alone."
        )
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each seizure-type label, aligned by index."
    )


class ExectS0S1MedicationSignature(dspy.Signature):
    """Extract benchmark-facing ExECT annotated medications only."""

    note_text: str = dspy.InputField(desc="Section-aware ExECT note context for medication")
    annotated_medication: list[str] = dspy.OutputField(
        desc=(
            "Audited prescription-style anti-seizure medication names. Exclude planned, "
            "previous, taper/stop, and medication-history-only mentions."
        )
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each medication label, aligned by index."
    )


class ExectS0S1DiagnosisRecallSignature(dspy.Signature):
    """Find additional missed benchmark-facing ExECT diagnosis labels.

    Review the note and the initial diagnosis list. Return ONLY additional
    established epilepsy diagnoses that the initial pass missed. This is an
    add-only recall pass — do not repeat labels already in initial_diagnosis.

    Recall policy:
    - Add co-listed lobe-specific or syndrome epilepsy diagnoses when the note
      explicitly names them alongside a broader epilepsy diagnosis (e.g. add
      parietal lobe epilepsy when focal epilepsy and probable parietal onset
      are both stated).
    - Add generic epilepsy when the note explicitly states established epilepsy
      but initial_diagnosis omitted it while listing only a more specific label.
    - Preserve audited diagnosis surfaces such as epilepsy with generalized
      tonic clonic seizures on awakening when that exact phrasing appears.
    - Do not infer epilepsy subtype from seizure-type evidence alone.
    - Do not add a diagnosis for a single seizure event without established
      epilepsy wording.
    - Do not add non-epilepsy conditions or seizure-type phrases.
    - Return [] when no additional benchmark-facing diagnoses are supported.
    - additional_diagnosis_evidence must be exact contiguous note quotes aligned
      by index with additional_diagnosis.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    initial_diagnosis: list[str] = dspy.InputField(
        desc="Diagnosis labels already extracted in the first pass."
    )
    additional_diagnosis: list[str] = dspy.OutputField(
        desc=(
            "Additional benchmark-facing epilepsy diagnosis labels not already "
            "in initial_diagnosis. Use [] when none."
        )
    )
    additional_diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact source quotes supporting each additional diagnosis, aligned by index."
    )


class ExectS0S1DiagnosisRecallProbeModule(dspy.Module):
    """Monolithic extraction plus add-only diagnosis recall pass."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(ExectS0S1FieldFamilySignature)
        self.recall_diagnosis = dspy.Predict(ExectS0S1DiagnosisRecallSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extract(note_text=note_text)
        initial_diagnosis = _as_list(getattr(initial, "diagnosis", []))
        initial_diagnosis_evidence = _as_list(getattr(initial, "diagnosis_evidence", []))
        recall = self.recall_diagnosis(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
        )
        merged_diagnosis, merged_diagnosis_evidence, recall_added = _merge_diagnosis_recall(
            initial_diagnosis=initial_diagnosis,
            initial_diagnosis_evidence=initial_diagnosis_evidence,
            additional_diagnosis=_as_list(getattr(recall, "additional_diagnosis", [])),
            additional_diagnosis_evidence=_as_list(
                getattr(recall, "additional_diagnosis_evidence", [])
            ),
        )
        return dspy.Prediction(
            diagnosis=merged_diagnosis,
            diagnosis_evidence=merged_diagnosis_evidence,
            seizure_type=_as_list(getattr(initial, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(initial, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(initial, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(initial, "annotated_medication_evidence", [])
            ),
            diagnosis_recall_added=recall_added,
            initial_diagnosis=initial_diagnosis,
        )


class ExectS0S1VerifierSignature(dspy.Signature):
    """Verify and repair benchmark-facing ExECT S0/S1 field-family extraction.

    Review the initial extraction against the note. This is a confirm-first verifier:
    preserve correct initial labels and evidence; repair only clear errors.

    Confirm-first policy:
    - When initial labels and evidence are benchmark-facing and note-supported, confirm
      unchanged. Do not add diagnoses, seizure types, or medications for recall.
    - Repair evidence quotes to the shortest exact contiguous substring of note_text.
    - Remove unsupported labels, cross-family leakage, planned/previous ASM, and granular
      seizure descriptors (jerks, absences) when coarse benchmark surfaces apply.
    - Do not add medications from prescription requests, planned starts, taper/stop
      instructions, or medication-history mentions.
    - Do not add-only co-listed diagnoses (diagnosis-recall probe was negative).
    - Prefer removing a label over inventing evidence.

    Evidence rules:
    - Evidence lists align by index with value lists.
    - Each evidence entry must be an exact contiguous quote from note_text.
    - On confirm, keep initial evidence when it already matches the note.
    """

    note_text: str = dspy.InputField(desc="Synthetic epilepsy clinic letter text")
    initial_diagnosis: list[str] = dspy.InputField(
        desc="Initial diagnosis labels from the extraction pass."
    )
    initial_diagnosis_evidence: list[str] = dspy.InputField(
        desc="Initial diagnosis evidence quotes, aligned by index."
    )
    initial_seizure_type: list[str] = dspy.InputField(
        desc="Initial seizure-type labels from the extraction pass."
    )
    initial_seizure_type_evidence: list[str] = dspy.InputField(
        desc="Initial seizure-type evidence quotes, aligned by index."
    )
    initial_annotated_medication: list[str] = dspy.InputField(
        desc="Initial annotated medication labels from the extraction pass."
    )
    initial_annotated_medication_evidence: list[str] = dspy.InputField(
        desc="Initial medication evidence quotes, aligned by index."
    )
    diagnosis: list[str] = dspy.OutputField(
        desc="Confirmed or repaired benchmark-facing diagnosis labels."
    )
    diagnosis_evidence: list[str] = dspy.OutputField(
        desc="Exact note quotes supporting each diagnosis label, aligned by index."
    )
    seizure_type: list[str] = dspy.OutputField(
        desc="Confirmed or repaired benchmark-facing seizure-type labels."
    )
    seizure_type_evidence: list[str] = dspy.OutputField(
        desc="Exact note quotes supporting each seizure-type label, aligned by index."
    )
    annotated_medication: list[str] = dspy.OutputField(
        desc="Confirmed or repaired prescription-style ASM labels only."
    )
    annotated_medication_evidence: list[str] = dspy.OutputField(
        desc="Exact note quotes supporting each medication label, aligned by index."
    )
    verifier_decision: str = dspy.OutputField(
        desc=(
            "confirm when all initial labels are already correct; repair when at least "
            "one label or evidence quote was corrected; abstain only as a last resort"
        )
    )
    verifier_reason: str = dspy.OutputField(
        desc="Brief explanation of confirm/repair/abstain citing note spans"
    )


class ExectS0S1VerifierModule(dspy.Module):
    """Confirm-first verifier for ExECT S0/S1 field-family extraction."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(ExectS0S1VerifierSignature)

    def forward(
        self,
        note_text: str,
        *,
        initial_diagnosis: list[str],
        initial_diagnosis_evidence: list[str],
        initial_seizure_type: list[str],
        initial_seizure_type_evidence: list[str],
        initial_annotated_medication: list[str],
        initial_annotated_medication_evidence: list[str],
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
            initial_diagnosis_evidence=initial_diagnosis_evidence,
            initial_seizure_type=initial_seizure_type,
            initial_seizure_type_evidence=initial_seizure_type_evidence,
            initial_annotated_medication=initial_annotated_medication,
            initial_annotated_medication_evidence=initial_annotated_medication_evidence,
        )


class ExectS0S1VerifyRepairModule(dspy.Module):
    """Monolithic v4.2 extraction plus confirm-first verify/repair pass."""

    def __init__(self) -> None:
        super().__init__()
        self.extractor = ExectS0S1FieldFamilyModule()
        self.verifier = ExectS0S1VerifierModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        initial_diagnosis = _as_list(getattr(initial, "diagnosis", []))
        initial_diagnosis_evidence = _as_list(getattr(initial, "diagnosis_evidence", []))
        initial_seizure_type = _as_list(getattr(initial, "seizure_type", []))
        initial_seizure_type_evidence = _as_list(getattr(initial, "seizure_type_evidence", []))
        initial_medication = _as_list(getattr(initial, "annotated_medication", []))
        initial_medication_evidence = _as_list(
            getattr(initial, "annotated_medication_evidence", [])
        )
        verified = self.verifier(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
            initial_diagnosis_evidence=initial_diagnosis_evidence,
            initial_seizure_type=initial_seizure_type,
            initial_seizure_type_evidence=initial_seizure_type_evidence,
            initial_annotated_medication=initial_medication,
            initial_annotated_medication_evidence=initial_medication_evidence,
        )
        guarded = _apply_exect_verifier_guards(
            note_text=note_text,
            initial_diagnosis=initial_diagnosis,
            initial_seizure_type=initial_seizure_type,
            initial_annotated_medication=initial_medication,
            verified=verified,
        )
        return dspy.Prediction(
            diagnosis=_as_list(getattr(guarded, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(guarded, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(guarded, "seizure_type", [])),
            seizure_type_evidence=_as_list(getattr(guarded, "seizure_type_evidence", [])),
            annotated_medication=_as_list(getattr(guarded, "annotated_medication", [])),
            annotated_medication_evidence=_as_list(
                getattr(guarded, "annotated_medication_evidence", [])
            ),
            verifier_decision=getattr(guarded, "verifier_decision", None),
            verifier_reason=getattr(guarded, "verifier_reason", None),
            initial_diagnosis=initial_diagnosis,
            initial_seizure_type=initial_seizure_type,
            initial_annotated_medication=initial_medication,
        )


class ExectS0S1SectionAwareFieldFamilyModule(dspy.Module):
    """Section-aware ExECT S0/S1 field-family extractor."""

    def __init__(self) -> None:
        super().__init__()
        self.extract_diagnosis = dspy.ChainOfThought(ExectS0S1DiagnosisSignature)
        self.extract_seizure_type = dspy.ChainOfThought(ExectS0S1SeizureTypeSignature)
        self.extract_medication = dspy.ChainOfThought(ExectS0S1MedicationSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        diagnosis_context = _family_context(
            note_text,
            target_field="diagnosis",
            max_sections=2,
        )
        seizure_context = _family_context(
            note_text,
            target_field="seizure_type",
            max_sections=3,
        )
        medication_context = _family_context(
            note_text,
            target_field="medication",
            max_sections=2,
        )

        diagnosis = self.extract_diagnosis(note_text=diagnosis_context)
        seizure_type = self.extract_seizure_type(note_text=seizure_context)
        medication = self.extract_medication(note_text=medication_context)
        return dspy.Prediction(
            diagnosis=_as_list(getattr(diagnosis, "diagnosis", [])),
            diagnosis_evidence=_as_list(getattr(diagnosis, "diagnosis_evidence", [])),
            seizure_type=_as_list(getattr(seizure_type, "seizure_type", [])),
            seizure_type_evidence=_as_list(
                getattr(seizure_type, "seizure_type_evidence", [])
            ),
            annotated_medication=_as_list(
                getattr(medication, "annotated_medication", [])
            ),
            annotated_medication_evidence=_as_list(
                getattr(medication, "annotated_medication_evidence", [])
            ),
        )


def build_exect_s0_s1_module(program_variant: str = EXECT_S0_S1_VARIANT) -> dspy.Module:
    """Build an ExECT S0/S1 module for the requested program variant."""
    if program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT:
        return ExectS0S1SectionAwareFieldFamilyModule()
    if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT:
        return ExectS0S1DiagnosisRecallProbeModule()
    if program_variant == EXECT_S0_S1_VERIFY_REPAIR_VARIANT:
        return ExectS0S1VerifyRepairModule()
    if program_variant == EXECT_S0_S1_VARIANT:
        return ExectS0S1FieldFamilyModule()
    raise ValueError(f"Unsupported ExECT S0/S1 program variant: {program_variant!r}")


def _apply_exect_verifier_guards(
    *,
    note_text: str,
    initial_diagnosis: list[str],
    initial_seizure_type: list[str],
    initial_annotated_medication: list[str],
    verified: dspy.Prediction,
) -> dspy.Prediction:
    """Deterministic confirm-first guards for ExECT verify-repair."""
    initial_diagnosis_keys = {
        canonical_clinical_phrase(value)
        for value in initial_diagnosis
        if value.strip()
    }
    diagnosis = []
    diagnosis_evidence = []
    for index, raw_value in enumerate(_as_list(getattr(verified, "diagnosis", []))):
        normalized = canonical_clinical_phrase(raw_value)
        if not normalized or normalized not in initial_diagnosis_keys:
            continue
        diagnosis.append(raw_value.strip())
        diagnosis_evidence.append(
            _evidence_at(_as_list(getattr(verified, "diagnosis_evidence", [])), index) or ""
        )

    initial_seizure_keys = {
        canonical_clinical_phrase(value) for value in initial_seizure_type if value.strip()
    }
    seizure_type = []
    seizure_type_evidence = []
    for index, raw_value in enumerate(_as_list(getattr(verified, "seizure_type", []))):
        normalized = canonical_clinical_phrase(raw_value)
        if normalized in _REJECTED_GRANULAR_SEIZURE_TYPES:
            continue
        if normalized and not _verified_seizure_allowed(normalized, initial_seizure_keys):
            continue
        seizure_type.append(raw_value.strip())
        seizure_type_evidence.append(
            _evidence_at(_as_list(getattr(verified, "seizure_type_evidence", [])), index) or ""
        )

    initial_medication_keys = {
        canonical_medication_name(value)
        for value in initial_annotated_medication
        if value.strip()
    }
    medication = []
    medication_evidence = []
    verified_medication = _as_list(getattr(verified, "annotated_medication", []))
    verified_medication_evidence = _as_list(
        getattr(verified, "annotated_medication_evidence", [])
    )
    for index, raw_value in enumerate(verified_medication):
        evidence_text = _evidence_at(verified_medication_evidence, index)
        if evidence_text and evidence_text not in note_text:
            continue
        if _medication_evidence_excluded(evidence_text):
            continue
        normalized = canonical_medication_name(raw_value)
        repaired = _MEDICATION_SURFACE_REPAIRS.get(normalized, normalized)
        if repaired in _REJECTED_ANNOTATED_MEDICATIONS:
            continue
        if repaired and repaired not in initial_medication_keys:
            continue
        if repaired:
            medication.append(raw_value.strip())
            medication_evidence.append(evidence_text or "")

    return dspy.Prediction(
        diagnosis=diagnosis,
        diagnosis_evidence=diagnosis_evidence,
        seizure_type=seizure_type,
        seizure_type_evidence=seizure_type_evidence,
        annotated_medication=medication,
        annotated_medication_evidence=medication_evidence,
        verifier_decision=getattr(verified, "verifier_decision", "repair"),
        verifier_reason=getattr(verified, "verifier_reason", ""),
    )


def _merge_diagnosis_recall(
    *,
    initial_diagnosis: list[str],
    initial_diagnosis_evidence: list[str],
    additional_diagnosis: list[str],
    additional_diagnosis_evidence: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Merge add-only recalled diagnoses with deterministic guards."""
    merged_diagnosis = list(initial_diagnosis)
    merged_evidence = _align_evidence(initial_diagnosis, initial_diagnosis_evidence)
    seen = {
        canonical_clinical_phrase(value)
        for value in initial_diagnosis
        if value.strip()
    }
    recall_added: list[str] = []

    for index, raw_value in enumerate(additional_diagnosis):
        if not raw_value.strip():
            continue
        normalized = canonical_clinical_phrase(raw_value)
        normalized, _ = _normalize_diagnosis_surface(normalized)
        if not normalized or normalized in seen or normalized not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        evidence_text = _evidence_at(additional_diagnosis_evidence, index)
        merged_diagnosis.append(raw_value.strip())
        merged_evidence.append(evidence_text or "")
        seen.add(normalized)
        recall_added.append(normalized)

    return merged_diagnosis, merged_evidence, recall_added


def _align_evidence(values: list[str], evidence_values: list[str]) -> list[str]:
    aligned = list(evidence_values)
    while len(aligned) < len(values):
        aligned.append("")
    return aligned[: len(values)]


def make_exect_s0_s1_dspy_examples(
    records: list[ExectGoldDocument],
) -> list[dspy.Example]:
    """Convert audited ExECT gold documents into DSPy examples."""
    return [
        dspy.Example(
            note_text=record.text,
            diagnosis=record.diagnoses,
            seizure_type=record.seizure_types,
            annotated_medication=record.current_medications,
        ).with_inputs("note_text")
        for record in records
    ]


def predict_exect_records(
    module: dspy.Module,
    records: list[ExectGoldDocument],
    *,
    model_provider: str,
    model_name: str,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    program_variant: str = EXECT_S0_S1_VARIANT,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> PredictionSet:
    """Run ``module`` on ExECT records and return a shared ``PredictionSet``."""
    predictions = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        predictions.append(_predict_record(module, record, program_variant=program_variant))
        if progress_callback is not None:
            progress_callback(index, total, record.document_id)
    return PredictionSet(
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        predictions=predictions,
        metadata={
            "program_variant": program_variant,
            "model_provider": model_provider,
            "model_name": model_name,
            "prompt_version": prompt_version,
            "scorer_mode": EXECT_S0_S1_SCORER,
        },
    )


def _predict_record(
    module: dspy.Module,
    record: ExectGoldDocument,
    *,
    program_variant: str,
) -> DocumentPrediction:
    pred = module(note_text=record.text)
    values: list[ExtractedValue] = []

    diagnosis_inputs = _as_list(getattr(pred, "diagnosis", []))
    if program_variant == EXECT_S0_S1_VARIANT:
        diagnosis_inputs, diagnosis_header_flags = _filter_diagnosis_for_seizure_descriptor_header(
            diagnosis_inputs,
            record.text,
        )
        diagnosis_raw, diagnosis_augmented, specificity_collapse_augmented = (
            _augment_diagnosis_co_lists(
                diagnosis_inputs,
                record.text,
            )
        )
    else:
        diagnosis_raw = diagnosis_inputs
        diagnosis_augmented = set()
        specificity_collapse_augmented = set()
        diagnosis_header_flags = []
    diagnoses, collapsed = _normalize_diagnoses(diagnosis_raw)
    diagnosis_evidence = _as_list(getattr(pred, "diagnosis_evidence", []))
    values.extend(
        _values_for_family(
            record=record,
            field_name="diagnosis",
            raw_values=diagnoses,
            evidence_values=diagnosis_evidence,
            collapsed_values=collapsed,
            augmented_values=diagnosis_augmented,
            specificity_collapse_augmented=specificity_collapse_augmented,
            extra_quality_flags=diagnosis_header_flags,
        )
    )
    if program_variant == EXECT_S0_S1_VARIANT:
        values.extend(
            _seizure_type_values_for_record(
                record=record,
                raw_values=_as_list(getattr(pred, "seizure_type", [])),
                evidence_values=_as_list(getattr(pred, "seizure_type_evidence", [])),
            )
        )
    else:
        values.extend(
            _values_for_family(
                record=record,
                field_name="seizure_type",
                raw_values=_as_list(getattr(pred, "seizure_type", [])),
                evidence_values=_as_list(getattr(pred, "seizure_type_evidence", [])),
            )
        )
    if program_variant == EXECT_S0_S1_VARIANT:
        medication_raw, medication_evidence, medication_augmented = (
            _augment_current_prescription_medications(
                _as_list(getattr(pred, "annotated_medication", [])),
                _as_list(getattr(pred, "annotated_medication_evidence", [])),
                record.text,
            )
        )
    else:
        medication_raw = _as_list(getattr(pred, "annotated_medication", []))
        medication_evidence = _as_list(getattr(pred, "annotated_medication_evidence", []))
        medication_augmented = set()
    values.extend(
        _values_for_family(
            record=record,
            field_name="annotated_medication",
            raw_values=medication_raw,
            evidence_values=medication_evidence,
            augmented_values=medication_augmented,
        )
    )

    return DocumentPrediction(
        document_id=record.document_id,
        dataset=EXECT_DATASET,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        values=values,
        quality_flags=record.quality_flags,
        metadata={"program_variant": program_variant},
    )


def _family_context(note_text: str, *, target_field: str, max_sections: int) -> str:
    selected = select_context(
        note_text,
        target_field=target_field,
        max_sections=max_sections,
    )
    if not selected:
        return note_text

    formatted = []
    for span in selected:
        label = span.section or "document"
        formatted.append(f"Section: {label}\n{span.text.strip()}")
    return "\n\n".join(chunk for chunk in formatted if chunk.strip()) or note_text


def _augment_diagnosis_co_lists(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], set[str], set[str]]:
    """Add note-supported co-listed diagnoses that monolithic extraction often omits."""
    note_lower = note_text.lower()
    normalized = {
        canonical_clinical_phrase(value)
        for value in raw_values
        if value.strip()
    }
    additions: list[str] = []
    augmented: set[str] = set()

    def add(label: str) -> None:
        key = canonical_clinical_phrase(label)
        if key in normalized or key not in ALLOWED_DIAGNOSIS_LABELS:
            return
        additions.append(label)
        normalized.add(key)
        augmented.add(key)

    for trigger in _GENERIC_EPILEPSY_CO_LIST_TRIGGERS:
        if trigger in normalized and _note_has_standalone_epilepsy(note_lower):
            add("epilepsy")
            break

    if "epilepsy" not in normalized:
        header = _diagnosis_header_text(note_text)
        if header and _header_establishes_generic_epilepsy(header):
            add("epilepsy")

    if "focal epilepsy" in normalized and "focal onset epilepsy" not in normalized:
        if "focal onset epilepsy" in note_lower:
            add("focal onset epilepsy")

    if "focal onset epilepsy" in normalized and "focal epilepsy" not in normalized:
        if re.search(r"\bfocal epilepsy\b", note_lower):
            add("focal epilepsy")

    if "parietal lobe epilepsy" not in normalized and _note_supports_parietal_lobe_epilepsy(
        note_lower
    ):
        if normalized & {"focal epilepsy", "focal onset epilepsy"}:
            add("parietal lobe epilepsy")

    if _ON_AWAKENING_SYNDROME_DIAGNOSIS not in normalized and _note_supports_on_awakening_syndrome_diagnosis(
        note_lower
    ):
        add(_ON_AWAKENING_SYNDROME_DIAGNOSIS)

    collapse_additions, collapse_augmented = _augment_specificity_collapse_diagnosis_tokens(
        [*raw_values, *additions],
        note_text,
    )
    for label in collapse_additions:
        key = canonical_clinical_phrase(label)
        if key in normalized or key not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        additions.append(label)
        normalized.add(key)

    return [*raw_values, *additions], augmented, collapse_augmented


def _diagnosis_header_text(note_text: str) -> str | None:
    match = _DIAGNOSIS_HEADER_RE.search(note_text)
    if not match:
        return None
    return match.group(1).strip().lower()


def _header_establishes_generic_epilepsy(header: str) -> bool:
    if re.search(r"\bunclassified epilepsy\b|\bepilepsy unclassified\b", header):
        return True
    if re.search(r"^epilepsy\b", header):
        return True
    return False


def _note_has_standalone_epilepsy(note_lower: str) -> bool:
    for match in re.finditer(r"\bepilepsy\b", note_lower):
        prefix = note_lower[max(0, match.start() - 30) : match.start()]
        if re.search(
            r"(?:focal\s+onset|focal|juvenile\s+myoclonic|lobe|structural|symptomatic|"
            r"generalized|refractory|drug)\s*$",
            prefix,
        ):
            continue
        return True
    return False


def _note_supports_parietal_lobe_epilepsy(note_lower: str) -> bool:
    return bool(
        re.search(
            r"parietal lobe epilepsy|probable parietal|parietal onset|parietal lobe",
            note_lower,
        )
    )


def _note_supports_on_awakening_syndrome_diagnosis(note_lower: str) -> bool:
    return bool(_ON_AWAKENING_SYNDROME_NOTE_RE.search(note_lower))


def _augment_specificity_collapse_diagnosis_tokens(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], set[str]]:
    note_lower = note_text.lower()
    if not _note_supports_specificity_collapse_diagnosis_co_list(note_lower):
        return [], set()

    normalized = {
        canonical_clinical_phrase(value)
        for value in raw_values
        if value.strip()
    }
    if not normalized & _SPECIFICITY_COLLAPSE_TRIGGER_DIAGNOSES:
        return [], set()

    additions: list[str] = []
    augmented: set[str] = set()
    for token in _SPECIFICITY_COLLAPSE_DIAGNOSIS_TOKENS:
        if token in normalized or token not in ALLOWED_DIAGNOSIS_LABELS:
            continue
        additions.append(token)
        normalized.add(token)
        augmented.add(token)
    return additions, augmented


def _note_supports_specificity_collapse_diagnosis_co_list(note_lower: str) -> bool:
    return bool(
        re.search(r"drug[- ]?refractory\s+focal", note_lower)
        or re.search(
            r"focal epilepsy.{0,80}probable occipital|probable occipital.{0,80}focal epilepsy",
            note_lower,
        )
        or re.search(r"occipital lobe\)?\s*epilepsy", note_lower)
    )


def _augment_current_prescription_medications(
    raw_values: list[str],
    evidence_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str], set[str]]:
    normalized = {
        canonical_medication_name(value)
        for value in raw_values
        if value.strip()
    }
    additions: list[str] = []
    augmented_evidence: list[str] = list(evidence_values)
    augmented: set[str] = set()

    for medication, evidence_line in _current_prescription_entries(note_text):
        if medication in normalized:
            continue
        additions.append(medication)
        augmented_evidence.append(evidence_line)
        normalized.add(medication)
        augmented.add(medication)

    return [*raw_values, *additions], augmented_evidence, augmented


def _current_prescription_entries(note_text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in _CURRENT_PRESCRIPTION_LINE_RE.finditer(note_text):
        line = match.group(0).strip()
        segment = match.group(1).strip()
        segment = re.split(r"\n\s*to start\b", segment, maxsplit=1, flags=re.IGNORECASE)[0]
        for medication in _medications_in_prescription_segment(segment):
            if medication in seen:
                continue
            seen.add(medication)
            entries.append((medication, line))
    return entries


def _medications_in_prescription_segment(segment: str) -> list[str]:
    segment_lower = segment.lower()
    found: list[str] = []
    for medication in _KNOWN_PRESCRIPTION_MEDICATIONS:
        if re.search(rf"\b{re.escape(medication)}\b", segment_lower):
            found.append(medication)
    return found


def _evidence_from_current_prescription_line(evidence_text: str) -> bool:
    lower = evidence_text.lower().strip()
    return any(lower.startswith(prefix) for prefix in _MEDICATION_EVIDENCE_PREFIXES)


def _normalize_diagnoses(raw_values: list[str]) -> tuple[list[str], list[str]]:
    normalized = _dedupe(
        [canonical_clinical_phrase(value) for value in raw_values if value.strip()]
    )
    kept, collapsed = collapse_diagnoses_to_most_specific(normalized)
    kept_set = set(kept)
    return [value for value in raw_values if canonical_clinical_phrase(value) in kept_set], collapsed


def _filter_diagnosis_for_seizure_descriptor_header(
    raw_values: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    """Drop diagnosis outputs when the header only lists seizure-type descriptors."""
    if not raw_values:
        return raw_values, []
    if not _diagnosis_header_lists_seizure_descriptors_only(note_text):
        return raw_values, []
    return [], ["benchmark_bridge:diagnosis_seizure_descriptor_header_suppressed"]


def _diagnosis_header_lists_seizure_descriptors_only(note_text: str) -> bool:
    header = _diagnosis_header_text(note_text)
    if not header:
        return False
    if re.search(r"\b(?:epilepsy|juvenile myoclonic epilepsy|juvenile myoclonic)\b", header):
        return False
    if re.search(r"\b(?:tle|temporal lobe epilepsy)\b", header):
        return False
    if re.search(r"\b(?:probably|probable)\s+jme\s+presenting\b", header):
        return False
    if re.search(r"\bjme\b", header) and not re.search(
        r"\b(?:possible|probably|probable)\s+jme\b",
        header,
    ):
        return False
    seizure_markers = (
        "seizure",
        "jerks",
        "tonic",
        "myoclonic",
        "absence",
        "gtcs",
    )
    return any(marker in header for marker in seizure_markers)


def _seizure_type_values_for_record(
    *,
    record: ExectGoldDocument,
    raw_values: list[str],
    evidence_values: list[str],
) -> list[ExtractedValue]:
    expanded: list[tuple[str, str | None, str, list[str]]] = []
    for index, raw_value in enumerate(raw_values):
        evidence_text = _evidence_at(evidence_values, index)
        for normalized, bridge_flags in _benchmark_values(
            "seizure_type",
            raw_value,
            note_text=record.text,
            evidence_text=evidence_text,
        ):
            expanded.append((raw_value, evidence_text, normalized, bridge_flags))

    normalized_labels = _dedupe([item[2] for item in expanded])
    adjusted_labels, jme_flags = _apply_jme_coarse_seizure_policy(
        normalized_labels,
        record.text,
    )
    adjusted_labels, dissociative_flags = _apply_dissociative_epileptic_seizure_policy(
        adjusted_labels,
        record.text,
    )
    adjusted_labels, collapse_flags = _apply_specificity_collapse_seizure_policy(
        adjusted_labels,
        record.text,
    )
    if collapse_flags:
        co_list_flags: list[str] = []
    else:
        adjusted_labels, co_list_flags = _apply_secondary_token_co_list_policy(
            adjusted_labels,
            record.text,
        )
    policy_flags = [*jme_flags, *dissociative_flags, *collapse_flags, *co_list_flags]
    label_to_source = {
        normalized: (raw_value, evidence_text, bridge_flags)
        for raw_value, evidence_text, normalized, bridge_flags in expanded
    }

    values: list[ExtractedValue] = []
    seen: set[str] = set()
    for normalized in adjusted_labels:
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        _raw_value, evidence_text, bridge_flags = _source_for_adjusted_seizure_label(
            normalized,
            label_to_source,
        )
        values.extend(
            _values_for_family(
                record=record,
                field_name="seizure_type",
                raw_values=[_raw_value],
                evidence_values=[evidence_text or ""],
                fixed_normalized=normalized,
                fixed_bridge_flags=bridge_flags,
                extra_quality_flags=[*bridge_flags, *policy_flags],
            )
        )
    return values


def _source_for_adjusted_seizure_label(
    normalized: str,
    label_to_source: dict[str, tuple[str, str | None, list[str]]],
) -> tuple[str, str | None, list[str]]:
    if normalized in label_to_source:
        return label_to_source[normalized]
    for coarse in (
        "generalized tonic clonic seizures",
        "generalized tonic clonic seizure",
    ):
        if coarse not in label_to_source:
            continue
        raw_value, evidence_text, bridge_flags = label_to_source[coarse]
        if normalized == "tonic clonic seizures":
            return "tonic clonic seizures", evidence_text, [
                *bridge_flags,
                "benchmark_bridge:jme_tonic_clonic_surface",
            ]
        if normalized == "generalized tonic seizures":
            return "generalized tonic seizures", evidence_text, [
                *bridge_flags,
                "benchmark_bridge:jme_generalized_tonic_surface",
            ]
    return normalized, None, []


def _apply_jme_coarse_seizure_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    if not labels or not _note_has_jme_context(note_text.lower()):
        return labels, []

    flags: list[str] = []
    adjusted = list(labels)

    preferred = _jme_preferred_coarse_seizure_surface(note_text.lower())
    if preferred is not None:
        remapped: list[str] = []
        for label in adjusted:
            if label in {
                "generalized tonic clonic seizures",
                "generalized tonic clonic seizure",
            }:
                if preferred == "tonic clonic seizures":
                    remapped.append("tonic clonic seizures")
                    flags.append("benchmark_bridge:jme_tonic_clonic_surface")
                    continue
                if preferred == "generalized tonic seizures":
                    remapped.append("generalized tonic seizures")
                    flags.append("benchmark_bridge:jme_generalized_tonic_surface")
                    continue
            remapped.append(label)
        adjusted = _dedupe(remapped)

    if any(label in _JME_COARSE_SEIZURE_LABELS for label in adjusted) and any(
        label in _JME_MYCLONIC_SEIZURE_LABELS for label in adjusted
    ):
        adjusted = [
            label for label in adjusted if label not in _JME_MYCLONIC_SEIZURE_LABELS
        ]
        flags.append("benchmark_bridge:jme_myoclonic_suppressed_for_coarse_label")

    if (
        "generalized tonic clonic seizures" in adjusted
        and "generalized tonic clonic seizure" not in adjusted
        and re.search(r"generali[sz]ed tonic clonic seizure\b", note_text.lower())
    ):
        adjusted.append("generalized tonic clonic seizure")
        flags.append("benchmark_bridge:jme_gtcs_singular_co_listed")

    return _dedupe(adjusted), flags


def _apply_specificity_collapse_seizure_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    note_lower = note_text.lower()
    if not _note_supports_specificity_collapse_diagnosis_co_list(note_lower):
        return labels, []
    if not _SECONDARY_GENERALISED_SEIZURE_NOTE_RE.search(note_lower):
        return labels, []

    return [_SECONDARY_COLLAPSED_SEIZURE_TOKEN], [
        "benchmark_bridge:specificity_collapse_seizure_surface"
    ]


def _apply_secondary_token_co_list_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    if _SECONDARY_COLLAPSED_SEIZURE_TOKEN in labels:
        return labels, []
    if not _SECONDARY_GENERALISED_SEIZURE_NOTE_RE.search(note_text.lower()):
        return labels, []
    if not any(label in _SECONDARY_GENERALISED_SEIZURE_LABELS for label in labels):
        return labels, []

    return [*labels, _SECONDARY_COLLAPSED_SEIZURE_TOKEN], [
        "benchmark_bridge:secondary_token_co_listed"
    ]


def _note_has_jme_context(note_lower: str) -> bool:
    return bool(
        re.search(r"\bjme\b", note_lower)
        or "juvenile myoclonic epilepsy" in note_lower
        or "juvenile myoclonic" in note_lower
    )


def _jme_preferred_coarse_seizure_surface(note_lower: str) -> str | None:
    if re.search(r"generali[sz]ed tonic clonic", note_lower):
        return None
    if re.search(r"generali[sz]ed tonic seizures?\b", note_lower):
        return "generalized tonic seizures"
    if re.search(r"\btonic clonic seizures?\b", note_lower):
        return "tonic clonic seizures"
    return None


def _apply_dissociative_epileptic_seizure_policy(
    labels: list[str],
    note_text: str,
) -> tuple[list[str], list[str]]:
    note_lower = note_text.lower()
    if not _note_has_dissociative_epileptic_seizure_contrast(note_lower):
        return labels, []
    if not _note_supports_epileptic_seizures_conclusion(note_lower):
        return labels, []

    flags: list[str] = []
    adjusted = list(labels)

    if not re.search(r"\bfocal seizures?\b", note_lower):
        without_focal = [
            label
            for label in adjusted
            if label not in _DISSOCIATIVE_EPILEPTIC_FOCAL_SEIZURE_LABELS
        ]
        if len(without_focal) != len(adjusted):
            adjusted = without_focal
            flags.append("benchmark_bridge:dissociative_focal_seizure_suppressed")

    if _EPILEPTIC_SEIZURES_LABEL not in adjusted:
        adjusted.append(_EPILEPTIC_SEIZURES_LABEL)
        flags.append("benchmark_bridge:epileptic_seizures_surface_restored")

    return _dedupe(adjusted), flags


def _note_has_dissociative_epileptic_seizure_contrast(note_lower: str) -> bool:
    if "dissociative" not in note_lower:
        return False
    return bool(
        re.search(r"epileptic\s+or\s+dissociative|dissociative\s+or\s+epileptic", note_lower)
        or re.search(r"non[- ]epileptic", note_lower)
    )


def _note_supports_epileptic_seizures_conclusion(note_lower: str) -> bool:
    return bool(
        re.search(
            r"(?:sound|seem|appear)s?\s+like\s+epileptic\s+seizures?",
            note_lower,
        )
        or re.search(
            r"on\s+balance\s+these\s+(?:do\s+)?(?:sound|are)\s+like\s+epileptic",
            note_lower,
        )
        or re.search(
            r"(?:think|believe)\s+(?:these|this|they)\s+(?:are|represent)\s+epileptic\s+seizures?",
            note_lower,
        )
    )


def _values_for_family(
    *,
    record: ExectGoldDocument,
    field_name: str,
    raw_values: list[str],
    evidence_values: list[str],
    collapsed_values: list[str] | None = None,
    augmented_values: set[str] | None = None,
    specificity_collapse_augmented: set[str] | None = None,
    extra_quality_flags: list[str] | None = None,
    fixed_normalized: str | None = None,
    fixed_bridge_flags: list[str] | None = None,
) -> list[ExtractedValue]:
    values: list[ExtractedValue] = []
    seen: set[str] = set()
    collapsed_values = collapsed_values or []
    augmented_values = augmented_values or set()
    specificity_collapse_augmented = specificity_collapse_augmented or set()
    extra_quality_flags = extra_quality_flags or []

    for index, raw_value in enumerate(raw_values):
        evidence_text = _evidence_at(evidence_values, index)
        if field_name == "annotated_medication":
            if _medication_evidence_excluded(evidence_text):
                continue
            evidence_text = _repair_medication_evidence_quote(record, evidence_text)
        benchmark_pairs: list[tuple[str, list[str]]]
        if fixed_normalized is not None:
            benchmark_pairs = [(fixed_normalized, list(fixed_bridge_flags or []))]
        else:
            benchmark_pairs = list(
                _benchmark_values(
                    field_name,
                    raw_value,
                    note_text=record.text,
                    evidence_text=evidence_text,
                )
            )
        for normalized, bridge_flags in benchmark_pairs:
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            evidence_spans, evidence_flags = _evidence_spans(record, evidence_text)
            quality_flags = _quality_flags(
                field_name=field_name,
                normalized_value=normalized,
                collapsed_values=collapsed_values,
                evidence_text=evidence_text,
            )
            co_list_flags: list[str] = []
            if field_name == "diagnosis" and normalized in augmented_values:
                co_list_flags.append("benchmark_bridge:diagnosis_co_list_augmented")
            if field_name == "diagnosis" and normalized in specificity_collapse_augmented:
                co_list_flags.append(
                    "benchmark_bridge:specificity_collapse_diagnosis_co_listed"
                )
            if field_name == "annotated_medication" and normalized in augmented_values:
                co_list_flags.append(
                    "benchmark_bridge:current_prescription_medication_augmented"
                )
            values.append(
                ExtractedValue(
                    field_name=field_name,
                    raw_value=raw_value,
                    normalized_value=normalized,
                    evidence=evidence_spans,
                    temporality="not_applicable",
                    negation="affirmed",
                    confidence=None,
                    quality_flags=[
                        *quality_flags,
                        *bridge_flags,
                        *co_list_flags,
                        *extra_quality_flags,
                        *evidence_flags,
                    ],
                )
            )
    return values


def _benchmark_values(
    field_name: str,
    value: str,
    *,
    note_text: str = "",
    evidence_text: str | None = None,
) -> list[tuple[str, list[str]]]:
    normalized = _normalize_value(field_name, value)
    bridge_flags: list[str] = []

    if field_name == "diagnosis":
        normalized, bridge_flags = _normalize_diagnosis_surface(normalized)
        if not normalized:
            return []
        if normalized not in ALLOWED_DIAGNOSIS_LABELS:
            return []
    elif field_name == "seizure_type":
        normalized, surface_flags = _normalize_seizure_type_surface(
            normalized,
            note_text=note_text,
        )
        bridge_flags.extend(surface_flags)
        coarsened = _coarsen_granular_seizure_type(normalized)
        if coarsened is not None:
            return coarsened
        split_values = _split_fused_seizure_type(normalized)
        if split_values is not None:
            return [
                (
                    split_value,
                    [*bridge_flags, "benchmark_bridge:fused_seizure_type_split"],
                )
                for split_value in split_values
            ]
    elif field_name == "annotated_medication":
        normalized, med_flags = _normalize_annotated_medication_surface(
            normalized,
            note_text=note_text,
            evidence_text=evidence_text,
        )
        if not normalized:
            return []
        bridge_flags.extend(med_flags)

    return [(normalized, bridge_flags)]


def _normalize_diagnosis_surface(normalized: str) -> tuple[str, list[str]]:
    flags: list[str] = []
    for prefix in ("probable ", "possible "):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].strip()
            flags.append("benchmark_bridge:diagnosis_uncertainty_stripped")
            break
    if normalized in {"epilepsy unclassified", "unclassified epilepsy"}:
        return "epilepsy", [*flags, "benchmark_bridge:unclassified_epilepsy_surface"]
    if normalized == "symptomatic structural epilepsy":
        return "symptomatic structural focal epilepsy", [
            *flags,
            "benchmark_bridge:symptomatic_structural_focal_restored",
        ]
    if normalized == "epilepsy with generalized tonic clonic seizures from sleep":
        return _ON_AWAKENING_SYNDROME_DIAGNOSIS, [
            *flags,
            "benchmark_bridge:on_awakening_diagnosis_surface",
        ]
    return normalized, flags


def _normalize_seizure_type_surface(
    normalized: str,
    *,
    note_text: str = "",
) -> tuple[str, list[str]]:
    if normalized in {
        "focal onset convulsive seizure",
        "focal onset convulsive seizures",
    }:
        bilateral = (
            "focal to bilateral convulsive seizures"
            if normalized.endswith("seizures")
            else "focal to bilateral convulsive seizure"
        )
        return bilateral, ["benchmark_bridge:focal_onset_to_bilateral_surface"]
    if normalized in {"focal to bilateral seizures", "focal to bilateral seizure"}:
        convulsive = (
            "focal to bilateral convulsive seizures"
            if normalized.endswith("seizures")
            else "focal to bilateral convulsive seizure"
        )
        return convulsive, ["benchmark_bridge:seizure_type_convulsive_modifier"]
    if normalized == "generalized tonic clonic seizures from sleep":
        return "generalized tonic clonic seizures", [
            "benchmark_bridge:seizure_temporal_modifier_stripped"
        ]
    return normalized, []


def _coarsen_granular_seizure_type(
    normalized: str,
) -> list[tuple[str, list[str]]] | None:
    if normalized in _REJECTED_GRANULAR_SEIZURE_TYPES:
        return []
    coarsened = _GRANULAR_SEIZURE_TYPE_COARSENING.get(normalized)
    if coarsened is not None:
        return [
            (
                coarsened,
                ["benchmark_bridge:granular_seizure_surface_coarsened"],
            )
        ]
    return None


def _normalize_annotated_medication_surface(
    normalized: str,
    *,
    note_text: str = "",
    evidence_text: str | None = None,
) -> tuple[str, list[str]]:
    flags: list[str] = []
    repaired = _MEDICATION_SURFACE_REPAIRS.get(normalized)
    if repaired is not None:
        normalized = repaired
        flags.append("benchmark_bridge:medication_surface_repaired")
    brand_surface, brand_flags = _medication_brand_surface_from_note(
        normalized,
        note_text=note_text,
        evidence_text=evidence_text,
    )
    if brand_surface is not None:
        normalized = brand_surface
        flags.extend(brand_flags)
    if normalized in _REJECTED_ANNOTATED_MEDICATIONS:
        return "", [*flags, "benchmark_bridge:non_asm_medication_rejected"]
    return normalized, flags


def _medication_brand_surface_from_note(
    normalized: str,
    *,
    note_text: str,
    evidence_text: str | None,
) -> tuple[str | None, list[str]]:
    if not note_text:
        return None, []
    note_lower = note_text.lower()
    search_text = " ".join(
        part
        for part in (note_lower, (evidence_text or "").lower())
        if part
    )
    for generic, brand_marker, brand_surface in _MEDICATION_BRAND_NOTE_SURFACES:
        if normalized != generic:
            continue
        if brand_marker in search_text:
            return brand_surface, ["benchmark_bridge:medication_brand_surface_preserved"]
    return None, []


def _repair_medication_evidence_quote(
    record: ExectGoldDocument,
    evidence_text: str | None,
) -> str | None:
    if not evidence_text:
        return None
    if evidence_text in record.text:
        return evidence_text

    stripped = _strip_medication_evidence_prefix(evidence_text)
    if stripped and stripped in record.text:
        return stripped

    normalized = evidence_text.replace("\t", " ")
    if normalized in record.text:
        return normalized

    collapsed = re.sub(r"\s+", " ", evidence_text).strip()
    if collapsed in record.text:
        return collapsed

    ellipsis_span = _repair_ellipsis_evidence_span(record, evidence_text)
    if ellipsis_span is not None:
        return ellipsis_span.text

    note_lower = record.text.lower()
    for fragment in _medication_evidence_fragments(evidence_text):
        start = note_lower.find(fragment)
        if start == -1:
            continue
        return record.text[start : start + len(fragment)]

    return evidence_text


def _strip_medication_evidence_prefix(evidence_text: str) -> str:
    lower = evidence_text.lower().strip()
    for prefix in _MEDICATION_EVIDENCE_PREFIXES:
        if lower.startswith(prefix):
            return evidence_text[len(prefix) :].strip()
    return evidence_text


def _medication_evidence_fragments(evidence_text: str) -> list[str]:
    fragments: list[str] = []
    for token in re.split(r"[^a-zA-Z0-9]+", evidence_text):
        token = token.strip().lower()
        if len(token) >= 8:
            fragments.append(token)
    return sorted(fragments, key=len, reverse=True)


def _verified_seizure_allowed(normalized: str, initial_keys: set[str]) -> bool:
    if normalized in initial_keys:
        return True
    for initial_key in initial_keys:
        coarsened = _coarsen_granular_seizure_type(initial_key)
        if coarsened and any(value for value, _ in coarsened) == normalized:
            return True
    return False


def _medication_evidence_excluded(evidence_text: str | None) -> bool:
    if not evidence_text:
        return False
    lower = evidence_text.lower()
    if _evidence_from_current_prescription_line(lower):
        return any(
            phrase in lower
            for phrase in _MEDICATION_PLANNED_OR_HISTORICAL_EVIDENCE_PHRASES
        )
    return any(phrase in lower for phrase in _MEDICATION_EVIDENCE_EXCLUSION_PHRASES)


def _split_fused_seizure_type(normalized: str) -> list[str] | None:
    if normalized in {
        "temporal lobe onset focal seizures",
        "temporal lobe focal seizures",
        "temporal onset focal seizures",
        "temporal lobe seizures",
    }:
        return ["temporal lobe seizure", "focal seizures"]
    if normalized in {
        "focal seizures with secondary generalisation",
        "focal seizures with secondary generalization",
    }:
        return [
            "focal seizures",
            "secondary generalisation",
            "generalized tonic clonic seizure",
        ]
    return None


def _normalize_value(field_name: str, value: str) -> str:
    if field_name == "annotated_medication":
        return canonical_medication_name(value)
    return canonical_clinical_phrase(value)


def _quality_flags(
    *,
    field_name: str,
    normalized_value: str,
    collapsed_values: list[str],
    evidence_text: str | None,
) -> list[str]:
    flags: list[str] = []
    if field_name == "diagnosis" and normalized_value not in ALLOWED_DIAGNOSIS_LABELS:
        flags.append("unsupported_label")
    if field_name == "diagnosis" and collapsed_values:
        flags.append("specificity_collapsed")
    if not evidence_text:
        flags.append("missing_evidence")
    return flags


def _evidence_at(evidence_values: list[str], index: int) -> str | None:
    if index >= len(evidence_values):
        return None
    evidence = evidence_values[index].strip()
    return evidence or None


def _evidence_spans(
    record: ExectGoldDocument,
    evidence_text: str | None,
) -> tuple[list[EvidenceSpan], list[str]]:
    if not evidence_text:
        return [], []
    start = record.text.find(evidence_text)
    if start != -1:
        return [
            EvidenceSpan(
                text=evidence_text,
                start=start,
                end=start + len(evidence_text),
                document_id=record.document_id,
            )
        ], []

    repaired_span = _repair_ellipsis_evidence_span(record, evidence_text)
    if repaired_span is not None:
        return [repaired_span], ["evidence_repair:ellipsis_contiguous_span"]

    return [EvidenceSpan(text=evidence_text, document_id=record.document_id)], []


def _repair_ellipsis_evidence_span(
    record: ExectGoldDocument,
    evidence_text: str,
) -> EvidenceSpan | None:
    if "..." not in evidence_text:
        return None

    fragments = [fragment.strip() for fragment in evidence_text.split("...") if fragment.strip()]
    if len(fragments) < 2:
        return None

    search_from = 0
    first_start: int | None = None
    last_end: int | None = None
    for fragment in fragments:
        start = record.text.find(fragment, search_from)
        if start == -1:
            return None
        if first_start is None:
            first_start = start
        last_end = start + len(fragment)
        search_from = last_end

    if first_start is None or last_end is None:
        return None

    repaired_text = record.text[first_start:last_end]
    if len(repaired_text) > 300 or "\n\n" in repaired_text:
        return None

    return EvidenceSpan(
        text=repaired_text,
        start=first_start,
        end=last_end,
        document_id=record.document_id,
    )


def _as_list(value: Optional[object]) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [] if stripped.lower() in {"", "none", "null"} else [stripped]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def exect_s0_s1_run_metadata(
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    *,
    prompt_version: str = EXECT_S0_S1_PROMPT_VERSION,
    program_variant: str = EXECT_S0_S1_VARIANT,
    extra: dict | None = None,
) -> RunMetadata:
    """Build run metadata for an ExECT S0/S1 field-family run."""
    return RunMetadata(
        run_id=run_id,
        dataset=EXECT_DATASET,
        split_name=split_name,
        model_provider=model_provider,
        model_name=model_name,
        schema_level=EXECT_S0_S1_SCHEMA_LEVEL,
        program_variant=program_variant,
        scorer_mode=EXECT_S0_S1_SCORER,
        metric_caveats=[
            "These are partial ExECT S0/S1 diagnostics, not published ExECTv2 benchmark reproduction.",
            "Benchmark-facing fields are limited to diagnosis, seizure type, and annotated medications.",
            "Medication temporality is intentionally not benchmark-facing in this baseline.",
            "Evidence quote support is diagnostic and should be reported separately from label metrics.",
        ],
        metadata={
            "prompt_version": prompt_version,
            **(extra or {}),
        },
    )
