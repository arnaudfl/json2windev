from pathlib import Path

from json2windev.core.input import parse_json
from json2windev.core.infer import infer_schema
from json2windev.rules.loader import load_rules
from json2windev.renderers.markdown import MarkdownRenderer


def test_dirty_keys_markdown_contains_original_json_keys():
    repo = Path(__file__).resolve().parents[1]
    rules = load_rules(repo / "config" / "windev_rules.yaml")

    json_text = (repo / "tests" / "fixtures" / "dirty_keys.json").read_text(encoding="utf-8")
    data = parse_json(json_text)
    schema = infer_schema(data)

    md = MarkdownRenderer(rules).render(schema)

    # The structures table should show original JSON keys
    assert "`123abc`" in md
    assert "`@id`" in md
    assert "`vehicle-build.id`" in md
    assert "`type-approval`" in md
    assert "`SELON`" in md
    assert "`FIN`" in md
