from __future__ import annotations
from .schema import SchemaNode

def merge(a: SchemaNode, b: SchemaNode) -> SchemaNode:
    if a.kind == b.kind:
        if a.kind == "object":
            out = SchemaNode("object", fields=dict(a.fields))
            for k, vb in b.fields.items():
                out.fields[k] = merge(out.fields[k], vb) if k in out.fields else vb
            return out
        if a.kind == "array":
            if a.item is None: return b
            if b.item is None: return a
            return SchemaNode("array", item=merge(a.item, b.item))
        return a

    if "null" in {a.kind, b.kind}:
        return b if a.kind == "null" else a

    if {a.kind, b.kind} == {"number_int","number_real"}:
        return SchemaNode("number_real")

    return SchemaNode("variant")
