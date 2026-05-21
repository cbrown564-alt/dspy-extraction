# Outline

## Goal

We want to build a hybrid deterministic + LLM clinical extraction system, with DSPy orchestrating the pipeline and optimizing prompts/modules, and a local Qwen3.6:35b model doing the hard semantic extraction.

The high level objectives are:

1. Beat the benchmarks set by ExECTv2 (broad epilepsy schema) and Gan (precise epilepsy frequency) - refer to their papers in data/ to extract the benchmark results
2. Build a modular system that can specialise in these two very different tasks, and then test how easily it can adapted to distinct downstream use cases: clinical support, billing extraction, research cohort selection or outcome variable construction
3. Conduct comprehensive ablation studies to measure the effects of different components (few-shot prompting, verification, section splitting, evidence capture) and how they interact with different tasks (schema complexity, downstream use cases)
4. Identify the best mix of deterministic + LLM components (e.g. normalisation, schema construction)
5. Assess whether the latest local models (Qwen3.6:35b) can perform the most complex tasks (ideal for hospitals on local servers with sensitive data) or whether there are some tasks that require the largest closed modesl (e.g. GPT 5.5).

## Models

The primary model to be used in this research will be [Qwen3.6:35b](https://ollama.com/library/qwen3.6:35b) and it will be tested on a Windows laptop with an Nvidia GPU. 

Early stage experiments will be conducted on this mac with GPT 4.1-mini to enable rapid iteration at low cost.

The repo needs to be setup to handle both closed and open models across mac and windows.

The full model list is:

Local:

Qwen3.6:35b
Qwen3.5:9b 

Closed:

Gemini 3 Flash
GPT 5.5
GPT 4.1-mini

## Dataset

We have two core data sources in /data. 

- ExECTv2 (2025): a rich hierarchical schema capturing diagnosis, treatment, patient history and more. Certain fields also include certainty indicators and timestamps. 200 synthetic clinical letters.
- Gan (2026): a more straightforward data schema focused on seizure frequency. 1,500 synthetic clinical letters.

The related research papers for both data sources are in the folder which outline the annotation guidelines for the ExECTv2 data schema, the normalisation guidelines for the Gan data schema, and more.

A key focus of this research is to identify how effectively the modular system can be adapted to specialise in two very different tasks. 

The ExECTv2 task is difficult because it creates a wide, hierarchical data schema across a broad range of concepts. It requires the model to different between current vs. historical medication, effectively handle negation and contradictions, etc. In certain cases it also includes confidence scores representing the complex clinical judgment of experts.

The Gan task is difficult because it requires the model to perform complex temporal logic, parsing statements like "seizure free since changing to the latest medication, 4 seizures in the 6 weeks prior". It also requires the model to provide evidence to justify the selection.

The data/splits folder already contains a suggested train/dev/test set for the ExECTv2 data. We need that for Gan too.

Considerable effort needs to be put into understanding the data structure of the gold label schemas, loading and representing them accurately. There is a sufficient complexity here to misinterpret the data structure. Look at docs/datasets/exect/exect_gold_label_audit.md and docs/datasets/gan/gan_2026_label_audit.md for data audits from a previous project.

## Architecture

I would divide your experiment system into four layers.

Layer 1: fixed infrastructure

- note loading
- train/dev/test split
- schema definitions
- deterministic validators
- canonical gold-label scorer
- run tracking
- error analysis

Layer 2: DSPy modules

- context selection
- extraction
- evidence selection
- verifier/adjudicator
- repair/abstention

Layer 3: optimizable configurations

- signatures
- module composition
- few-shot examples
- prompt instructions
- context policy
- verifier policy

Layer 4: experiment orchestration

- ablations
- model comparison
- field-specific metrics
- bootstrap confidence intervals
- failure taxonomy

You could have signatures like:

```python 
class SelectRelevantContext(dspy.Signature):
    """Select note spans relevant to a target extraction field."""
    note: str = dspy.InputField()
    target_field: str = dspy.InputField()
    context_spans: list[dict] = dspy.OutputField()


class ExtractFieldGroup(dspy.Signature):
    """Extract a group of clinically related fields with evidence."""
    context: str = dspy.InputField()
    schema: dict = dspy.InputField()
    field_group: str = dspy.InputField()
    extraction: dict = dspy.OutputField()


class VerifyEvidence(dspy.Signature):
    """Check whether each extracted value is directly supported by its evidence span."""
    note: str = dspy.InputField()
    extraction: dict = dspy.InputField()
    verification: dict = dspy.OutputField()


class RepairExtraction(dspy.Signature):
    """Repair extraction errors using validation and evidence-verification feedback."""
    note: str = dspy.InputField()
    extraction: dict = dspy.InputField()
    errors: list[dict] = dspy.InputField()
    repaired_extraction: dict = dspy.OutputField()
```

A practical structure for the clinical extraction project could be:

clinical-extraction-dspy/
├── README.md
├── pyproject.toml
├── .env.example
├── configs/
│   ├── models/
│   │   ├── qwen_35b_local.yaml
│   │   ├── qwen_9b_local.yaml
│   │   ├── gemini3_flash.yaml
│   │   ├── claude_sonnet4.6.yaml
│   │   ├── gpt5.5.yaml
│   │   └── gpt4.1_mini.yaml
│   ├── experiments/
│   │   ├── baseline_current_pipeline.yaml
│   │   ├── dspy_monolithic_full_schema.yaml
│   │   ├── dspy_field_group_extraction.yaml
│   │   ├── dspy_context_extractor_verifier.yaml
│   │   └── ablation_no_evidence_requirement.yaml
│   └── schemas/
│       ├── epilepsy_core.schema.json
│       ├── epilepsy_full.schema.json
│       ├── gan_frequency.schema.json
│       └── field_groups.yaml
│
├── data/
│   ├── raw/
│   │   └── README.md
│   ├── processed/
│   │   ├── train.jsonl
│   │   ├── dev.jsonl
│   │   └── test.jsonl
│   ├── gold/
│   │   ├── annotations.json
│   │   └── normalized_gold.jsonl
│   └── examples/
│       ├── fewshot_candidates.jsonl
│       └── adversarial_cases.jsonl
│
├── src/
│   └── clinical_extraction/
│       ├── __init__.py
│       ├── settings.py
│       ├── llms.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── epilepsy.py
│       │   ├── medication.py
│       │   ├── seizure.py
│       │   └── evidence.py
│       │
│       ├── dspy_programs/
│       │   ├── __init__.py
│       │   ├── signatures.py
│       │   ├── modules.py
│       │   ├── monolithic.py
│       │   ├── field_group.py
│       │   ├── context_then_extract.py
│       │   ├── extract_verify_repair.py
│       │   └── compiled/
│       │       └── README.md
│       │
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── preprocess.py
│       │   ├── sectioning.py
│       │   ├── context_selection.py
│       │   ├── normalization.py
│       │   ├── validation.py
│       │   ├── repair.py
│       │   └── postprocess.py
│       │
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── metrics.py
│       │   ├── field_scorers.py
│       │   ├── evidence_scoring.py
│       │   ├── error_analysis.py
│       │   └── reports.py
│       │
│       ├── experiments/
│       │   ├── __init__.py
│       │   ├── run_experiment.py
│       │   ├── compile_program.py
│       │   ├── evaluate_program.py
│       │   ├── compare_runs.py
│       │   └── ablations.py
│       │
│       └── utils/
│           ├── io.py
│           ├── logging.py
│           ├── hashing.py
│           └── reproducibility.py
│
├── scripts/
│   ├── prepare_data.py
│   ├── compile_dspy_program.py
│   ├── run_experiment.py
│   ├── evaluate_predictions.py
│   ├── compare_experiments.py
│   └── export_errors_for_review.py
│
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_error_analysis.ipynb
│   └── 03_schema_breadth_analysis.ipynb
│
├── runs/
│   ├── README.md
│   └── .gitkeep
│
├── artifacts/
│   ├── compiled_programs/
│   ├── predictions/
│   ├── evaluation_reports/
│   ├── error_samples/
│   └── prompts/
│
└── tests/
    ├── test_schema_validation.py
    ├── test_normalization.py
    ├── test_evidence_scoring.py
    ├── test_metrics.py
    └── test_pipeline_contracts.py

## Experiment loop

For each experiment, define a program variant rather than a prompt variant.

A. Monolithic extraction
note → full schema JSON

B. Section-aware extraction
sections → field groups → merged schema

C. Field-family extraction
diagnosis module
seizure module
medication module
investigation module
history module

D. Extract then verify
extractor → evidence verifier → repair/abstain

E. Context-injected extraction
retrieved relevant snippets → field extractor → verifier

F. Minimal schema first, expansion second
core fields → conditional detail fields

Then every variant gets evaluated through the same scorer:

field-level F1
document-level F1
evidence support accuracy
negation accuracy
temporality accuracy
normalization accuracy
schema-validity rate
repair rate
abstention rate
latency
tokens / local inference time

##  Pipeline

Clinical notes
   ↓
De-identification / PHI guardrails
   ↓
Document segmentation
   ↓
Section classification
   ↓
Entity + event extraction
   ↓
Normalization
   ↓
Negation / temporality / experiencer detection
   ↓
Evidence span capture
   ↓
Schema validation
   ↓
Human review queue for low-confidence items
   ↓
Structured outputs: JSON / FHIR / OMOP / CSV

We could experiment with variants like:

Variant A:
single-pass extraction → validator
Variant B:
section extraction → field-specific extraction → verifier
Variant C:
candidate extraction → evidence verifier → repair module
Variant D:
small model extraction → larger model adjudication

## Ablations

DSPy is especially attractive when you want to run proper ablations:

Does few-shot prompting help each field equally?
Does a verifier improve precision but reduce recall?
Does splitting by section improve onset/aetiology extraction?
Is normalisation more effective and reliable in an LLM call or a deterministic harness?
Is there significant performance variance across model variants?
Does overall performance decline as schema complexity increases?
Does evidence extraction first improve precision?
Is performance sensitive to the kind of clinical guidelines presented (e.g. ExECTv2 annotation guidelines, ILAE 2022, etc.)
Does a multi-step pipeline improve performance or just create new failure modes?
Do explicit temporality guidelines help the models differentiate between planned and current use?
Do larger reasoning models benefit from looser instructions?

## Schema

The key is not to ask the LLM to “summarize the note.” Instead, define a strict clinical schema and force every field to include:

{
  "field": "seizure_frequency",
  "value": "2 per month",
  "normalized_value": {
    "count": 2,
    "period": "month"
  },
  "status": "present",
  "temporality": "current",
  "evidence": "She reports two focal impaired awareness seizures per month.",
  "confidence": 0.86
}

For epilepsy, the schema could include:

diagnosis
epilepsy_type
seizure_type
seizure_frequency
last_seizure_date
age_at_onset
aetiology
anti_seizure_medications
previous_medications
EEG_findings
MRI_findings
comorbidities
driving_status
pregnancy_status
rescue_medication
adverse_effects

Treat schema breadth as an experimental parameter. I would explicitly define schema levels:

Schema S0:
core diagnostic fields only

Schema S1:
diagnosis + seizure + medication

Schema S2:
S1 + investigations + comorbidities

Schema S3:
S2 + birth/development/family/social/driving/pregnancy

Schema S4:
full ExECTv2-like schema

## Suggested stack

Runtime:

- Python
- DSPy
- Pydantic
- FastAPI

Local LLM:
- Qwen 35B-class model via Ollama

- Prefer JSON-schema constrained decoding where available

Clinical NLP helpers:

- spaCy / scispaCy for sentence splitting and abbreviation handling
- MedCAT, QuickUMLS, or custom terminology maps
- NegEx / pyConText-style rules for negation and temporality

Storage:

- Postgres for extracted facts
- Object storage for original notes, if permitted
- Vector DB optional, mainly for retrieval/debugging, not primary extraction

Review:

- React review UI
- Annotation export compatible with BRAT/Prodigy/Label Studio/Markup-like formats

## Evaluation plan

1. Load the gold standard data
2. Evaluate:
   - exact entity match
   - partial span match
   - field-level F1
   - document-level F1
   - negation accuracy
   - temporality accuracy
   - evidence-span correctness
3. Track errors by category.

We could define a metric like:

```python

score = (
    0.40 * field_level_f1
  + 0.20 * evidence_span_overlap
  + 0.15 * temporality_accuracy
  + 0.15 * negation_accuracy
  + 0.10 * schema_validity
)
```

Then DSPy can search for better instructions, demonstrations, or module compositions that improve that metric.

A good metric probably would not be simple exact match. You might want different scoring by field

Medication:
- generic drug match
- dose match
- route match
- current vs historical status

Seizure frequency:
- category match
- normalized count/period match
- current/historical distinction
- evidence span support

Diagnosis:
- epilepsy syndrome/type match
- uncertainty handling
- negation exclusion

Investigations:
- modality match
- result match
- date/temporality match

## Minimal prototype shape

```python
import dspy
from pydantic import BaseModel, Field
from typing import Literal, Optional, List

lm = dspy.LM(
    "openai/qwen-local",
    api_base="http://localhost:8000/v1",
    api_key="local",
)
dspy.configure(lm=lm)


class EvidenceSpan(BaseModel):
    text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None


class SeizureFrequency(BaseModel):
    raw_text: str
    category: Literal[
        "explicit_rate",
        "range",
        "cluster",
        "seizure_free",
        "unknown",
        "no_current_seizures",
        "historical_only"
    ]
    count: Optional[float] = None
    period: Optional[Literal["day", "week", "month", "year"]] = None
    temporality: Literal["current", "historical", "future", "uncertain"]
    evidence: EvidenceSpan
    confidence: float = Field(ge=0, le=1)


class ExtractSeizureFrequency(dspy.Signature):
    """Extract current seizure frequency from a clinical note.

    Return only facts directly supported by evidence in the note.
    Do not infer beyond the text.
    """
    note: str = dspy.InputField()
    seizure_frequency: SeizureFrequency = dspy.OutputField()


extract_frequency = dspy.Predict(ExtractSeizureFrequency)

result = extract_frequency(note=clinical_note)
```



## Rationale

### Why not just use an LLM end-to-end?

Because clinical extraction needs auditability. I’d use the local LLM for interpretation, but keep deterministic checks around it:

LLM extracts candidate facts
Rules verify impossible values
Terminology service normalizes concepts
Evidence spans are required
JSON schema validates output
A second verifier module checks note → extracted fact consistency
Low-confidence or conflicting outputs go to human review

For example, seizure frequency is especially tricky because notes say things like:

“Previously daily, now no seizures since March.”
“Clusters every few months.”
“Two nocturnal events last week but none before that for a year.”