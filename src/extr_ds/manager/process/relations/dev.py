from typing import Dict, List
import re
import os
import json

from extr.relations.viewers import HtmlViewer
from extr_ds.models import RelationLabel

from ..workspace import WORKSPACE
from ...utils.filesystem import load_document, save_document


HTML_PATH = os.path.join(WORKSPACE, '3', 'dev-rels.html')
DEV_PATH = os.path.join(WORKSPACE, '3', 'dev-rels.json')

def create_dev_files(relation_groups: Dict[str, List[RelationLabel]]) -> None:
    viewer = HtmlViewer()
    ordered_relations: List[RelationLabel] = []
    for key, items in relation_groups.items():
        viewer.append_header(header=key)
        for relation_label in items:
            viewer.append_relation(
                text=relation_label.original_sentence,
                relation=relation_label.relation
            )

            ordered_relations.append(relation_label)

    save_document(
        DEV_PATH,
        json.dumps(
            list(map(lambda relation: relation.todict(), ordered_relations)),
            indent=2
        )
    )

    save_document(
        HTML_PATH,
        viewer.create_view()
    )

def change_label(label: str, rows: List[int]) -> None:
    html = load_document(HTML_PATH)
    for row in rows:
        html = re.sub(
            r'(<tr id="' + str(row) + '"><td>' + str(row) + '</td><td class="label">)(.+?)(</td>)',
            r'\1' + label + r'\3',
            html
        )

    save_document(HTML_PATH, html)

    dev = json.loads(load_document(DEV_PATH))
    for row in rows:
        dev[row] = {
            'sentence': dev[row]['sentence'],
            'label': label,
            'definition': dev[row]['definition'],
        }

    save_document(DEV_PATH, json.dumps(dev, indent=2))

def delete_row(rows: List[int]) -> None:
    html = load_document(HTML_PATH)
    for row in rows:
        html = re.sub(
            r'(<tr )(id="' + str(row) + '")',
            r'\1class="delete" \2',
            html
        )

    save_document(HTML_PATH, html)

    dev = json.loads(load_document(DEV_PATH))
    for row in rows:
        dev[row] = {
            'sentence': dev[row]['sentence'],
            'label': dev[row]['label'],
            'definition': dev[row]['definition'],
            'attribute': 'delete',
        }

    save_document(DEV_PATH, json.dumps(dev, indent=2))

def recover_row(rows: List[int]) -> None:
    html = load_document(HTML_PATH)
    for row in rows:
        html = re.sub(
            r'(<tr) class="delete" (id="' + str(row) + '")',
            r'\1 \2',
            html
        )

    save_document(HTML_PATH, html)

    dev = json.loads(load_document(DEV_PATH))
    for row in rows:
        dev[row] = {
            'sentence': dev[row]['sentence'],
            'label': dev[row]['label'],
            'definition': dev[row]['definition'],
        }

    save_document(DEV_PATH, json.dumps(dev, indent=2))
