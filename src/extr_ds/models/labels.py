from typing import List
from dataclasses import dataclass
from extr.models import Token


@dataclass
class Label:
    tokens: List[Token]
    labels: List[str]

    def __repr__(self) -> str:
        return f'<Label tokens={self.tokens}, labels={self.labels}>'

@dataclass
class RelationLabel:
    sentence: str
    label: str

    def __repr__(self) -> str:
        return f'<RelationLabel sentence="{self.sentence}" label="{self.label}">'
