import pytest
from json2windev.core.input import parse_json, JsonParseError

def test_parse_json_error_has_line_col_and_snippet():
    bad = '{ "a": 1, }'  # trailing comma invalid in strict JSON
    with pytest.raises(JsonParseError) as ex:
        parse_json(bad)
    err = ex.value
    assert err.lineno is not None
    assert err.colno is not None
    assert err.snippet is not None
    assert "^" in err.snippet
