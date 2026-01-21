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

        stats = self._schema_stats(root)

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
        lines.append(f"- Max depth: **{stats['max_depth']}**")
        lines.append("")
        lines.extend(self._rules_snapshot_lines())
        lines.append("## Notes")
        lines.append("")
        lines.append("- Fields are generated using WinDev prefixes (if enabled) but keep JSON compatibility via `<serialize=\"jsonKey\">`.")
        lines.append("- `null` values and heterogeneous types are mapped to `Variant`.")
        lines.append("- Empty arrays are mapped according to `array.empty` in the rules.")
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

    def _rules_snapshot_lines(self) -> list[str]:
        r = self.rules

        naming = r.naming
        prefixes = r.prefixes
        types = r.types
        array = r.array

        lines: list[str] = []
        lines.append("## Rules snapshot")
        lines.append("")
        lines.append(f"- Prefixes enabled: **{bool(naming.get('use_variable_prefixes'))}**")
        lines.append(f"- Serialize enabled: **{bool(naming.get('serialize_attribute'))}**")
        lines.append("")
        lines.append("### Prefixes")
        lines.append("")
        lines.append("| Kind | Prefix |")
        lines.append("|---|---|")
        lines.append(f"| string | `{prefixes.get('string','')}` |")
        lines.append(f"| int | `{prefixes.get('int','')}` |")
        lines.append(f"| real | `{prefixes.get('real','')}` |")
        lines.append(f"| boolean | `{prefixes.get('boolean','')}` |")
        lines.append(f"| array | `{prefixes.get('array','')}` |")
        lines.append(f"| structure | `{prefixes.get('structure','')}` |")
        lines.append(f"| variant | `{prefixes.get('variant','')}` |")
        lines.append("")
        lines.append("### Type mapping")
        lines.append("")
        lines.append("| JSON kind | WinDev type |")
        lines.append("|---|---|")
        lines.append(f"| string | `{types.get('string','')}` |")
        lines.append(f"| int | `{types.get('int','')}` |")
        lines.append(f"| real | `{types.get('real','')}` |")
        lines.append(f"| boolean | `{types.get('boolean','')}` |")
        lines.append(f"| null / heterogeneous | `{types.get('variant','')}` |")
        lines.append("")
        lines.append("### Array rules")
        lines.append("")
        lines.append(f"- Empty array: `{array.get('empty','')}`")
        lines.append(f"- Array of strings: `{array.get('string_plural','')}`")
        lines.append(f"- Generic: `{array.get('generic','')}`")
        lines.append("")
        return lines

    def _schema_stats(self, root: SchemaNode) -> dict[str, int]:
        stats = {
            "objects": 0,
            "fields_total": 0,
            "arrays_total": 0,
            "arrays_of_objects": 0,
            "arrays_of_scalars": 0,
            "variants_total": 0,
            "null_fields_detected": 0,
            "max_depth": 0,
        }

        def walk(node: SchemaNode, depth: int) -> None:
            stats["max_depth"] = max(stats["max_depth"], depth)

            if node.kind == "object":
                stats["objects"] += 1
                stats["fields_total"] += len(node.fields)
                for child in node.fields.values():
                    walk(child, depth + 1)

            elif node.kind == "array":
                stats["arrays_total"] += 1
                if node.item is None:
                    stats["variants_total"] += 1
                else:
                    if node.item.kind == "object":
                        stats["arrays_of_objects"] += 1
                    elif node.item.kind in ("string", "number_int", "number_real", "boolean"):
                        stats["arrays_of_scalars"] += 1
                    elif node.item.kind == "null":
                        stats["null_fields_detected"] += 1
                        stats["variants_total"] += 1
                    elif node.item.kind == "variant":
                        stats["variants_total"] += 1
                    walk(node.item, depth + 1)

            elif node.kind == "null":
                stats["null_fields_detected"] += 1
                stats["variants_total"] += 1

            elif node.kind == "variant":
                stats["variants_total"] += 1

            else:
                # scalar
                pass

        walk(root, 0)
        return stats
