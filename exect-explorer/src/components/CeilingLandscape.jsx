import React, { useEffect, useState } from "react";
import {
  Mountain, Flag, Lock, XCircle, TrendingUp, Activity,
  ChevronRight, Wind, MapPin, Anchor, ShieldAlert, Compass
} from "lucide-react";

/*
  Elevation = current evidence strength (0-100).
  CeilingGap = how much unknown summit sits above us in the clouds.
  A tall elevation with small gap = near-ceiling, well-mapped.
  A small elevation with large gap = early foothill, vast unknown above.
*/

const GAN_PEAKS = [
  {
    id: "frequency_gate",
    name: "Frequency Gate",
    subtitle: "Content detection",
    status: "operational",
    elevation: 82,
    ceilingGap: 18,
    widthFactor: 0.9,
    description: "Does the note contain any seizure-frequency reference? D1 v1.2b operates here silently.",
    experiments: [],
    nextAction: "Frozen into D1 v1.2b baseline; no independent ceiling claimed.",
    detail: "This gate is not scored independently. It is implicit in every downstream component."
  },
  {
    id: "candidate_inventory",
    name: "Candidate Inventory",
    subtitle: "G1 coverage probe",
    status: "mechanism_open",
    elevation: 22,
    ceilingGap: 65,
    widthFactor: 1.1,
    description: "Deterministic substrate emits candidates for 65 records; exact-covers 61 gold labels. No-reference coverage is 0/11.",
    experiments: ["G1"],
    nextAction: "Split target selection from label construction before new adjudicator variants.",
    detail: "A coverage gate, not a ceiling. The true summit is still deep in cloud."
  },
  {
    id: "temporal_anchor",
    name: "Temporal Anchoring",
    subtitle: "Date math & scope",
    status: "mechanism_open",
    elevation: 68,
    ceilingGap: 45,
    widthFactor: 0.95,
    description: "R11 showed D1 wins; arithmetic injection and broad anchor guardrails regressed.",
    experiments: ["R11", "R15"],
    nextAction: "Keep arithmetic diagnostic-only until parser is seizure-specific.",
    detail: "Precision vs recall trade-off unresolved. The summit is glimpsed but not reached."
  },
  {
    id: "target_selection",
    name: "Target Selection",
    subtitle: "Scope & benchmark target",
    status: "mechanism_open",
    elevation: 85,
    ceilingGap: 55,
    widthFactor: 1.0,
    description: "G2 showed candidate-constrained hits 92% on enriched slice. Free adjudication fell to 16.0%.",
    experiments: ["G2"],
    nextAction: "G4 explicit reason-code adjudicator should beat same-slice baselines before full validation.",
    detail: "Candidate-constrained is the current mechanism anchor, but slice metrics are not a full ceiling."
  },
  {
    id: "label_construction",
    name: "Label Construction",
    subtitle: "Canonical aggregation",
    status: "mechanism_open",
    elevation: 70,
    ceilingGap: 48,
    widthFactor: 0.9,
    description: "Constructor validates 64/65 current candidate records. Malformed strings remain unsupported.",
    experiments: ["G2"],
    nextAction: "Inspect G2 differential records before adding new explicit reason-code logic.",
    detail: "Label construction must stay separated from target selection in reports."
  },
  {
    id: "unknown_policy",
    name: "Unknown Policy",
    subtitle: "No-ref isolation",
    status: "mechanism_open",
    elevation: 35,
    ceilingGap: 72,
    widthFactor: 0.8,
    description: "Canonical scorer keeps them distinct; paper reproduction collapses them differently.",
    experiments: ["G3"],
    nextAction: "Use G3 policy-isolation cues to guide G4 adjudicator design.",
    detail: "This is a semantics boundary, not a numeric ceiling. Misclassification here poisons benchmark claims."
  },
  {
    id: "evidence",
    name: "Evidence & Schema",
    subtitle: "Validation gate",
    status: "diagnostic",
    elevation: 28,
    ceilingGap: 78,
    widthFactor: 0.75,
    description: "Schema validity and evidence presence are necessary but not sufficient for correctness.",
    experiments: [],
    nextAction: "Keep as gates and diagnostics, never as proof of semantic correctness.",
    detail: "High schema/evidence rates often coexist with wrong frequency labels."
  }
];

