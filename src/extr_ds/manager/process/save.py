from typing import Any, Dict, cast, Callable, List, Set

import re
import os
import json

from extr import Entity, Location
from .workspace import WORKSPACE, load_config
from ...labelers.iob import Labeler
from ..utils import imports
from ..utils.filesystem import load_data, \
                               append_data, \
                               save_document, \
                               load_document


def entity_text_annotation_to_json(text_annotation: str) -> Dict[str, Any]:
    blob: Dict[str, Any] = {
        'text': text_annotation,
        'entities': []
    }

    while True:
        match = re.search(r'(<(\w+?)>.+?</\w+>)', blob['text'])
        if match is None:
            break

        start, match_end = match.span()
        entity_text = re.sub(r'</?\w+>', '', match.group(1))
        label = match.group(2)

        blob['entities'].append(
            {
                'start': start,
                'end': start + len(entity_text),
                'label': label,
                'text': entity_text
            }
        )

        blob['text'] = blob['text'][:start] + entity_text + blob['text'][match_end:]

    return blob

def blob_to_entity(identifier: int, blob: Dict[str, Any]) -> Entity:
    return Entity(
        identifier=identifier,
        label=blob['label'],
        text=blob['text'],
        location=Location(start=blob['start'], end=blob['end'])
    )

def output_iob_for_entities(blobs: List[Dict[str, Any]]) -> None:
    def format_blob_storage(blobs: str) -> str:
        text = re.sub(r'(?<=\[)\n +', '', blobs)
        text = re.sub(r'\n +(?=\])', '', text)
        text = re.sub(r'(?<=",)\n +', '', text)
        return text

    iob_dataset: List[Dict[str, List[str]]] = []

    utils = imports.load_file('utils', os.path.join(WORKSPACE, 'utils.py'))
    iob_labeler = Labeler(
        cast(Callable[[str], List[str]], utils.word_tokenizer)
    )

    for i, blob in enumerate(blobs):
        try:
            entities = []
            for i, item in enumerate(blob['entities']):
                entities.append(
                    blob_to_entity(i+1, item)
                )

            label = iob_labeler.label(blob['text'], entities)
            iob_dataset.append(
                {
                    'tokens': [tk.text for tk in label.tokens],
                    'labels': label.labels
                }
            )
        except:
            print('* record', i, 'in `ents.json` could not be converted to iob.')
            print(' - please check your `utils.word_tokenizer` method to ensure singular tokens.')

    save_document(
        os.path.join(WORKSPACE, '4', 'ents-iob.json'),
        format_blob_storage(json.dumps(iob_dataset, indent=2))
    )

def uniq(blobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    keys: Set[str] = set()

    dataset: List[Dict[str, Any]] = []
    for blob in blobs:
        key = cast(str, blob['text'])
        if key in keys:
            continue

        keys.add(key)
        dataset.append(blob)

    return dataset

def save_entities() -> None:
    blob_storage = os.path.join(WORKSPACE, '4', 'ents.json')

    blobs = [
        entity_text_annotation_to_json(text)
        for text in load_data(os.path.join(WORKSPACE, '3', 'dev-ents.txt'))
    ]

    blobs.extend(
        json.loads(load_document(blob_storage, default_value='[]'))
    )

    dataset = uniq(blobs)

    save_document(
        blob_storage,
        json.dumps(dataset, indent=2)
    )

    config = load_config()['annotations']
    if config['output-iob']:
        output_iob_for_entities(dataset)

    append_data(
        os.path.join(WORKSPACE, '4', 'ents-redacted.txt'),
        set(
            load_data(os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt'))
        )
    )

def save_relations() -> None:
    data = [
        row
        for row in json.loads(
            load_document(os.path.join(WORKSPACE, '3', 'dev-rels.json'), '[]')
        )
        if not 'attribute' in row
    ]

    output_path = os.path.join(WORKSPACE, '4', 'rels.json')
    data.extend(
        json.loads(load_document(output_path, '[]'))
    )

    lookup: Dict[str, Dict[str, Any]] = {}
    for row in data:
        key = row['sentence'].lower()
        if not key in lookup:
            lookup[key] = { 'labels': set(), 'items': [] }

        lookup[key]['labels'].add(row['label'])
        lookup[key]['items'].append(row)

    slim_data = []
    for key, item in lookup.items():
        labels = item['labels']
        items = item['items']

        if len(labels) == 1:
            slim_data.append(items[0])
        else:
            print('Label mismatch found (skipping):')
            print('sentence:', items[0]['sentence'])
            print('labels:', ', '.join(labels))
            print()

    save_document(
        output_path,
        json.dumps(slim_data, indent=2)
    )

    print('#rows:', len(slim_data))
