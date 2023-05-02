from typing import List
import os
import json

from extr.entities import create_entity_extractor
from extr.relations import RelationExtractor
from extr_ds.models import RelationLabel
from extr_ds.labelers import RelationClassification

from .workspace import WORKSPACE
from ..utils.filesystem import load_data
from ..utils import imports

utils = imports.load_file(
    'utils',
    os.path.join(WORKSPACE, 'utils.py')
)


def get_labeler() -> RelationClassification:
    labels = imports.load_file(
        'labels',
        os.path.join(WORKSPACE, 'labels.py')
    )

    return RelationClassification(
        utils.sentence_tokenizer,
        create_entity_extractor(labels.entity_patterns, labels.kb),
        RelationExtractor(labels.relation_patterns),
        labels.relation_defaults,
    )

def relate() -> None:
    labeler = get_labeler()

    relation_labels: List[RelationLabel] = []
    for row in load_data(os.path.join(WORKSPACE, '2', 'dev.txt')):
        text = utils.transform_text(row)
        relation_labels.extend(labeler.label(text))

    blobs = list(map(lambda rl: rl.todict(), relation_labels))
    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(json.dumps(blobs, indent=2))
