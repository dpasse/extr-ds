from typing import Dict, List
import re
import os
import json

from extr.relations import HtmlRelationAnnotator
from extr_ds.models import RelationLabel

from ..workspace import WORKSPACE
from ...utils.filesystem import load_document, save_document


HTML_PATH = os.path.join(WORKSPACE, '3', 'dev-rels.html')
DEV_PATH = os.path.join(WORKSPACE, '3', 'dev-rels.json')

def create_html_file(rows: List[str]) -> str:
    def get_default_styles() -> str:
        return """
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

    return """
<html>
    <head>
        <style>""" + get_default_styles() + """</style>
    </head>
    <body><table>""" + '\n'.join(rows) + """</table></body>
</html>
"""

def create_dev_files(relation_groups: Dict[str, List[RelationLabel]]) -> None:
    html_rows: List[str] = []
    ordered_relations: List[RelationLabel] = []

    index = 0
    html_annotator = HtmlRelationAnnotator()
    for key, items in relation_groups.items():
        html_rows.append(f'<tr><td class="header" colspan=3>{key}</td></tr>')
        for relation_label in items:
            text = html_annotator.annotate(
                relation_label.original_sentence,
                relation_label.relation
            )

            html_rows.append(
                f'<tr id="{index}"><td>{index}</td><td class="label">{relation_label.relation.label}</td><td>{text}</td></tr>'
            )

            ordered_relations.append(relation_label)

            index += 1

    save_document(
        DEV_PATH,
        json.dumps(
            list(map(lambda relation: relation.todict(), ordered_relations)),
            indent=2
        )
    )

    save_document(
        HTML_PATH,
        create_html_file(html_rows)
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
            'label': label
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
        }

    save_document(DEV_PATH, json.dumps(dev, indent=2))