const EXECT_PEAKS = [
  {
    id: "freq_payload",
    name: "Frequency Payload",
    subtitle: "E1 / E10",
    status: "mechanism_open",
    elevation: 55,
    ceilingGap: 50,
    widthFactor: 1.0,
    description: "Broad payload covers all 43 validation gold labels but emits 151 extra candidates (22.2% precision).",
    experiments: ["E1", "E10"],
    nextAction: "Split candidate selection/adjudication from label construction.",
    detail: "Coverage gate is passed. Adjudication is wide open."
  },
  {
    id: "med_current",
    name: "Medication Current-Rx",
    subtitle: "E6 ceiling",
    status: "promoted",
    elevation: 100,
    ceilingGap: 0,
    widthFactor: 1.15,
    description: "Annotation-derived current-Rx payload reaches perfect F1 on validation. A true no-model ceiling substrate.",
    experiments: ["E6"],
    nextAction: "Route E7 to explain S5 over-emission before changing prompts or bridges.",
    detail: "S5 recall is 100% but precision drops to 79.7%. This is stack interference, not a payload failure."
  },
  {
    id: "family_spans",
    name: "Family Spans",
    subtitle: "E4 / E8",
    status: "mechanism_open",
    elevation: 72,
    ceilingGap: 38,
    widthFactor: 1.05,
    description: "Typed document geometry covers core-family validation evidence. 88.8% of full-note characters used.",
    experiments: ["E4", "E8"],
    nextAction: "Preregister full-note vs family-span prompt comparison before promotion.",
    detail: "False-family spans remain measurable. Promotion requires recall preservation."
  },
  {
    id: "investigation",
    name: "Investigation",
    subtitle: "E12 confirmation",
    status: "mechanism_open",
    elevation: 78,
    ceilingGap: 30,
    widthFactor: 0.9,
    description: "Appears near-ceiling in broad stacks, but isolated ceiling is unmeasured.",
    experiments: ["E12"],
    nextAction: "Confirm through isolated family probe before calling solved.",
    detail: "Broad-stack stability is not enough. Needs component-scoped confirmation."
  }
];

const STATUS_META = {
  promoted: { label: "Promoted", colour: "#2d8a5e", icon: Flag, pulse: false },
  operational: { label: "Operational", colour: "#2d8a5e", icon: Anchor, pulse: false },
  mechanism_open: { label: "Open", colour: "#b88a5c", icon: Activity, pulse: true },
  diagnostic: { label: "Diagnostic", colour: "#5c7db8", icon: TrendingUp, pulse: false },
  rejected: { label: "Rejected", colour: "#c45c3e", icon: XCircle, pulse: false },
  blocked: { label: "Blocked", colour: "#a0a0a0", icon: Lock, pulse: false }
};

function PeakDetail({ peak, onClose }) {
  if (!peak) return null;
  const meta = STATUS_META[peak.status] || STATUS_META.diagnostic;
  const Icon = meta.icon;

  return (
    <div className="landscape-detail" onClick={(e) => e.stopPropagation()}>
      <button className="landscape-detail-close" onClick={onClose} title="Close">
        <XCircle size={16} />
      </button>

      <div className="landscape-detail-header">
        <span className="landscape-detail-badge" style={{ color: meta.colour, borderColor: meta.colour }}>
          <Icon size={12} />
          {meta.label}
        </span>
        <h3>{peak.name}</h3>
        <p className="landscape-detail-sub">{peak.subtitle}</p>
      </div>

      <div className="landscape-detail-metric">
        <span className="landscape-detail-metric-val">{peak.elevation}%</span>
        <span className="landscape-detail-metric-label">known summit</span>
        <span className="landscape-detail-metric-sep">·</span>
        <span className="landscape-detail-metric-val is-gap">{peak.ceilingGap}%</span>
        <span className="landscape-detail-metric-label">still in cloud</span>
      </div>

      <div className="landscape-detail-body">
        <p>{peak.description}</p>
        <div className="landscape-detail-section">
          <span className="landscape-detail-section-title">Experiments</span>
          <div className="landscape-detail-tags">
            {peak.experiments.length ? peak.experiments.map(e => (
              <span key={e} className="landscape-detail-tag">{e}</span>
            )) : <span className="landscape-detail-tag is-ghost">None yet</span>}
          </div>
        </div>
        <div className="landscape-detail-section">
          <span className="landscape-detail-section-title">Next Action</span>
          <p className="landscape-detail-action">{peak.nextAction}</p>
        </div>
        <div className="landscape-detail-note">
          <ShieldAlert size={14} />
          <p>{peak.detail}</p>
        </div>
      </div>
    </div>
  );
}

