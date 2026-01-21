from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import yaml

class RulesError(ValueError):
    pass

@dataclass(frozen=True)
class Rules:
    raw: Dict[str, Any]

    @property
    def structure(self): return self.raw["structure"]
    @property
    def result(self): return self.raw["result"]
    @property
    def types(self): return self.raw["types"]
    @property
    def number(self): return self.raw.get("number", {"detection":"auto"})
    @property
    def array(self): return self.raw["array"]
    @property
    def null_handling(self): return self.raw.get("null_handling", {"mode":"variant"})
    @property
    def naming(self): return self.raw["naming"]
    @property
    def prefixes(self): return self.raw["prefixes"]
    @property
    def generation(self): return self.raw.get("generation", {"order":"children_first"})
    @property
    def fmt(self): return self.raw["format"]

REQUIRED_TOP_LEVEL = ["structure","result","types","array","naming","prefixes","format"]

def load_rules(path: str | Path) -> Rules:
    path = Path(path)
    if not path.exists():
        raise RulesError(f"Rules file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RulesError("Rules YAML must be a mapping (dict)")
    _validate_rules(data)
    return Rules(data)

def _validate_rules(r: Dict[str, Any]) -> None:
    for k in REQUIRED_TOP_LEVEL:
        if k not in r:
            raise RulesError(f"Missing required key in rules: {k}")
    if "type_prefix" not in r["structure"]:
        raise RulesError("structure.type_prefix is required")
    if "type_name" not in r["result"] or "var_name" not in r["result"]:
        raise RulesError("result.type_name and result.var_name are required")
    generic = r["array"].get("generic","")
    if "{item}" not in generic:
        raise RulesError("array.generic must contain '{item}' placeholder")
