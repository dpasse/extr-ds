import os
import re
from types import ModuleType
from typing import List, Dict, Set, cast, Union
import sys
import json
import random
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

from extr.entities import create_entity_extractor, LabelOnlyEntityAnnotator, HtmlEntityAnnotator

from .filesystem import load_config, \
                       save_config, \
                       load_data, \
                       save_data, \
                       append_data, \
                       WORKSPACE


def init() -> None:
    config = {
        'source': 'source.txt',
        'split': {
            'amount': 25
        },
    }

    print()
    print('INIT')
    print('WORKSPACE:', WORKSPACE)
    print('SOURCE:', os.path.join('1', 'source.txt'))

    for folder in ['1', '2', '3', '4']:
        directory = os.path.join(WORKSPACE, folder)
        if not os.path.exists(directory):
            os.mkdir(directory)

    with open(os.path.join(WORKSPACE, '1', 'source.txt'), 'w', encoding='UTF8') as source_file:
        source_file.write('')

    with open(os.path.join(WORKSPACE, 'labels.py'), 'w', encoding='UTF8') as labels_file:
        labels_file.write("""from typing import Dict, List
import re

from extr.regexes import RegEx, RegExLabel


kb: Dict[str, List[str]]= {}
entity_patterns: List[RegExLabel] = []
""")

    with open(os.path.join(WORKSPACE, 'utils.py'), 'w', encoding='UTF8') as utils_file:
        utils_file.write("""from typing import List


def sentence_tokenizer(text: str) -> List[List[str]]:
    return [
        text.split(' ')
    ]

def transform_text(text: str) -> str:
    return text
""")

    save_config(config)

def split() -> None:
    config = load_config()

    source_path = os.path.join(WORKSPACE, '1', config['source'])
    source_data = load_data(source_path)

    split_config = config['split']

    if 'seed' in split_config:
        random.seed(split_config['seed'])

    random.shuffle(source_data)

    pivot = split_config['amount']
    if split_config['amount'] < 1:
        pivot = int(len(source_data) * split_config['amount'])

    development_set, holdout_set = (source_data[:pivot], source_data[pivot:])

    output_directory = os.path.join(WORKSPACE, '2')
    save_data(os.path.join(output_directory, 'dev.txt'), development_set)
    save_data(os.path.join(output_directory, 'holdouts.txt'), holdout_set)

def annotate() -> None:
    def get_redacted_templates() -> Set[str]:
        redacted_templates = set()
        redacted_templates_file_path = os.path.join(WORKSPACE, '4', 'ents-redacted.txt')
        if os.path.exists(redacted_templates_file_path):
            redacted_templates = set(load_data(redacted_templates_file_path))
        return redacted_templates

    def load_file(name: str) -> ModuleType:
        path = os.path.join(WORKSPACE, f'{name}.py')

        print(
            path,
            os.path.exists(path)
        )

        spec = spec_from_loader(name, SourceFileLoader(name, path))
        if spec is None:
            raise TypeError('SPEC IS NONE')

        if spec.loader is None:
            raise TypeError('SPEC LOADER IS NONE')

        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)

        return mod

    labels = load_file('labels')
    utils = load_file('utils')

    entity_extractor = create_entity_extractor(labels.entity_patterns, labels.kb)
    entity_annotator = LabelOnlyEntityAnnotator()
    entity_html_annotator = HtmlEntityAnnotator()

    text_annotations: List[str] = []
    html_annotations: List[str] = []
    extracted_text_by_label: Dict[str, Union[List[str], Set[str]]] = {}

    for row in load_data(os.path.join(WORKSPACE, '2', 'dev.txt')):
        text = cast(str, utils.transform_text(row))

        entities = entity_extractor.get_entities(text)
        annotation_result = entity_annotator.annotate(text, entities)
        text_annotations.append(
            annotation_result.annotated_text
        )

        html_annotations.append(
            '<p>' + entity_html_annotator.annotate(text, entities).annotated_text + '</p>'
        )

        for entity in entities:
            if not entity.label in extracted_text_by_label:
                extracted_text_by_label[entity.label] = set()

            cast(set, extracted_text_by_label[entity.label]).add(entity.text)

    save_data(os.path.join(WORKSPACE, '3', 'dev-ents.txt'), text_annotations)

    redacted_templates = get_redacted_templates()
    save_data(
        os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt'),
        [
            row
            for _, row in (
                (i, re.sub(' +', ' ', re.sub(r'<[A-Z]+>.+?</[A-Z]+>', ' ', row)))
                for i, row
                in enumerate(text_annotations)
            )
            if not row in redacted_templates
        ],
    )

    for key, value in extracted_text_by_label.items():
        extracted_text_by_label[key] = list(sorted(value))

    stats_path = os.path.join(WORKSPACE, '3', 'dev-ents.stats.json')
    with open(stats_path, 'w', encoding='UTF8') as dev_stats:
        dev_stats.write(json.dumps(extracted_text_by_label, indent=2))

    html_path = os.path.join(WORKSPACE, '3', 'dev-ents.html')
    with open(html_path, 'w', encoding='UTF8') as html_file:
        rows = '\n'.join(html_annotations)
        html_file.write("""
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
""")

def save() -> None:
    dataset = set(load_data(os.path.join(WORKSPACE, '2', 'dev-ents.txt')))
    append_data(os.path.join(WORKSPACE, '4', 'ents.txt'), dataset)

    redacted_dataset = set(load_data(os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt')))
    append_data(os.path.join(WORKSPACE, '4', 'ents-redacted.txt'), redacted_dataset)

def reset() -> None:
    files = [
        os.path.join(WORKSPACE, '4', 'ents.txt'),
        os.path.join(WORKSPACE, '4', 'ents-redacted.txt')
    ]

    for file in files:
        if os.path.exists(file):
            os.remove(file)

def main() -> int:
    if len(sys.argv) == 1:
        return -1

    args = sys.argv[1:]
    method = args[0]

    if method == '--init':
        init()

    elif method == '--split':
        split()
        annotate()

    elif method == '--annotate':
        annotate()

    elif method == '--save':
        save()

    elif method == '--reset':
        reset()

    else:
        print(f'"{method}" is not a valid command.')

    return 0
