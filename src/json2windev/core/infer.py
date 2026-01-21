from __future__ import annotations
import json
from typing import Any
from .schema import SchemaNode
from .merge import merge

def parse_json(text: str) -> Any:
    return json.loads(text)

def infer_schema(value: Any) -> SchemaNode:
    if value is None:
        return SchemaNode("null")
    if isinstance(value, bool):
        return SchemaNode("boolean")
    if isinstance(value, int) and not isinstance(value, bool):
        return SchemaNode("number_int")
    if isinstance(value, float):
        return SchemaNode("number_real")
    if isinstance(value, str):
        return SchemaNode("string")
    if isinstance(value, list):
        if not value:
            return SchemaNode("array", item=SchemaNode("null"))
        item = infer_schema(value[0])
        for v in value[1:]:
            item = merge(item, infer_schema(v))
        return SchemaNode("array", item=item)
    if isinstance(value, dict):
        node = SchemaNode("object")
        for k, v in value.items():
            node.fields[k] = infer_schema(v)
        return node
    return SchemaNode("variant")
