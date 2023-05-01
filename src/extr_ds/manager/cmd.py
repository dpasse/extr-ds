import sys

from .process import workspace
from .process import split, annotate, relate, save


def main() -> int:
    if len(sys.argv) == 1:
        return -1

    args = sys.argv[1:]
    method = args[0]

    if method == '--init':
        workspace.init()

    elif method == '--reset':
        workspace.clean()

    elif method == '--split':
        split()
        annotate()

    elif method == '--annotate':
        annotate()

    elif method == '--relate':
        relate()

    elif method == '--save':
        save()

    elif method == '--reset':
        workspace.clean()

    else:
        print(f'"{method}" is not a valid command.')

    return 0
