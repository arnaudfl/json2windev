from pathlib import Path
from json2windev.rules.loader import load_rules
from json2windev.core.infer import parse_json, infer_schema
from json2windev.renderers.markdown import MarkdownRenderer

def test_glossary_markdown_matches_expected():
    repo = Path(__file__).resolve().parents[1]
    rules = load_rules(repo / "config" / "windev_rules.yaml")

    json_text = (repo / "docs" / "examples" / "glossary.json").read_text(encoding="utf-8")
    data = parse_json(json_text)
    schema = infer_schema(data)

    out = MarkdownRenderer(rules).render(schema).strip()
    expected = (repo / "docs" / "examples" / "glossary_expected.md").read_text(encoding="utf-8").strip()

    assert out == expected
