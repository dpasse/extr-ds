import os
import re
import sys
import pytest
from typing import Generator, List
from extr import RegEx, RegExLabel, EntityExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labelers import IOB


@pytest.mark.skip()
def test_end_to_end():
    text = 'Walk; Mountcastle to 3B; Odor to 2B'

    entity_patterns = [
        RegExLabel('PLAYER', [
            RegEx([r'\b[A-Z]\w+(?=\s+to\b)'])
        ]),
        RegExLabel('BASE', [
            RegEx([r'[123]B\b'])
        ]),
        RegExLabel('EVENT', [
            RegEx([r'\b(?:walk|single|double|triple)\b'], re.IGNORECASE)
        ]),
    ]

    entity_extractor = EntityExtractor(entity_patterns)

    ## mock sentence tokenizer
    def sentence_tokenizer(text: str) -> Generator[List[str], None, None]:
        sentences = text.split(';')

        for i, sentence in enumerate(sentences):
            tokens = sentence.strip().split(' ')

            if i + 1 != len(sentences):
                tokens.append(';')

            yield tokens

    observations = IOB(sentence_tokenizer, entity_extractor).label(text)

    labels = list(
        map(
            lambda item: (
                list(map(lambda tk: tk.text, item.tokens)),
                item.labels
            ),
            observations
        )
    )

    print(labels)
