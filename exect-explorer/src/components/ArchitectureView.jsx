import React, { useEffect, useState } from "react";
import {
  Box, GitBranch, CheckCircle2, XCircle, FlaskConical, Lock,
  Layers, X, CircleDot, Activity
} from "lucide-react";

/* ─── Pipeline Registry ─── */

const NODE_STATE = {
  implemented: { label: "Implemented", colour: "#2d8a5e", icon: CheckCircle2, fill: "#e8f5ee" },
  experiment:  { label: "Under Experiment", colour: "#b88a5c", icon: FlaskConical, fill: "#fdf6ed" },
  stubbed:     { label: "Stubbed", colour: "#5c7db8", icon: Box, fill: "#eef2fa" },
  frozen:      { label: "Frozen", colour: "#6b6b6b", icon: Lock, fill: "#f3f1ee" },
  rejected:    { label: "Rejected", colour: "#c45c3e", icon: XCircle, fill: "#fdf0ec" },
};

const EDGE_STATE = {
  validated:  { label: "Validated", colour: "#2d8a5e", dash: "0" },
  speculative:{ label: "Speculative", colour: "#b88a5c", dash: "6 4" },
  broken:     { label: "Broken", colour: "#c45c3e", dash: "3 3" },
};

const GAN_ARCHITECTURE = {
  nodes: [
    { id: "input", label: "Clinical Note", x: 80, y: 280, state: "implemented", layer: 0, detail: "Unstructured clinic letter input." },
    { id: "candidate_builder", label: "Candidate Builder", x: 280, y: 280, state: "implemented", layer: 1,
      detail: "Deterministic D1/builder substrate emits candidates. 299/299 coverage. Exact-covers 278/299 gold labels.",
      hypothesis: "Deterministic substrate can cover all quantified, qualitative, seizure-free, and unknown-cluster cases.",
      varied: "Builder gap vs. schema-guard-only vs. entity-first interfaces.",
      scope: "mechanism" },
    { id: "temporal_parser", label: "Temporal Parser", x: 480, y: 200, state: "experiment", layer: 2,
      detail: "Date math and scope resolution. R11 showed D1 wins; arithmetic injection regressed.",
      hypothesis: "Seizure-specific temporal anchoring outperforms broad relative-anchor guardrails.",
      varied: "Arithmetic injection, broad vs. seizure-specific anchor guardrails.",
      scope: "mechanism" },
    { id: "adjudicator", label: "Adjudicator", x: 480, y: 360, state: "experiment", layer: 2,
      detail: "Target selection from candidate inventory. G2 candidate-constrained 92.0%; G4 explicit reason-code 80.0%.",
      hypothesis: "Explicit reason-code adjudicator with candidate constraints improves target selection.",
      varied: "Free adjudication vs. candidate-constrained vs. seeded reason-code selector.",
      scope: "arm" },
    { id: "label_constructor", label: "Label Constructor", x: 680, y: 280, state: "implemented", layer: 3,
      detail: "Canonical aggregation of selected candidate into benchmark label. 1605/1605 records validated with 0 invalid.",
      hypothesis: "Deterministic construction from selected candidate preserves traceability.",
      varied: "Construction string format and malformed-string handling.",
      scope: "mechanism" },
    { id: "unknown_policy", label: "Unknown Policy", x: 480, y: 480, state: "experiment", layer: 2,
      detail: "Seizure-free vs. unknown vs. no-reference semantics boundary. G5 forensics show special-class target semantics are the key failure mode.",
      hypothesis: "Separate reason codes for seizure-free, unknown, and no-reference improve policy clarity.",
      varied: "Canonical scorer vs. paper-reproduction scorer special-class collapse.",
      scope: "mechanism" },
    { id: "evidence_gate", label: "Evidence Gate", x: 680, y: 480, state: "stubbed", layer: 3,
      detail: "Schema validity and evidence presence are necessary but not sufficient for correctness.",
      hypothesis: "High schema/evidence rates often coexist with wrong frequency labels.",
      varied: "Schema strictness, evidence span requirements.",
      scope: "diagnostic" },
    { id: "output", label: "Benchmark Label", x: 880, y: 280, state: "frozen", layer: 4, detail: "Final Gan S0 monthly frequency label." },
  ],
  edges: [
    { from: "input", to: "candidate_builder", state: "validated", label: "raw text" },
    { from: "candidate_builder", to: "temporal_parser", state: "validated", label: "candidate schema" },
    { from: "candidate_builder", to: "adjudicator", state: "validated", label: "candidate list" },
    { from: "temporal_parser", to: "adjudicator", state: "speculative", label: "temporal scope" },
    { from: "adjudicator", to: "label_constructor", state: "validated", label: "selected candidate" },
    { from: "label_constructor", to: "output", state: "validated", label: "canonical label" },
    { from: "candidate_builder", to: "unknown_policy", state: "speculative", label: "coverage gate" },
    { from: "unknown_policy", to: "adjudicator", state: "speculative", label: "policy filter" },
    { from: "adjudicator", to: "evidence_gate", state: "speculative", label: "selected + evidence" },
    { from: "evidence_gate", to: "output", state: "speculative", label: "validated label" },
  ]
};

