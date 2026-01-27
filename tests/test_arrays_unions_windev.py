from pathlib import Path

from json2windev.core.input import parse_json
from json2windev.core.infer import infer_schema
from json2windev.rules.loader import load_rules
from json2windev.renderers.windev import WinDevRenderer


def test_arrays_and_unions_render_windev_types():
    repo = Path(__file__).resolve().parents[1]
    rules = load_rules(repo / "config" / "windev_rules.yaml")

    json_text = (repo / "tests" / "fixtures" / "arrays_unions.json").read_text(encoding="utf-8")
    data = parse_json(json_text)
    schema = infer_schema(data)

    out = WinDevRenderer(rules).render(schema)

    # Basic sanity
    assert "STRoot est une structure" in out
    assert "STResult est une structure" in out

    # Arrays: just assert they exist with serialize
    assert '<serialize="ints">' in out
    assert '<serialize="reals">' in out
    assert '<serialize="strings">' in out
    assert '<serialize="empty_array">' in out

    # Mixed arrays should end up Variant (most robust expectation)
    assert '<serialize="mixed_scalars">' in out
    assert '<serialize="mixed_with_null">' in out

    # Nullable fields should map to Variant
    assert '<serialize="nullable_field">' in out

    # Array of objects should create a structure reference (some ST...Item)
    # We don't assert exact name to avoid coupling, just check "un tableau de ST"
    assert "array_of_objects" in out  # serialize exists in structure line
    assert "un tableau de ST" in out  # should appear at least once

    # Object references should create child structures
    assert "STNullableOrObject" in out or "STNullable_or_object" in out or "STNullableOrObjectItem" in out
