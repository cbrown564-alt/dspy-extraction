You are drafting a review-only artifact for the dspy-extraction research repo.

Workflow: Model config compatibility check
Repository root: C:\Users\cbrow\Code\dspy-extraction

Hard rules:
- Do not edit files.
- Do not change scorer semantics, dataset policy, registry rows, Kanban, or source-of-truth docs.
- Do not treat this draft as evidence for paper claims unless it points to primary artifacts.
- Preserve decision scopes: operational, arm, mechanism, open, blocked, stale_check.
- Separate facts from interpretation and uncertainty.
- Include concrete source paths for every claim.
- Flag missing context instead of guessing.

Task:
Scan the model configurations and source wrapper code to identify potential compatibility issues.
Draft compatibility adapters, wrappers, or parameters validation lists. Do not make edits.

Primary sources:
- configs/models/
- src/clinical_extraction/llms.py
- docs/policies/model_config_smoke_tests.md
- .agents/skills/model-config-compatibility/SKILL.md

Output shape:
# Model Compatibility and Adapter Report

## Sources Read
List paths.

## Model Config Gaps & Gaps Matrix
Analyze the differences in settings across:
- local Qwen configs (e.g., context length, Ollama specifics)
- hosted Gemini / OpenAI / Anthropic configs (e.g. reasoning parameters, json mode)
Flag unsupported parameters or risk of timeouts.

## Draft Adapter Wrapper/Interface Proposals
Provide Python code snippets or configuration recommendations to map provider-specific parameters safely in clinical_extraction wrappers.

## Recommended Parameter Validations
Rules to check during startup to prevent API crashes.
