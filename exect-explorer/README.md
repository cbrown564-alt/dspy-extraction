# ExECT Explorer — Clinical Annotation Theatre

ExECT Explorer is a modern, high-fidelity React visualization interface ("Clinical Annotation Theatre") designed to assist clinical researchers in exploring, annotating, and evaluating DSPy-based extraction pipelines on the **ExECTv2** and **Gan 2026** datasets.

---

## 🎯 Purpose & Core Value

Clinical extraction involves mapping unstructured clinic letters to structured databases (e.g., diagnoses, medications, seizure frequencies, and timeline anchors). The ExECT Explorer serves as a steering surface to:

1. **Analyze Gold-Standard Data**: Review clinical annotation sheets side-by-side with ontology categories.
2. **Expose Pipeline Ceilings**: Investigate data flaws, temporal sparsity, and label ambiguity.
3. **Compare Model Runs**: Track DSPy validation metrics, scorer setups, and program traces directly against raw inputs.
4. **Navigate Component Terrain**: Visualise the decomposed pipeline as a landscape of independent components, each with its own evidence summit and unknown ceiling.

---

## 💎 Features & Architecture

The application is structured around two main orthogonal navigation selectors:

### 1. Context Lenses (Sidebar Context)
* **Annotator**: Displays gold-standard clinical annotation overlays.
* **Oracle**: Exposes "Hard Ceilings" (accuracy limits), annotation flaws (tuple ambiguity, overlapping entities), and temporal sparsity indicators.
* **Clinician**: Summarizes flat text into structured clinical cards (Medications, Diagnoses with certainty ratings, Seizure Frequencies, and Investigations).
* **Model**: Shows document-specific **Letter pipeline** prediction traces (matching LLM outputs, Rule mappings, outcomes, and text evidence quotes).

### 2. Main Stage Views
* **Reader**: Interactive, highlighted clinical sheet.
* **Timeline**: Reconstructs patient history chronologically.
* **Annotate**: Custom annotation sandbox equipped with UMLS guidelines.
* **Runs**: A high-level leaderboard dashboard showcasing overall metrics (F1, Precision, Recall), run parameters (Schema, Scorer, Program, Prompt), Family F1 charts, and a predicted documents index with matched outcome badges.
* **Landscape**: A topographic terrain visualization where each pipeline component is a peak. Solid rock represents known evidence; clouds above hide the true ceiling. Click any peak to inspect experiments, next actions, and caution notes.

---

## ⚡ Recent Changes

### Component Ceiling Landscape (`v0.2.0` — May 2026)
The Landscape view has been rebuilt from a flat status table into an interactive expedition map.

* **Rock vs. Cloud Metaphor**: Each component is rendered as a peak where the solid rock portion represents current evidence strength and the cloud layer above represents the unknown ceiling gap. A 100% oracle ceiling appears as a fully-visible fortress; a 22% coverage gate appears as a tiny foothill swallowed by fog.
* **Dramatic Height Encoding**: Peak heights are scaled aggressively so differences are immediately visible. Target Selection (85% known, 55% cloud) towers over Candidate Inventory (22% known, 65% cloud).
* **HTML Label Layer**: Component names and metrics render as crisp HTML overlays, independent of SVG viewBox scaling, ensuring readability at any viewport size.
* **Interactive Detail Panels**: Clicking a peak opens a detail panel with status badges, experiment tags (G1, G2, E7, etc.), next actions, and caution notes drawn directly from the component ceiling registry.
* **Domain Toggle**: Switch between Gan S0 (7 peaks) and ExECT (4 peaks) without leaving the view.
* **Flow Paths**: Animated dashed rivers arc between summits, showing how data travels from Frequency Gate → Candidate Inventory → Temporal Anchoring → Target Selection → Label Construction.
* **Simplified Background**: Removed distracting contour grids and wind particles. One horizon line, one distant contour, and the peaks themselves are the heroes.

### Previous Enhancements
* **Runs Dashboard View**: Extracted overall validation statistics, surface settings, and Family F1 summaries from the sidebar to a dedicated main-stage dashboard.
* **Focused Model Sidebar**: Simplified the model lens sidebar to focus exclusively on the active document's pipeline trace.
* **Prediction Filters**: Integrated automatic list filtering in the left letter sidebar, displaying only documents that contain predictions for the selected model run.
* **Auto-Routing Fallback**: Implemented a React hook to automatically select the first available predicted letter when switching runs or model lenses.

---

## 🔮 Future Enhancements

The Landscape view is the first step toward a richer visual research command centre. The following are planned or aspirational:

