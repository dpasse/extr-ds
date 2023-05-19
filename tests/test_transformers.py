import os
import sys
import re
from typing import List
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

    def word_tokenizer(_: str) -> List[str]:
        return ['Ted', 'Johnson', 'iii', 'is', 'a', 'pitcher', '.']

    text = 'Ted Johnson iii is a pitcher.'

    observation = IOB(word_tokenizer, extractor).label(text)
    entities: List[Entity] = IOBtoEntitiesTransfomer().unlabel(observation)

    assert len(entities) == 1
    assert entities[0].text == 'Ted Johnson iii'
