import os

from ..workspace import WORKSPACE
from ..filesystem import load_data, \
                         append_data


def save() -> None:
    dataset = set(load_data(os.path.join(WORKSPACE, '2', 'dev-ents.txt')))
    append_data(os.path.join(WORKSPACE, '4', 'ents.txt'), dataset)

    redacted_dataset = set(load_data(os.path.join(WORKSPACE, '3', 'dev-ents-redacted.txt')))
    append_data(os.path.join(WORKSPACE, '4', 'ents-redacted.txt'), redacted_dataset)
