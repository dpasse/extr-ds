from typing import List, Set, Union

import os


def load_data(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as dev:
        dataset = [
            row
            for row in dev.read().split('\n')
            if len(row.strip()) > 0
        ]

    return dataset

def save_data(file_path: str, data: List[str]) -> None:
    sorted_data = list(
        sorted(
            filter(lambda a: len(a.strip()) > 0, data),
            key=len,
            reverse=True
        )
    )

    with open(file_path, 'w', encoding='utf-8') as output:
        output.write(
            '\n'.join(sorted_data)
        )

def append_data(file_path: str, dataset: Union[Set[str], List[str]]) -> None:
    if os.path.exists(file_path):
        for record in load_data(file_path):
            if isinstance(record, set):
                dataset.add(record)
            if isinstance(record, list):
                dataset.append(record)

    dataset = list(sorted(dataset, key=len, reverse=True))

    with open(file_path, 'w', encoding='utf-8') as dev:
        dev.write(
            '\n'.join(dataset).strip()
        )
