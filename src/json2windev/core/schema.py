from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class SchemaNode:
    kind: str
    fields: Dict[str, "SchemaNode"] = field(default_factory=dict)
    item: Optional["SchemaNode"] = None
    type_name: Optional[str] = None
