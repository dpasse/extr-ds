from typing import Dict, Set, cast
import os

from extr.entities import create_entity_extractor, \
                          LabelOnlyEntityAnnotator, \
                          HtmlEntityAnnotator, \
                          EntityExtractor

from .models import Annotations
from .dev import create_html_file, create_parsed_by_file, create_redacted_file
from ..workspace import load_config, WORKSPACE
from ...utils.filesystem import load_data, save_data
from ...utils import imports


entity_annotator = LabelOnlyEntityAnnotator()
entity_html_annotator = HtmlEntityAnnotator()

def get_extractor() -> EntityExtractor:
    labels = imports.load_file(
        'labels',
        os.path.join(WORKSPACE, 'labels.py')
    )

    return create_entity_extractor(labels.entity_patterns, labels.kb)

def annotate_file(file_path: str) -> Annotations:
    entity_extractor = get_extractor()
    utils = imports.load_file('utils', os.path.join(WORKSPACE, 'utils.py'))

    cache = Annotations()
    text_by_label: Dict[str, Set[str]] = {}

    for row in load_data(file_path):
        text = cast(str, utils.transform_text(row))
        entities = entity_extractor.get_entities(text)

        cache.text.append(
            entity_annotator.annotate(text, entities).annotated_text
        )

        cache.html.append(
            entity_html_annotator.annotate(text, entities).annotated_text
        )

        for entity in entities:
            if not entity.label in text_by_label:
                text_by_label[entity.label] = set()

            text_by_label[entity.label].add(entity.text)

    for key, value in text_by_label.items():
        cache.text_by_label[key] = list(sorted(value))

    return cache

def annotate() -> None:
    cache = annotate_file(os.path.join(WORKSPACE, '2', 'dev.txt'))

    save_data(
        os.path.join(WORKSPACE, '3', 'dev-ents.txt'),
        cache.text
    )

    create_redacted_file(cache.text)
    create_parsed_by_file(cache.text_by_label)

    config = load_config()
    if bool(config['annotations']['enable-html']):
        create_html_file(cache.html)
