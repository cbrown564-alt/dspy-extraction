import React from "react";
import {
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  Database,
  FlaskConical,
  GitBranch,
  ArrowUpRight
} from "lucide-react";

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "not stated";
  return String(value);
}

function outcomeClass(outcome) {
  if (outcome === "matched") return "ok";
  if (outcome === "evidence_issue") return "warn";
  return "bad";
}

export default function ModelPanel({
  letterId,
  selectedRun,
  pipeline,
  onNavigateToRuns
}) {
  const steps = pipeline?.pipeline || [];

  return (
    <div className="side-panel model-panel">
      <div className="panel-header">
        <BrainCircuit size={15} />
        <span>Model pipeline</span>
      </div>

      {selectedRun && (
        <div className="panel-section">
          <div className="model-sidebar-run-summary">
            <div className="sidebar-run-label">
              <span>Active Model Run</span>
              <strong>{selectedRun.model_label}</strong>
            </div>
            <button className="sidebar-change-run-btn" onClick={onNavigateToRuns} title="Change run or view overall validation stats">
              <span>Runs Dashboard</span>
              <ArrowUpRight size={12} />
            </button>
          </div>
        </div>
      )}

      <div className="panel-section">
        <div className="section-title">
          <Database size={12} />
          Letter pipeline
        </div>
        {steps.length === 0 ? (
          <div className="challenge-box">
            <AlertCircle size={12} />
            <p>No prediction is available for {letterId} in this validation run.</p>
          </div>
        ) : (
          <div className="pipeline-list">
            {steps.map((step) => (
              <div key={step.id} className={`pipeline-step ${outcomeClass(step.outcome)}`}>
                <div className="pipeline-step-head">
                  <span>{step.field.replace(/_/g, " ")}</span>
                  <strong>{step.outcome.replace(/_/g, " ")}</strong>
                </div>
                <div className="pipeline-value">{formatValue(step.normalized_value || step.raw_value)}</div>
                <div className="pipeline-flow">
                  <div>
                    <FlaskConical size={11} />
                    <span>LLM</span>
                    <p>{formatValue(step.raw_value)}</p>
                  </div>
                  <div>
                    <CheckCircle2 size={11} />
                    <span>Rule</span>
                    <p>{formatValue(step.deterministic_step?.output)}</p>
                  </div>
                </div>
                {(step.evidence || []).length > 0 && (
                  <div className="pipeline-evidence">
                    {(step.evidence || []).slice(0, 2).map((span, idx) => (
                      <q key={idx}>{span.text}</q>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
