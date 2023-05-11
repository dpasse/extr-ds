from typing import Dict, List, Tuple
import re
from dataclasses import dataclass
from extr.models import Token, TokenGroup, Relation


class Label:
    def __init__(self, token_group: TokenGroup, labels: List[str]) -> None:
        assert len(token_group.tokens) == len(labels)

        self.token_group = token_group
        self.labels = labels

    @property
    def tokens(self) -> List[Token]:
        return self.token_group.tokens

    def zip(self) -> List[Tuple[Token, str]]:
        return list(zip(self.tokens, self.labels))

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

    @property
    def original_sentence(self) -> str:
        return re.sub(r'</?e\d+>', '', self.sentence)

    def todict(self) -> Dict[str, str]:
        return {
            'sentence': self.sentence,
            'label': self.label,
        }

    def __repr__(self) -> str:
        return f'<RelationLabel sentence="{self.sentence}" label="{self.label}">'
