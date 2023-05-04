import sys
from typing import List, Optional, Tuple, cast
from dataclasses import dataclass

from .process import workspace, entities, relations
from .process import split, \
                     save_entities, \
                     save_relations


@dataclass
class Command:
    branch: str
    sub_command: Optional[str]
    args: Optional[str]

    @property
    def has_sub_command(self) -> bool:
        return not self.sub_command is None

    @property
    def has_args(self) -> bool:
        return not self.args is None

    def get_args(self, delim='=') -> Optional[Tuple[str, List[str]]]:
        if self.has_args:
            a1, a2 = cast(str, self.args).split(delim)
            return (a1, a2.split(','))

        return None

def create_command(args: List[str]) -> Command:
    return Command(
        branch=args[0],
        sub_command=args[1] if len(args) > 1 else None,
        args=args[2] if len(args) > 2 else None
    )

def main() -> int:
    if len(sys.argv) == 1:
        return -1

    command = create_command(sys.argv[1:])

    if command.branch == '--init':
        workspace.init()

    if command.branch == '--reset':
        workspace.clean()

    if command.branch == '--split':
        split()
        entities.annotate()
        relations.relate()

    if command.branch == '--annotate':
        if not command.has_sub_command:
            return -1

        if command.sub_command == '-ents':
            ## --annotate -ents
            entities.annotate()

        if command.sub_command == '-rels':
            ## --annotate -rels
            relations.relate()

    if command.branch == '--relate':
        if not command.has_sub_command:
            return -1

        if command.sub_command == '-label':
            ## --relate -label NO_RELATION=1,3,6
            label, args = cast(Tuple[str, List[str]], command.get_args())
            for index in map(int, args):
                relations.change_label(label, index)

        if command.sub_command == '-delete':
            ## --relate -delete 1,3,6
            for index in map(int, cast(str, command.args).split(',')):
                relations.delete_row(index)

    if command.branch == '--save':
        if not command.has_sub_command:
            return -1

        if command.sub_command == '-ents':
            ## --save -ents
            save_entities()

        if command.sub_command == '-rels':
            ## --save -rels
            save_relations()

    return 0
