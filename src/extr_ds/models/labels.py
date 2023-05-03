from typing import List, Dict
from dataclasses import dataclass
from extr.models import Token, Relation


@dataclass
class Label:
    tokens: List[Token]
    labels: List[str]

    def __repr__(self) -> str:
        return f'<Label tokens={self.tokens}, labels={self.labels}>'

@dataclass
class RelationLabel:
    sentence: str
    relation: Relation

    @property
    def label(self) -> str:
        return self.relation.label

    @property
    def definition(self) -> str:
        return self.relation.definition

    def todict(self) -> Dict[str, str]:
        return {
            'sentence': self.sentence,
            'label': self.label,
        }

    def __repr__(self) -> str:
        return f'<RelationLabel sentence="{self.sentence}" label="{self.label}">'
