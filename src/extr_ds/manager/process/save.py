from typing import Any, Dict

import re
import os
import json

from .workspace import WORKSPACE
from ..utils.filesystem import load_data, \
                               append_data, \
                               save_data, \
                               save_document


def entity_text_annotation_to_json(text_annotation: str) -> Dict[str, Any]:
    blob = {
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


def save_entities() -> None:
    blobs = [
        entity_text_annotation_to_json(text)
        for text in load_data(os.path.join(WORKSPACE, '3', 'dev-ents.txt'))
    ]

    current_size = 0

    blob_storage = os.path.join(WORKSPACE, '4', 'ents.json')
    if os.path.exists(blob_storage):
        with open(blob_storage, 'r', encoding='utf-8') as blob_outputs:
            current_data = json.loads(blob_outputs.read())

        current_size = len(current_data)
        blobs.extend(current_data)

    keys = set()
    dataset = []
    for blob in blobs:
        key = blob['text']
        if key in keys:
            continue

        keys.add(key)
        dataset.append(blob)

    save_data(
        os.path.join(WORKSPACE, '4', 'ents.txt'),
        list(map(lambda item: item['text'], dataset))
    )

    print('#rows:', len(dataset) - current_size)

    save_document(
        blob_storage,
        json.dumps(dataset, indent=2)
    )

    redacted_dataset = set(load_data(os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt')))
    append_data(os.path.join(WORKSPACE, '4', 'ents-redacted.txt'), redacted_dataset)

def save_relations() -> None:
    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'r', encoding='utf-8') as relation_outputs:
        data = [row for row in json.loads(relation_outputs.read()) if not 'attribute' in row]

    output_path = os.path.join(WORKSPACE, '4', 'rels.json')
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as relation_outputs:
            current_data = json.loads(relation_outputs.read())

        data.extend(current_data)

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
