from typing import List, Callable, Generator, Iterator, cast
from extr import Entity, TokenGroup
from extr.entities import EntityExtractor
from extr.tokenizers import tokenizer
from ..models import Label


class Labeler():
    def __init__(self, sentence_tokenizer: Callable[[str], List[List[str]]]) -> None:
        self._sentence_tokenizer = sentence_tokenizer

    def label(self, text: str, entities: List[Entity]) -> Generator[Label, None, None]:
        return self.__merge(
            tokenizer(text, self._sentence_tokenizer(text)),
            entities
        )

    def __merge(self, token_groups: Generator[TokenGroup, None, None], entities: List[Entity]) -> Generator[Label, None, None]:
        for token_group in token_groups:
            tokens = list(enumerate(token_group.tokens))
            labels = ['O' for _ in range(len(tokens))]
            for entity in cast(Iterator[Entity], filter(token_group.contains, entities)):
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

            yield Label(token_group, labels)

class IOB():
    def __init__(self, \
                 sentence_tokenizer: Callable[[str], List[List[str]]], \
                 entity_extractor: EntityExtractor) -> None:
        self._labeler = Labeler(sentence_tokenizer)
        self._entity_extractor = entity_extractor

    def label(self, text: str) -> Generator[Label, None, None]:
        entities = self._entity_extractor.get_entities(text)
        return self._labeler.label(text, entities)
