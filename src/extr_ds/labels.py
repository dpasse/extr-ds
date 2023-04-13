from typing import List, Callable
from .models import TokenGroup
from extr import Entity, EntityExtractor

from .tokenizer import tokenizer

## label type = IOB2

class IOB2():

    def __init__(self, sentence_tokenizer: Callable[[str], List[List[str]]], entity_extractor: EntityExtractor) -> None:
        self._sentence_tokenizer = sentence_tokenizer
        self._entity_extractor = entity_extractor

    def label(self, text: str) -> List[List[str]]:
        entities = self._entity_extractor.get_entities(text)
        token_groups = tokenizer(text, self._sentence_tokenizer(text))

        return self.__merge(token_groups, entities)

    def __merge(self, token_groups, entities: List[Entity]):

        action = []

        for token_group in token_groups:

            tokens = [(i, token) for i, token in enumerate(token_group.tokens)]
            
            labels = [
                'O' for _ in range(len(tokens))
            ]

            entities_in_group = filter(
                lambda entity: token_group.contains(entity),
                entities
            )

            for entity in entities_in_group:

                span = list(
                    filter(
                        lambda token: entity.is_in(token[1]),
                        tokens
                    )
                )

                x = 0
                for i, _ in span:
                    assert labels[i] == 'O', f'bad tokenizer? multiple entities belong to the same token - {labels[i]}'

                    labels[i] = 'B-' if x == 0 else 'I-'
                    labels[i] += entity.label

                    x += 1

            action.append(labels)

        return action



        