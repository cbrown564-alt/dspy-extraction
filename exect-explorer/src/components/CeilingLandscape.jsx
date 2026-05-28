import React, { useEffect, useRef, useState } from "react";
import {
  Mountain, Flag, Lock, XCircle, TrendingUp, Activity,
  ChevronRight, Wind, MapPin, Anchor, ShieldAlert, Compass
} from "lucide-react";

const GAN_PEAKS = [
  {
    id: "frequency_gate",
    name: "Frequency Gate",
    subtitle: "Content detection",
    status: "operational",
    metric: null,
    elevation: 85,
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
    metric: "63 / 299",
    elevation: 65,
    description: "What candidate frequencies exist? Deterministic substrate emits candidates for 65 records; exact-covers 61 gold labels.",
    experiments: ["G1"],
    nextAction: "Split target selection from label construction before new adjudicator variants.",
    detail: "No-reference coverage is 0/11. This is a coverage gate, not a ceiling."
  },
  {
    id: "temporal_anchor",
    name: "Temporal Anchoring",
    subtitle: "Date math & scope",
    status: "mechanism_open",
    metric: "~80% monthly",
    elevation: 78,
    description: "Which time window does each candidate belong to? R11 showed D1 wins; arithmetic injection regressed.",
    experiments: ["R11", "R15"],
    nextAction: "Keep arithmetic diagnostic-only until parser is seizure-specific.",
    detail: "Broad relative-anchor guardrails caused regression. Precision vs recall trade-off unresolved."
  },
  {
    id: "target_selection",
    name: "Target Selection",
    subtitle: "Scope & benchmark target",
    status: "mechanism_open",
    metric: "92.0% slice",
    elevation: 88,
    description: "Which candidate becomes the benchmark-facing label? G2 showed candidate-constrained hits 92% on enriched slice.",
    experiments: ["G2"],
    nextAction: "G4 explicit reason-code adjudicator should beat same-slice baselines before full validation.",
    detail: "Free adjudication fell to 16.0% monthly. Candidate-constrained is the current mechanism anchor."
  },
  {
    id: "label_construction",
    name: "Label Construction",
    subtitle: "Canonical aggregation",
    status: "mechanism_open",
    metric: "64 / 65 valid",
    elevation: 75,
    description: "How is the final monthly / per-4wk label built? Constructor validates most records; leaves malformed cases unsupported.",
    experiments: ["G2"],
    nextAction: "Inspect G2 differential records before adding new explicit reason-code logic.",
    detail: "Malformed strings like 'a pair of per 4 month' are not scorer-repaired. Label construction must stay separated from target selection in reports."
  },
  {
    id: "unknown_policy",
    name: "Unknown vs No-Ref",
    subtitle: "Policy isolation",
    status: "mechanism_open",
    metric: null,
    elevation: 60,
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
    metric: "High rates",
    elevation: 55,
    description: "Schema validity and evidence presence are necessary but not sufficient for correctness.",
    experiments: [],
    nextAction: "Keep as gates and diagnostics, never as proof of semantic correctness.",
    detail: "High schema/evidence rates often coexist with wrong frequency labels. Do not optimize for this alone."
  }
];

