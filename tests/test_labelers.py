import os
import sys
import re
from typing import List
from extr import RegEx, RegExLabel, EntityExtractor, RegExRelationLabelBuilder, RelationExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labelers import IOB, RelationClassification
from extr_ds.labelers.relation import RelationBuilder, BaseRelationLabeler, RuleBasedRelationLabeler


def test_iob_label():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'(ted johnson|ted)'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ])

    def word_tokenizer(_: str) -> List[str]:
        return ['Ted', 'Johnson', 'is', 'a', 'pitcher', '.']

    text = 'Ted Johnson is a pitcher.'

    iob_labeler = IOB(word_tokenizer, extractor)

    observation = iob_labeler.label(text)

    assert observation.labels == ['B-PERSON', 'I-PERSON', 'O', 'O', 'B-POSITION', 'O']

def test_iob_label_2():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'(ted johnson iii)'], re.IGNORECASE)
        ]),
    ])

    def word_tokenizer(_: str) -> List[str]:
        return ['Ted', 'Johnson', 'iii', 'is', 'a', 'pitcher', '.']

    text = 'Ted Johnson iii is a pitcher.'

    observation = IOB(word_tokenizer, extractor).label(text)
    assert observation.labels == ['B-PERSON', 'I-PERSON', 'I-PERSON', 'O', 'O', 'O', 'O']

def test_relation_label():
    texts = [
        'Ted Johnson is a pitcher.',
        'Bob is not a pitcher.'
    ]

    labeler = RelationClassification(
        EntityExtractor([
            RegExLabel('PERSON', [
                RegEx([r'(ted johnson|bob)'], re.IGNORECASE)
            ]),
            RegExLabel('POSITION', [
                RegEx([r'pitcher'], re.IGNORECASE)
            ]),
        ]),
        BaseRelationLabeler(
            RelationBuilder(
                relation_formats=[('PERSON', 'POSITION', 'NO_RELATION')]
            )
        ),
        additional_relation_labelers=[
            RuleBasedRelationLabeler(
                RelationExtractor([
                    RegExRelationLabelBuilder('is_a') \
                        .add_e1_to_e2(
                            'PERSON',
                            [
                                r'\s+is\s+a\s+',
                            ],
                            'POSITION'
                        ) \
                        .build()
                ])
            )
        ]
    )

    annotations = []
    classification_labels = []

    for text in texts:
        results = labeler.label(text)
        for relation_label in results.relation_labels:
            annotations.append(relation_label.sentence)
            classification_labels.append(relation_label.label)

    assert annotations == [
        '<e1:PERSON>Ted Johnson</e1:PERSON> is a <e2:POSITION>pitcher</e2:POSITION>.',
        '<e1:PERSON>Bob</e1:PERSON> is not a <e2:POSITION>pitcher</e2:POSITION>.',
    ]

    assert classification_labels == [
        'is_a',
        'NO_RELATION'
    ]