function buildPeakPath(x, baseY, elevation, gap, widthFactor) {
  const knownH = elevation * 3.2;
  const cloudH = gap * 2.0;
  const totalH = knownH + cloudH;
  const w = 70 * widthFactor;

  const summitY = baseY - totalH;
  const rockTopY = baseY - knownH;

  // Asymmetric mountain silhouette
  const leftShoulder = { x: x - w * 0.55, y: baseY - knownH * 0.35 };
  const rightShoulder = { x: x + w * 0.5, y: baseY - knownH * 0.3 };
  const leftMid = { x: x - w * 0.3, y: rockTopY + cloudH * 0.15 };
  const rightMid = { x: x + w * 0.25, y: rockTopY + cloudH * 0.1 };

  const rockPath = [
    `M ${x - w * 0.5} ${baseY}`,
    `L ${leftShoulder.x} ${leftShoulder.y}`,
    `Q ${leftMid.x} ${leftMid.y} ${x} ${rockTopY}`,
    `Q ${rightMid.x} ${rightMid.y} ${rightShoulder.x} ${rightShoulder.y}`,
    `L ${x + w * 0.45} ${baseY}`,
    "Z"
  ].join(" ");

  // Summit spike that disappears into cloud
  const summitPath = [
    `M ${x - w * 0.12} ${rockTopY}`,
    `L ${x} ${summitY}`,
    `L ${x + w * 0.1} ${rockTopY + cloudH * 0.05}`,
    "Z"
  ].join(" ");

  return { rockPath, summitPath, rockTopY, summitY, w };
}

