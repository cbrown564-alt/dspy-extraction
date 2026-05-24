import React from "react";
import {
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  Database,
  FlaskConical,
  GitBranch,
  ListFilter,
  RadioTower,
} from "lucide-react";

const STATUS_LABEL = {
  paper_frozen: "paper-frozen",
  workspace_candidate: "workspace candidate",
};

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
  catalog,
  letterId,
  selectedTask,
  selectedRunId,
  selectedRun,
  pipeline,
  onSelectTask,
  onSelectRun,
}) {
  const tasks = catalog?.tasks || [];
  const task = tasks.find((item) => item.id === selectedTask);
  const taskRuns = (catalog?.runs || []).filter((run) => run.task === selectedTask);
  const metrics = selectedRun?.metrics || {};
  const steps = pipeline?.pipeline || [];

  return (
    <div className="side-panel model-panel">
      <div className="panel-header">
        <BrainCircuit size={15} />
        <span>Model pipeline</span>
      </div>

      <div className="panel-section">
        <div className="model-control-grid">
          <label>
            <span><ListFilter size={12} /> Task</span>
            <select value={selectedTask} onChange={(e) => onSelectTask(e.target.value)}>
              {tasks.map((item) => (
                <option key={item.id} value={item.id}>{item.label}</option>
              ))}
            </select>
          </label>
          <label>
            <span><RadioTower size={12} /> Model run</span>
            <select value={selectedRunId || ""} onChange={(e) => onSelectRun(e.target.value)}>
              {taskRuns.map((run) => (
                <option key={run.run_id} value={run.run_id}>
                  {run.best ? "Best - " : ""}{run.model_label}
                </option>
              ))}
            </select>
          </label>
        </div>
        {task && <p className="panel-lead">{task.scope}</p>}
      </div>

      {selectedRun && (
        <div className="panel-section">
          <div className="model-run-card">
            <div className="run-card-top">
              <div>
                <div className="candidate-name">{selectedRun.model_label}</div>
                <div className="candidate-meta">{selectedRun.run_id}</div>
              </div>
              <span className={`run-status ${selectedRun.evidence_status}`}>
                {STATUS_LABEL[selectedRun.evidence_status] || selectedRun.evidence_status}
              </span>
            </div>
            <div className="candidate-scores">
              <div className="c-score">
                <span className="c-label">Micro F1</span>
                <span className="c-val">{formatValue(metrics.micro_f1)}%</span>
              </div>
              <div className="c-score">
                <span className="c-label">Precision</span>
                <span className="c-val">{formatValue(metrics.micro_precision)}%</span>
              </div>
              <div className="c-score">
                <span className="c-label">Recall</span>
                <span className="c-val">{formatValue(metrics.micro_recall)}%</span>
              </div>
              <div className="c-score">
                <span className="c-label">Evidence</span>
                <span className="c-val">{formatValue(metrics.evidence_support)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedRun && (
        <div className="panel-section">
          <div className="section-title">
            <GitBranch size={12} />
            Run surface
          </div>
          <div className="surface-list">
            <div><span>Schema</span><strong>{selectedRun.schema_level}</strong></div>
            <div><span>Scorer</span><strong>{selectedRun.scorer_mode}</strong></div>
            <div><span>Program</span><strong>{selectedRun.program_variant}</strong></div>
            <div><span>Prompt</span><strong>{selectedRun.prompt_version}</strong></div>
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

      <div className="panel-section">
        <div className="section-title">Family F1</div>
        <div className="field-f1-list">
          {Object.entries(metrics.field_f1 || {}).map(([field, value]) => (
            <div key={field} className="field-f1-row">
              <span>{field.replace(/_/g, " ")}</span>
              <div>
                <i style={{ width: `${Math.max(0, Math.min(100, value || 0))}%` }} />
              </div>
              <strong>{formatValue(value)}%</strong>
            </div>
          ))}
          {selectedRun?.evidence_status === "workspace_candidate" && (
            <div className="challenge-box compact">
              <AlertCircle size={12} />
              <p>S5 is shown from current workspace artifacts, not the frozen paper table.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
