from __future__ import annotations

from typing import Dict, List, Set
from json2windev.core.schema import SchemaNode
from json2windev.rules.loader import Rules
from json2windev.utils.naming import pascal_case


def assign_type_names(root: SchemaNode, rules: Rules) -> None:
    """
    Assigns .type_name on object nodes, deterministically.
    Single source of truth used by all renderers.
    """

    if root.kind != "object":
        raise ValueError("Root JSON must be an object to assign WinDev type names.")

    type_prefix: str = rules.structure["type_prefix"]
    root_name: str = rules.result["type_name"]

    used_type_names: Set[str] = set()
    sig_to_name: Dict[str, str] = {}

    def node_signature(node: SchemaNode) -> str:
        if node.kind != "object":
            return node.kind
        parts: List[str] = []
        for k in sorted(node.fields.keys()):
            parts.append(k + ":" + node_signature(node.fields[k]))
        return "object{" + ",".join(parts) + "}"

    def unique_type_name(proposed: str, node: SchemaNode) -> str:
        sig = node_signature(node)
        # Reuse same name for identical signature
        if sig in sig_to_name:
            return sig_to_name[sig]

        base = proposed
        name = base
        n = 1
        while name in used_type_names:
            n += 1
            name = f"{base}{n}"

        used_type_names.add(name)
        sig_to_name[sig] = name
        return name

    def assign(node: SchemaNode, suggested: str) -> None:
        if node.kind == "object":
            if node.type_name is None:
                node.type_name = unique_type_name(suggested, node)

            # Recurse fields
            for key, child in node.fields.items():
                if child.kind == "object":
                    sugg = type_prefix + pascal_case(key)
                    if sugg in used_type_names:
                        # add parent context
                        parent_base = node.type_name.replace(type_prefix, "")
                        sugg = type_prefix + pascal_case(parent_base) + pascal_case(key)
                    assign(child, sugg)

                elif child.kind == "array" and child.item is not None and child.item.kind == "object":
                    sugg = type_prefix + pascal_case(key) + "Item"
                    if sugg in used_type_names:
                        parent_base = node.type_name.replace(type_prefix, "")
                        sugg = type_prefix + pascal_case(parent_base) + pascal_case(key) + "Item"
                    assign(child.item, sugg)

                elif child.kind == "array" and child.item is not None:
                    # recurse inside arrays even if scalar/variant (may contain nested arrays/objects)
                    assign(child.item, suggested)

        elif node.kind == "array" and node.item is not None:
            assign(node.item, suggested)

    # Root
    root.type_name = root_name
    used_type_names.add(root_name)
    assign(root, root_name)
