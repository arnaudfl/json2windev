from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from json2windev.core.schema import SchemaNode
from json2windev.rules.loader import Rules
from json2windev.renderers.base import Renderer
from json2windev.renderers.windev import WinDevRenderer
from json2windev.utils.naming import pascal_case, sanitize_identifier, escape_reserved


@dataclass(frozen=True)
class StructureDoc:
    type_name: str
    rows: List[Tuple[str, str, str, str]]  # json_key, windev_field, windev_type, serialize


class MarkdownRenderer(Renderer):
    """
    Markdown renderer:
    - Generates a documentation section (structures + fields)
    - Includes the full WinDev output as a code block
    """

    def render(self, root: SchemaNode) -> str:
        # 1) Generate WinDev code (source of truth)
        wd_code = WinDevRenderer(self.rules).render(root).rstrip("\n")

        # 2) Build documentation from the inferred schema
        structures = self._collect_structures(root)
        summary = self._compute_summary(structures)

        # 3) Markdown output
        lines: List[str] = []
        lines.append("# JSON → WinDev structures")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Structures: **{summary['structures']}**")
        lines.append(f"- Fields: **{summary['fields']}**")
        lines.append(f"- Arrays: **{summary['arrays']}**")
        lines.append(f"- Variant fields: **{summary['variants']}**")
        lines.append("")
        lines.append("## Table of contents")
        lines.append("")
        for s in structures:
            lines.append(f"- [{s.type_name}](#{self._anchor(s.type_name)})")
        lines.append("")
        lines.append("## Structures")
        lines.append("")

        for s in structures:
            lines.append(f"### {s.type_name}")
            lines.append("")
            lines.append("| JSON key | WinDev field | WinDev type | Serialize |")
            lines.append("|---|---|---|---|")
            for json_key, wd_field, wd_type, serialize in s.rows:
                lines.append(f"| `{json_key}` | `{wd_field}` | `{wd_type}` | `{serialize}` |")
            lines.append("")

        lines.append("## Generated WinDev code")
        lines.append("")
        lines.append("```wlanguage")
        lines.append(wd_code)
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def _anchor(self, title: str) -> str:
        # GitHub-style-ish anchor: lower + strip non-alnum to hyphen
        import re
        s = title.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s

    def _collect_structures(self, root: SchemaNode) -> List[StructureDoc]:
        # We rely on the same naming conventions as WinDevRenderer.
        # Root must be object for STResult contract.
        if root.kind != "object":
            raise ValueError("Root JSON must be an object to generate Markdown documentation.")

        # Ensure type names exist by rendering once via WinDevRenderer? already done.
        # But we still need them on the schema. WinDevRenderer assigns type_name internally.
        # So we reproduce minimal type-name assignment here to be consistent.
        # Easiest: instantiate WinDevRenderer and call its render already done above,
        # but it doesn't expose the internal named nodes.
        #
        # Practical compromise: we infer type names deterministically here in the same way.
        self._assign_type_names(root)

        ordered: List[SchemaNode] = []
        declared: Set[str] = set()
        self._collect_objects_children_first(root, ordered, declared)

        docs: List[StructureDoc] = []
        for obj in ordered:
            docs.append(StructureDoc(type_name=obj.type_name or "STUnknown", rows=self._doc_rows(obj)))
        return docs

    def _collect_objects_children_first(self, node: SchemaNode, ordered: List[SchemaNode], declared: Set[str]) -> None:
        if node.kind == "object":
            for child in node.fields.values():
                self._collect_objects_children_first(child, ordered, declared)
            if node.type_name and node.type_name not in declared:
                declared.add(node.type_name)
                ordered.append(node)
        elif node.kind == "array" and node.item is not None:
            self._collect_objects_children_first(node.item, ordered, declared)

    def _assign_type_names(self, root: SchemaNode) -> None:
        # Minimal consistent naming with our WinDev rules:
        # - root: STResult
        # - child object: ST + PascalCase(json_key)
        # - collisions: add numeric suffix
        type_prefix = self.rules.structure["type_prefix"]
        used: Set[str] = set()

        def unique(name: str) -> str:
            if name not in used:
                used.add(name)
                return name
            i = 2
            while f"{name}{i}" in used:
                i += 1
            out = f"{name}{i}"
            used.add(out)
            return out

        root_name: str = self.rules.result["type_name"]
        root.type_name = root_name
        used.add(root_name)

        def walk(node: SchemaNode) -> None:
            if node.kind != "object":
                if node.kind == "array" and node.item is not None:
                    walk(node.item)
                return

            for key, child in node.fields.items():
                if child.kind == "object":
                    child.type_name = unique(type_prefix + pascal_case(key))
                    walk(child)
                elif child.kind == "array" and child.item is not None and child.item.kind == "object":
                    child.item.type_name = unique(type_prefix + pascal_case(key) + "Item")
                    walk(child.item)
                elif child.kind == "array" and child.item is not None:
                    walk(child.item)

        walk(root)

    def _doc_rows(self, obj: SchemaNode) -> List[Tuple[str, str, str, str]]:
        rows: List[Tuple[str, str, str, str]] = []
        for json_key, child in obj.fields.items():
            wd_field, serialize = self._field_name_and_serialize(json_key, child)
            wd_type = self._wd_type(child)
            rows.append((json_key, wd_field, wd_type, serialize))
        return rows

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

        serialize = ""
        if naming.get("serialize_attribute", False):
            serialize = f'<serialize="{json_key}">'
        return field_name, serialize

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

        if node.kind in ("null", "variant"):
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
                return a["empty"]
            if node.item.kind == "string":
                return a["string_plural"]
            if node.item.kind == "object":
                return a["generic"].format(item=node.item.type_name)
            item = self._wd_type(node.item).replace("un ", "").replace("une ", "")
            return a["generic"].format(item=item)

        return t["variant"]

    def _compute_summary(self, structures: List[StructureDoc]) -> Dict[str, int]:
        fields = sum(len(s.rows) for s in structures)
        arrays = 0
        variants = 0
        for s in structures:
            for _, _, wd_type, _ in s.rows:
                if "tableau" in wd_type:
                    arrays += 1
                if "Variant" in wd_type:
                    variants += 1
        return {
            "structures": len(structures),
            "fields": fields,
            "arrays": arrays,
            "variants": variants,
        }
