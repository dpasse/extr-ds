import sys

from .process import workspace, entities, relations
from .process import split, \
                     save_all, \
                     save_entities, \
                     save_relations


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
        print('split file')
        split()

        print('annotate entities')
        entities.annotate()

        print('annotate relations')
        relations.relate()

    elif method == '--annotate':
        type_of_save = (args[1] if len(args) > 1 else '').lower()

        if type_of_save == 'ents':
            entities.annotate()
        elif type_of_save == 'rels':
            relations.relate()
        else:
            entities.annotate()
            relations.relate()

    elif method == '--relate':
        if len(args) >= 3:
            action = args[1]
            row = args[2]

            if action == 'label':
                index, label = row.split('=')
                relations.change_label(label, int(index))

            elif action == 'delete':
                relations.delete_row(int(row))


    elif method == '--save':
        type_of_save = (args[1] if len(args) > 1 else '').lower()

        if type_of_save == 'ents':
            save_entities()
        elif type_of_save == 'rels':
            save_relations()
        else:
            save_all()

    elif method == '--reset':
        workspace.clean()

    else:
        print(f'"{method}" is not a valid command.')

    return 0
