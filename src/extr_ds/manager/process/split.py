import os
import random

from ..workspace import load_config, WORKSPACE
from ..filesystem import load_data, \
                         save_data


def split() -> None:
    config = load_config()

    split_config = config['split'] if 'split' in config else {}
    seed = split_config['seed'] if 'seed' in split_config else None
    partition_point = split_config['amount'] if 'amount' in split_config else 25

    source_data = load_data(
        os.path.join(WORKSPACE, '1', config['source'])
    )

    if seed:
        random.seed(seed)

    random.shuffle(source_data)

    pivot = int(len(source_data) * partition_point) if partition_point < 1 else partition_point
    development_set, holdout_set = (source_data[:pivot], source_data[pivot:])

    output_directory = os.path.join(WORKSPACE, '2')
    save_data(os.path.join(output_directory, 'dev.txt'), development_set)
    save_data(os.path.join(output_directory, 'holdouts.txt'), holdout_set)
