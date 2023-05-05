import os
import random

from .workspace import load_config, WORKSPACE
from ..utils.filesystem import load_data, \
                               save_data


def split() -> None:
    config = load_config()

    seed = config['split']['seed']
    split_point = config['split']['amount']

    source_data = load_data(
        os.path.join(WORKSPACE, '1', config['source'])
    )

    if seed:
        random.seed(seed)

    random.shuffle(source_data)

    pivot = int(len(source_data) * split_point) if split_point < 1 else split_point
    development_set, holdout_set = (source_data[:pivot], source_data[pivot:])

    output_directory = os.path.join(WORKSPACE, '2')
    save_data(os.path.join(output_directory, 'dev.txt'), development_set)
    save_data(os.path.join(output_directory, 'holdouts.txt'), holdout_set)
