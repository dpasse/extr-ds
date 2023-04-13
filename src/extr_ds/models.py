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

    def add_token(self, entity: Entity):
        self.entities.append(entity)

    def __len__(self) -> int:
        return len(self.entities)

    def __repr__(self) -> str:
        return f'<Token text="{self.text}", location={repr(self.location)}, order={self.order}>'

@dataclass(frozen=True)
class TokenGroup(ILocation):
    location: Location
    tokens: List[Token]
