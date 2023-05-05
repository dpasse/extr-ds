from typing import Callable, Dict, List
import re
import os
import json

from extr.entities import create_entity_extractor
from extr.relations import RelationExtractor, HtmlRelationAnnotator
from extr_ds.models import RelationLabel
from extr_ds.labelers import RelationClassification

from .workspace import WORKSPACE
from ..utils.filesystem import load_data
from ..utils import imports


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

def create_html_file(relation_groups: Dict[str, List[RelationLabel]]) -> List[RelationLabel]:
    html_rows: List[str] = []
    ordered_relations: List[RelationLabel] = []

    index = 0
    html_annotator = HtmlRelationAnnotator()
    for key, items in relation_groups.items():
        html_rows.append(f'<tr><td class="header" colspan=3>{key}</td></tr>')
        for relation_label in items:
            text = html_annotator.annotate(
                re.sub(r'</?e\d+>', '', relation_label.sentence),
                relation_label.relation
            )

            row_id = str(index)
            html_rows.append(
                f'<tr id="{row_id}"><td>{row_id}</td><td class="label">{relation_label.relation.label}</td><td>{text}</td></tr>'
            )

            ordered_relations.append(relation_label)

            index += 1

    styles = """
span.entity { border: 1px solid black; border-radius: 5px; padding: 5px; margin: 3px; cursor: pointer; }
span.label { font-weight: bold; padding: 3px; color: black; }
span.e1 { background-color: aqua; }
span.e2 { background-color: coral; }
tr.delete { background-color: black !important; }
tr.delete span { background-color: black !important; }
td { line-height: 30px; border: 1px solid black; padding: 5px; }
td.header { font-weight: bold; }
td.label { font-weight: bold; text-align: center; }
"""

    html = """
<html>
    <head>
        <style>""" + styles + """</style>
    </head>
    <body><table>""" + '\n'.join(html_rows) + """</table></body>
</html>
"""

    html_path = os.path.join(WORKSPACE, '3', 'dev-rels.html')
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html)

    return ordered_relations

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

    ordered_relations = create_html_file(relation_groups)

    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(
            json.dumps(
                list(map(lambda relation: relation.todict(), ordered_relations)),
                indent=2
            )
        )

def change_label(label: str, rows: List[int]) -> None:
    html_path = os.path.join(WORKSPACE, '3', 'dev-rels.html')
    with open(html_path, 'r', encoding='utf-8') as html_file:
        html = html_file.read()

    for row in rows:
        html = re.sub(
            r'(<tr id="' + str(row) + '"><td>' + str(row) + '</td><td class="label">)(.+?)(</td>)',
            r'\1' + label + r'\3',
            html
        )

    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html)

    dev_path = os.path.join(WORKSPACE, '3', 'dev-rels.json')
    with open(dev_path, 'r', encoding='utf-8') as relation_outputs:
        dev = json.loads(relation_outputs.read())

    for row in rows:
        dev[row] = {
            'sentence': dev[row]['sentence'],
            'label': label
        }

    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(json.dumps(dev, indent=2))

def delete_row(rows: List[int]) -> None:
    html_path = os.path.join(WORKSPACE, '3', 'dev-rels.html')
    with open(html_path, 'r', encoding='utf-8') as html_file:
        html = html_file.read()

    for row in rows:
        html = re.sub(
            r'(<tr )(id="' + str(row) + '")',
            r'\1class="delete" \2',
            html
        )

    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html)

    dev_path = os.path.join(WORKSPACE, '3', 'dev-rels.json')
    with open(dev_path, 'r', encoding='utf-8') as relation_outputs:
        dev = json.loads(relation_outputs.read())

    for row in rows:
        dev[row] = {
            'sentence': dev[row]['sentence'],
            'label': dev[row]['label'],
            'attribute': 'delete',
        }

    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(json.dumps(dev, indent=2))

def recover_row(rows: List[int]) -> None:
    html_path = os.path.join(WORKSPACE, '3', 'dev-rels.html')
    with open(html_path, 'r', encoding='utf-8') as html_file:
        html = html_file.read()

    for row in rows:
        html = re.sub(
            r'(<tr) class="delete" (id="' + str(row) + '")',
            r'\1 \2',
            html
        )

    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html)

    dev_path = os.path.join(WORKSPACE, '3', 'dev-rels.json')
    with open(dev_path, 'r', encoding='utf-8') as relation_outputs:
        dev = json.loads(relation_outputs.read())

    for row in rows:
        dev[row] = {
            'sentence': dev[row]['sentence'],
            'label': dev[row]['label'],
        }

    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(json.dumps(dev, indent=2))
