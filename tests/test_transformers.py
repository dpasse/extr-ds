import os
import sys
import re
from typing import Generator, List
from extr import RegEx, RegExLabel, EntityExtractor
from extr.models import Entity

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labelers import IOB
from extr_ds.transformers import IOBtoEntitiesTransfomer


def test_reverse_iob_to_entities() -> None:
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'(ted johnson iii)'], re.IGNORECASE)
        ]),
    ])

    def sentence_tokenizer(_: str) -> Generator[List[str], None, None]:
        return (
            record for record in [
                ['Ted', 'Johnson', 'iii', 'is', 'a', 'pitcher', '.'],
            ]
        )

    text = 'Ted Johnson iii is a pitcher.'

    rev = IOBtoEntitiesTransfomer()
    observations = IOB(sentence_tokenizer, extractor).label(text)

    entities: List[Entity] = []
    for label in observations:
        entities.extend(rev.unlabel(label))

    assert len(entities) == 1
    assert entities[0].text == 'Ted Johnson iii'