const EXECT_ARCHITECTURE = {
  nodes: [
    { id: "input", label: "Clinical Note", x: 80, y: 300, state: "implemented", layer: 0, detail: "Unstructured clinic letter input." },
    { id: "family_spans", label: "Family Span Router", x: 260, y: 200, state: "experiment", layer: 1,
      detail: "Typed document geometry. E4 covers 100% core-family validation evidence using 88.8% of full-note characters.",
      hypothesis: "Family-span context preserves recall while reducing noise vs. full-note replacement.",
      varied: "Full-note vs. family-span prompt context.",
      scope: "arm" },
    { id: "s1_extractor", label: "S1 Raw Extractor", x: 260, y: 300, state: "implemented", layer: 1,
      detail: "Diagnosis, seizure type, medication, investigation raw extraction. E2 split audit separates raw, bridge, and prompt effects.",
      hypothesis: "Raw extraction ceiling is lower than bridge-assisted surface; bridges are necessary for near-ceiling claims.",
      varied: "Prompt version, bridge policy, field-family scope.",
      scope: "mechanism" },
    { id: "med_current_rx", label: "Medication Current-Rx", x: 260, y: 420, state: "implemented", layer: 1,
      detail: "Annotation-derived current-Rx payload reaches 100.0% medication F1 on validation. E7 attributes S5 loss to over-emission.",
      hypothesis: "Isolated current-Rx payload is a no-model ceiling substrate.",
      varied: "Lifecycle categories (planned, previous, taper, dose-only) are diagnostic-only.",
      scope: "mechanism" },
    { id: "s2_comorbidity", label: "S2 Comorbidity", x: 440, y: 240, state: "experiment", layer: 2,
      detail: "Sparse S3 families; weak and support-sensitive. Broad ladder does not isolate causes.",
      hypothesis: "Support counts and family contract needed before new tuning.",
      varied: "Support threshold, family contract strictness.",
      scope: "mechanism" },
    { id: "s3_sparse", label: "S3 Sparse Families", x: 440, y: 320, state: "experiment", layer: 2,
      detail: "Per-family parallel S5 was rejected. Family-first decomposition remains open with better substrates.",
      hypothesis: "Component substrates enable family-first decomposition without regression.",
      varied: "Parallel vs. sequential family stacking.",
      scope: "arm" },
    { id: "s4_frequency", label: "S4 Frequency / Temporality", x: 440, y: 400, state: "experiment", layer: 2,
      detail: "E10 shows broad payload 36.3% F1, gold-constrained oracle 100.0% F1. Adjudication is the open mechanism.",
      hypothesis: "Candidate adjudicator/ranker against fixed broad payload unlocks next stack work.",
      varied: "Direct promotion vs. high-precision payload vs. S4 GPT vs. S5 GPT.",
      scope: "mechanism" },
    { id: "s5_core", label: "S5 Core Stack", x: 620, y: 300, state: "implemented", layer: 3,
      detail: "Promoted baseline. GPT v2b 85.8% micro / 73.9% frequency F1. Qwen 85.4% / 71.4%.",
      hypothesis: "Stacked baseline is useful but not proof of optimal decomposition.",
      varied: "Model provider, prompt version, pre-vocab guard, frequency verify module.",
      scope: "arm" },
    { id: "holdout_gate", label: "Holdout Gate", x: 620, y: 420, state: "experiment", layer: 3,
      detail: "E11 confirms S1 GPT 92.3→77.8 micro driven by diagnosis/seizure-type transfer. S5 frequency 73.9→47.1 F1.",
      hypothesis: "Holdout drop is residual-analysis only; must not drive tuning.",
      varied: "Validation vs. holdout split, generalization surface.",
      scope: "diagnostic" },
    { id: "output", label: "Benchmark Label", x: 820, y: 300, state: "frozen", layer: 4, detail: "Final ExECT field-family extraction. CUI-aware Table 1 reproduction blocked." },
  ],
  edges: [
    { from: "input", to: "family_spans", state: "validated", label: "full note" },
    { from: "input", to: "s1_extractor", state: "validated", label: "raw text" },
    { from: "input", to: "med_current_rx", state: "validated", label: "annotations" },
    { from: "family_spans", to: "s1_extractor", state: "speculative", label: "span context" },
    { from: "s1_extractor", to: "s2_comorbidity", state: "validated", label: "diagnosis / seizure" },
    { from: "s1_extractor", to: "s3_sparse", state: "validated", label: "field families" },
    { from: "s1_extractor", to: "s4_frequency", state: "validated", label: "frequency candidates" },
    { from: "med_current_rx", to: "s5_core", state: "speculative", label: "current-Rx payload" },
    { from: "s2_comorbidity", to: "s5_core", state: "validated", label: "comorbidity" },
    { from: "s3_sparse", to: "s5_core", state: "validated", label: "sparse families" },
    { from: "s4_frequency", to: "s5_core", state: "validated", label: "frequency label" },
    { from: "s5_core", to: "holdout_gate", state: "speculative", label: "validation→holdout" },
    { from: "s5_core", to: "output", state: "validated", label: "field-family labels" },
    { from: "holdout_gate", to: "output", state: "speculative", label: "generalization check" },
  ]
};

