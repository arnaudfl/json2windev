from json2windev.core.input import parse_json
from json2windev.core.infer import infer_schema
from json2windev.renderers.windev import WinDevRenderer
from json2windev.rules.loader import load_rules


def generate_windev_from_json(json_text: str, rules_path: str = "config/windev_rules.yaml") -> str:
    rules = load_rules(rules_path)
    data = parse_json(json_text)
    schema = infer_schema(data)
    return WinDevRenderer(rules).render(schema)
