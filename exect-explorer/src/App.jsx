import React, { useEffect, useReducer, useState, useCallback } from "react";
import {
  BookOpen, Microscope, Stethoscope, BrainCircuit,
  Clock, LayoutList, PenTool, Mountain,
  ChevronLeft, ChevronRight, AlertTriangle
} from "lucide-react";
import LetterSelector from "./components/LetterSelector.jsx";
import LensBar from "./components/LensBar.jsx";
import EntityLayers from "./components/EntityLayers.jsx";
import ReaderView from "./components/ReaderView.jsx";
import TimelineView from "./components/TimelineView.jsx";
import OraclePanel from "./components/OraclePanel.jsx";
import ClinicianPanel from "./components/ClinicianPanel.jsx";
import ModelPanel from "./components/ModelPanel.jsx";
import AnnotateView from "./components/AnnotateView.jsx";
import ShortcutsModal from "./components/ShortcutsModal.jsx";
import CeilingLandscape from "./components/CeilingLandscape.jsx";
import AnnotationProgress from "./components/AnnotationProgress.jsx";

const ENTITY_TYPES = [
  "Diagnosis",
  "Prescription",
  "SeizureFrequency",
  "PatientHistory",
  "Investigations",
  "BirthHistory",
  "Onset",
  "EpilepsyCause",
  "WhenDiagnosed",
];

const LENSES = [
  { id: "annotator", label: "Annotator", icon: BookOpen, desc: "The gold-standard layers" },
  { id: "oracle", label: "Oracle", icon: Microscope, desc: "Hard ceilings & flaws" },
  { id: "clinician", label: "Clinician", icon: Stethoscope, desc: "Clinical utility view" },
  { id: "model", label: "Model", icon: BrainCircuit, desc: "Run outputs and pipeline trace" },
];


const VIEWS = [
  { id: "reader", label: "Reader", icon: LayoutList },
  { id: "timeline", label: "Timeline", icon: Clock },
  { id: "annotate", label: "Annotate", icon: PenTool },
  { id: "landscape", label: "Landscape", icon: Mountain },
];

function appReducer(state, action) {
  switch (action.type) {
    case "SET_DATASET": {
      const defaultId = action.payload === "gan" ? "gan_0" : "EA0001";
      const layers = action.payload === "gan" ? ["SeizureFrequency"] : ENTITY_TYPES;
      return {
        ...state,
        dataset: action.payload,
        letterId: defaultId,
        letterData: null,
        selectedEntity: null,
        visibleLayers: new Set(layers),
        modelCatalog: null,
        selectedTask: null,
        selectedRunId: null,
      };
    }
    case "SET_LETTER":
      return { ...state, letterId: action.payload, letterData: null, selectedEntity: null };
    case "SET_LETTER_DATA":
      return { ...state, letterData: action.payload };
    case "SET_LENS":
      return { ...state, lens: action.payload };
    case "SET_VIEW":
      return { ...state, view: action.payload };
    case "TOGGLE_LAYER": {
      const next = new Set(state.visibleLayers);
      if (next.has(action.payload)) next.delete(action.payload);
      else next.add(action.payload);
      return { ...state, visibleLayers: next };
    }
    case "SET_LAYERS":
      return { ...state, visibleLayers: new Set(action.payload) };
    case "SET_HOVERED":
      return { ...state, hoveredEntity: action.payload };
    case "SET_SELECTED":
      return { ...state, selectedEntity: action.payload };
    case "SET_INDEX":
      return { ...state, index: action.payload };
    case "CLEAR_MODEL_CATALOG":
      return {
        ...state,
        modelCatalog: null,
        selectedTask: null,
        selectedRunId: null,
      };
    case "SET_MODEL_CATALOG": {
      const firstTask = action.payload?.tasks?.[0];
      return {
        ...state,
        modelCatalog: action.payload,
        selectedTask: firstTask?.id || null,
        selectedRunId: firstTask?.default_run_id || null,
      };
    }
    case "SET_MODEL_TASK": {
      const task = state.modelCatalog?.tasks?.find((item) => item.id === action.payload);
      return {
        ...state,
        selectedTask: action.payload,
        selectedRunId: task?.default_run_id || state.selectedRunId,
      };
    }
    case "SET_MODEL_RUN":
      return { ...state, selectedRunId: action.payload };
    case "NEXT_LETTER": {
      if (!state.index) return state;
      const ids = state.index.letters.map((l) => l.id);
      const idx = ids.indexOf(state.letterId);
      const nextId = idx < ids.length - 1 ? ids[idx + 1] : ids[0];
      return { ...state, letterId: nextId, letterData: null, selectedEntity: null };
    }
    case "PREV_LETTER": {
      if (!state.index) return state;
      const ids = state.index.letters.map((l) => l.id);
      const idx = ids.indexOf(state.letterId);
      const prevId = idx > 0 ? ids[idx - 1] : ids[ids.length - 1];
      return { ...state, letterId: prevId, letterData: null, selectedEntity: null };
    }
    case "TOGGLE_SHORTCUTS":
      return { ...state, showShortcuts: !state.showShortcuts };
    default:
      return state;
  }
}

