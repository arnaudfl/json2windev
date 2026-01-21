from __future__ import annotations
from pathlib import Path
from json2windev.core.infer import parse_json, infer_schema
from json2windev.rules.loader import load_rules
from json2windev.renderers.windev import WinDevRenderer

def generate_windev_from_json(json_text: str, rules_path: str | Path) -> str:
    rules = load_rules(rules_path)
    data = parse_json(json_text)
    schema = infer_schema(data)
    renderer = WinDevRenderer(rules)
    return renderer.render(schema)