const EXECT_PEAKS = [
  {
    id: "freq_payload",
    name: "Frequency Payload",
    subtitle: "E1 / E10",
    status: "mechanism_open",
    metric: "43/43 recall",
    elevation: 72,
    description: "Broad payload covers all validation gold labels but emits 151 extra candidates (22.2% precision).",
    experiments: ["E1", "E10"],
    nextAction: "Split candidate selection/adjudication from label construction.",
    detail: "Coverage gate is passed. Adjudication is wide open."
  },
  {
    id: "med_current",
    name: "Medication Current-Rx",
    subtitle: "E6 ceiling",
    status: "promoted",
    metric: "100.0% F1",
    elevation: 95,
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
    metric: "100% evidence",
    elevation: 80,
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
    metric: "High & stable",
    elevation: 85,
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

      {peak.metric && (
        <div className="landscape-detail-metric">
          <span className="landscape-detail-metric-val">{peak.metric}</span>
          <span className="landscape-detail-metric-label">current evidence</span>
        </div>
      )}

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

export default function CeilingLandscape() {
  const [domain, setDomain] = useState("gan");
  const [selectedId, setSelectedId] = useState(null);
  const [hoveredId, setHoveredId] = useState(null);
  const svgRef = useRef(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const peaks = domain === "gan" ? GAN_PEAKS : EXECT_PEAKS;
  const selectedPeak = peaks.find(p => p.id === selectedId) || null;

  const W = 1000;
  const H = 520;
  const baseY = H - 80;

  function peakPos(index, total) {
    const gap = W / (total + 1);
    const x = gap * (index + 1);
    const elevationScale = 2.2;
    const y = baseY - peaks[index].elevation * elevationScale;
    return { x, y };
  }

  function peakPoly(index, total) {
    const { x, y } = peakPos(index, total);
    const w = 64;
    const h = baseY - y;
    return `${x},${baseY} ${x - w * 0.5},${baseY} ${x - w * 0.25},${y + h * 0.3} ${x},${y} ${x + w * 0.25},${y + h * 0.3} ${x + w * 0.5},${baseY}`;
  }

  function pathBetween(i, j, total) {
    const a = peakPos(i, total);
    const b = peakPos(j, total);
    const midY = Math.min(a.y, b.y) - 40;
    return `M ${a.x} ${a.y + 20} Q ${(a.x + b.x) / 2} ${midY} ${b.x} ${b.y + 20}`;
  }

  const contours = [
    "M 0 480 Q 200 460 400 470 T 800 465 T 1000 480",
    "M 0 440 Q 250 400 500 420 T 1000 430",
    "M 0 380 Q 300 320 600 350 T 1000 360",
    "M 0 300 Q 350 220 700 260 T 1000 280",
    "M 0 200 Q 400 120 800 160 T 1000 180"
  ];

  return (
    <div className="ceiling-landscape">
      <div className="landscape-topbar">
        <div className="landscape-title-group">
          <Mountain size={18} className="landscape-title-icon" />
          <div>
            <h2 className="landscape-title">Component Ceiling Landscape</h2>
            <p className="landscape-subtitle">
              {domain === "gan"
                ? "Gan S0 decomposition — seven peaks, one summit"
                : "ExECT component map — ceilings, substrates, and open terrain"}
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
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="xMidYMid meet"
          className="landscape-svg"
        >
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f3f1ee" />
              <stop offset="100%" stopColor="#faf9f7" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background */}
          <rect width={W} height={H} fill="url(#skyGrad)" />

          {/* Fog layers */}
          <g className={mounted ? "fog-layer is-visible" : "fog-layer"}>
            <ellipse cx="200" cy="420" rx="180" ry="30" fill="#e4e2df" opacity="0.35" />
            <ellipse cx="750" cy="400" rx="220" ry="40" fill="#e4e2df" opacity="0.3" />
            <ellipse cx="500" cy="350" rx="300" ry="50" fill="#e4e2df" opacity="0.2" />
          </g>

          {/* Contour lines */}
          <g className="contour-lines">
            {contours.map((d, i) => (
              <path
                key={i}
                d={d}
                className={mounted ? "contour-line is-drawn" : "contour-line"}
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </g>

          {/* Flowing rivers between peaks */}
          <g className="flow-paths">
            {peaks.map((_, i) => {
              if (i >= peaks.length - 1) return null;
              const d = pathBetween(i, i + 1, peaks.length);
              return (
                <g key={`flow-${i}`}>
                  <path d={d} className="flow-river" />
                  <path d={d} className="flow-particle" style={{ animationDelay: `${i * 0.4}s` }} />
                </g>
              );
            })}
          </g>

          {/* Base line */}
          <line x1="0" y1={baseY} x2={W} y2={baseY} className="landscape-base" />

          {/* Peaks */}
          {peaks.map((peak, i) => {
            const { x, y } = peakPos(i, peaks.length);
            const meta = STATUS_META[peak.status] || STATUS_META.diagnostic;
            const isHovered = hoveredId === peak.id;
            const isSelected = selectedId === peak.id;
            const isOpen = peak.status === "mechanism_open";

            return (
              <g
                key={peak.id}
                className={`peak-group ${isHovered ? "is-hovered" : ""} ${isSelected ? "is-selected" : ""} ${mounted ? "is-mounted" : ""}`}
                style={{ animationDelay: `${0.3 + i * 0.12}s` }}
                onMouseEnter={() => setHoveredId(peak.id)}
                onMouseLeave={() => setHoveredId(null)}
                onClick={() => setSelectedId(selectedId === peak.id ? null : peak.id)}
                transform={`translate(${x}, ${y})`}
              >
                {/* Pulse halo for open mechanisms */}
                {isOpen && (
                  <circle
                    cx="0"
                    cy={(baseY - y) * 0.3}
                    r="50"
                    fill="none"
                    stroke={meta.colour}
                    strokeWidth="1.5"
                    opacity="0.25"
                    className="pulse-halo"
                  />
                )}

                {/* Mountain body */}
                <polygon
                  points={peakPoly(i, peaks.length).split(" ").map((pair, idx) => {
                    const [px, py] = pair.split(",");
                    return `${parseFloat(px) - x},${parseFloat(py) - y}`;
                  }).join(" ")}
                  fill={meta.colour}
                  opacity={peak.status === "rejected" ? 0.25 : 0.12}
                  stroke={meta.colour}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  strokeLinejoin="round"
                  className="peak-body"
                />

                {/* Snow cap */}
                <polygon
                  points={(() => {
                    const w = 64;
                    const h = baseY - y;
                    const pts = [
                      `0,0`,
                      `${-w * 0.12},${h * 0.15}`,
                      `${w * 0.12},${h * 0.15}`
                    ];
                    return pts.join(" ");
                  })()}
                  fill="#ffffff"
                  opacity={peak.status === "rejected" ? 0.3 : 0.9}
                  className="peak-cap"
                />

                {/* Status icon */}
                <g transform={`translate(-6, ${(baseY - y) * 0.45})`}>
                  <meta.icon size={12} color={meta.colour} strokeWidth={2.5} />
                </g>

                {/* Label */}
                <text
                  y={baseY - y + 22}
                  textAnchor="middle"
                  className="peak-label"
                >
                  {peak.name}
                </text>
                {peak.metric && (
                  <text
                    y={baseY - y + 38}
                    textAnchor="middle"
                    className="peak-metric"
                  >
                    {peak.metric}
                  </text>
                )}

                {/* Elevation tick */}
                <line
                  x1="-40"
                  y1={baseY - y}
                  x2="-28"
                  y2={baseY - y}
                  stroke={meta.colour}
                  strokeWidth="1"
                  opacity="0.4"
                />
                <text
                  x="-46"
                  y={baseY - y + 4}
                  textAnchor="end"
                  className="peak-elev-label"
                >
                  {peak.elevation}m
                </text>
              </g>
            );
          })}

          {/* Compass */}
          <g transform="translate(920, 60)" className={mounted ? "compass is-visible" : "compass"}>
            <circle r="28" fill="#fff" stroke="#d4d2cf" strokeWidth="1.5" />
            <Compass size={20} color="#6b6b6b" strokeWidth={1.5} transform="translate(-10, -10)" />
            <text y="42" textAnchor="middle" className="compass-label">Axis 1-3</text>
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

      {/* Ambient wind particles */}
      <div className="wind-layer">
        {[...Array(6)].map((_, i) => (
          <Wind
            key={i}
            size={16 + i * 4}
            className="wind-particle"
            style={{ animationDelay: `${i * 1.2}s`, top: `${15 + i * 12}%` }}
            color="#d4d2cf"
            strokeWidth={1}
          />
        ))}
      </div>
    </div>
  );
}