/* ─── Helpers ─── */

function nodeById(nodes, id) { return nodes.find(n => n.id === id); }

function bezierPath(x1, y1, x2, y2) {
  const dx = Math.abs(x2 - x1);
  const cx1 = x1 + dx * 0.4;
  const cx2 = x2 - dx * 0.4;
  return `M ${x1} ${y1} C ${cx1} ${y1}, ${cx2} ${y2}, ${x2} ${y2}`;
}

/* ─── Tooltip ─── */

function HoverTooltip({ node, mouse }) {
  if (!node || !node.hypothesis) return null;
  return (
    <div
      className="arch-tooltip"
      style={{ left: mouse.x + 16, top: mouse.y + 16 }}
    >
      <div className="arch-tooltip-header">
        <CircleDot size={12} />
        <span>{node.label}</span>
      </div>
      <div className="arch-tooltip-row">
        <span className="arch-tooltip-key">Hypothesis</span>
        <span className="arch-tooltip-val">{node.hypothesis}</span>
      </div>
      <div className="arch-tooltip-row">
        <span className="arch-tooltip-key">Varied Factor</span>
        <span className="arch-tooltip-val">{node.varied}</span>
      </div>
      <div className="arch-tooltip-row">
        <span className="arch-tooltip-key">Decision Scope</span>
        <span className={`arch-tooltip-scope is-${node.scope}`}>{node.scope}</span>
      </div>
    </div>
  );
}

/* ─── Detail Panel ─── */

