import os
import sys
import re
from typing import Generator, List
from extr import RegEx, RegExLabel, EntityExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labellers import IOB


def test_label():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'ted'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ])

    def sentence_tokenizer(text: str) -> Generator[List[str], None, None]:
        yield ['Ted', 'is', 'a', 'pitcher', '.']
        yield ['Ted', 'went', 'to', 'my', 'school', '.']

    text = 'Ted is a pitcher. Ted went to my school.'

    observations = list(IOB(sentence_tokenizer, extractor).label(text))

    expected = [
        ['B-PERSON', 'O', 'O', 'B-POSITION', 'O'],
        ['B-PERSON', 'O', 'O', 'O', 'O', 'O']
    ]
    
    assert observations == expected