const initialState = {
  dataset: "exect",
  letterId: "EA0001",
  letterData: null,
  lens: "annotator",
  view: "reader",
  visibleLayers: new Set(ENTITY_TYPES),
  hoveredEntity: null,
  selectedEntity: null,
  index: null,
  modelCatalog: null,
  selectedTask: "S1",
  selectedRunId: null,
  showShortcuts: false,
};

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("App render failed:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="loading-screen">
          <AlertTriangle size={32} className="load-err-icon" />
          <p className="load-title">The app hit a render error</p>
          <p className="load-sub">{this.state.error.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

function AppContent() {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load index
  useEffect(() => {
    setLoading(true);
    const indexPath = state.dataset === "gan" ? "/data/index_gan.json" : "/data/index.json";
    fetch(indexPath)
      .then((r) => r.json())
      .then((data) => {
        dispatch({ type: "SET_INDEX", payload: data });
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [state.dataset]);

  // Load model catalog
  useEffect(() => {
    dispatch({ type: "CLEAR_MODEL_CATALOG" });
    const catalogPath = state.dataset === "gan" ? "/data/model_catalog_gan.json" : "/data/model_catalog.json";
    fetch(catalogPath)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) dispatch({ type: "SET_MODEL_CATALOG", payload: data });
      })
      .catch((e) => console.warn("Failed to load model catalog:", e));
  }, [state.dataset]);

  // Load letter data when letterId changes
  useEffect(() => {
    if (!state.letterId) return;
    fetch(`/data/${state.letterId}.json`)
      .then((r) => r.json())
      .then((data) => dispatch({ type: "SET_LETTER_DATA", payload: data }))
      .catch((e) => console.error("Failed to load letter:", e));
  }, [state.letterId]);

  const handleKeyDown = useCallback(
    (e) => {
      const tag = e.target?.tagName?.toLowerCase();
      const isTyping = tag === "input" || tag === "textarea" || tag === "select" || e.target?.isContentEditable;
      if (e.key === "?" && !e.metaKey && !e.ctrlKey && !e.altKey && !isTyping) {
        e.preventDefault();
        dispatch({ type: "TOGGLE_SHORTCUTS" });
      }
      if (e.key === "ArrowRight" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        dispatch({ type: "NEXT_LETTER" });
      }
      if (e.key === "ArrowLeft" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        dispatch({ type: "PREV_LETTER" });
      }
    },
    [state.index, state.letterId]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="load-spinner" />
        <p className="load-title">Preparing the clinical theatre</p>
        <p className="load-sub">
          {state.dataset === "gan"
            ? "Loading annotations and indexing 1,500 Gan records…"
            : "Loading annotations and indexing 200 ExECT letters…"}
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-screen">
        <AlertTriangle size={32} className="load-err-icon" />
        <p className="load-title">Failed to load data</p>
        <p className="load-sub">{error}</p>
      </div>
    );
  }

  const currentMeta = state.index?.letters.find((l) => l.id === state.letterId);
  const selectedRun = state.modelCatalog?.runs?.find((run) => run.run_id === state.selectedRunId) || null;
  const selectedPipeline = selectedRun?.documents?.[state.letterId] || null;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Microscope size={18} />
          <span>ExECT Explorer</span>
        </div>
        <div className="dataset-switcher">
          <button
            className={state.dataset === "exect" ? "is-active" : ""}
            onClick={() => dispatch({ type: "SET_DATASET", payload: "exect" })}
          >
            ExECTv2
          </button>
          <button
            className={state.dataset === "gan" ? "is-active" : ""}
            onClick={() => dispatch({ type: "SET_DATASET", payload: "gan" })}
          >
            Gan 2026
          </button>
        </div>
        <AnnotationProgress letters={state.index?.letters || []} />
        <LetterSelector
          letters={state.index?.letters || []}
          currentId={state.letterId}
          onSelect={(id) => dispatch({ type: "SET_LETTER", payload: id })}
        />
        <EntityLayers
          types={state.dataset === "gan" ? ["SeizureFrequency"] : ENTITY_TYPES}
          colours={state.index?.entity_colours || {}}
          visible={state.visibleLayers}
          onToggle={(t) => dispatch({ type: "TOGGLE_LAYER", payload: t })}
        />
      </aside>

      <div className="main">
        <header className="topbar">
          <div className="nav-arrows">
            <button onClick={() => dispatch({ type: "PREV_LETTER" })} title="Previous letter (Ctrl/Cmd + ←)">
              <ChevronLeft size={16} />
            </button>
            <span className="letter-id">{state.letterId}</span>
            <button onClick={() => dispatch({ type: "NEXT_LETTER" })} title="Next letter (Ctrl/Cmd + →)">
              <ChevronRight size={16} />
            </button>
          </div>

          <LensBar
            lenses={LENSES}
            active={state.lens}
            onSelect={(id) => dispatch({ type: "SET_LENS", payload: id })}
          />

          <div className="view-toggle">
            {VIEWS.map((v) => (
              <button
                key={v.id}
                className={state.view === v.id ? "is-active" : ""}
                onClick={() => dispatch({ type: "SET_VIEW", payload: v.id })}
              >
                <v.icon size={14} />
                <span>{v.label}</span>
              </button>
            ))}
          </div>
        </header>

        <div className="stage">
          {state.view === "reader" && (
            <ReaderView
              data={state.letterData}
              lens={state.lens}
              visibleLayers={state.visibleLayers}
              hoveredEntity={state.hoveredEntity}
              selectedEntity={state.selectedEntity}
              modelPipeline={state.lens === "model" ? selectedPipeline : null}
              onHover={(id) => dispatch({ type: "SET_HOVERED", payload: id })}
              onSelect={(id) => dispatch({ type: "SET_SELECTED", payload: id })}
            />
          )}
          {state.view === "timeline" && (
            <TimelineView
              data={state.letterData}
              lens={state.lens}
              visibleLayers={state.visibleLayers}
            />
          )}
          {state.view === "annotate" && (
            <AnnotateView
              data={state.letterData}
              visibleLayers={state.visibleLayers}
            />
          )}
          {state.view === "landscape" && <CeilingLandscape />}

          {state.view === "reader" && state.lens === "oracle" && state.letterData && (
            <OraclePanel data={state.letterData} oracleRates={state.index?.oracle_rates || {}} />
          )}
          {state.view === "reader" && state.lens === "clinician" && state.letterData && (
            <ClinicianPanel data={state.letterData} onSelectEntity={(id) => dispatch({ type: "SET_SELECTED", payload: id })} />
          )}
          {state.view === "reader" && state.lens === "model" && (
            <ModelPanel
              catalog={state.modelCatalog}
              letterId={state.letterId}
              selectedTask={state.selectedTask}
              selectedRunId={state.selectedRunId}
              selectedRun={selectedRun}
              pipeline={selectedPipeline}
              onSelectTask={(id) => dispatch({ type: "SET_MODEL_TASK", payload: id })}
              onSelectRun={(id) => dispatch({ type: "SET_MODEL_RUN", payload: id })}
            />
          )}
        </div>

        <footer className="statusbar">
          <span>{currentMeta ? `${currentMeta.type_counts ? Object.values(currentMeta.type_counts).reduce((a, b) => a + b, 0) : 0} entities` : "—"}</span>
          <span className="sep">·</span>
          <span>{state.letterData?.flaws?.length || 0} flaw{state.letterData?.flaws?.length === 1 ? "" : "s"} detected</span>
          <span className="sep">·</span>
          <span className="hint">Ctrl/Cmd + ← → to navigate · ? for help</span>
        </footer>
      </div>

      {state.showShortcuts && (
        <ShortcutsModal onClose={() => dispatch({ type: "TOGGLE_SHORTCUTS" })} />
      )}
    </div>
  );
}

export default function App() {
  return (
    <AppErrorBoundary>
      <AppContent />
    </AppErrorBoundary>
  );
}