function NodeDetail({ node, onClose }) {
  if (!node) return null;
  const meta = NODE_STATE[node.state] || NODE_STATE.stubbed;
  const Icon = meta.icon;
  return (
    <div className="arch-detail" onClick={(e) => e.stopPropagation()}>
      <button className="arch-detail-close" onClick={onClose} title="Close">
        <X size={16} />
      </button>
      <div className="arch-detail-header">
        <span className="arch-detail-badge" style={{ color: meta.colour, borderColor: meta.colour }}>
          <Icon size={12} />
          {meta.label}
        </span>
        <h3>{node.label}</h3>
      </div>
      <p className="arch-detail-body">{node.detail}</p>
      {node.hypothesis && (
        <div className="arch-detail-section">
          <span className="arch-detail-key">Preregistered Hypothesis</span>
          <p className="arch-detail-val">{node.hypothesis}</p>
        </div>
      )}
      {node.varied && (
        <div className="arch-detail-section">
          <span className="arch-detail-key">Varied Factor</span>
          <p className="arch-detail-val">{node.varied}</p>
        </div>
      )}
      {node.scope && (
        <div className="arch-detail-section">
          <span className="arch-detail-key">Decision Scope</span>
          <span className={`arch-detail-scope is-${node.scope}`}>{node.scope}</span>
        </div>
      )}
    </div>
  );
}

/* ─── Main Component ─── */

