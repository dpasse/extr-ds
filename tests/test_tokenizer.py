import os
import sys
import re

from extr import RegEx, RegExLabel, EntityExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.tokenizer import tokenizer
from extr_ds.labels import IOB2


def test_get_entities():
    tokens = tokenizer('Ted is a pitcher.', [['Ted', 'is', 'a', 'pitcher', '.']])
    print(list(tokens))

def test_label():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'ted'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ])

    def sentence_tokenizer(text: str) -> str:
        return [
            ['Ted', 'is', 'a', 'pitcher', '.'],
            ['Ted', 'went', 'to', 'my', 'school', '.']
        ]

    text = 'Ted is a pitcher. Ted went to my school.'

    ugh = IOB2(sentence_tokenizer, extractor).label(text)


    print(ugh)

    

