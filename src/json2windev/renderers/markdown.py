from __future__ import annotations

from json2windev.core.schema import SchemaNode
from json2windev.rules.loader import Rules
from json2windev.renderers.windev import WinDevRenderer
from json2windev.renderers.base import Renderer


class MarkdownRenderer(Renderer):
    """
    Markdown wrapper renderer:
    - Generates WinDev code using WinDevRenderer
    - Wraps it into a Markdown document
    """

    def render(self, root: SchemaNode) -> str:
        wd = WinDevRenderer(self.rules).render(root)

        # Minimal, clean Markdown output
        lines: list[str] = []
        lines.append("# JSON → WinDev structures")
        lines.append("")
        lines.append("## Generated WinDev code")
        lines.append("")
        lines.append("```wlanguage")
        lines.append(wd.rstrip("\n"))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)
