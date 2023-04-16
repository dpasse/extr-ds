from typing import List
from dataclasses import dataclass, field
from extr import Entity, Location
from extr.models import ILocation


@dataclass(frozen=True)
class Token(ILocation):
    text: str
    location: Location
    order: int
    entities: List[Entity] = field(default_factory=lambda: [])

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def __len__(self) -> int:
        return len(self.entities)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f'<Token text="{self.text}", location={repr(self.location)}, order={self.order}>'

@dataclass(frozen=True)
class TokenGroup(ILocation):
    location: Location
    sentence: str
    tokens: List[Token]

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
