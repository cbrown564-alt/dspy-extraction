"""ExECT S0/S1 field-family DSPy program compatibility facade."""
from __future__ import annotations

from importlib import import_module

_REEXPORT_MODULES = (
    "clinical_extraction.exect.s0_s1.constants",
    "clinical_extraction.exect.s0_s1.prompt_routing",
    "clinical_extraction.exect.s0_s1.signatures",
    "clinical_extraction.exect.s0_s1.modules",
    "clinical_extraction.exect.s0_s1.prediction_artifacts",
    "clinical_extraction.exect.s0_s1.optimizer_setup",
    "clinical_extraction.exect.s0_s1.metrics",
)

for _module_name in _REEXPORT_MODULES:
    _module = import_module(_module_name)
    for _name, _value in vars(_module).items():
        if _name.startswith("__"):
            continue
        globals()[_name] = _value

del import_module, _module_name, _module, _name, _value
