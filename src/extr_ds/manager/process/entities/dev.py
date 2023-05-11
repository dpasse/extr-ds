from typing import Dict, List, Set
import os
import re
import json

from ..workspace import load_config, WORKSPACE
from ...utils.filesystem import load_data, save_data, save_document, load_document


def create_redacted_file(annotations: List[str]) -> None:
    def get_redacted_templates() -> Set[str]:
        redacted_templates = set()
        redacted_templates_file_path = os.path.join(WORKSPACE, '4', 'ents-redacted.txt')
        if os.path.exists(redacted_templates_file_path):
            redacted_templates = set(load_data(redacted_templates_file_path))

        return redacted_templates

    redactions: List[str] = [
        re.sub(' +', ' ', re.sub(r'<[A-Z]+>.+?</[A-Z]+>', ' ', row))
        for row in annotations
    ]

    config = load_config()
    if bool(config['annotations']['filter-redactions']):
        redacted_templates = get_redacted_templates()
        redactions = [row for row in redactions if not row in redacted_templates]

    save_data(
        os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt'),
        redactions
    )

def create_parsed_by_file(text_by_label: Dict[str, List[str]]) -> None:
    stats_path = os.path.join(WORKSPACE, '3', 'dev-ents.stats.json')
    with open(stats_path, 'w', encoding='UTF8') as dev_stats:
        dev_stats.write(json.dumps(text_by_label, indent=2))

def create_html_file(annotations: List[str]) -> None:
    styles = """
p { margin: 5px; line-height: 45px; }
span.entity { border: 1px solid black; border-radius: 5px; padding: 5px; margin: 3px; cursor: pointer; }
span.label { font-weight: bold; padding: 3px; color: black; }
"""

    custom_styles_path = os.path.join(WORKSPACE, 'styles.css')
    if os.path.exists(custom_styles_path):
        styles += load_document(custom_styles_path)

    rows = '<hr />\n'.join(
        [f'<p>{annotation}</p>' for annotation in annotations]
    )

    save_document(
        os.path.join(WORKSPACE, '3', 'dev-ents.html'),
        """
<html>
    <head>
        <style>
            """ + \
            styles + \
            """
        </style>
    </head>
    <body>""" + rows + """</body>
</html>
"""
    )
