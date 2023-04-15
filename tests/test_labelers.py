import os
import sys
import re
from typing import Generator, List
from extr import RegEx, RegExLabel, EntityExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labelers import IOB


def test_label():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'(ted johnson|ted)'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ])

    ## mock sentence tokenizer
    def sentence_tokenizer(text: str) -> Generator[List[str], None, None]:
        return (
            record for record in [
                ['Ted', 'Johnson', 'is', 'a', 'pitcher', '.'],
                ['Ted', 'went', 'to', 'my', 'school', '.']
            ]
        )

    text = 'Ted Johnson is a pitcher. Ted went to my school.'

    observations = IOB(sentence_tokenizer, extractor).label(text)

    expected = [
        ['B-PERSON', 'I-PERSON', 'O', 'O', 'B-POSITION', 'O'],
        ['B-PERSON', 'O', 'O', 'O', 'O', 'O']
    ]

    assert list(map(lambda item: item.labels, observations)) == expected
