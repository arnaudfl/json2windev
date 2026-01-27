from pathlib import Path

from json2windev.core.input import parse_json
from json2windev.core.infer import infer_schema
from json2windev.rules.loader import load_rules
from json2windev.renderers.markdown import MarkdownRenderer


def test_arrays_and_unions_render_markdown_sections():
    repo = Path(__file__).resolve().parents[1]
    rules = load_rules(repo / "config" / "windev_rules.yaml")

    json_text = (repo / "tests" / "fixtures" / "arrays_unions.json").read_text(encoding="utf-8")
    data = parse_json(json_text)
    schema = infer_schema(data)

    md = MarkdownRenderer(rules).render(schema)

    # Key sections exist
    assert "## Summary" in md
    assert "## Structures" in md
    assert "## Generated WinDev code" in md

    # Original keys appear in tables
    assert "`mixed_scalars`" in md
    assert "`empty_array`" in md
    assert "`array_of_objects`" in md
    assert "`nullable_field`" in md
