from __future__ import annotations
from typing import Dict, List, Set, Tuple
from json2windev.core.schema import SchemaNode
from json2windev.rules.loader import Rules
from json2windev.utils.naming import pascal_case, sanitize_identifier, escape_reserved
from json2windev.core.type_naming import assign_type_names
from .base import Renderer

class WinDevRenderer(Renderer):
    def __init__(self, rules: Rules):
        super().__init__(rules)
        self._declared: Set[str] = set()

    def render(self, root: SchemaNode) -> str:
        if root.kind != "object":
            raise ValueError("Root JSON must be an object to generate STResult.")

        assign_type_names(root, self.rules)

        ordered: List[SchemaNode] = []
        self._collect_children_first(root, ordered)

        lines: List[str] = []
        for obj in ordered:
            lines.extend(self._render_structure(obj))
            if self.rules.fmt.get("blank_line_after_structure", True):
                lines.append("")

        lines.append(f"{self.rules.result['var_name']} {self.rules.result['assignment']} {self.rules.result['type_name']}")
        return "\n".join(lines).rstrip() + "\n"

    def _collect_children_first(self, node: SchemaNode, ordered: List[SchemaNode]) -> None:
        if node.kind == "object":
            for child in node.fields.values():
                self._collect_children_first(child, ordered)
            if node.type_name and node.type_name not in self._declared:
                self._declared.add(node.type_name)
                ordered.append(node)
        elif node.kind == "array" and node.item is not None:
            self._collect_children_first(node.item, ordered)

    def _render_structure(self, node: SchemaNode) -> List[str]:
        indent = self.rules.fmt["indent"]
        lines = [f"{node.type_name} {self.rules.structure['keyword']}"]
        for json_key, child in node.fields.items():
            field_name, ser = self._field_name_and_serialize(json_key, child)
            wd_type = self._wd_type(child)
            suffix = f" {ser}" if ser else ""
            lines.append(f"{indent}{field_name} est {wd_type}{suffix}")
        lines.append(self.rules.structure["end"])
        return lines

    def _field_name_and_serialize(self, json_key: str, node: SchemaNode) -> Tuple[str, str]:
        naming = self.rules.naming
        forbidden = naming.get("forbidden_chars", r"[^A-Za-z0-9_]")
        reserved = naming.get("reserved_words", [])
        escape_tpl = naming.get("escape_reserved", "_{name}")

        if naming.get("use_variable_prefixes", False):
            prefix = self._prefix_for(node)
            win_base = pascal_case(sanitize_identifier(json_key, forbidden))
            field_name = prefix + win_base
        else:
            field_name = sanitize_identifier(json_key, forbidden)

        field_name = escape_reserved(field_name, reserved, escape_tpl)

        ser = f'<serialize="{json_key}">' if naming.get("serialize_attribute", False) else ""
        return field_name, ser

    def _prefix_for(self, node: SchemaNode) -> str:
        p = self.rules.prefixes
        return {
            "string": p["string"],
            "boolean": p["boolean"],
            "number_int": p["int"],
            "number_real": p["real"],
            "array": p["array"],
            "object": p["structure"],
            "null": p["variant"],
            "variant": p["variant"],
        }.get(node.kind, p["variant"])

    def _wd_type(self, node: SchemaNode) -> str:
        t = self.rules.types
        a = self.rules.array

        if node.kind in ("null","variant"):
            return t["variant"]
        if node.kind == "string":
            return t["string"]
        if node.kind == "boolean":
            return t["boolean"]
        if node.kind == "number_int":
            return t["int"]
        if node.kind == "number_real":
            return t["real"]
        if node.kind == "object":
            return f"un {node.type_name}"
        if node.kind == "array":
            if node.item is None or node.item.kind == "null":
                return a["empty"]
            if node.item.kind == "variant":
                return a["empty"] if a.get("heterogeneous") == "variant" else a["empty"]
            if node.item.kind == "string":
                return a["string_plural"]
            if node.item.kind == "object":
                return a["generic"].format(item=node.item.type_name)
            # scalar other
            item = self._wd_type(node.item).replace("un ","").replace("une ","")
            return a["generic"].format(item=item)

        return t["variant"]
