from typing import List, Callable
from extr import Entity, TokenGroup
from extr.entities import EntityExtractor
from extr.tokenizers import word_tokenizer
from ..models import Label


class Labeler():
    def __init__(self, tokenizer: Callable[[str], List[str]]) -> None:
        self._tokenizer = tokenizer

    def label(self, text: str, entities: List[Entity]) -> Label:
        return self.__merge(
            word_tokenizer(text, self._tokenizer(text)),
            entities
        )

    def __merge(self, token_group: TokenGroup, entities: List[Entity]) -> Label:
        tokens = list(enumerate(token_group.tokens))
        labels = ['O' for _ in range(len(tokens))]
        for entity in token_group.find_entities(entities):
            used_counter = 0

            for i, token in tokens:
                if not entity.is_in(token) and not entity.contains(token):
                    continue

                current_label = labels[i]
                assert current_label == 'O', f'bad tokenizer? multiple entities belong to the same token - {current_label}'

                labels[i] = 'B-' if used_counter == 0 else 'I-'
                labels[i] += entity.label

                token.add_entity(entity)

                used_counter += 1

        return Label(token_group, labels)

class IOB():
    def __init__(self, \
                 tokenizer: Callable[[str], List[str]], \
                 entity_extractor: EntityExtractor) -> None:
        self._labeler = Labeler(tokenizer)
        self._entity_extractor = entity_extractor

    def label(self, text: str) -> Label:
        entities = self._entity_extractor.get_entities(text)
        return self._labeler.label(text, entities)
