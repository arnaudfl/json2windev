\
from __future__ import annotations
import re
from typing import Iterable

def pascal_case(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name.strip())
    parts = [p for p in parts if p]
    if not parts:
        return "X"
    return "".join(p[:1].upper() + p[1:] for p in parts)

def sanitize_identifier(name: str, forbidden_pattern: str) -> str:
    name = re.sub(forbidden_pattern, "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "X"

def escape_reserved(name: str, reserved_words: Iterable[str], escape_template: str) -> str:
    if name.upper() in {w.upper() for w in reserved_words}:
        return escape_template.format(name=name)
    return name
