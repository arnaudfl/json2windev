from pathlib import Path
from json2windev import generate_windev_from_json

def test_glossary_example_matches_expected():
    repo = Path(__file__).resolve().parents[1]
    json_text = (repo / "docs" / "examples" / "glossary.json").read_text(encoding="utf-8")
    expected = (repo / "docs" / "examples" / "glossary_expected.txt").read_text(encoding="utf-8").strip()
    out = generate_windev_from_json(json_text, repo / "config" / "windev_rules.yaml").strip()
    assert out == expected
