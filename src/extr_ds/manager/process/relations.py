from typing import Dict, List
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

utils = imports.load_file(
    'utils',
    os.path.join(WORKSPACE, 'utils.py')
)

def get_labeler() -> RelationClassification:
    labels = imports.load_file(
        'labels',
        os.path.join(WORKSPACE, 'labels.py')
    )

    entity_extractor = create_entity_extractor(labels.entity_patterns, labels.kb)
    relation_extractor = RelationExtractor(labels.relation_patterns)

    return RelationClassification(
        utils.sentence_tokenizer,
        entity_extractor,
        relation_extractor,
        labels.relation_defaults,
    )

def relate() -> None:
    labeler = get_labeler()

    relation_groups: Dict[str, List[RelationLabel]] = {}
    for row in load_data(os.path.join(WORKSPACE, '2', 'dev.txt')):
        text = utils.transform_text(row)
        for relation_label in labeler.label(text):
            if not relation_label.definition in relation_groups:
                relation_groups[relation_label.definition] = []

            relation_groups[relation_label.definition].append(relation_label)

    rows = []
    blobs = []

    ## make html work off of dev-rels.json file somehow...
    ## instead of removing data just add a class to the row?
    ## to flip a label, just update the row?

    index = 0
    html_annotator = HtmlRelationAnnotator()
    for key, items in relation_groups.items():
        rows.append(f'<tr><td class="header" colspan=3>{key}</td></tr>')
        for relation_label in items:
            text = html_annotator.annotate(
                re.sub(r'</?e\d+>', '', relation_label.sentence),
                relation_label.relation
            )

            row_id = str(index)
            rows.append(f'<tr id="{row_id}"><td>{row_id}</td><td class="label">{relation_label.relation.label}</td><td>{text}</td></tr>')
            blobs.append(relation_label.todict())

            index += 1

    styles = """
span.entity { border: 1px solid black; border-radius: 5px; padding: 5px; margin: 3px; cursor: pointer; }
span.label { font-weight: bold; padding: 3px; color: black; }
span.e1 { background-color: aqua; }
span.e2 { background-color: coral; }
td { line-height: 30px; border: 1px solid black; padding: 5px; }
td.header { font-weight: bold; }
td.label { font-weight: bold; text-align: center; }
"""

    html = """
<html>
    <head>
        <style>""" + styles + """</style>
    </head>
    <body><table>""" + '\n'.join(rows) + """</table></body>
</html>
"""

    html_path = os.path.join(WORKSPACE, '3', 'dev-rels.html')
    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html)

    with open(os.path.join(WORKSPACE, '3', 'dev-rels.json'), 'w', encoding='utf-8') as relation_outputs:
        relation_outputs.write(json.dumps(blobs, indent=2))
