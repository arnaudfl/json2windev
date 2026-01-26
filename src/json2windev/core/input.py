from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class JsonParseError(ValueError):
    message: str
    lineno: Optional[int] = None
    colno: Optional[int] = None
    snippet: Optional[str] = None

    def __str__(self) -> str:
        loc = ""
        if self.lineno is not None and self.colno is not None:
            loc = f" (line {self.lineno}, col {self.colno})"
        s = f"{self.message}{loc}"
        if self.snippet:
            s += f"\n{self.snippet}"
        return s


def parse_json(text: str) -> Any:
    """
    Parse JSON with friendlier errors (line/col + context snippet).
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        snippet = _make_snippet(text, e.pos, e.lineno, e.colno)
        raise JsonParseError(
            message=e.msg,
            lineno=e.lineno,
            colno=e.colno,
            snippet=snippet,
        ) from None


def pretty_json(value: Any) -> str:
    """
    Deterministic pretty print, useful for CLI/GUI display.
    """
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def _make_snippet(text: str, pos: int, lineno: int, colno: int, radius: int = 60) -> str:
    """
    Build a small snippet around the error position, plus a caret pointer.
    Works even on large JSON.
    """
    start = max(0, pos - radius)
    end = min(len(text), pos + radius)

    segment = text[start:end]
    segment = segment.replace("\r\n", "\n").replace("\r", "\n")

    caret_pos = pos - start
    if caret_pos < 0:
        caret_pos = 0
    if caret_pos > len(segment):
        caret_pos = len(segment)

    # Keep it single-line friendly: show current line segment only when possible
    # But if segment contains newlines, keep it as-is and caret points to exact index in segment.
    caret_line = " " * caret_pos + "^"

    header = f"Near line {lineno}, col {colno}:"
    return f"{header}\n{segment}\n{caret_line}"
