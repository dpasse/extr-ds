import os
import re
import sys
import pytest
from typing import List
from extr import RegEx, RegExLabel, EntityExtractor, RegExRelationLabelBuilder, RelationExtractor

sys.path.insert(0, os.path.join('../src'))

from extr_ds.labelers import IOB, RelationClassification
from extr_ds.labelers.relation import RelationBuilder, BaseRelationLabeler, RuleBasedRelationLabeler


@pytest.mark.skip
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

    def word_tokenizer(text: str) -> List[str]:
        sentences = text.split(';')

        tokens = []
        for i, sentence in enumerate(sentences):
            tokens.extend(sentence.strip().split(' '))

            if i + 1 != len(sentences):
                tokens.append(';')

        return tokens

    observation = IOB(
        word_tokenizer,
        entity_extractor
    ).label(text)

    labels = (
        list(map(lambda tk: tk.text, observation.tokens)),
        observation.labels
    )

    print('IOB:')
    print(labels)

    base_relation_labeler = BaseRelationLabeler(
        RelationBuilder(
            relation_formats=[('PLAYER', 'BASE', 'NO_RELATION')]
        )
    )

    rule_based_relation_labeler = RuleBasedRelationLabeler(
        RelationExtractor([
            RegExRelationLabelBuilder('is_on') \
                .add_e1_to_e2(
                    'PLAYER',
                    [
                        r'\s+to\s+',
                    ],
                    'BASE'
                ) \
                .build()
        ])
    )

    labeler = RelationClassification(
        entity_extractor,
        base_relation_labeler,
        relation_labelers=[
            rule_based_relation_labeler
        ]
    )

    results = labeler.label(text)
    assert len(results.relation_labels) == 4

    ## [
    ##    <RelationLabel sentence="Walk; Mountcastle to 3B; <e1>Odor</e1> to <e2>2B</e2>" label="is_on">,
    ##    <RelationLabel sentence="Walk; Mountcastle to <e2>3B</e2>; <e1>Odor</e1> to 2B" label="NO_RELATION">,
    ##    <RelationLabel sentence="Walk; <e1>Mountcastle</e1> to 3B; Odor to <e2>2B</e2>" label="NO_RELATION">,
    ##    <RelationLabel sentence="Walk; <e1>Mountcastle</e1> to <e2>3B</e2>; Odor to 2B" label="is_on">
    ## ]
