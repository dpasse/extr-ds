import os
import sys
import re
from typing import Generator, List
from extr import RegEx, RegExLabel, EntityExtractor, RegExRelationLabelBuilder, RelationExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labelers import IOB, RelationClassification


def test_iob_label():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'(ted johnson|ted)'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ])

    def sentence_tokenizer(_: str) -> Generator[List[str], None, None]:
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

def test_iob_label_2():
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

    observations = IOB(sentence_tokenizer, extractor).label(text)

    expected = [
        ['B-PERSON', 'I-PERSON', 'I-PERSON', 'O', 'O', 'O', 'O'],
    ]

    assert list(map(lambda item: item.labels, observations)) == expected

def test_relation_label():
    text = 'Ted Johnson is a pitcher. Bob is not a pitcher.'

    def sentence_tokenizer(_: str) -> Generator[List[str], None, None]:
        return (
            record for record in [
                ['Ted', 'Johnson', 'is', 'a', 'pitcher', '.'],
                ['Bob', 'is', 'not', 'a', 'pitcher', '.']
            ]
        )

    person_to_position_relationship = RegExRelationLabelBuilder('is_a') \
        .add_e1_to_e2(
            'PERSON',
            [
                r'\s+is\s+a\s+',
            ],
            'POSITION'
        ) \
        .build()

    labeler = RelationClassification(
        sentence_tokenizer,
        EntityExtractor([
            RegExLabel('PERSON', [
                RegEx([r'(ted johnson|bob)'], re.IGNORECASE)
            ]),
            RegExLabel('POSITION', [
                RegEx([r'pitcher'], re.IGNORECASE)
            ]),
        ]),
        RelationExtractor([person_to_position_relationship]),
        [('PERSON', 'POSITION', 'NO_RELATION')],
    )

    labels = labeler.label(text)

    annotations = []
    classification_labels = []
    for relation_label in labels:
        annotations.append(relation_label.sentence)
        classification_labels.append(relation_label.label)


    assert annotations == [
        '<e1>Ted Johnson</e1> is a <e2>pitcher</e2>.',
        '<e1>Bob</e1> is not a <e2>pitcher</e2>.'
    ]

    assert classification_labels == [
        'is_a',
        'NO_RELATION'
    ]
