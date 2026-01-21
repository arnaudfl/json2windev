from __future__ import annotations
from abc import ABC, abstractmethod
from json2windev.core.schema import SchemaNode
from json2windev.rules.loader import Rules

class Renderer(ABC):
    def __init__(self, rules: Rules):
        self.rules = rules

    @abstractmethod
    def render(self, root: SchemaNode) -> str: ...