export default function ArchitectureView() {
  const [domain, setDomain] = useState("gan");
  const [hoveredId, setHoveredId] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const arch = domain === "gan" ? GAN_ARCHITECTURE : EXECT_ARCHITECTURE;
  const hoveredNode = nodeById(arch.nodes, hoveredId);
  const selectedNode = nodeById(arch.nodes, selectedId);

  const W = 960;
  const H = 560;
  const NODE_R = 28;

  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }

  return (
    <div className="architecture-view" onMouseMove={handleMouseMove}>
      <div className="arch-topbar">
        <div className="arch-title-group">
          <Layers size={18} className="arch-title-icon" />
          <div>
            <h2 className="arch-title">Pipeline Architecture</h2>
            <p className="arch-subtitle">
              {domain === "gan"
                ? "Gan S0 — what we are building, testing, evaluating, and why"
                : "ExECT — what we are building, testing, evaluating, and why"}
            </p>
          </div>
        </div>
        <div className="arch-domain-toggle">
          <button className={domain === "gan" ? "is-active" : ""} onClick={() => { setDomain("gan"); setSelectedId(null); }}>
            Gan S0
          </button>
          <button className={domain === "exect" ? "is-active" : ""} onClick={() => { setDomain("exect"); setSelectedId(null); }}>
            ExECT
          </button>
        </div>
      </div>

      <div className="arch-canvas-wrap">
        {/* ── SVG layer: edges + circles only ── */}
        <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" className="arch-svg">
          <defs>
            <marker id="arrow-validated" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 L2,4 Z" fill="#2d8a5e" />
            </marker>
            <marker id="arrow-speculative" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 L2,4 Z" fill="#b88a5c" />
            </marker>
            <marker id="arrow-broken" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 L2,4 Z" fill="#c45c3e" />
            </marker>
          </defs>

          {/* Edges */}
          {arch.edges.map((edge, i) => {
            const a = nodeById(arch.nodes, edge.from);
            const b = nodeById(arch.nodes, edge.to);
            if (!a || !b) return null;
            const em = EDGE_STATE[edge.state] || EDGE_STATE.speculative;
            const angle = Math.atan2(b.y - a.y, b.x - a.x);
            const x1 = a.x + Math.cos(angle) * NODE_R;
            const y1 = a.y + Math.sin(angle) * NODE_R;
            const x2 = b.x - Math.cos(angle) * (NODE_R + 4);
            const y2 = b.y - Math.sin(angle) * (NODE_R + 4);
            const d = bezierPath(x1, y1, x2, y2);
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2 - 6;
            return (
              <g key={`edge-${i}`} className={`arch-edge ${mounted ? "is-mounted" : ""}`} style={{ animationDelay: `${0.1 * i}s` }}>
                <path
                  d={d}
                  fill="none"
                  stroke={em.colour}
                  strokeWidth="1.5"
                  strokeDasharray={em.dash}
                  opacity="0.6"
                  markerEnd={`url(#arrow-${edge.state})`}
                />
                {edge.label && (
                  <g>
                    <rect
                      x={midX - 38}
                      y={midY - 9}
                      width={76}
                      height={18}
                      rx={4}
                      fill="#faf9f7"
                      opacity="0.9"
                    />
                    <text
                      x={midX}
                      y={midY + 3}
                      textAnchor="middle"
                      fontSize="9"
                      fill={em.colour}
                      fontFamily="var(--font-sans)"
                    >
                      {edge.label}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* Circles only — no foreignObject, no CSS transform animation */}
          {arch.nodes.map((node) => {
            const meta = NODE_STATE[node.state] || NODE_STATE.stubbed;
            const isHovered = hoveredId === node.id;
            const isSelected = selectedId === node.id;
            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
              >
                <circle
                  r={NODE_R}
                  fill={meta.fill}
                  stroke={meta.colour}
                  strokeWidth={isSelected ? 2.5 : isHovered ? 2 : 1.5}
                  opacity={node.state === "rejected" ? 0.35 : 1}
                  style={{ transition: "stroke-width 0.15s ease" }}
                />
                {node.state === "experiment" && (
                  <circle r={34} fill="none" stroke={meta.colour} strokeWidth="1" opacity="0.2" className="pulse-halo" />
                )}
              </g>
            );
          })}
        </svg>

        {/* ── HTML overlay layer: icons, labels, hit areas ── */}
        <div className="arch-overlays">
          {arch.nodes.map((node) => {
            const meta = NODE_STATE[node.state] || NODE_STATE.stubbed;
            const Icon = meta.icon;
            const isHovered = hoveredId === node.id;
            const isSelected = selectedId === node.id;
            return (
              <div
                key={`overlay-${node.id}`}
                className={`arch-node-overlay ${isHovered ? "is-hovered" : ""} ${isSelected ? "is-selected" : ""}`}
                style={{
                  left: `${(node.x / W) * 100}%`,
                  top: `${(node.y / H) * 100}%`,
                }}
                onMouseEnter={() => setHoveredId(node.id)}
                onMouseLeave={() => setHoveredId(null)}
                onClick={() => setSelectedId(selectedId === node.id ? null : node.id)}
              >
                <div className="arch-node-icon" style={{ color: meta.colour, opacity: node.state === "rejected" ? 0.4 : 1 }}>
                  <Icon size={18} />
                </div>
                <div className="arch-node-label" style={{ color: meta.colour, opacity: node.state === "rejected" ? 0.4 : 1 }}>
                  {node.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="arch-legend">
          <div className="arch-legend-title">
            <Activity size={12} />
            Node State
          </div>
          {Object.entries(NODE_STATE).map(([key, meta]) => (
            <div key={key} className="arch-legend-row">
              <span className="arch-legend-swatch" style={{ background: meta.colour }} />
              <span className="arch-legend-name">{meta.label}</span>
            </div>
          ))}
          <div className="arch-legend-divider" />
          <div className="arch-legend-title">
            <GitBranch size={12} />
            Edge State
          </div>
          {Object.entries(EDGE_STATE).map(([key, meta]) => (
            <div key={key} className="arch-legend-row">
              <span className="arch-legend-line" style={{ borderColor: meta.colour, borderStyle: key === "validated" ? "solid" : key === "speculative" ? "dashed" : "dotted" }} />
              <span className="arch-legend-name">{meta.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Floating tooltip */}
      <HoverTooltip node={hoveredNode} mouse={mousePos} />

      {/* Detail panel */}
      {selectedNode && <NodeDetail node={selectedNode} onClose={() => setSelectedId(null)} />}
    </div>
  );
}
