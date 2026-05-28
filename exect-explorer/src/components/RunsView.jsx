import React from "react";
import {
  BrainCircuit,
  ListFilter,
  RadioTower,
  GitBranch,
  Database,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Trophy
} from "lucide-react";

const STATUS_LABEL = {
  paper_frozen: "paper-frozen",
  workspace_candidate: "workspace candidate",
};

const DEFAULT_METRIC_LABELS = {
  micro_f1: "Micro F1",
  micro_precision: "Precision",
  micro_recall: "Recall",
  evidence_support: "Evidence",
};

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "not stated";
  return String(value);
}

export default function RunsView({
  catalog,
  selectedTask,
  selectedRunId,
  selectedRun,
  onSelectTask,
  onSelectRun,
  onViewDocument
}) {
  const tasks = catalog?.tasks || [];
  const task = tasks.find((item) => item.id === selectedTask);
  const taskRuns = (catalog?.runs || []).filter((run) => run.task === selectedTask);
  const metrics = selectedRun?.metrics || {};
  const metricLabels = catalog?.metric_labels || DEFAULT_METRIC_LABELS;

  // Compile list of documents and their outcomes
  const documentsList = React.useMemo(() => {
    if (!selectedRun?.documents) return [];
    return Object.entries(selectedRun.documents).map(([id, doc]) => {
      const pipeline = doc.pipeline || [];
      const stats = {
        matched: 0,
        warn: 0,
        bad: 0,
        total: pipeline.length
      };
      pipeline.forEach((step) => {
        if (step.outcome === "matched") stats.matched++;
        else if (step.outcome === "evidence_issue") stats.warn++;
        else stats.bad++;
      });
      return { id, stats };
    });
  }, [selectedRun]);

  return (
    <div className="runs-view">
      <div className="runs-view-header">
        <div className="runs-title-group">
          <BrainCircuit size={20} className="runs-title-icon" />
          <div>
            <h2>Model Validation Results</h2>
            <p>High-level metrics, run surface, and document index</p>
          </div>
        </div>
      </div>

      <div className="runs-view-grid">
        {/* Left column: Controls and summary stats */}
        <div className="runs-control-col">
          <div className="runs-card">
            <h3>Configuration</h3>
            <div className="runs-control-grid">
              <label>
                <span><ListFilter size={12} /> Task Scope</span>
                <select value={selectedTask} onChange={(e) => onSelectTask(e.target.value)}>
                  {tasks.map((item) => (
                    <option key={item.id} value={item.id}>{item.label}</option>
                  ))}
                </select>
              </label>
              <label>
                <span><RadioTower size={12} /> Model Run Selection</span>
                <select value={selectedRunId || ""} onChange={(e) => onSelectRun(e.target.value)}>
                  {taskRuns.map((run) => (
                    <option key={run.run_id} value={run.run_id}>
                      {run.best ? "⭐ " : ""}{run.model_label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            {task && <p className="runs-scope-desc">{task.scope}</p>}
          </div>

          {selectedRun && (
            <>
              <div className="runs-card">
                <div className="runs-card-header">
                  <h3>Metrics Summary</h3>
                  <span className={`run-status-badge ${selectedRun.evidence_status}`}>
                    {STATUS_LABEL[selectedRun.evidence_status] || selectedRun.evidence_status}
                  </span>
                </div>
                <div className="runs-metrics-grid">
                  <div className="metric-box">
                    <span className="metric-lbl">{metricLabels.micro_f1}</span>
                    <span className="metric-val">{formatValue(metrics.micro_f1)}%</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-lbl">{metricLabels.micro_precision}</span>
                    <span className="metric-val">{formatValue(metrics.micro_precision)}%</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-lbl">{metricLabels.micro_recall}</span>
                    <span className="metric-val">{formatValue(metrics.micro_recall)}%</span>
                  </div>
                  <div className="metric-box">
                    <span className="metric-lbl">{metricLabels.evidence_support}</span>
                    <span className="metric-val">{formatValue(metrics.evidence_support)}%</span>
                  </div>
                </div>
              </div>

              <div className="runs-card">
                <h3>Run Surface</h3>
                <div className="surface-grid">
                  <div><span>Schema Level</span><strong>{selectedRun.schema_level}</strong></div>
                  <div><span>Scorer Mode</span><strong>{selectedRun.scorer_mode}</strong></div>
                  <div><span>Program</span><strong>{selectedRun.program_variant}</strong></div>
                  <div><span>Prompt Ver</span><strong>{selectedRun.prompt_version}</strong></div>
                </div>
              </div>

              <div className="runs-card">
                <h3>Component Family F1</h3>
                <div className="family-f1-chart">
                  {Object.entries(metrics.field_f1 || {}).map(([field, value]) => (
                    <div key={field} className="runs-f1-row">
                      <span className="f1-row-lbl">{field.replace(/_/g, " ")}</span>
                      <div className="f1-row-bar-wrap">
                        <div
                          className="f1-row-bar"
                          style={{ width: `${Math.max(0, Math.min(100, value || 0))}%` }}
                        />
                      </div>
                      <strong className="f1-row-val">{formatValue(value)}%</strong>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Right column: Document index for this run */}
        <div className="runs-docs-col">
          <div className="runs-card flex-1">
            <div className="runs-card-header">
              <h3>Predicted Clinical Letters</h3>
              <span className="docs-count-badge">{documentsList.length} documents predicted</span>
            </div>
            
            <div className="docs-table-wrapper">
              <table className="docs-table">
                <thead>
                  <tr>
                    <th>Letter ID</th>
                    <th>Prediction Steps</th>
                    <th>Match Outcomes</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {documentsList.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="empty-table-cell">
                        No document predictions found for this model run.
                      </td>
                    </tr>
                  ) : (
                    documentsList.map((doc) => (
                      <tr key={doc.id} className="docs-table-row">
                        <td className="doc-id-cell">{doc.id}</td>
                        <td className="doc-steps-cell">{doc.stats.total} fields predicted</td>
                        <td className="doc-outcomes-cell">
                          <div className="outcome-chips">
                            <span className="outcome-chip matched" title="Matched predictions">
                              <CheckCircle size={10} /> {doc.stats.matched}
                            </span>
                            {doc.stats.warn > 0 && (
                              <span className="outcome-chip warn" title="Evidence issues">
                                <AlertTriangle size={10} /> {doc.stats.warn}
                              </span>
                            )}
                            {doc.stats.bad > 0 && (
                              <span className="outcome-chip bad" title="Mismatched/unsupported predictions">
                                <XCircle size={10} /> {doc.stats.bad}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="doc-action-cell">
                          <button
                            className="doc-open-btn"
                            onClick={() => onViewDocument(doc.id)}
                            title={`Inspect ${doc.id} pipeline trace`}
                          >
                            <span>Inspect</span>
                            <ArrowRight size={12} />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
