from typing import Callable, Dict, List
import os

from extr.entities import create_entity_extractor
from extr.relations import RelationExtractor
from extr_ds.models import RelationLabel
from extr_ds.labelers import RelationClassification

from .dev import create_dev_files
from ..workspace import WORKSPACE
from ...utils.filesystem import load_data
from ...utils import imports


def get_labeler(sentence_tokenizer: Callable[[str], List[List[str]]]) -> RelationClassification:
    labels = imports.load_file(
        'labels',
        os.path.join(WORKSPACE, 'labels.py')
    )

    entity_extractor = create_entity_extractor(labels.entity_patterns, labels.kb)
    relation_extractor = RelationExtractor(labels.relation_patterns)

    return RelationClassification(
        sentence_tokenizer,
        entity_extractor,
        relation_extractor,
        labels.relation_defaults,
    )

def relate() -> None:
    utils = imports.load_file(
        'utils',
        os.path.join(WORKSPACE, 'utils.py')
    )

    labeler = get_labeler(utils.sentence_tokenizer)

    relation_groups: Dict[str, List[RelationLabel]] = {}
    for row in load_data(os.path.join(WORKSPACE, '2', 'dev.txt')):
        text = utils.transform_text(row)
        for relation_label in labeler.label(text):
            if not relation_label.definition in relation_groups:
                relation_groups[relation_label.definition] = []

            relation_groups[relation_label.definition].append(relation_label)

    create_dev_files(relation_groups)