export default function CeilingLandscape() {
  const [domain, setDomain] = useState("gan");
  const [selectedId, setSelectedId] = useState(null);
  const [hoveredId, setHoveredId] = useState(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const peaks = domain === "gan" ? GAN_PEAKS : EXECT_PEAKS;
  const selectedPeak = peaks.find(p => p.id === selectedId) || null;

  const W = 1200;
  const H = 600;
  const baseY = H - 75;

  function peakX(index, total) {
    const margin = 90;
    const usable = W - margin * 2;
    return margin + (usable / (total - 1)) * index;
  }

  function pathBetween(i, j, total) {
    const a = peakX(i, total);
    const b = peakX(j, total);
    const ax = a;
    const ay = baseY - peaks[i].elevation * 3.2 - peaks[i].ceilingGap * 2.0 + 15;
    const bx = b;
    const by = baseY - peaks[j].elevation * 3.2 - peaks[j].ceilingGap * 2.0 + 15;
    const midY = Math.min(ay, by) - 50;
    return `M ${ax} ${ay} Q ${(ax + bx) / 2} ${midY} ${bx} ${by}`;
  }

  return (
    <div className="ceiling-landscape">
      <div className="landscape-topbar">
        <div className="landscape-title-group">
          <Mountain size={18} className="landscape-title-icon" />
          <div>
            <h2 className="landscape-title">Component Ceiling Landscape</h2>
            <p className="landscape-subtitle">
              {domain === "gan"
                ? "Gan S0 — solid rock is what we know; clouds hide the true ceiling"
                : "ExECT — solid rock is what we know; clouds hide the true ceiling"}
            </p>
          </div>
        </div>

        <div className="landscape-domain-toggle">
          <button className={domain === "gan" ? "is-active" : ""} onClick={() => { setDomain("gan"); setSelectedId(null); }}>
            Gan S0
          </button>
          <button className={domain === "exect" ? "is-active" : ""} onClick={() => { setDomain("exect"); setSelectedId(null); }}>
            ExECT
          </button>
        </div>
      </div>

      <div className="landscape-canvas-wrap">
        {/* HTML labels layer — sits above SVG, unaffected by viewBox scaling */}
        <div className="peak-labels-layer">
          {peaks.map((peak, i) => {
            const x = peakX(i, peaks.length);
            const meta = STATUS_META[peak.status] || STATUS_META.diagnostic;
            return (
              <div
                key={`label-${peak.id}`}
                className="peak-label-wrap"
                style={{
                  left: `${(x / W) * 100}%`,
                  top: `${(baseY / H) * 100}%`,
                  color: meta.colour,
                  animationDelay: `${0.4 + i * 0.1}s`
                }}
              >
                <div className="peak-label-name">{peak.name}</div>
                <div className="peak-label-metric">
                  {peak.elevation}% known
                  {peak.ceilingGap > 0 ? ` · ${peak.ceilingGap}% cloud` : " · ceiling visible"}
                </div>
              </div>
            );
          })}
        </div>

        <svg
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="xMidYMid meet"
          className="landscape-svg"
          style={{ pointerEvents: 'none' }}
        >
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f3f1ee" />
              <stop offset="100%" stopColor="#faf9f7" />
            </linearGradient>
            <linearGradient id="rockGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#e8e4df" />
              <stop offset="100%" stopColor="#d4cfc8" />
            </linearGradient>
            <filter id="cloudBlur">
              <feGaussianBlur stdDeviation="14" />
            </filter>
            <filter id="softShadow">
              <feDropShadow dx="0" dy="3" stdDeviation="5" floodColor="#000" floodOpacity="0.06" />
            </filter>
          </defs>

          {/* Background */}
          <rect width={W} height={H} fill="url(#skyGrad)" pointerEvents="none" />

          {/* Horizon line */}
          <line x1="0" y1={baseY} x2={W} y2={baseY} stroke="#d4d2cf" strokeWidth="1.5" />

          {/* Subtle distant contour */}
          <path
            d={`M 0 ${baseY - 30} Q ${W * 0.3} ${baseY - 55} ${W * 0.5} ${baseY - 40} T ${W} ${baseY - 35}`}
            fill="none"
            stroke="#e4e2df"
            strokeWidth="1"
            opacity="0.6"
          />

          {/* Flow paths */}
          <g pointerEvents="none">
            {peaks.map((_, i) => {
              if (i >= peaks.length - 1) return null;
              const d = pathBetween(i, i + 1, peaks.length);
              return (
                <g key={`flow-${i}`}>
                  <path d={d} className="flow-river" />
                  <path d={d} className="flow-particle" style={{ animationDelay: `${i * 0.6}s` }} />
                </g>
              );
            })}
          </g>

          {/* Peaks */}
          {peaks.map((peak, i) => {
            const x = peakX(i, peaks.length);
            const meta = STATUS_META[peak.status] || STATUS_META.diagnostic;
            const isHovered = hoveredId === peak.id;
            const isSelected = selectedId === peak.id;
            const isOpen = peak.status === "mechanism_open";

            const { rockPath, summitPath, rockTopY, summitY, w } = buildPeakPath(
              x, baseY, peak.elevation, peak.ceilingGap, peak.widthFactor
            );

            return (
              <g
                key={peak.id}
                className={`peak-group ${isHovered ? "is-hovered" : ""} ${isSelected ? "is-selected" : ""} ${mounted ? "is-mounted" : ""}`}
                style={{ animationDelay: `${0.2 + i * 0.1}s`, pointerEvents: 'all' }}
                onMouseEnter={() => setHoveredId(peak.id)}
                onMouseLeave={() => setHoveredId(null)}
                onClick={() => setSelectedId(selectedId === peak.id ? null : peak.id)}
              >
                {/* Known rock (solid) */}
                <path
                  d={rockPath}
                  fill={meta.colour}
                  opacity={peak.status === "rejected" ? 0.2 : 0.42}
                  stroke={meta.colour}
                  strokeWidth={isSelected ? 2.2 : 1.2}
                  strokeLinejoin="round"
                  filter="url(#softShadow)"
                  className="peak-rock"
                />

                {/* Summit spike (fades into cloud) */}
                {peak.ceilingGap > 5 && (
                  <path
                    d={summitPath}
                    fill={meta.colour}
                    opacity={0.12}
                    stroke={meta.colour}
                    strokeWidth={0.8}
                    strokeLinejoin="round"
                  />
                )}

                {/* Snow cap on known rock */}
                {peak.elevation > 15 && (
                  <path
                    d={[
                      `M ${x - w * 0.08} ${rockTopY + 6}`,
                      `L ${x} ${rockTopY - 4}`,
                      `L ${x + w * 0.07} ${rockTopY + 6}`,
                      "Z"
                    ].join(" ")}
                    fill="#fff"
                    opacity={0.85}
                  />
                )}

                {/* Cloud layer sitting on the rock top */}
                {peak.ceilingGap > 5 && (
                  <ellipse
                    cx={x}
                    cy={rockTopY + 8}
                    rx={w * 0.55}
                    ry={16 + peak.ceilingGap * 0.25}
                    fill="#f3f1ee"
                    opacity={0.85}
                    filter="url(#cloudBlur)"
                    className="peak-cloud"
                  />
                )}

                {/* Status icon badge on the rock face */}
                <g transform={`translate(${x - 7}, ${baseY - peak.elevation * 1.6})`}>
                  <meta.icon size={14} color={meta.colour} strokeWidth={2.2} />
                </g>

                {/* Open pulse ring */}
                {isOpen && (
                  <ellipse
                    cx={x}
                    cy={baseY - peak.elevation * 1.6}
                    rx={w * 0.4}
                    ry={8}
                    fill="none"
                    stroke={meta.colour}
                    strokeWidth="1.2"
                    opacity="0.2"
                    className="pulse-halo"
                  />
                )}

                {/* Invisible hit area for easier clicking */}
                <rect
                  x={x - w * 0.6}
                  y={baseY - peak.elevation * 3.2 - peak.ceilingGap * 2.0}
                  width={w * 1.2}
                  height={peak.elevation * 3.2 + peak.ceilingGap * 2.0 + 40}
                  fill="transparent"
                  pointerEvents="all"
                />
              </g>
            );
          })}

          {/* Compass */}
          <g transform="translate(1140, 50)" className={mounted ? "compass is-visible" : "compass"}>
            <circle r="26" fill="#fff" stroke="#d4d2cf" strokeWidth="1.5" />
            <Compass size={18} color="#6b6b6b" strokeWidth={1.5} transform="translate(-9, -9)" />
          </g>
        </svg>

        {/* Legend */}
        <div className="landscape-legend">
          <div className="landscape-legend-title">
            <MapPin size={12} />
            Terrain Legend
          </div>
          {Object.entries(STATUS_META).map(([key, meta]) => (
            <div key={key} className="landscape-legend-row">
              <span className="landscape-legend-swatch" style={{ background: meta.colour }} />
              <span className="landscape-legend-name">{meta.label}</span>
              {meta.pulse && <span className="landscape-legend-pulse" />}
            </div>
          ))}
          <div className="landscape-legend-divider" />
          <div className="landscape-legend-note">
            <span className="landscape-legend-swatch is-cloud" />
            <span className="landscape-legend-name">Ceiling cloud</span>
          </div>
        </div>
      </div>

      {/* Base camp */}
      <div className="landscape-basecamp">
        <div className="basecamp-item">
          <span className="basecamp-label">Operational baseline</span>
          <span className="basecamp-val">
            {domain === "gan" ? "D1 v1.2b schema guard — 79.9% monthly" : "S5 v2b GPT — 85.8% micro / 73.9% freq F1"}
          </span>
        </div>
        <div className="basecamp-item">
          <span className="basecamp-label">Promoted ceilings</span>
          <span className="basecamp-val">
            {domain === "gan" ? "None yet (G5 rescoring pending)" : "Medication current-Rx — 100.0% F1 (oracle)"}
          </span>
        </div>
        <div className="basecamp-item">
          <span className="basecamp-label">Active risk</span>
          <span className="basecamp-val is-risk">
            {domain === "gan" ? "Paper comparison blocked until G5" : "Holdout drop: S1 92.3→77.8 / S5 freq 73.9→47.1"}
          </span>
        </div>
        <div className="basecamp-item">
          <span className="basecamp-label">Next pull</span>
          <span className="basecamp-val is-action">
            {domain === "gan" ? "G4 adjudicator · G5 paper rescore" : "E7 med interference · E10 freq adjudication · E8 spans"}
          </span>
        </div>
      </div>

      {/* Detail panel */}
      {selectedPeak && (
        <PeakDetail peak={selectedPeak} onClose={() => setSelectedId(null)} />
      )}
    </div>
  );
}
