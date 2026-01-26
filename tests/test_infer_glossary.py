from pathlib import Path
from json2windev.core.input import parse_json
from json2windev.core.infer import infer_schema


def test_infer_root_is_object():
    repo = Path(__file__).resolve().parents[1]
    data = parse_json((repo / "docs" / "examples" / "glossary.json").read_text(encoding="utf-8"))
    schema = infer_schema(data)
    assert schema.kind == "object"
    assert "glossary" in schema.fields
