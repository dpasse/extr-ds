import re
from typing import List
from extr import Entity, Location, Token
from ..models import Label


class IOBtoEntitiesTransfomer:
    def unlabel(self, label: Label) -> List[Entity]:
        i = 0
        entity_start = -1
        observations = label.zip()

        entities: List[Entity] = []
        for i, observation in enumerate(observations):
            token, annotation = observation

            if annotation == 'O':
                if entity_start >= 0:
                    entities.append(
                        self._create_entity(
                            len(entities) + 1,
                            label.token_group.sentence,
                            entity_start,
                            *observations[i-1]
                        )
                    )

                    entity_start = -1

                continue

            match = re.search(r'^([BI])-(.+)', annotation)
            assert not match is None, f'cannot make sense of label="{annotation}"'

            if match.group(1) == 'B':
                if entity_start >= 0:
                    entities.append(
                        self._create_entity(
                            len(entities) + 1,
                            label.token_group.sentence,
                            entity_start,
                            *observations[i-1]
                        )
                    )

                    entity_start = -1

                entity_start = token.location.start

        if i > 0 and entity_start >= 0:
            entities.append(
                self._create_entity(
                    len(entities) + 1,
                    label.token_group.sentence,
                    entity_start,
                    *observations[i-1]
                )
            )

        return entities

    def _create_entity(self, identifier: int, sentence: str, start: int, previous_token: Token, previous_annotation: str) -> Entity:
        end = previous_token.location.end
        text = sentence[start:end]

        return Entity(
            identifier,
            re.sub(r'^[BI]-', '', previous_annotation),
            text,
            location=Location(start, end)
        )
