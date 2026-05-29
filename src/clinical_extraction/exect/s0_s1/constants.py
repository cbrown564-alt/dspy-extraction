"""ExECT S0/S1 constants and benchmark-policy text."""
from __future__ import annotations

import re

EXECT_DATASET = "exect_v2"
EXECT_S0_S1_SCHEMA_LEVEL = "exect_s0_s1_field_family"
EXECT_S0_S1_VARIANT = "exect_s0_s1_field_family_single_pass"
EXECT_S0_S1_PRE_VOCAB_VARIANT = "exect_s0_s1_field_family_pre_vocab_single_pass"
EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT = (
    "exect_s0_s1_field_family_medication_pre_vocab_single_pass"
)
EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT = (
    "exect_s0_s1_field_family_seizure_pre_vocab_single_pass"
)
EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT = "exect_s1_clean_ladder_v1_single_pass"
EXECT_S0_S1_CLEAN_LADDER_V1_FAMILY_SPAN_VARIANT = (
    "exect_s1_clean_ladder_v1_family_span_single_pass"
)
EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT = (
    "exect_s1_clean_ladder_v2_diagnosis_stable_ensemble"
)
EXECT_S0_S1_MEDICATION_ONLY_E13_VARIANT = (
    "exect_s1_medication_only_e13_single_pass"
)
EXECT_S0_S1_MEDICATION_LIFECYCLE_CONTEXT_E13_VARIANT = (
    "exect_s1_medication_lifecycle_context_e13_single_pass"
)
EXECT_S0_S1_SECTION_AWARE_VARIANT = "exect_s0_s1_field_family_section_aware"
EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT = (
    "exect_s0_s1_field_family_prompt_graph_parallel"
)
EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT = (
    "exect_s0_s1_field_family_prompt_graph_sequential"
)
EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT = "exect_s0_s1_field_family_deterministic_only"
REPAIR_POLICY_ARTIFACT_BENCHMARK_BRIDGE_ONLY = "artifact_benchmark_bridge_only"
REPAIR_POLICY_RAW_NO_BENCHMARK_BRIDGES = "raw_no_benchmark_bridges"
EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT = "exect_s0_s1_field_family_diagnosis_recall"
EXECT_S0_S1_VERIFY_REPAIR_VARIANT = "exect_s0_s1_field_family_verify_repair"
EXECT_S0_S1_STAGE_GRAPH_BY_VARIANT = {
    EXECT_S0_S1_VERIFY_REPAIR_VARIANT: "g2_extract_verify",
    EXECT_S0_S1_SECTION_AWARE_VARIANT: "g3_family_split_merge",
    EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT: "g2_field_family_parallel",
    EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT: "g2_field_family_prompt_graph",
    EXECT_S0_S1_MEDICATION_ONLY_E13_VARIANT: "medication_payload_routing_v1",
    EXECT_S0_S1_MEDICATION_LIFECYCLE_CONTEXT_E13_VARIANT: (
        "medication_payload_routing_v1"
    ),
}
EXECT_S0_S1_ACTIVE_VARIANTS = frozenset(
    {
        EXECT_S0_S1_VARIANT,
        EXECT_S0_S1_CLEAN_LADDER_V1_VARIANT,
        EXECT_S0_S1_CLEAN_LADDER_V1_FAMILY_SPAN_VARIANT,
        EXECT_S0_S1_CLEAN_LADDER_V2_DIAGNOSIS_STABLE_VARIANT,
        EXECT_S0_S1_MEDICATION_ONLY_E13_VARIANT,
        EXECT_S0_S1_MEDICATION_LIFECYCLE_CONTEXT_E13_VARIANT,
    }
)
EXECT_S0_S1_ARCHIVE_VARIANTS = frozenset(
    {
        EXECT_S0_S1_PRE_VOCAB_VARIANT,
        EXECT_S0_S1_MEDICATION_PRE_VOCAB_VARIANT,
        EXECT_S0_S1_SEIZURE_PRE_VOCAB_VARIANT,
        EXECT_S0_S1_SECTION_AWARE_VARIANT,
        EXECT_S0_S1_PROMPT_GRAPH_PARALLEL_VARIANT,
        EXECT_S0_S1_PROMPT_GRAPH_SEQUENTIAL_VARIANT,
        EXECT_S0_S1_DETERMINISTIC_ONLY_VARIANT,
        EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
        EXECT_S0_S1_VERIFY_REPAIR_VARIANT,
    }
)
EXECT_S0_S1_L0_PROMPT_VERSION = "exect_s0_s1_field_family_l0_minimal"
EXECT_S0_S1_L1_SCHEMA_PROMPT_VERSION = "exect_s0_s1_field_family_l1_schema"
EXECT_S0_S1_D1_PROMPT_VERSION = "exect_s0_s1_field_family_d1_feasibility"
EXECT_S0_S1_SCORER = "exect_field_family_deterministic_v1"
EXECT_S0_S1_PROMPT_VERSION = "exect_s0_s1_field_family_v4_10_label_policy"
EXECT_S0_S1_V4_12_PROMPT_VERSION = "exect_s0_s1_field_family_v4_12_label_policy"
EXECT_S0_S1_V4_11_PROMPT_VERSION = "exect_s0_s1_field_family_v4_11_label_policy"
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
EXECT_S0_S1_V4_10_EVIDENCE_STRICT_PROMPT_VERSION = (
    "exect_s0_s1_field_family_v4_10_evidence_strict_v1"
)
EXECT_S0_S1_V4_10_EVIDENCE_SOFT_PROMPT_VERSION = (
    "exect_s0_s1_field_family_v4_10_evidence_soft_v1"
)
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
EXECT_S0_S1_V4_11_LABEL_POLICY_ADDENDUM = (
    "When the diagnosis or seizure-type row uses a plural audited benchmark surface "
    "(for example generalized tonic clonic seizures or focal seizures), emit that plural "
    "benchmark label; do not singularize to generalized tonic clonic seizure or focal seizure "
    "when the audited scorer expects the plural form.",
    "Do not emit absence seizure, absence seizures, myoclonic seizure, or myoclonic seizures "
    "unless the note explicitly names that seizure type as a current type in the diagnosis "
    "or seizure-type surface; do not infer absence or myoclonic types from EEG narrative, "
    "jerk wording, or diagnosis alone when the audited gold has no such seizure types.",
    "When the note supports a full secondary-generalised benchmark phrase (for example secondary "
    "generalisation, secondary generalized seizures, or secondarily generalized seizures), use "
    "that audited surface; do not emit bare secondary alone unless specificity-collapse rules "
    "require only secondary.",
    "Do not add a separate secondary generalised tonic-clonic seizure type unless the letter "
    "names multiple distinct current seizure types; secondary generalisation is not an extra "
    "seizure type when only one audited seizure surface applies.",
)
EXECT_S0_S1_V4_12_LABEL_POLICY_ADDENDUM = (
    "Apply the v4.11 seizure-type rules only inside seizure_type; do not let plural, "
    "absence/myoclonic, or secondary-generalisation examples change diagnosis labels.",
    "For diagnosis, keep the v4.10 audited epilepsy-diagnosis policy: do not replace a "
    "generic epilepsy gold surface with focal epilepsy, focal onset epilepsy, or temporal "
    "lobe epilepsy unless the diagnosis or impression line explicitly names that epilepsy "
    "diagnosis surface.",
    "Do not emit symptomatic structural focal epilepsy from MRI lesions, amygdala signal, "
    "surgery history, or cause narrative alone; use that diagnosis only when the audited "
    "diagnosis/impression surface itself names symptomatic or structural focal epilepsy.",
    "When the diagnosis header states focal onset epilepsy, keep focal onset epilepsy as a "
    "diagnosis; do not drop it because seizure-type rules also mention focal seizures.",
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
EXECT_S0_S1_V4_11_POLICY_EXAMPLES = (
    {
        "case": "plural_gtcs_from_diagnosis_row",
        "note_fragment": (
            "Diagnosis: generalized tonic clonic seizures. Seizure type and frequency: "
            "generalized tonic clonic seizures."
        ),
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": (
            "Use the plural audited GTCS surface when the diagnosis or seizure row uses "
            "generalized tonic clonic seizures."
        ),
    },
    {
        "case": "plural_focal_to_bilateral_convulsive",
        "note_fragment": "Seizure type: focal to bilateral convulsive seizures.",
        "benchmark_output": {"seizure_type": ["focal to bilateral convulsive seizures"]},
        "policy": (
            "Preserve the plural focal to bilateral convulsive seizures surface when "
            "that is the audited benchmark label."
        ),
    },
    {
        "case": "no_seizure_types_without_absence_myoclonic_overcall",
        "note_fragment": (
            "Diagnosis: focal epilepsy. EEG shows occasional spike-wave activity. "
            "No seizure type documented."
        ),
        "benchmark_output": {"seizure_type": []},
        "policy": (
            "Do not invent absence or myoclonic seizure types from EEG narrative when "
            "no current seizure type is named."
        ),
    },
    {
        "case": "gtcs_only_no_absence_co_list",
        "note_fragment": (
            "Diagnosis: generalized tonic clonic seizures. Seizure type: "
            "generalized tonic clonic seizures."
        ),
        "benchmark_output": {"seizure_type": ["generalized tonic clonic seizures"]},
        "policy": (
            "Do not add absence seizures when the audited surface is GTCS-only on the "
            "diagnosis and seizure rows."
        ),
    },
    {
        "case": "secondary_generalisation_full_phrase",
        "note_fragment": (
            "Seizure type: complex partial seizures with secondary generalisation."
        ),
        "benchmark_output": {
            "seizure_type": [
                "complex partial seizures",
                "secondary generalisation",
            ]
        },
        "policy": (
            "Emit secondary generalisation as its own audited label when the note names "
            "secondary generalisation; do not collapse to bare secondary alone."
        ),
    },
    {
        "case": "secondary_generalized_seizures_not_bare_secondary",
        "note_fragment": (
            "She has focal seizures that secondarily generalize. Seizure type: "
            "secondary generalized seizures."
        ),
        "benchmark_output": {
            "seizure_type": ["focal seizures", "secondary generalized seizures"]
        },
        "policy": (
            "Use the full secondary generalized seizures phrase when that is the audited "
            "surface; do not emit secondary alone."
        ),
    },
    {
        "case": "multi_type_secondary_generalized_co_list",
        "note_fragment": (
            "Seizure type: complex partial seizures, secondary generalized seizures."
        ),
        "benchmark_output": {
            "seizure_type": [
                "complex partial seizures",
                "secondary generalized seizures",
            ]
        },
        "policy": (
            "Co-list multiple audited current seizure types including secondary "
            "generalized seizures when the note names each."
        ),
    },
)
EXECT_S0_S1_V4_12_POLICY_EXAMPLES = (
    {
        "case": "diagnosis_generic_epilepsy_not_focal_from_seizure_context",
        "note_fragment": (
            "Diagnosis: epilepsy. Seizure type: focal to bilateral convulsive seizure."
        ),
        "benchmark_output": {
            "diagnosis": ["epilepsy"],
            "seizure_type": ["focal to bilateral convulsive seizure"],
        },
        "policy": (
            "Do not upgrade generic epilepsy to focal epilepsy from seizure-type wording; "
            "keep the audited diagnosis surface separate from seizure_type."
        ),
    },
    {
        "case": "diagnosis_no_structural_overcall_from_mri_context",
        "note_fragment": (
            "She was diagnosed with epilepsy at the age of 22. MRI showed a small "
            "hyperintensity in the right amygdala."
        ),
        "benchmark_output": {"diagnosis": ["epilepsy"]},
        "policy": (
            "Do not emit symptomatic structural focal epilepsy from structural imaging "
            "context alone when the diagnosis surface is generic epilepsy."
        ),
    },
    {
        "case": "diagnosis_focal_onset_recall_kept",
        "note_fragment": (
            "Diagnosis: focal onset epilepsy. Seizure type: epileptic seizures."
        ),
        "benchmark_output": {
            "diagnosis": ["focal onset epilepsy"],
            "seizure_type": ["epileptic seizures"],
        },
        "policy": (
            "Keep focal onset epilepsy when the diagnosis header names it; seizure-type "
            "routing rules must not suppress diagnosis recall."
        ),
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

_PRE_VOCAB_SEIZURE_TYPE_SURFACES = (
    "epileptic seizures",
    "focal seizure",
    "focal seizures",
    "focal seizures with altered awareness",
    "focal to bilateral convulsive seizure",
    "focal to bilateral convulsive seizures",
    "generalized seizures",
    "generalized tonic clonic seizure",
    "generalized tonic clonic seizures",
    "generalized tonic seizures",
    "myoclonic seizures",
    "occipital lobe seizures",
    "secondary",
    "secondary generalisation",
    "secondary generalized",
    "temporal lobe seizure",
    "temporal lobe seizures",
    "tonic clonic seizures",
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


__all__ = [
    name
    for name in globals()
    if not name.startswith("__") and name not in {"re", "annotations"}
]


