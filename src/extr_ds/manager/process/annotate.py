from typing import Dict, List, Set, cast
import os
import re
import json
from dataclasses import dataclass, field

from extr.entities import create_entity_extractor, LabelOnlyEntityAnnotator, HtmlEntityAnnotator, EntityExtractor

from .. import imports
from ..workspace import load_config, WORKSPACE
from ..filesystem import load_data, \
                       save_data


entity_annotator = LabelOnlyEntityAnnotator()
entity_html_annotator = HtmlEntityAnnotator()

def get_extractor() -> EntityExtractor:
    labels = imports.load_file(
        'labels',
        os.path.join(WORKSPACE, 'labels.py')
    )

    return create_entity_extractor(labels.entity_patterns, labels.kb)

@dataclass()
class Annotations:
    text: List[str] = field(default_factory=lambda: [])
    html: List[str] = field(default_factory=lambda: [])
    text_by_label: Dict[str, List[str]] = field(default={})

def annotate_file(file_path: str) -> Annotations:
    entity_extractor = get_extractor()
    utils = imports.load_file('utils', os.path.join(WORKSPACE, 'utils.py'))

    cache = Annotations()
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
            if not entity.label in cache.text_by_label:
                cache.text_by_label[entity.label] = []

            cache.text_by_label[entity.label].append(entity.text)

    return cache

def create_redacted_file(annotations: List[str]) -> None:
    def get_redacted_templates() -> Set[str]:
        redacted_templates = set()
        redacted_templates_file_path = os.path.join(WORKSPACE, '4', 'ents-redacted.txt')
        if os.path.exists(redacted_templates_file_path):
            redacted_templates = set(load_data(redacted_templates_file_path))

        return redacted_templates

    config = load_config()
    annotations_config = config['annotations'] if 'annotations' in config else {}

    redactions: List[str] = [
        re.sub(' +', ' ', re.sub(r'<[A-Z]+>.+?</[A-Z]+>', ' ', row))
        for row in annotations
    ]

    if annotations_config['filter-redactions'] if 'filter-redactions' in annotations_config else True:
        redacted_templates = get_redacted_templates()
        redactions = [row for row in redactions if not row in redacted_templates]

    save_data(
        os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt'),
        redactions
    )

def create_parsed_by_file(text_by_label: Dict[str, List[str]]) -> None:
    for key, value in text_by_label.items():
        text_by_label[key] = list(sorted(set(value)))

    stats_path = os.path.join(WORKSPACE, '3', 'dev-ents.stats.json')
    with open(stats_path, 'w', encoding='UTF8') as dev_stats:
        dev_stats.write(json.dumps(text_by_label, indent=2))

def create_html_file(annotations: List[str]) -> None:
    rows = '\n'.join(
        [f'<p>{annotation}</p>' for annotation in annotations]
    )

    html = """
<html>
    <head>
        <style>
            p {
                margin: 5px;
                line-height: 45px;
            }

            span.entity {
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px;
                margin: 3px;
                color: gray;
                cursor: pointer;
            }

            span.label {
                font-weight: bold;
                padding: 3px;
                color: black;
            }
        </style>
    </head>
    <body>""" + rows + """</body>
</html>
"""
    html_path = os.path.join(WORKSPACE, '3', 'dev-ents.html')
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html)

def annotate() -> None:
    cache = annotate_file(os.path.join(WORKSPACE, '2', 'dev.txt'))

    save_data(
        os.path.join(WORKSPACE, '3', 'dev-ents.txt'),
        cache.text
    )

    create_redacted_file(cache.text)
    create_parsed_by_file(cache.text_by_label)

    config = load_config()
    annotations_config = config['annotations'] if 'annotations' in config else {}
    if annotations_config['enable-html'] if 'enable-html' in annotations_config else True:
        create_html_file(cache.html)
