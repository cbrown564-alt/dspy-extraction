import json
from typing import Any, Iterable


def _detect_format(file_path: str, content = None) -> str:
    lower = file_path.lower()
    if lower.endswith(".jsonl"):
        return "jsonl"
    if lower.endswith(".json"):
        return "json"
    if content is not None:
        stripped = content.lstrip()
        if stripped.startswith("{") or stripped.startswith("["):
            return "json"
    return "jsonl"


def load_json(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    fmt = _detect_format(file_path, content)
    if fmt == "json":
        return json.loads(content)

    items = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        items.append(json.loads(line))
    return items


def dump_json(file_path: str, obj: Any) -> None:
    fmt = _detect_format(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        if fmt == "jsonl":
            if isinstance(obj, (list, tuple)):
                items: Iterable[Any] = obj
            else:
                items = [obj]
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False))
                f.write("\n")
        else:
            json.dump(obj, f, ensure_ascii=False, indent=2)
