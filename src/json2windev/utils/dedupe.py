from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class NameRegistry:
    """
    Registry used to ensure unique names within a scope (e.g. one structure).
    """
    counts: Dict[str, int]

    def __init__(self) -> None:
        self.counts = {}

    def unique(self, base: str) -> str:
        """
        Return a unique name based on base:
        base, base2, base3, ...
        """
        n = self.counts.get(base, 0) + 1
        self.counts[base] = n
        return base if n == 1 else f"{base}{n}"
