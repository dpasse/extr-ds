from typing import Any, Dict
import os
import json

from .workspace import WORKSPACE
from ..utils.filesystem import load_data, \
                               append_data


def save_entities() -> None:
    dataset = set(load_data(os.path.join(WORKSPACE, '2', 'dev.txt')))
    rows = append_data(os.path.join(WORKSPACE, '4', 'ents.txt'), dataset)

    print('#rows:', rows)

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

    with open(output_path, 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(json.dumps(slim_data, indent=2))

    print('#rows:', len(slim_data))