### 1. Pipeline Architecture Diagram *(Implemented in v0.3.0)*
A dedicated **Architecture** view that renders the decomposed pipeline as an interactive network graph or node diagram. Unlike the Landscape (which shows *results*), the Architecture view focuses on *what we are building, testing, evaluating, and why*.

* **Nodes** = pipeline stages (Candidate Builder, Temporal Parser, Adjudicator, Label Constructor, Verifier, etc.)
* **Edges** = data contracts between stages (candidate schema, event payload, benchmark bridge)
* **Node State** = whether a stage is implemented, stubbed, under experiment, or frozen
* **Edge State** = whether the contract is validated, speculative, or broken
* **Annotations** = hover to see the preregistered hypothesis, the varied factor, and the decision scope (arm vs. mechanism)
* **Animation** = data packets flowing through the graph during a live run replay

This answers questions like: "What is the D1 v1.2b stage actually doing?", "Where does the candidate schema hand off to the adjudicator?", and "Which contract changes if we promote the family-span payload?"

### 2. Pairwise Interaction Matrix
A grid view showing how optimised components interfere when stacked. Each cell represents a pairwise interaction (e.g., Medication × Temporality, Diagnosis × Seizure Type) with:
* Isolated ceiling F1 for each component
* Stacked F1 when combined
* Visual delta showing the interaction loss
* Links to residual analysis reports

### 3. Live Run Replay
Ability to load a specific run artifact and watch the data flow through the Architecture graph in real time, with nodes lighting up as they execute and edges showing payload summaries.

### 4. Three-Axis Experiment Grid
A cap-25 search grid visualiser for the hybrid pipeline research program:
* **Axis 1**: Stage count (1-stage → 5-stage pipeline graphs)
* **Axis 2**: Per-stage executor assignment (deterministic / LLM / hybrid)
* **Axis 3**: Implementation variant (prompt policy, tool interface, bridge placement)

Each cell shows the best validation score found for that configuration, with colour intensity and direct links to inspection docs.

### 5. Holdout Drop Forensics
A specialised residual-analysis view that visualises the validation → holdout drop as a "meltdown" animation on the Landscape peaks. Components that degrade significantly flare red; stable components stay green. Hover reveals the attributed cause (raw extraction, bridge policy, prompt sensitivity, scorer effect).

---

## 📊 Data Architecture & Refresh Pipeline

The explorer frontend is a fully static React application that fetches structured JSON files from the `public/data/` directory at runtime. This avoids running an active backend database, optimizing for a fast and beautiful frontend experience.

### Data Sources
1. **Dataset Gold Standards (Manifests)**: 
   * **ExECTv2 (2025)**: Parsed from raw texts, BRAT annotations (`.ann`), and JSON files in `data/ExECTv2 (2025)/`.
   * **Gan (2026)**: Parsed from `data/Gan (2026)/synthetic_data_subset_1500.json`.
2. **Model Run Artifacts (Catalogs)**:
   * Sourced from DSPy evaluation runs outputting to the `runs/` directory (metrics, predictions, configs).

### How to Refresh Data
Python build scripts under `scripts/` process and serialize raw datasets and run artifacts into static JSON files for the frontend:
* **To rebuild ExECTv2 letter manifests**: `python scripts/build_manifest.py` (generates `public/data/EA*.json` & `public/data/index.json`)
* **To rebuild Gan letter manifests**: `python scripts/build_manifest_gan.py` (generates `public/data/gan_*.json` & `public/data/index_gan.json`)
* **To rebuild ExECTv2 runs catalog**: `python scripts/build_model_catalog.py` (generates `public/data/model_catalog.json`)
* **To rebuild Gan runs catalog**: `python scripts/build_model_catalog_gan.py` (generates `public/data/model_catalog_gan.json`)

### Manual Curation & Run Registry
* **Known Flaws**: Custom clinical annotations/anomalies (like split-dose ambiguities) are manually curated in the `KNOWN_FLAWS` dictionary inside `scripts/build_manifest.py`.
* **Model Catalog Registry**: The models and runs displayed on the Runs dashboard are registry-based. To add a new run to the interface, you must add the folder run ID to the `RUN_SPECS` array inside `scripts/build_model_catalog.py` (or `scripts/build_model_catalog_gan.py` for Gan) and run the build script.

---

## 🚀 Setup & Local Development

### Prerequisites
* Node.js (v18+)

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```
The server will boot locally at `http://127.0.0.1:5173/`.

### Build for Production
```bash
npm run build
```

### Run Playwright Visual Tests
To programmatically click through the application flows and regenerate UI screenshots:
```bash
node test_exploration_debug.cjs
```
Screenshots are saved directly in `test_screenshots/`.
