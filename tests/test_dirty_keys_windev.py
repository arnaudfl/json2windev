from pathlib import Path

from json2windev.core.input import parse_json
from json2windev.core.infer import infer_schema
from json2windev.rules.loader import load_rules
from json2windev.renderers.windev import WinDevRenderer


def test_dirty_keys_generate_valid_fields_and_keep_serialize():
    repo = Path(__file__).resolve().parents[1]
    rules = load_rules(repo / "config" / "windev_rules.yaml")

    json_text = (repo / "tests" / "fixtures" / "dirty_keys.json").read_text(encoding="utf-8")
    data = parse_json(json_text)
    schema = infer_schema(data)

    out = WinDevRenderer(rules).render(schema)

    # Serialize must keep original JSON keys
    assert '<serialize="123abc">' in out
    assert '<serialize="@id">' in out
    assert '<serialize="vehicle-build.id">' in out
    assert '<serialize="type-approval">' in out
    assert '<serialize="">' in out
    assert '<serialize="SELON">' in out
    assert '<serialize="FIN">' in out

    # Must not crash / must produce a structure for root + result
    assert "STRoot est une structure" in out
    assert "STResult est une structure" in out
    assert "Resultat est un STResult" in out
