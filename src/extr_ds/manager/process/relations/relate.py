from typing import Dict, List
import os

from extr.entities import create_entity_extractor
from extr.relations import RelationExtractor
from extr.relations.annotator import RelationAnnotatorWithEntityType
from extr_ds.models import RelationLabel
from extr_ds.labelers import RelationClassification
from extr_ds.labelers.relation import BaseRelationLabeler, RuleBasedRelationLabeler

from .dev import create_dev_files
from ..workspace import WORKSPACE
from ...utils.filesystem import load_data
from ...utils import imports

def get_labeler() -> RelationClassification:
    labels = imports.load_file(
        'labels',
        os.path.join(WORKSPACE, 'labels.py')
    )

    return RelationClassification(
        create_entity_extractor(
            labels.entity_patterns,
            labels.kb
        ),
        base_labeler=BaseRelationLabeler(labels.relation_defaults),
        relation_labelers=[
            RuleBasedRelationLabeler(
                relation_extractor=RelationExtractor(labels.relation_patterns),
                relation_annotator=RelationAnnotatorWithEntityType()
            )
        ]
    )

def relate() -> None:
    utils = imports.load_file(
        'utils',
        os.path.join(WORKSPACE, 'utils.py')
    )

    labeler = get_labeler()

    relation_groups: Dict[str, List[RelationLabel]] = {}
    for row in load_data(os.path.join(WORKSPACE, '2', 'dev.txt')):
        text = utils.transform_text(row)

        for relation_label in labeler.label(text):
            if not relation_label.definition in relation_groups:
                relation_groups[relation_label.definition] = []

            relation_groups[relation_label.definition].append(relation_label)

    create_dev_files(relation_groups)
